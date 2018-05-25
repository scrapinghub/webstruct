from __future__ import absolute_import
import six


def _get_accuracy(true_entities, pred_entities):
    acc = {}
    for label, entities in true_entities.items():
        if label in pred_entities:
            true_pos = true_entities[label].intersection(pred_entities[label])
            acc[label] = len(true_pos) / len(true_entities[label])
            if six.PY2:
                print "label, true_pos, acc[label], true_entities[label]: ", label, true_pos, acc[label],true_entities[label]
        else:
            acc[label] = 0
    entities_in_common = set(true_entities.keys()).intersection(
                                                    set(pred_entities.keys())
                                                                )
    pred_extra_entities = set(pred_entities.keys()) - entities_in_common
    if pred_extra_entities:
        # should this raise an exception?
        for label in pred_extra_entities:
            acc[label] = 0
    if six.PY2:
        print "true_pos: ", acc
    return acc


def _get_precision(true_entities, pred_entities):
    prec = {}
    for label, entities in true_entities.items():
        if label in pred_entities:
            true_pos = true_entities[label].intersection(pred_entities[label])
            false_pos = pred_entities[label] - true_pos
            prec[label] = len(true_pos) / (len(true_pos) + len(false_pos))
        else:
            prec[label] = 0
    entities_in_common = set(true_entities.keys()).intersection(
                                                    set(pred_entities.keys())
                                                                )
    pred_extra_entities = set(pred_entities.keys()) - entities_in_common
    if pred_extra_entities:
        # should this raise an exception?
        for label in pred_extra_entities:
            prec[label] = 0
    return prec


def _get_recall(true_entities, pred_entities):
    rec = {}
    for label, entities in true_entities.items():
        if label in pred_entities:
            true_pos = true_entities[label].intersection(pred_entities[label])
            false_neg = true_entities[label] - true_pos
            rec[label] = len(true_pos) / (len(true_pos) + len(false_neg))
        else:
            rec[label] = 0
    entities_in_common = set(true_entities.keys()).intersection(
                                                    set(pred_entities.keys())
                                                                )
    pred_extra_entities = set(pred_entities.keys()) - entities_in_common
    if pred_extra_entities:
        # should this raise an exception?
        for label in pred_extra_entities:
            rec[label] = 0
    return rec


def _get_f1_score(prec, rec):
    f1 = {}
    for label in prec:
        denominator = (prec[label] + rec[label])
        if denominator != 0:
            f1[label] = 2 * (prec[label] * rec[label]) / denominator
        else:
            f1[label] = 0
    return f1


def get_label_entities(X, y):
    label_entities = {}
    buffer = []
    for token, tag in zip(X, y):
        label = tag[2:]
        if tag == 'O':
            # in order to consider partial entity matches ({'PER': {'Doe'}} John
            # missing) filter out only O elements and append all BILU independently
            continue
        if tag[0] == 'B' or tag[0] == 'U':
            if buffer:
                buf_label, entity = buffer
                entity = ' '.join(entity)
                if buf_label not in label_entities:
                    label_entities[buf_label] = set()
                label_entities[buf_label].update([entity])
                buffer = []
        if not buffer:
            buffer = (label, [])
        buffer[1].append(token.token)
    if buffer:
        # if token sequence ends with an entity
        buf_label, entity = buffer
        entity = ' '.join(entity)
        if buf_label not in label_entities:
            label_entities[buf_label] = set()
        label_entities[buf_label].update([entity])
    return label_entities


def get_metrics_single(X_true, y_true, X_pred, y_pred):
    true_entities = get_label_entities(X_true, y_true)
    pred_entities = get_label_entities(X_pred, y_pred)
    acc = _get_accuracy(true_entities, pred_entities)
    prec = _get_precision(true_entities, pred_entities)
    rec = _get_recall(true_entities, pred_entities)
    f1 = _get_f1_score(prec, rec)
    return acc, prec, rec, f1


def _update_metric(metric, new_values):
    for k, v in new_values.items():
        if k not in metric:
            metric[k] = []
        metric[k].append(v)


def _get_mean(metric):
    avg = {}
    for k, v in metric.items():
        avg[k] = sum(v) / len(v)
    return avg


def get_metrics(X_true, y_true, X_pred, y_pred):
    acc, prec, rec, f1 = {}, {}, {}, {}
    for Xt, yt, Xp, yp in zip(X_true, y_true, X_pred, y_pred):
        a, p, r, f = get_metrics_single(Xt, yt, Xp, yp)
        _update_metric(acc, a)
        _update_metric(prec, p)
        _update_metric(rec, r)
        _update_metric(f1, f)
    return _get_mean(acc), _get_mean(prec), _get_mean(rec), _get_mean(f1)
