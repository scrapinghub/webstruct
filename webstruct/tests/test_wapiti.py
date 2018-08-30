# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import unittest
import pickle
import tempfile

import webstruct
from webstruct.features import EXAMPLE_TOKEN_FEATURES
from webstruct.metrics import bio_classification_report
from webstruct.wapiti import WapitiCRF, create_wapiti_pipeline, merge_top_n
from webstruct.utils import train_test_split_noshuffle, run_command
from webstruct.sequence_encoding import IobEncoder, BilouEncoder
from webstruct.model import NER
from .utils import get_trees, DATA_PATH



def test_is_wapiti_binary_present():
    run_command(['which', WapitiCRF.WAPITI_CMD])


def test_merge_top_n_bilou():
    encoder = BilouEncoder()
    # non-overlap
    chains = [['U-PER', 'O'], ['O', 'U-FUNC']]
    assert merge_top_n(chains, sequence_encoder=encoder) == ['U-PER', 'U-FUNC']

    # partially overlap
    chains = [['B-PER', 'L-PER', 'O'], ['O', 'B-PER', 'L-PER']]
    assert merge_top_n(chains, sequence_encoder=encoder) == ['B-PER', 'L-PER', 'O']

    chains = [['O', 'U-ORG', 'O'], ['B-PER', 'L-PER', 'O']]
    assert merge_top_n(chains, sequence_encoder=encoder) == ['O', 'U-ORG', 'O']

    # fully overlap
    chains = [['B-PER', 'L-PER'], ['B-ORG', 'L-ORG']]
    assert merge_top_n(chains, sequence_encoder=encoder) == ['B-PER', 'L-PER']


class WapitiTest(unittest.TestCase):

    TAGSET = ['ORG', 'CITY', 'STREET', 'ZIPCODE', 'STATE', 'TEL', 'FAX']

    def _get_Xy(self, num):
        trees = get_trees(num)
        html_tokenizer = webstruct.HtmlTokenizer(tagset=self.TAGSET)
        return html_tokenizer.tokenize(trees)

    def _get_train_test(self, train_size, test_size):
        X, y = self._get_Xy(train_size+test_size)
        return train_test_split_noshuffle(X, y, test_size=test_size)

    def get_pipeline(self, **kwargs):
        params = dict(
            token_features=EXAMPLE_TOKEN_FEATURES,
            verbose=False,
            top_n=5,
        )
        params.update(kwargs)
        return create_wapiti_pipeline(**params)

    def test_training_tagging(self):
        X_train, X_test, y_train, y_test = self._get_train_test(8, 2)

        # Train the model:
        model = self.get_pipeline()
        model.fit(X_train, y_train)

        # Model should learn something:
        #
        # y_pred = model.predict(X_test)
        # print(bio_classification_report(y_test, y_pred))
        assert model.score(X_test, y_test) > 0.3
