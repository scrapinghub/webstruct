# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import unittest
import pickle
import tempfile

import webstruct
from webstruct.features import EXAMPLE_TOKEN_FEATURES
from webstruct.metrics import bio_classification_report
from webstruct.wapiti import create_wapiti_pipeline, merge_top_n
from webstruct.utils import train_test_split_noshuffle
from webstruct.model import NER
from .utils import get_trees, DATA_PATH


def test_merge_top_n_bilou():
    # non-overlap
    chains = [['U-PER', 'O'], ['O', 'U-FUNC']]
    assert merge_top_n(chains, bilou=True) == ['U-PER', 'U-FUNC']

    # partially overlap
    chains = [['B-PER', 'L-PER', 'O'], ['O', 'B-PER', 'L-PER']]
    assert merge_top_n(chains, bilou=True) == ['B-PER', 'L-PER', 'O']

    chains = [['O', 'U-ORG', 'O'], ['B-PER', 'L-PER', 'O']]
    assert merge_top_n(chains, bilou=True) == ['O', 'U-ORG', 'O']

    # fully overlap
    chains = [['B-PER', 'L-PER'], ['B-ORG', 'L-ORG']]
    assert merge_top_n(chains, bilou=True) == ['B-PER', 'L-PER']


class WapitiTest(unittest.TestCase):

    TAGSET = ['ORG', 'CITY', 'STREET', 'ZIPCODE', 'STATE', 'TEL', 'FAX']

    def _get_Xy(self, num, bilou=False):
        trees = get_trees(num)
        html_tokenizer = webstruct.HtmlTokenizer(tagset=self.TAGSET, bilou=bilou)
        return html_tokenizer.tokenize(trees)

    def _get_train_test(self, train_size, test_size, bilou=False):
        X, y = self._get_Xy(train_size+test_size, bilou)
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

    def test_pickle(self):
        X_train, X_test, y_train, y_test = self._get_train_test(8, 2)

        model = self.get_pipeline()
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        assert score > 0.3

        data = pickle.dumps(model, pickle.HIGHEST_PROTOCOL)
        filename = model.steps[-1][1].modelfile.name

        # make sure model file is gone
        del model
        try:
            os.unlink(filename)
        except OSError:
            pass

        # model should work after unpickling
        model2 = pickle.loads(data)
        score2 = model2.score(X_test, y_test)
        assert score2 > 0.3
        assert abs(score2-score) < 1e-6

    def test_wapiti(self):
        X, y = self._get_Xy(10)
        model = self.get_pipeline()
        model.fit(X, y)

        ner = NER(model)

        # Load 7.html file - model is trained on it, so
        # the prediction should work well.
        with open(os.path.join(DATA_PATH, '7.html'), 'rb') as f:
            html = f.read()

        groups = ner.extract_groups(html, dont_penalize={'TEL', 'FAX'})
        group1 = [
            (u'4503 W. Lovers Lane', 'STREET'),
            (u'Dallas', 'CITY'),
            (u'TX', 'STATE'),
            (u'75206', 'ZIPCODE'),
            (u'214-351-2456', 'TEL'),
            (u'214-904-1716', 'FAX'),
        ]
        group2 = [
            (u'4515 W. Lovers Lane', 'STREET'),
            (u'Dallas', 'CITY'),
            (u'TX', 'STATE'),
            (u'75206', 'ZIPCODE'),
            (u'214-352-0031', 'TEL'),
            (u'214-350-5302', 'FAX')
        ]
        self.assertIn(group1, groups)
        self.assertIn(group2, groups)

        # pickle/unpickle NER instance
        dump = pickle.dumps(ner, pickle.HIGHEST_PROTOCOL)
        ner2 = pickle.loads(dump)

        self.assertNotEqual(
            ner.model.steps[-1][1].modelfile.name,
            ner2.model.steps[-1][1].modelfile.name,
        )

        groups = ner2.extract_groups(html, dont_penalize={'TEL', 'FAX'})
        self.assertIn(group1, groups)
        self.assertIn(group2, groups)

    def test_ner_bilou(self):
        X, y = self._get_Xy(10, bilou=True)
        model = self.get_pipeline()
        model.fit(X, y)

        ner = NER(model, bilou=True)

        # Load 7.html file - model is trained on it, so
        # the prediction should work well.
        with open(os.path.join(DATA_PATH, '7.html'), 'rb') as f:
            html = f.read()

        groups = ner.extract_groups(html, dont_penalize={'TEL', 'FAX'})
        group1 = [
            (u'4503 W. Lovers Lane', 'STREET'),
            (u'Dallas', 'CITY'),
            (u'TX', 'STATE'),
            (u'75206', 'ZIPCODE'),
            (u'214-351-2456', 'TEL'),
            (u'214-904-1716', 'FAX'),
        ]
        group2 = [
            (u'4503 W. Lovers Lane', 'STREET'),
            (u'Dallas', 'CITY'),
            (u'TX', 'STATE'),
            (u'75206', 'ZIPCODE'),
            (u'214-351-2456', 'TEL'),
            (u'214-904-1716', 'FAX')
        ]
        self.assertIn(group1, groups)
        self.assertIn(group2, groups)
        # pickle/unpickle NER instance
        dump = pickle.dumps(ner, pickle.HIGHEST_PROTOCOL)
        ner2 = pickle.loads(dump)

        self.assertNotEqual(
            ner.model.steps[-1][1].modelfile.name,
            ner2.model.steps[-1][1].modelfile.name,
        )

        groups = ner2.extract_groups(html, dont_penalize={'TEL', 'FAX'})
        self.assertIn(group1, groups)
        self.assertIn(group2, groups)
