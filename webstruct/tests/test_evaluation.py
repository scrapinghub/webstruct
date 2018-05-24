import os

import webstruct
from webstruct import GateLoader, HtmlTokenizer
from webstruct.evaluation import get_metrics, get_label_entities
from webstruct.tests.utils import DATA_PATH


def almost_equal(result, expected):
    for k, v in result.items():
        if v == expected[k]:
            return True
        else:
            return round(v - expected[k], 2) == 0


def test_get_label_entities():
    text = (b"<p>hello, <PER>John <b>Doe</b></PER> <br> <PER>Mary</PER> said.\
              </p><CITY>San Francisco</CITY>")
    loader = GateLoader(known_entities={'PER', 'CITY'})
    html_tokenizer = HtmlTokenizer(replace_html_tags={'b': 'strong'})
    tree = loader.loadbytes(text)
    X_true, y_true = html_tokenizer.tokenize_single(tree)
    expected = {'PER': {'John Doe', 'Mary'}, 'CITY': {'San Francisco'}}
    assert get_label_entities(X_true, y_true) == expected


def test_get_metrics():
    KNOWN_TRUE_ENTITIES={'CITY', 'EMAIL', 'ORG', 'STATE', 'STREET', 'SUBJ'}
    KNOWN_PRED_ENTITIES={'EMAIL', 'ORG', 'STATE', 'STREET', 'SUBJ', 'TEL'}
    EVAL_PATH = os.path.abspath(os.path.join(
                                    DATA_PATH, '..', '..', '..', 'evaluation',
                                             )
                                )
    true_path = os.path.join(EVAL_PATH, 'annotated_webpage.html')
    html_tokenizer = HtmlTokenizer()
    wa_loader = webstruct.WebAnnotatorLoader(known_entities=KNOWN_TRUE_ENTITIES)
    trees = webstruct.load_trees(true_path, loader=wa_loader)
    X_true, y_true = html_tokenizer.tokenize(trees)

    pred_path = os.path.join(EVAL_PATH, 'predicted.html')
    html_tokenizer = HtmlTokenizer()
    wa_loader = webstruct.WebAnnotatorLoader(known_entities=KNOWN_PRED_ENTITIES)
    trees = webstruct.load_trees(pred_path, loader=wa_loader)
    X_pred, y_pred = html_tokenizer.tokenize(trees)

    acc, prec, rec, f1 = get_metrics(X_true[0], y_true[0], X_pred[0], y_pred[0])

    assert almost_equal(acc, {'CITY': 0,
                              'EMAIL': 0.777,
                              'ORG': 1.0,
                              'STATE': 0,
                              'STREET': 1.0,
                              'SUBJ': 0.666,
                              'TEL': 0})

    assert almost_equal(prec, {'CITY': 0,
                               'EMAIL': 0.875,
                               'ORG': 0.666,
                               'STATE': 0,
                               'STREET': 1.0,
                               'SUBJ': 0.666,
                               'TEL': 0})

    assert almost_equal(rec, {'CITY': 0,
                              'EMAIL': 0.777,
                              'ORG': 1.0,
                              'STATE': 0,
                              'STREET': 1.0,
                              'SUBJ': 0.666,
                              'TEL': 0})

    assert almost_equal(f1, {'CITY': 0,
                             'EMAIL': 0.823,
                             'ORG': 0.8,
                             'STATE': 0,
                             'STREET': 1.0,
                             'SUBJ': 0.666,
                             'TEL': 0})
