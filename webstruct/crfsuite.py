# -*- coding: utf-8 -*-
"""
CRFsuite_ backend for webstruct based on python-crfsuite_

.. _CRFsuite: http://www.chokkan.org/software/crfsuite/
.. _python-crfsuite: https://github.com/tpeng/python-crfsuite

"""
from __future__ import absolute_import
from sklearn.pipeline import Pipeline

from webstruct import HtmlFeatureExtractor
from webstruct.base import BaseSequenceClassifier
from webstruct._fileresource import FileResource


class CRFsuiteCRF(BaseSequenceClassifier):
    def __init__(self, algorithm=None, train_params=None, verbose=False,
                 model_filename=None, keep_tempfiles=False, trainer_cls=None):
        self.algorithm = algorithm
        self.train_params = train_params
        self.modelfile = FileResource(
            filename =model_filename,
            keep_tempfiles=keep_tempfiles,
            suffix=".crfsuite",
            prefix="model"
        )
        self.verbose = verbose
        self._tagger = None
        if trainer_cls is None:
            import pycrfsuite
            self.trainer_cls = pycrfsuite.Trainer
        else:
            self.trainer_cls = trainer_cls
        self.training_log_ = None
        super(CRFsuiteCRF, self).__init__()

    def fit(self, X, y, X_dev=None, y_dev=None):
        """
        Train a model.

        Parameters
        ----------
        X : list of lists of dicts
            Feature dicts for several documents (in a python-crfsuite format).

        y : list of lists of strings
            Labels for several documents.

        X_dev : (optional) list of lists of dicts
            Feature dicts used for testing.

        y_dev : (optional) list of lists of strings
            Labels corresponding to X_dev.
        """
        if (X_dev is None and y_dev is not None) or (X_dev is not None and y_dev is None):
            raise ValueError("Pass both X_dev and y_dev to use the holdout data")

        if self._tagger is not None:
            self._tagger.close()
            self._tagger = None
        self.modelfile.refresh()

        trainer = self._get_trainer()

        for xseq, yseq in zip(X, y):
            trainer.append(xseq, yseq)

        if X_dev is not None:
            for xseq, yseq in zip(X_dev, y_dev):
                trainer.append(xseq, yseq, 1)

        trainer.train(self.modelfile.name, holdout=-1 if X_dev is None else 1)
        self.training_log_ = trainer.logparser
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
        tagger = self.tagger
        for xseq in X:
            y.append(tagger.tag(xseq))
        return y

    @property
    def tagger(self):
        if self._tagger is None:
            if self.modelfile.name is None:
                raise Exception("Can't load model. Is the model trained?")

            import pycrfsuite
            tagger = pycrfsuite.Tagger()
            tagger.open(self.modelfile.name)
            self._tagger = tagger
        return self._tagger

    def _get_trainer(self):
        return self.trainer_cls(
            algorithm=self.algorithm,
            params=self.train_params,
            verbose=self.verbose,
        )

    def __getstate__(self):
        dct = self.__dict__.copy()
        dct['_tagger'] = None
        return dct


class CRFsuitePipeline(Pipeline):
    """
    A pipeline for HTML tagging using CRFsuite. It combines
    a feature extractor and a CRF; they are available
    as :attr:`fe` and :attr:`crf` attributes for easier access.

    In addition to that, this class adds support for X_dev/y_dev arguments
    for :meth:`fit` and :meth:`fit_transform` methods - they work as expected,
    being transformed using feature extractor.
    """
    def __init__(self, fe, crf):
        self.fe = fe
        self.crf = crf
        super(CRFsuitePipeline, self).__init__([
            ('fe', self.fe),
            ('crf', self.crf),
        ])

    def fit(self, X, y=None, **fit_params):
        X_dev = fit_params.pop('X_dev', None)
        if X_dev is not None:
            fit_params['crf__X_dev'] = self.fe.transform(X_dev)
            fit_params['crf__y_dev'] = fit_params.pop('y_dev', None)
        return super(CRFsuitePipeline, self).fit(X, y, **fit_params)

    def fit_transform(self, X, y=None, **fit_params):
        X_dev = fit_params.pop('X_dev', None)
        if X_dev is not None:
            fit_params['crf__X_dev'] = self.fe.transform(X_dev)
            fit_params['crf__y_dev'] = fit_params.pop('y_dev', None)
        return super(CRFsuitePipeline, self).fit_transform(X, y, **fit_params)


def create_crfsuite_pipeline(token_features=None,
                             global_features=None,
                             min_df=1,
                             **crf_kwargs):
    """
    Create :class:`CRFsuitePipeline` for HTML tagging using CRFsuite.
    This pipeline expects data produced by
    :class:`~.HtmlTokenizer` as an input and produces
    sequences of IOB2 tags as output.

    Example::

        import webstruct
        from webstruct.features import EXAMPLE_TOKEN_FEATURES

        # load train data
        html_tokenizer = webstruct.HtmlTokenizer()
        train_trees = webstruct.load_trees(
            "train/*.html",
            webstruct.WebAnnotatorLoader()
        )
        X_train, y_train = html_tokenizer.tokenize(train_trees)

        # train
        model = webstruct.create_crfsuite_pipeline(
            token_features = EXAMPLE_TOKEN_FEATURES,
        )
        model.fit(X_train, y_train)

        # load test data
        test_trees = webstruct.load_trees(
            "test/*.html",
            webstruct.WebAnnotatorLoader()
        )
        X_test, y_test = html_tokenizer.tokenize(test_trees)

        # do a prediction
        y_pred = model.predict(X_test)

    """
    if token_features is None:
        token_features = []

    fe = HtmlFeatureExtractor(token_features, global_features, min_df=min_df)
    crf = CRFsuiteCRF(**crf_kwargs)

    return CRFsuitePipeline(fe, crf)
