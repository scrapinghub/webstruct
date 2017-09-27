"""
:mod:`webstruct.webannotator` provides functions for working with HTML
pages annotated with WebAnnotator_ Firefox extension.

.. _WebAnnotator: https://github.com/xtannier/WebAnnotator
"""
from __future__ import absolute_import
import re
import warnings
import random
import itertools
from copy import deepcopy
from collections import defaultdict, OrderedDict, namedtuple
from lxml import etree
from lxml.etree import Element, LXML_VERSION
import six

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
        for attr in  wa_title.attrib:
            wa_title.attrib.pop(attr)
        return


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

TagPosition = namedtuple('TagPosition', ['element',
                                         'tag',
                                         'position',
                                         'length',
                                         'is_tail',
                                         'dfs_number'])
def translate_to_dfs(positions, ordered):
    for position in positions:
        number = ordered[(position.element, position.is_tail)]
        yield TagPosition(element=position.element,
                          tag=position.tag,
                          position=position.position,
                          length=position.length,
                          is_tail=position.is_tail,
                          dfs_number=number)

def enclose(tasks, entity_colors):
    if not tasks:
        return

    first = tasks[0][0]
    element = first.element
    is_tail = first.is_tail
    source = element.text
    if is_tail:
        source = element.tail

    if not source or not source.strip():
        return

    remainder = source[:first.position]

    nodes = list()
    for number, (start, end, _id) in enumerate(tasks):

        limit = len(source)
        is_last = number == len(tasks) - 1
        if not is_last:
            limit = tasks[number + 1][0].position

        tag = start.tag
        text = source[start.position + start.length:end.position]
        tail = source[end.position + end.length:limit]

        fg, bg, _ = entity_colors[tag]
        attrs = OrderedDict([
            ('wa-id', str(_id)),
            ('wa-type', str(tag)),
            ('wa-subtypes', ''),
            ('style', 'color:%s; background-color:%s;' % (fg, bg)),
            ('class', 'WebAnnotator_%s' % tag),
        ])

        node = Element('span', _fix_sax_attributes(attrs))
        node.text = text
        node.tail = tail
        nodes.append(node)


    if is_tail:
        element.tail = remainder
    else:
        element.text = remainder

    if is_tail:
        parent = element.getparent()
        shift = parent.index(element) + 1
    else:
        parent = element
        shift = 0

    for number, node in enumerate(nodes):
        parent.insert(number + shift, node)

def fabricate_start(element, is_tail, tag):
    return TagPosition(element=element,
                       tag=tag,
                       position=0,
                       length=0,
                       is_tail=is_tail,
                       dfs_number=0)

def fabricate_end(element, is_tail, tag):
    target = element.text
    if is_tail:
        target = element.tail

    length = 0
    if target:
        length = len(target)

    return TagPosition(element=element,
                       tag=tag,
                       position=length,
                       length=0,
                       is_tail=is_tail,
                       dfs_number=0)

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
    if not entity_colors:
        entity_colors = EntityColors()

    root = deepcopy(tree)

    START_RE = re.compile(r' __START_(\w+)__ ')
    END_RE = re.compile(r' __END_(\w+)__ ')

    starts = list()
    ends = list()
    for _, element in etree.iterwalk(root, events=('start',)):

        tasks = [(element.text, START_RE, starts, False),
                 (element.text, END_RE, ends, False),
                 (element.tail, START_RE, starts, True),
                 (element.tail, END_RE, ends, True)]


        for text, regexp, storage, is_tail in tasks:
            if not text:
                continue

            for match in regexp.finditer(text):

                if not match:
                    continue

                storage.append(TagPosition(element=element,
                                           tag=match.group(1),
                                           position=match.start(),
                                           length=match.end() - match.start(),
                                           is_tail=is_tail,
                                           dfs_number=-1))

    if len(ends) != len(starts):
        raise ValueError('len(ends) != len(starts)')

    # traverse tree in DFS manner
    # each text is first child
    # each tail is last
    ordered = dict()
    number = 0
    for action, element in etree.iterwalk(root, events=('start','end')):

        if action == 'end':
            is_tail = True
            ordered[(element, is_tail)] = number
            number = number + 1# for tail

        if action == 'start':
            is_tail = False
            ordered[(element, is_tail)] = number
            number = number + 1# for text
            number = number + 1# for element

    starts = [s for s in translate_to_dfs(starts, ordered)]
    ends = [e for e in translate_to_dfs(ends, ordered)]

    dfs_order = (max(n for n in ordered.values()) + 1) * [None]
    for text_node, dfs_number in ordered.items():
        dfs_order[dfs_number] = text_node

    tasks = []
    for _id, (start, end) in enumerate(zip(starts, ends)):
        start_number = start.dfs_number
        end_number = end.dfs_number

        if start_number == end_number:
            tasks.append((start, end, _id))
            continue

        for text_node in dfs_order[start_number + 1:end_number]:
            if text_node is None:
                continue

            element, is_tail = text_node

            if not isinstance(element.tag, six.string_types) and not isinstance(element.tag, six.text_type):
                continue

            if element.tag in ['script', 'style']:
                continue

            fictive_start = fabricate_start(element, is_tail, start.tag)
            fictive_end = fabricate_end(element, is_tail, start.tag)
            tasks.append((fictive_start, fictive_end, _id))

        fictive_end = fabricate_end(start.element, start.is_tail, start.tag)
        tasks.append((start, fictive_end, _id))

        fictive_start = fabricate_start(end.element, end.is_tail, end.tag)
        tasks.append((fictive_start, end, _id))

    byelement = lambda rec: (rec[0].element, rec[0].is_tail)
    tasks.sort(key=lambda rec:(ordered[byelement(rec)],rec[0].position))
    for _, enclosures in itertools.groupby(tasks, byelement):
        enclosures = [e for e in enclosures]
        enclose(enclosures, entity_colors)

    _copy_title(root)
    _add_wacolor_elements(root, entity_colors)
    if url is not None:
        _set_base(root, url)

    return root
