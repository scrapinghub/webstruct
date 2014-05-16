# -*- coding: utf-8 -*-
"""
:mod:`webstruct.model` contains convetional wrappers for creating NER models.
"""
from __future__ import absolute_import
import urllib2
from lxml.html import tostring

from webstruct.loaders import HtmlLoader
from webstruct.feature_extraction import HtmlTokenizer
from webstruct.sequence_encoding import IobEncoder
from webstruct.utils import smart_join
from webstruct.grouping import choose_best_clustering
from webstruct.webannotator import EntityColors, to_webannotator


class NER(object):
    """
    Class for extracting named entities from HTML.

    Initialize it with a trained ``model``. ``model`` must have
    ``predict`` method that accepts lists of :class:`~.HtmlToken`
    sequences and returns lists of predicted IOB2 tags.
    :func:`~.create_wapiti_pipeline` function returns such model.
    """
    def __init__(self, model, loader=None, html_tokenizer=None):
        self.model = model
        self.loader = loader or HtmlLoader()
        self.html_tokenizer = html_tokenizer or HtmlTokenizer()
        self.entity_colors = EntityColors()

    def extract(self, bytes_data):
        """
        Extract named entities from binary HTML data ``bytes_data``.
        Return a list of ``(entity_text, entity_type)`` tuples.
        """
        html_tokens, tags = self.extract_raw(bytes_data)
        groups = IobEncoder.group(zip(html_tokens, tags))
        return _drop_empty(
            (self.build_entity(tokens, tag), tag)
            for (tokens, tag) in groups if tag != 'O'
        )

    def extract_from_url(self, url):
        """
        A convenience wrapper for :meth:`extract` method that downloads
        input data from a remote URL.
        """
        data = urllib2.urlopen(url).read()
        return self.extract(data)

    def extract_raw(self, bytes_data):
        """
        Extract named entities from binary HTML data ``bytes_data``.
        Return a list of ``(html_token, iob2_tag)`` tuples.
        """
        tree = self.loader.loadbytes(bytes_data)
        html_tokens, _ = self.html_tokenizer.tokenize_single(tree)
        tags = self.model.predict([html_tokens])[0]
        return html_tokens, tags

    def extract_groups(self, bytes_data, dont_penalize=None):
        """
        Extract groups of named entities from binary HTML data ``bytes_data``.
        Return a list of lists of ``(entity_text, entity_type)`` tuples.

        Entites are grouped using algorithm from :mod:`webstruct.grouping`.
        """
        html_tokens, tags = self.extract_raw(bytes_data)
        _, _, clusters = choose_best_clustering(
            html_tokens,
            tags,
            score_kwargs={'dont_penalize': dont_penalize}
        )

        entities = []
        for cluster in clusters:
            text_entities = _drop_empty(
                (self.build_entity(tokens, tag), tag)
                for tokens, tag, dist in cluster
            )
            if text_entities:
                entities.append(text_entities)

        return entities

    def build_entity(self, html_tokens, tag):
        """
        Join tokens to an entity. Return an entity, as text.
        By default this function uses :func:`webstruct.utils.smart_join`.

        Override it to customize :meth:`extract`, :meth:`extract_from_url`
        and :meth:`extract_groups` results. If this function returns empty
        string or None, entity is dropped.
        """
        return smart_join(t.token for t in html_tokens)

    def annotate(self, bytes_data, pretty_print=False):
        """
        Return annotated HTML data in WebAnnotator format.
        """
        html_tokens, tags = self.extract_raw(bytes_data)
        tree = self.html_tokenizer.detokenize_single(html_tokens, tags)
        tree = to_webannotator(tree, self.entity_colors)
        return tostring(tree, pretty_print=pretty_print)

    def annotate_url(self, url):
        """
        Return annotated HTML data in WebAnnotator format; input is downloaded
        from ``url``.
        """
        data = urllib2.urlopen(url).read()
        return self.annotate(data)

    def __getstate__(self):
        dct = self.__dict__.copy()
        dct['entity_colors'] = dict(self.entity_colors)
        return dct

    def __setstate__(self, state):
        state['entity_colors'] = EntityColors(**state['entity_colors'])
        self.__dict__.update(state)


def _drop_empty(entities):
    return [(text, tag) for (text, tag) in entities if text]
