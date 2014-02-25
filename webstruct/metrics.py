# -*- coding: utf-8 -*-
"""
:mod:`webstruct.metrics` contains metric functions that can be used for
model developmenton: on their own or as scoring functions for
scikit-learn's `cross-validation`_ and `model selection`_.

.. _cross-validation: http://scikit-learn.org/stable/modules/cross_validation.html
.. _model selection: http://scikit-learn.org/stable/tutorial/statistical_inference/model_selection.html

"""
from __future__ import absolute_import
from itertools import chain
from sklearn.metrics import classification_report


def avg_bio_f1_score(y_true, y_pred):
    """
    Macro-averaged F1 score of lists of BIO-encoded sequences
    ``y_true`` and ``y_pred``.

    A named entity in a sequence from ``y_pred`` is considered
    correct only if it is an exact match of the corresponding entity
    in the ``y_true``.

    It requires https://github.com/larsmans/seqlearn to work.
    """
    from seqlearn.evaluation import bio_f_score
    return sum(map(bio_f_score, y_true, y_pred)) / len(y_true)


def bio_classification_report(y_true, y_pred):
    """
    Classification report for a list of BIO-encoded sequences.
    It computes token-level metrics and discards "O" labels.
    """
    y_true_combined = list(chain.from_iterable(y_true))
    y_pred_combined = list(chain.from_iterable(y_pred))
    tagset = (set(y_true_combined) | set(y_pred_combined)) - {'O'}
    return classification_report(
        y_true_combined,
        y_pred_combined,
        labels = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
    )
