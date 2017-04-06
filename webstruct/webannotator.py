"""
:mod:`webstruct.webannotator` provides functions for working with HTML
pages annotated with WebAnnotator_ Firefox extension.

.. _WebAnnotator: https://github.com/xtannier/WebAnnotator
"""
from __future__ import absolute_import
import re
import warnings
import random
from copy import deepcopy
from collections import defaultdict, OrderedDict
import xml.sax.handler
import lxml.sax
from lxml import html
from lxml.etree import Element, LXML_VERSION

from webstruct.utils import html_document_fromstring


DEFAULT_COLORS = [
    # foreground, background
    ("#000000", "#33CCFF"),
    ("#000000", "#FF0000"),
    ("#000000", "#33FF33"),
    ("#000000", "#CC66CC"),
    ("#000000", "#FF9900"),
    ("#000000", "#99FFFF"),
    ("#000000", "#FF6666"),
    ("#000000", "#66FF99"),
    ("#FFFFFF", "#3333FF"),
    ("#FFFFFF", "#660000"),
    ("#FFFFFF", "#006600"),
    ("#FFFFFF", "#663366"),
    ("#FFFFFF", "#993300"),
    ("#FFFFFF", "#336666"),
    ("#FFFFFF", "#666600"),
    ("#FFFFFF", "#009900"),
]


def _get_colors(index):
    try:
        return DEFAULT_COLORS[index]
    except IndexError:
        fg = random.choice(["#000000", "#FFFFFF"])
        bg = "#" + "".join(random.choice("01234567890ABCDEF") for x in range(6))
        return fg, bg


class EntityColors(defaultdict):
    """
    ``{"entity_name": ("fg_color", "bg_color", entity_index)}`` mapping
    that generates entries for new entities on first access.
    """
    def __init__(self, **kwargs):
        self.next_index = len(kwargs)
        super(EntityColors, self).__init__(self._new_item_factory, **kwargs)

    def _new_item_factory(self):
        fg, bg = _get_colors(self.next_index)
        self.next_index += 1
        return fg, bg, self.next_index-1

    @classmethod
    def from_htmlfile(cls, path, encoding=None):
        """ Load the color mapping from WebAnnotator-annotated HTML file """
        with open(path, 'rb') as f:
            return cls.from_htmlbytes(f.read(), encoding=encoding)

    @classmethod
    def from_htmlbytes(cls, html_bytes, encoding=None):
        colors = cls()
        tree = html_document_fromstring(html_bytes, encoding=encoding)
        for wa_color in tree.xpath('//wa-color'):
            assert wa_color.get('id').lower().startswith('wa-color-')
            idx = int(wa_color.get('id')[len("WA-color-"):])
            fg = wa_color.get('fg')
            bg = wa_color.get('bg')
            typ = wa_color.get('type')
            colors[typ] = (fg, bg, idx)
        return colors


def apply_wa_title(tree):
    """
    Replace page's ``<title>`` contents with a contents of
    ``<wa-title>`` element and remove ``<wa-title>`` tag.

    WebAnnotator > 1.14 allows annotation of ``<title>`` contents;
    it is stored after body in ``<wa-title>`` elements.
    """
    for wa_title in tree.xpath('//wa-title'):
        titles = tree.xpath('//title')
        if not titles:
            wa_title.drop_tree()
            return
        title = titles[0]
        head = title.getparent()
        head.insert(head.index(title), wa_title)
        title.drop_tree()
        wa_title.tag = 'title'
        return


