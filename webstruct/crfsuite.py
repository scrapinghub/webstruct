# -*- coding: utf-8 -*-
"""
CRFsuite_ backend for webstruct based on python-crfsuite_

.. _CRFsuite: http://www.chokkan.org/software/crfsuite/
.. _python-crfsuite: https://github.com/tpeng/python-crfsuite

"""
from __future__ import absolute_import
from sklearn.pipeline import Pipeline
from webstruct import HtmlFeatureExtractor

def create_crfsuite_pipeline(model_filename,
                             token_features=None,
                             global_features=None,
                             min_df=1,
                             **crfsuite_kwargs):
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
            model_filename = 'model.crfsuite',
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
    from pycrfsuite import CRFSuite

    if token_features is None:
        token_features = []

    return Pipeline([
        ('fe', HtmlFeatureExtractor(token_features, global_features, min_df=min_df)),
        ('crf', CRFSuite(model_filename, **crfsuite_kwargs)),
    ])