from __future__ import absolute_import
import six


def accuracy(X_true, y_true, X_pred, y_pred):
    acc = {}
    for Xt, yt, Xp, yp in zip(X_true, y_true, X_pred, y_pred):
        true_entities = get_label_entities(Xt, yt)
        pred_entities = get_label_entities(Xp, yp)
        a = _get_accuracy(true_entities, pred_entities)
        _update_metric(acc, a)
    return _get_mean(acc)


def _get_accuracy(true_entities, pred_entities):
    acc = {}
    for label, entities in true_entities.items():
        if label in pred_entities:
            true_pos = true_entities[label].intersection(pred_entities[label])
            acc[label] = (1.0 * len(true_pos)) / (1.0 * len(true_entities[label]))
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
    return acc


def precision(X_true, y_true, X_pred, y_pred):
    prec = {}
    for Xt, yt, Xp, yp in zip(X_true, y_true, X_pred, y_pred):
        true_entities = get_label_entities(Xt, yt)
        pred_entities = get_label_entities(Xp, yp)
        p = _get_precision(true_entities, pred_entities)
        _update_metric(prec, p)
    return _get_mean(prec)


def _get_precision(true_entities, pred_entities):
    prec = {}
    for label, entities in true_entities.items():
        if label in pred_entities:
            true_pos = true_entities[label].intersection(pred_entities[label])
            false_pos = pred_entities[label] - true_pos
            prec[label] = (1.0 * len(true_pos)) / (len(true_pos) + len(false_pos))
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


def recall(X_true, y_true, X_pred, y_pred):
    rec = {}
    for Xt, yt, Xp, yp in zip(X_true, y_true, X_pred, y_pred):
        true_entities = get_label_entities(Xt, yt)
        pred_entities = get_label_entities(Xp, yp)
        r = _get_recall(true_entities, pred_entities)
        _update_metric(rec, r)
    return _get_mean(rec)


def _get_recall(true_entities, pred_entities):
    rec = {}
    for label, entities in true_entities.items():
        if label in pred_entities:
            true_pos = true_entities[label].intersection(pred_entities[label])
            false_neg = true_entities[label] - true_pos
            rec[label] = (1.0 * len(true_pos)) / (len(true_pos) + len(false_neg))
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


def f1_score(X_true, y_true, X_pred, y_pred):
    f1 = {}
    for Xt, yt, Xp, yp in zip(X_true, y_true, X_pred, y_pred):
        true_entities = get_label_entities(Xt, yt)
        pred_entities = get_label_entities(Xp, yp)
        prec = _get_precision(true_entities, pred_entities)
        rec = _get_recall(true_entities, pred_entities)
        f = _get_f1_score(prec, rec)
        _update_metric(f1, f)
    return _get_mean(f1)


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
    '''returns accuracy, precision and f1 score for each label'''
    acc, prec, rec, f1 = {}, {}, {}, {}
    for Xt, yt, Xp, yp in zip(X_true, y_true, X_pred, y_pred):
        a, p, r, f = get_metrics_single(Xt, yt, Xp, yp)
        _update_metric(acc, a)
        _update_metric(prec, p)
        _update_metric(rec, r)
        _update_metric(f1, f)
    return _get_mean(acc), _get_mean(prec), _get_mean(rec), _get_mean(f1)
#
#
#
#
# import os
#
# from webstruct import GateLoader, HtmlTokenizer, WebAnnotatorLoader, load_trees
# from webstruct.tests.utils import DATA_PATH
#
#
# KNOWN_ENTITIES = {'CITY', 'EMAIL', 'ORG', 'STATE', 'STREET', 'SUBJ', 'TEL'}
# EVAL_PATH = '/Users/ludovica/Documents/Scrapinghub/webstruct/webstruct_data/evaluation/'
#
# result = acc
# expected = {'CITY': 0.0,
#                           'EMAIL': 0.777,
#                           'ORG': 1.0,
#                           'STATE': 0.0,
#                           'STREET': 1.0,
#                           'SUBJ': 0.666,
#                           'TEL': 0.0}
# def almost_equal(result, expected):
#     all_keys = []
#     for k, v in result.items():
#         if v == expected[k]:
#             all_keys.append(True)
#         elif round(v - expected[k], 1) == 0:
#             all_keys.append(True)
#         else:
#             print(k)
#             all_keys.append(False)
#     return all(all_keys)
#
#
# def load_true_pred(known_true_entities=KNOWN_ENTITIES,
#                    known_pred_entities=KNOWN_ENTITIES):
#     true_path = os.path.join(EVAL_PATH, 'annotated_webpage*.html')
#     html_tokenizer = HtmlTokenizer()
#     wa_loader = WebAnnotatorLoader(known_entities=known_true_entities)
#     trees = load_trees(true_path, loader=wa_loader)
#     X_true, y_true = html_tokenizer.tokenize(trees)
#
#     pred_path = os.path.join(EVAL_PATH, 'predicted*.html')
#     wa_loader = WebAnnotatorLoader(known_entities=known_pred_entities)
#     trees = load_trees(pred_path, loader=wa_loader)
#     X_pred, y_pred = html_tokenizer.tokenize(trees)
#
#     return X_true, y_true, X_pred, y_pred
#
#
# def test_get_label_entities():
#     text = (b"<p>hello, <PER>John <b>Doe</b></PER> <br> <PER>Mary</PER> said.\
#               </p><CITY>San Francisco</CITY>")
#     loader = GateLoader(known_entities={'PER', 'CITY'})
#     html_tokenizer = HtmlTokenizer(replace_html_tags={'b': 'strong'})
#     tree = loader.loadbytes(text)
#     X_true, y_true = html_tokenizer.tokenize_single(tree)
#     expected = {'PER': {'John Doe', 'Mary'}, 'CITY': {'San Francisco'}}
#     assert get_label_entities(X_true, y_true) == expected
#
# known_true_entities = KNOWN_ENTITIES.copy()
# known_true_entities.remove('TEL')
# known_pred_entities = KNOWN_ENTITIES.copy()
# known_pred_entities.remove('CITY')
#
# X_true, y_true, X_pred, y_pred = load_true_pred(known_true_entities,
#                                                 known_pred_entities)
#
# acc, prec, rec, f1 = get_metrics_single(X_true[1], y_true[1],
#                                         X_pred[1], y_pred[1])
#
# assert almost_equal(acc, {'CITY': 0.0,
#                           'EMAIL': 0.777,
#                           'ORG': 1.0,
#                           'STATE': 0.0,
#                           'STREET': 1.0,
#                           'SUBJ': 0.666,
#                           'TEL': 0.0})
#
# assert almost_equal(prec, {'CITY': 0.0,
#                            'EMAIL': 0.875,
#                            'ORG': 0.666,
#                            'STATE': 0.0,
#                            'STREET': 1.0,
#                            'SUBJ': 0.666,
#                            'TEL': 0})
#
# assert almost_equal(rec, {'CITY': 0.0,
#                           'EMAIL': 0.777,
#                           'ORG': 1.0,
#                           'STATE': 0.0,
#                           'STREET': 1.0,
#                           'SUBJ': 0.666,
#                           'TEL': 0.0})
#
# assert almost_equal(f1, {'CITY': 0,
#                          'EMAIL': 0.823,
#                          'ORG': 0.8,
#                          'STATE': 0.0,
#                          'STREET': 1.0,
#                          'SUBJ': 0.666,
#                          'TEL': 0})
