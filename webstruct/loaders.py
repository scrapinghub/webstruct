# -*- coding: utf-8 -*-
"""
Classes from this module load HTML annotated with WebAnnotator or GATE
into a common representation: cleaned lxml.etree.ElementTree with
annotation tags replaced by ``__START_TAGNAME__`` and ``__END_TAGNAME__``
tokens.
"""
from __future__ import absolute_import
import re
from collections import defaultdict
import lxml.html
import lxml.html.clean


class WebAnnotatorLoader(object):
    """
    Class for loading HTML annotated using
    `WebAnnotator <http://perso.limsi.fr/xtannier/en/WebAnnotator/>`_.

    .. note::

        Use WebAnnotator's "save format", not "export format".

    """
    def __init__(self, encoding=None, cleaner=None):
        self.encoding_ = encoding
        self.cleaner_ = cleaner or _default_cleaner

    def load(self, filename):
        with open(filename, 'rb') as f:
            return self.loadbytes(f.read())

    def loadbytes(self, data):
        parser = lxml.html.HTMLParser(encoding=self.encoding_)
        tree = lxml.html.document_fromstring(data, parser=parser)
        entities = self._get_entities(tree)
        self._process_entities(entities)
        return self._cleanup_tree(tree)

    def _get_entities(self, tree):
        entities = defaultdict(list)
        for el in tree.xpath('//span[@wa-id]'):
            entities[el.attrib['wa-id']].append(el)
        return dict(entities)

    def _process_entities(self, entities):
        for _id, elems in entities.items():
            tp = elems[0].attrib['wa-type']
            elems[0].text = ' __START_%s__ %s' % (tp, elems[0].text)
            elems[-1].text = '%s __END_%s__ ' % (elems[-1].text, tp)
            for el in elems:
                el.drop_tag()

    def _cleanup_tree(self, tree):
        for el in tree.xpath('//wa-color'):
            el.drop_tree()

        return self.cleaner_.clean_html(tree)


class GateLoader(object):
    """
    Class for loading HTML annotated using `GATE <http://gate.ac.uk/>`_

    >>> import lxml.html
    >>> from webstruct import GateLoader

    >>> loader = GateLoader(known_tags=['ORG', 'CITY'])
    >>> html = b"<html><body><p><ORG>Scrapinghub</ORG> has an <b>office</b> in <CITY>Montevideo</CITY></p></body></html>"
    >>> tree = loader.loadbytes(html)
    >>> lxml.html.tostring(tree)
    '<html><body><p> __START_ORG__ Scrapinghub __END_ORG__  has an <b>office</b> in  __START_CITY__ Montevideo __END_CITY__ </p></body></html>'

    """

    def __init__(self, encoding=None, cleaner=None, known_tags=None):
        if known_tags is None:
            raise ValueError("Please pass `tags` argument with a list of all possible tags")
        self.known_tags_ = known_tags
        self.encoding_ = encoding
        self.cleaner_ = cleaner or _default_cleaner

    def load(self, filename):
        with open(filename, 'rb') as f:
            return self.loadbytes(f.read())

    def loadbytes(self, data):
        # tags are replaced before parsing data as HTML because
        # GATE's html is invalid
        data = self._replace_tags(data)
        parser = lxml.html.HTMLParser(encoding=self.encoding_)
        tree = lxml.html.document_fromstring(data, parser=parser)
        return self.cleaner_.clean_html(tree)

    def _replace_tags(self, html_bytes):
        # replace requested tags with unified tokens
        open_re, close_re = self._tag_patterns(self.known_tags_)
        html_bytes = re.sub(open_re, r' __START_\1__ ', html_bytes)
        html_bytes = re.sub(close_re, r' __END_\1__ ', html_bytes)
        return html_bytes

    def _tag_patterns(self, tags):
        tags_pattern = '|'.join(list(tags))
        open_re = re.compile('<(%s)>' % tags_pattern, re.I)
        close_re = re.compile('</(%s)>' % tags_pattern, re.I)
        return open_re, close_re


_default_cleaner = lxml.html.clean.Cleaner(
    style=True,
    scripts=True,
    embedded=True,
    links=True,
    page_structure=False,
    remove_unknown_tags=False,
    meta=False,
    safe_attrs_only=False
)

