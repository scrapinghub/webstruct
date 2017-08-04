# -*- coding: utf-8 -*-
import numpy as np


def crf_cross_val_predict(pipe, X, y, cv, groups=None, n_folds=None):
    """
    Split data into folds according to cv iterator, do train/test prediction 
    on first n_folds (or on all folds if n_folds is None). 
    """
    X, y = np.array(X), np.array(y)
    y_pred = []
    y_true = []

    for idx, (train_idx, test_idx) in enumerate(cv.split(X, y, groups)):
        if n_folds and idx >= n_folds:
            break

        X_train, X_dev = X[train_idx], X[test_idx]
        y_train, y_dev = y[train_idx], y[test_idx]
        pipe.fit(X_train, y_train, X_dev=X_dev, y_dev=y_dev)
        y_true.append(y_dev)
        y_pred.append(pipe.predict(X_dev))

    y_pred = np.hstack(y_pred)
    y_true = np.hstack(y_true)
    return y_pred, y_true
