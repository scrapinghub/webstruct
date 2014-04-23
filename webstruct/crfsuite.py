# -*- coding: utf-8 -*-
"""
CRFsuite_ backend for webstruct base on python-crfsuite_

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

    Example of training, with all parameters default::

        >>> import webstruct
        >>> trees = webstruct.load_trees([
        ...    ("train/*.html", webstruct.WebAnnotatorLoader())
        ... ])  # doctest: +SKIP
        >>> X, y = webstruct.HtmlTokenizer().tokenize(trees)  # doctest: +SKIP
        >>> model = webstruct.create_crfsuite_pipeline('model.crfsuite')  # doctest: +SKIP
        >>> model.fit(X, y)  # doctest: +SKIP

    """
    from pycrfsuite import CRFSuite

    if token_features is None:
        token_features = DEFAULT_FEATURES

    return Pipeline([
        ('fe', HtmlFeatureExtractor(token_features, global_features, min_df=min_df)),
        ('crf', CRFSuite(model_filename, **crfsuite_kwargs)),
    ])