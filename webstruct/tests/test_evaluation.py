import os

from webstruct import GateLoader, HtmlTokenizer, WebAnnotatorLoader, load_trees
from webstruct.tests.utils import DATA_PATH
from webstruct.evaluation import (get_metrics,
                                  get_metrics_single,
                                  get_label_entities,
                                  accuracy,
                                  precision,
                                  recall,
                                  f1_score)

KNOWN_ENTITIES = {'CITY', 'EMAIL', 'ORG', 'STATE', 'STREET', 'SUBJ', 'TEL'}
EVAL_PATH = os.path.abspath(os.path.join(
                                DATA_PATH, '..', '..', '..', 'evaluation',
                                         )
                            )


def almost_equal(result, expected):
    all_keys = []
    for k, v in result.items():
        if v == expected[k]:
            all_keys.append(True)
        elif round(v - expected[k], 1) == 0:
            all_keys.append(True)
        else:
            all_keys.append(False)
    return all(all_keys)


def load_true_pred(known_true_entities=KNOWN_ENTITIES,
                   known_pred_entities=KNOWN_ENTITIES):
    true_path = os.path.join(EVAL_PATH, 'annotated_webpage*.html')
    html_tokenizer = HtmlTokenizer()
    wa_loader = WebAnnotatorLoader(known_entities=known_true_entities)
    trees = load_trees(true_path, loader=wa_loader)
    X_true, y_true = html_tokenizer.tokenize(trees)

    pred_path = os.path.join(EVAL_PATH, 'predicted*.html')
    wa_loader = WebAnnotatorLoader(known_entities=known_pred_entities)
    trees = load_trees(pred_path, loader=wa_loader)
    X_pred, y_pred = html_tokenizer.tokenize(trees)

    return X_true, y_true, X_pred, y_pred


def test_get_label_entities():
    text = (b"<p>hello, <PER>John <b>Doe</b></PER> <br> <PER>Mary</PER> said.\
              </p><CITY>San Francisco</CITY>")
    loader = GateLoader(known_entities={'PER', 'CITY'})
    html_tokenizer = HtmlTokenizer(replace_html_tags={'b': 'strong'})
    tree = loader.loadbytes(text)
    X_true, y_true = html_tokenizer.tokenize_single(tree)
    expected = {'PER': {'John Doe', 'Mary'}, 'CITY': {'San Francisco'}}
    assert get_label_entities(X_true, y_true) == expected


def test_accuracy():
    X_true, y_true, X_pred, y_pred = load_true_pred()
    result = accuracy(X_true, y_true, X_pred, y_pred)
    assert almost_equal(result, {'CITY': 1.0,
                                 'EMAIL': 0.805,
                                 'ORG': 1.0,
                                 'STATE': 0.0,
                                 'STREET': 0.5,
                                 'SUBJ': 0.833,
                                 'TEL': 0.833})


def test_precision():
    X_true, y_true, X_pred, y_pred = load_true_pred()
    result = precision(X_true, y_true, X_pred, y_pred)
    assert almost_equal(result, {'CITY': 1.0,
                                 'EMAIL': 0.854,
                                 'ORG': 0.833,
                                 'STATE': 0.0,
                                 'STREET': 0.5,
                                 'SUBJ': 0.833,
                                 'TEL': 1})


def test_recall():
    X_true, y_true, X_pred, y_pred = load_true_pred()
    result = recall(X_true, y_true, X_pred, y_pred)
    assert almost_equal(result, {'CITY': 1.0,
                                 'EMAIL': 0.805,
                                 'ORG': 1.0,
                                 'STATE': 0.0,
                                 'STREET': 0.5,
                                 'SUBJ': 0.833,
                                 'TEL': 0.833})


def test_f1_score():
    X_true, y_true, X_pred, y_pred = load_true_pred()
    result = f1_score(X_true, y_true, X_pred, y_pred)
    assert almost_equal(result, {'CITY': 1.0,
                                 'EMAIL': 0.828,
                                 'ORG': 0.9,
                                 'STATE': 0.0,
                                 'STREET': 0.5,
                                 'SUBJ': 0.833,
                                 'TEL': 0.9})


def test_get_metrics_single():
    known_true_entities = KNOWN_ENTITIES.copy()
    known_true_entities.remove('TEL')
    known_pred_entities = KNOWN_ENTITIES.copy()
    known_pred_entities.remove('CITY')

    X_true, y_true, X_pred, y_pred = load_true_pred(known_true_entities,
                                                    known_pred_entities)
    acc, prec, rec, f1 = get_metrics_single(X_true[1], y_true[1],
                                            X_pred[1], y_pred[1])

    assert almost_equal(acc, {'CITY': 0.0,
                              'EMAIL': 0.777,
                              'ORG': 1.0,
                              'STATE': 0.0,
                              'STREET': 1.0,
                              'SUBJ': 0.666,
                              'TEL': 0.0})

    assert almost_equal(prec, {'CITY': 0.0,
                               'EMAIL': 0.875,
                               'ORG': 0.666,
                               'STATE': 0.0,
                               'STREET': 1.0,
                               'SUBJ': 0.666,
                               'TEL': 0})

    assert almost_equal(rec, {'CITY': 0.0,
                              'EMAIL': 0.777,
                              'ORG': 1.0,
                              'STATE': 0.0,
                              'STREET': 1.0,
                              'SUBJ': 0.666,
                              'TEL': 0.0})

    assert almost_equal(f1, {'CITY': 0,
                             'EMAIL': 0.823,
                             'ORG': 0.8,
                             'STATE': 0.0,
                             'STREET': 1.0,
                             'SUBJ': 0.666,
                             'TEL': 0})


def test_get_metrics():
    X_true, y_true, X_pred, y_pred = load_true_pred()
    acc, prec, rec, f1 = get_metrics(X_true, y_true, X_pred, y_pred)

    assert almost_equal(acc, accuracy(X_true, y_true, X_pred, y_pred))
    assert almost_equal(prec, precision(X_true, y_true, X_pred, y_pred))
    assert almost_equal(rec, recall(X_true, y_true, X_pred, y_pred))
    assert almost_equal(f1, f1_score(X_true, y_true, X_pred, y_pred))
