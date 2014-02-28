# -*- coding: utf-8 -*-
"""
:mod:`webstruct.model` contains convetional wrappers for creating NER models.
"""

from __future__ import absolute_import
import urllib2
from webstruct.loaders import HtmlLoader
from webstruct.feature_extraction import HtmlTokenizer
from webstruct.sequence_encoding import IobEncoder
from webstruct.utils import smart_join


class NER(object):
    """
    Class for extracting named entities from HTML.

    Initialize it with a trained ``model``. ``model`` must have
    ``transform`` method that accepts lists of :class:`~.HtmlToken`
    sequences and returns lists of predicted IOB2 tags.
    :func:`~.create_wapiti_pipeline` function returns such model.
    """
    def __init__(self, model, loader=None, html_tokenizer=None):
        self.model = model
        self.loader = loader or HtmlLoader()
        self.html_tokenizer = html_tokenizer or HtmlTokenizer()

    def extract(self, bytes_data):
        """
        Extract named entities from binary HTML data ``bytes_data``.
        Return a list of ``(entity_text, entity_type)`` tuples.
        """
        html_tokens, tags = self.extract_raw(bytes_data)
        groups = IobEncoder.group(zip([tok.token for tok in html_tokens], tags))
        return [
            (self.build_entity(tokens, tag), tag)
            for (tokens, tag) in groups if tag != 'O'
        ]

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
        tags = self.model.transform([html_tokens])[0]
        return html_tokens, tags

    def build_entity(self, text_tokens, tag):
        """
        Join tokens to an entity. Return an entity, as text.
        By default this function uses :func:`webstruct.utils.smart_join`;
        override it to customize :meth:`extract` and :meth:`extract_from_url`
        results.
        """
        return smart_join(text_tokens)
