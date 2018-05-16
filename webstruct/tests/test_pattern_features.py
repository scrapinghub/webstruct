# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from webstruct import GateLoader, HtmlTokenizer, HtmlFeatureExtractor
from webstruct.features import token_lower, token_identity, looks_like_year, Pattern


class PatternTest(unittest.TestCase):

    def setUp(self):
        self.html_tokens = self._load_document()

    def _load_document(self):
        loader = GateLoader(known_entities=['PER'])
        tree = loader.loadbytes(b"<p>hello, <PER>John <b>Doe</b></PER> <br> <PER>Mary</PER> said</p>")
        html_tokens, _ = HtmlTokenizer().tokenize_single(tree)
        return html_tokens

    def test_pattern(self):
        #, (0, 'looks_like_year')
        featextractor = HtmlFeatureExtractor(
            token_features = [token_lower, token_identity, looks_like_year],
            global_features = [
                Pattern((-2, 'lower'), (-1, 'lower'), (-1, 'looks_like_year'))
            ]
        )
        X = featextractor.transform_single(self.html_tokens)
        key = 'lower[-2]/lower[-1]/looks_like_year[-1]'
        self.assertNotIn(key, X[0])
        self.assertListEqual(
            [feat[key] for feat in X[1:]],
            ['?/hello/False', 'hello/john/False', 'john/doe/False',
             'doe/mary/False'],
        )

    def test_pattern_lookups(self):
        featextractor = HtmlFeatureExtractor(
            token_features = [token_lower, token_identity],
            global_features=[
                Pattern((0, 'lower'), (1, 'token'), out_value='OUT'),
            ]
        )
        X = featextractor.transform_single(self.html_tokens)
        self.assertListEqual(
            [feat['lower/token[+1]'] for feat in X],
            ['hello/John', 'john/Doe', 'doe/Mary', 'mary/said', 'said/OUT']
        )