class _WaContentHandler(xml.sax.handler.ContentHandler):

    TAG_SPLIT_RE = re.compile(r'\s?(__(?:START|END)_(?:\w+)__)\s?')
    TAG_PARSE_RE = re.compile(r'__(START|END)_(\w+)__')

    def __init__(self, entity_colors=None):
        self.idx = 0
        self.entity = None
        self.text_buf = []
        self.out = lxml.sax.ElementTreeContentHandler(makeelement=html.Element)
        if entity_colors is None:
            entity_colors = EntityColors()
        self.entity_colors = entity_colors

    def startElementNS(self, name, qname, attributes):
        self._flush()
        self._closeSpan()
        # print('start %s' % qname)
        self.out.startElementNS(name, qname, attributes)
        self._openSpan()

    def endElementNS(self, name, qname):
        self._flush()
        self._closeSpan()
        # print('end %s' % qname)
        self.out.endElementNS(name, qname)
        self._openSpan()
        # print("")

    def characters(self, data):
        self.text_buf.append(data)

    def startDocument(self):
        self.out.startDocument()

    def endDocument(self):
        self.out.endDocument()

    def _flush(self):
        self.text = ''.join(self.text_buf)
        self.text_buf = []
        if self.text:
            tokens = self.TAG_SPLIT_RE.split(self.text)
            for token in tokens:
                m = self.TAG_PARSE_RE.match(token.strip())
                if m:
                    event, entity = m.groups()
                    if event == 'START':
                        self.entity = entity
                        self._openSpan()
                    elif event == 'END':
                        assert entity == self.entity
                        self._closeSpan()
                        self.idx += 1
                        self.entity = None
                else:
                    self.out.characters(token)
                    # print("write %r" % token)

    def _closeSpan(self):
        if self.entity:
            # print('close span %s' % self.entity)
            self.out.endElement('span')

    def _openSpan(self):
        if self.entity:
            # print('open span %s' % self.entity)
            fg, bg, entity_idx = self.entity_colors[self.entity]
            attrs = OrderedDict([
                ('wa-id', str(self.idx)),
                ('wa-type', str(self.entity)),
                ('wa-subtypes', ''),
                ('style', 'color:%s; background-color:%s;' % (fg, bg)),
                ('class', 'WebAnnotator_%s' % self.entity),
            ])
            self.out.startElement('span', _fix_sax_attributes(attrs))


def _fix_sax_attributes(attrs):
    """ Fix sax startElement attributes for lxml < 3.1.2 """
    if LXML_VERSION >= (3, 1, 2):
        return attrs
    items = [((None, key), value) for key, value in attrs.items()]
    return OrderedDict(items)


def _add_wacolor_elements(tree, entity_colors):
    """
    Add <wa-color> elements after <body>::

        <wa-color id="WA-color-0" bg="#33CCFF" fg="#000000" class="WebAnnotator_ORG" type="ORG">

    """
    body = tree.find('.//body')
    if body is None:
        warnings.warn("html has no <body>, <wa-color> elements are not added")
        return

    for wa_color in tree.xpath('//wa-color'):
        wa_color.drop_tree()

    items = sorted(entity_colors.items(), key=lambda it: -it[1][2])
    for ent, (fg, bg, idx) in items:
        attrs = OrderedDict([
            ('id', "WA-color-%s" % idx),
            ('bg', bg),
            ('fg', fg),
            ('class', "WebAnnotator_%s" % ent),
            ('type', ent),
        ])
        wa_color = Element("wa-color", attrs)
        body.addnext(wa_color)


def _copy_title(tree):
    # <wa-title style="box-shadow:0 0 1em black;border:2px solid blue;padding:0.5em;">Contact</wa-title>
    title = tree.find('.//title')
    if title is None:
        return

    body = tree.find('.//body')
    if body is None:
        warnings.warn("html has no <body>, <wa-title> element is not added")
        return

    for wa_title in tree.xpath('//wa-title'):
        wa_title.drop_tree()

    wa_title = deepcopy(title)
    wa_title.tag = 'wa-title'
    wa_title.set('style', 'box-shadow:0 0 1em black;border:2px solid blue;padding:0.5em;')
    body.addnext(wa_title)

    text = title.xpath('string()')
    title.clear()
    title.text = text


def _ensure_head(tree):
    """ Insert <head> element if it is missing. """
    heads = tree.xpath('//head')
    if heads:
        return heads[0]
    htmls = tree.xpath('//html')
    root = htmls[0] if htmls else tree.root
    head = Element("head")
    root.insert(0, head)
    return head


def _set_base(tree, baseurl):
    """ 
    Add <base> tag to the tree. If <base> tag already exists do nothing.
    """
    if tree.xpath('//base'):
        return
    head = _ensure_head(tree)
    head.insert(0, Element("base", href=baseurl))


def to_webannotator(tree, entity_colors=None, url=None):
    """
    Convert a tree loaded by one of WebStruct loaders to WebAnnotator format.

    If you want a predictable colors assignment use ``entity_colors`` argument;
    it should be a mapping ``{'entity_name': (fg, bg, entity_idx)}``;
    entity names should be lowercased. You can use :class:`EntityColors`
    to generate this mapping automatically:

    >>> from webstruct.webannotator import EntityColors, to_webannotator
    >>> # trees = ...
    >>> entity_colors = EntityColors()
    >>> wa_trees = [to_webannotator(tree, entity_colors) for tree in trees]  # doctest: +SKIP

    """
    handler = _WaContentHandler(entity_colors)
    lxml.sax.saxify(tree, handler)
    tree = handler.out.etree
    _copy_title(tree)
    _add_wacolor_elements(tree, handler.entity_colors)
    if url is not None:
        _set_base(tree, url)
    return tree
