# -*- coding: utf-8 -*-
from __future__ import absolute_import
# import nltk
import lxml.html
from sklearn.base import BaseEstimator
from .utils import merge_dicts
from .preprocess import IobSequence, Tagset, to_features_and_labels, DEFAULT_TAGSET
from . import features

def default_tokenizer(text):
    import nltk
    for tok in nltk.word_tokenize(text):
        if tok in ',;':
            continue
        yield tok


class HtmlFeaturesExtractor(BaseEstimator):

    def __init__(self,  tokenizer=default_tokenizer, tags=DEFAULT_TAGSET,
                 features=features.DEFAULT, tagset=None, label_encoder=None):
        self.tokenizer = tokenizer
        self.features = features
        if tagset is None:
            self.tagset = Tagset(tags)
        else:
            self.tagset = tagset

        if label_encoder is None:
            self.label_encoder = IobSequence(self.tagset)
        else:
            self.label_encoder = label_encoder

    def _parse_html(self, html):
        return lxml.html.fromstring(html)

    def fit_transform(self, X, y=None):
        """
        Converts HTML data :param:X to a sequence of dicts with features.
        :param:y is ignored.

        Return (features, labels) tuple.
        """
        html = self.tagset.encode_tags(X)
        doc = self._parse_html(html)
        res = to_features_and_labels(doc, self.tokenizer, self.label_encoder, self.features)
        if not res:
            return (), ()
        return zip(*res)

