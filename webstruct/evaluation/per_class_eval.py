

from webstruct import GateLoader, HtmlTokenizer
loader = GateLoader(known_entities={'PER', 'CITY'})
html_tokenizer = HtmlTokenizer(replace_html_tags={'b': 'strong'})
tree = loader.loadbytes(b"<p>hello, <PER>John <b>Doe</b></PER> <br> <PER>Mary</PER> said </p><CITY>GEnova</CITY>")
X_true, y_true = html_tokenizer.tokenize_single(tree)


def _get_accuracy(true_entities, pred_entities):
    acc = {}
    for label, entities in  true_entities.items():
        if label in pred_entities:
            true_pos = true_entities[label].intersection(pred_entities[label])
            acc[label] = len(true_pos) / len(true_entities[label])
        else:
            acc[label] = 0
    return acc


def _get_precision(true_entities, pred_entities):
    prec = {}
    for label, entities in  true_entities.items():
        if label in pred_entities:
            true_pos = true_entities[label].intersection(pred_entities[label])
            false_pos = pred_entities[label] - true_pos
            prec[label] = len(true_pos) / (len(true_pos) + len(false_pos))
        else:
            prec[label] = 0
    return prec



def _get_recall(true_entities, pred_entities):
    rec = {}
    for label, entities in  true_entities.items():
        if label in pred_entities:
            true_pos = true_entities[label].intersection(pred_entities[label])
            false_neg = true_entities[label] - true_pos
            rec[label] = len(true_pos) / (len(true_pos) + len(false_neg))
        else:
            rec[label] = 0
    return rec


def _get_f1_score(prec, rec):
    f1 = {}
    for label in  prec:
        f1[label] = 2 * (prec[label] * rec[label]) / (prec[label] + rec[label])
    return f1


def get_metrics(X_true, y_true, X_pred, y_pred):
    true_entities = {}
    for token, tag in zip(X_true, y_true):
        if tag == 'O':
            continue
        label = tag[2:]
        if label not in true_entities:
            true_entities[label] = set()
        true_entities[label].update([token.token])

    pred_entities = {}
    for token, tag in zip(X_pred, y_pred):
        if tag == 'O':
            continue
        label = tag[2:]
        if label not in pred_entities:
            pred_entities[label] = set()
        pred_entities[label].update([token.token])

    acc = _get_accuracy(true_entities, pred_entities)
    prec = _get_precision(true_entities, pred_entities)
    rec = _get_recall(true_entities, pred_entities)
    f1 = _get_f1_score(prec, rec)

    return acc, prec, rec, f1

pred_entities = {'CITY': {'GEnova', 'somethingelse'}, 'PER': {'John', 'Mary'}}
