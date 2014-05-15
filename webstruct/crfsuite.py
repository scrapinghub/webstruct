# -*- coding: utf-8 -*-
"""
CRFsuite_ backend for webstruct based on python-crfsuite_

.. _CRFsuite: http://www.chokkan.org/software/crfsuite/
.. _python-crfsuite: https://github.com/tpeng/python-crfsuite

"""
from __future__ import absolute_import
import os
import tempfile
from sklearn.pipeline import Pipeline
from sklearn.base import TransformerMixin, BaseEstimator

from webstruct import HtmlFeatureExtractor
from webstruct.base import BaseSequenceClassifier


def _prepare_dict(dct):
    """
    >>> _prepare_dict({'foo': 'bar'})
    {'foo=bar': 1.0}
    >>> _prepare_dict({'foo': 2.0})
    {'foo': 2.0}
    >>> _prepare_dict({'foo': False})
    {'foo': 0.0}
    >>> _prepare_dict({'foo': True})
    {'foo': 1.0}
    """
    res = {}
    for key, value in dct.items():
        if isinstance(value, basestring):
            res[key + "=" + value] = 1.0
        else:
            res[key] = float(value)
    return res


class CRFsuiteFeatureEncoder(BaseEstimator, TransformerMixin):
    """
    A Transformer for converting Webstruct feature dicts to
    python-crfsuite format.

    ``{"key": value}`` dicts are converted to ``{"key=%s" % value: 1.0}``
    if the value is a string and to ``{"key": float(value)}`` if the value
    is a number or a boolean value.
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [[_prepare_dict(dct) for dct in xseq] for xseq in X]


class CRFsuiteCRF(BaseSequenceClassifier):
    def __init__(self, algorithm=None, train_params=None, verbose=False,
                 model_filename=None, keep_tempfiles=False):
        self.algorithm = algorithm
        self.train_params = train_params

        self.model_filename_ = model_filename
        self._modelfile_auto = model_filename is None
        self.keep_tempfiles = keep_tempfiles

        self.verbose = verbose
        self._tagger = None
        super(CRFsuiteCRF, self).__init__()

    def fit(self, X, y):
        """
        Train a model.

        Parameters
        ----------
        X : list of lists of dicts
            Feature dicts for several documents (in a python-crfsuite format).

        y : list of lists of strings
            Labels for several documents.
        """
        self._cleanup()

        import pycrfsuite
        trainer = pycrfsuite.Trainer(
            algorithm=self.algorithm,
            params=self.train_params,
            verbose=self.verbose,
        )

        for xseq, yseq in zip(X, y):
            trainer.append(xseq, yseq)

        if self._modelfile_auto:
            self.model_filename_ = self._tempname()
        trainer.train(self.model_filename_)
        return self

    def predict(self, X):
        """
        Make a prediction.

        Parameters
        ----------
        X : list of lists of dicts
            feature dicts in python-crfsuite format

        Returns
        -------
        y : list of lists
            predicted labels

        """
        y = []
        tagger = self.get_tagger()
        for xseq in X:
            y.append(tagger.tag(xseq))
        return y

    def get_tagger(self):
        if self._tagger is None:
            if self.model_filename_ is None:
                raise Exception("Can't load model. Is the model trained?")

            import pycrfsuite
            tagger = pycrfsuite.Tagger()
            tagger.open(self.model_filename_)
            self._tagger = tagger
        return self._tagger

    def __del__(self):
        self._cleanup()

    def __getstate__(self):
        dct = self.__dict__.copy()
        dct['_tagger'] = None

        if self._modelfile_auto:
            filename = dct['model_filename_']
            if filename is not None:
                with open(filename, 'rb') as f:
                    dct['crfsuite_data'] = f.read()
                dct['model_filename_'] = None

        return dct

    def __setstate__(self, state):
        data = state.pop('crfsuite_data', None)
        if data is not None:
            assert state['_modelfile_auto']
            assert state['model_filename_'] is None
            state['model_filename_'] = self._tempname()
            with open(state['model_filename_'], 'wb') as f:
                f.write(data)
        self.__dict__.update(state)

    def _tempname(self):
        fd, fname = tempfile.mkstemp(suffix='.crfsuite', prefix='model')
        return fname

    def _cleanup(self):
        if self._tagger is not None:
            self._tagger.close()
            self._tagger = None

        if self.model_filename_ and self._modelfile_auto and not self.keep_tempfiles:
            try:
                os.unlink(self.model_filename_)
            except OSError:
                pass
            self.model_filename_ = None


def create_crfsuite_pipeline(token_features=None,
                             global_features=None,
                             min_df=1,
                             **crf_kwargs):
    """
    Create a scikit-learn Pipeline for HTML tagging using CRFsuite.
    This pipeline expects data produced by
    :class:`~.HtmlTokenizer` as an input and produces
    sequences of IOB2 tags as output.

    Example::

        import webstruct
        from webstruct.features import EXAMPLE_TOKEN_FEATURES

        # load train data
        html_tokenizer = webstruct.HtmlTokenizer()
        train_trees = webstruct.load_trees([
           ("train/*.html", webstruct.WebAnnotatorLoader())
        ])
        X_train, y_train = html_tokenizer.tokenize(train_trees)

        # train
        model = webstruct.create_crfsuite_pipeline(
            token_features = EXAMPLE_TOKEN_FEATURES,
        )
        model.fit(X_train, y_train)

        # load test data
        test_trees = webstruct.load_trees([
           ("test/*.html", webstruct.WebAnnotatorLoader())
        ])
        X_test, y_test = html_tokenizer.tokenize(test_trees)

        # do a prediction
        y_pred = model.predict(X_test)

    """
    if token_features is None:
        token_features = []

    return Pipeline([
        ('fe', HtmlFeatureExtractor(token_features, global_features, min_df=min_df)),
        ('enc', CRFsuiteFeatureEncoder()),
        ('crf', CRFsuiteCRF(**crf_kwargs)),
    ])
