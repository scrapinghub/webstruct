#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import argparse
from pathlib import Path
import pprint

import joblib
from sklearn.model_selection import GroupKFold
import eli5
from eli5.sklearn_crfsuite.explain_weights import sorted_for_ner
from sklearn_crfsuite.utils import flatten
from sklearn_crfsuite import metrics
import webstruct
from webstruct import features
from webstruct.infer_domain import get_tree_domain
from webstruct.model import NER
from webstruct.sequence_encoding import BilouEncoder

from .data import (
    CONTACT_ENTITIES,
    ADDRESS_ENTITIES,
    GAZETTEER_DATA,
    load_countries,
    load_webstruct_data,
)
from .utils import pages_progress
from .cv import crf_cross_val_predict


H_TAG_REPLACES = {
    'h4': 'h3',
    'h5': 'h3',
    'h6': 'h3',
    'h7': 'h3',
}

# common features
TOKEN_FEATURES = [
    features.bias,
    features.parent_tag,
    features.borders,
    features.block_length,

    features.InsideTag('a'),
    features.InsideTag('strong'),

    features.token_identity,
    features.token_lower,
    features.token_shape,
    features.token_endswith_colon,
    features.token_endswith_dot,
    features.token_has_copyright,
    features.number_pattern,
    features.prefixes_and_suffixes,

    features.looks_like_year,
    features.looks_like_month,
    features.looks_like_email,
    features.looks_like_street_part,
]

GLOBAL_FEATURES = [
    # nearby tokens:
    features.Pattern((-1, 'lower')),
    features.Pattern((-2, 'lower')),
    features.Pattern((-2, 'lower'), (-1, 'lower')),
    features.Pattern((+1, 'lower')),

    # nearby chars
    features.Pattern((-1, 'suffix4')),
    features.Pattern((+1, 'prefix4')),

    # nearby shapes
    features.Pattern((-1, 'shape')),
    features.Pattern((-1, 'shape'), (-2, 'shape')),
    features.Pattern((+1, 'shape')),
]


class LowercaseDAWGGlobalFeature(features.DAWGGlobalFeature):
    def __call__(self, doc):
        token_strings = [tok.token.lower() for tok, feat in doc]
        for start, end, matched_text in self.lm.find_ranges(token_strings):
            self.process_range(doc, start, end, matched_text)


def _gazetteer_feature(filename: str, name: str) -> features.DAWGGlobalFeature:
    file_path = GAZETTEER_DATA / filename
    return features.DAWGGlobalFeature(str(file_path), name)
    # return LowercaseDAWGGlobalFeature(str(file_path), name)


class ContactsModel:
    def get_html_tokenizer(self, sequence_encoder):
        return webstruct.HtmlTokenizer(
            tagset=CONTACT_ENTITIES,
            replace_html_tags=H_TAG_REPLACES,
            sequence_encoder=sequence_encoder,
        )

    def get_crf_pipeline(self):
        GAZETTEER_FEATURES = [
            features.LongestMatchGlobalFeature(load_countries(), 'COUNTRY'),
            _gazetteer_feature('cities1000.dafsa', 'CITY-1000'),
            _gazetteer_feature('cities5000.dafsa', 'CITY-5000'),
            _gazetteer_feature('cities15000.dafsa', 'CITY-15000'),
            _gazetteer_feature('adm1.dafsa', 'ADM1'),
            # _gazetteer_feature('adm2.dafsa', 'ADM2'),
        ]
        pipe = webstruct.create_crfsuite_pipeline(
            token_features=TOKEN_FEATURES,
            global_features=GLOBAL_FEATURES + GAZETTEER_FEATURES,
            verbose=True,
            max_iterations=50,  # stop early
            algorithm='lbfgs',
            c1=0.5,
            c2=0.05,
            all_possible_transitions=True,
            all_possible_states=False,
        )
        return pipe

    def load_training_data(self):
        return load_webstruct_data()


def get_groups(trees):
    return [get_tree_domain(tree) for tree in trees]


def get_labels(y):
    return sorted_for_ner(set(flatten(y)) - {'O'})


def _print_metrics(y_pred, y_true):
    labels = get_labels(y_true)
    print("Sequence accuracy: {:0.1%}".format(
        metrics.sequence_accuracy_score(y_true, y_pred))
    )
    print("Per-tag F1: {:0.3f}".format(
        metrics.flat_f1_score(y_true, y_pred,
                              average='macro',
                              labels=labels)
    ))
    print("Per-tag Classification report: \n{}".format(
        metrics.flat_classification_report(y_true, y_pred,
                                           labels=labels, digits=3))
    )


def save_explanation(crf, out_path='crf-features.html'):
    print("Writing explanation to {} file".format(out_path))
    expl = eli5.explain_weights(crf, top=100)
    html = eli5.format_as_html(expl)
    Path(out_path).write_text("""<!DOCTYPE html>
    <html>
        <title>Contact Extraction Model</title>
        <head><meta charset="utf-8"></head>
        <body>{}</body>
    </html>
    """.format(html))


def save_model(pipe, html_tokenizer, path='contact-extractor.joblib'):
    print("Saving the model as {} ...".format(path))
    ner = webstruct.NER(pipe, html_tokenizer=html_tokenizer)
    joblib.dump(ner, path)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--cv', type=int)
    p.add_argument('--test-folds', type=int)
    p.add_argument('--bilou', type=bool, default=False)
    args = p.parse_args()

    model = ContactsModel()
    sequence_encoder = None
    if args.bilou:
        sequence_encoder = BilouEncoder()
    html_tokenizer = model.get_html_tokenizer(sequence_encoder)

    trees = model.load_training_data()
    train_trees = trees[:400]
    test_trees = trees[400:]

    X, y = html_tokenizer.tokenize(pages_progress(trees, desc='Tokenizing'))
    pipe = model.get_crf_pipeline()

    if not args.cv:
        pipe.fit(pages_progress(X, desc='Extracting features'), y)
        print('tokenizing true')
        X_true, y_true = html_tokenizer.tokenize(pages_progress(test_trees, desc='Tokenizing test'))
        y_pred = pipe.predict(X_true)
        print('measuring metric')
        pp = pprint.PrettyPrinter(2)
        print('\ntrain')
        y_pred_train = pipe.predict(X)
        pp.pprint(webstruct.get_metrics(X, y, X, y_pred_train))
        _print_metrics(y_pred_train, y)
        print('\ntest')
        pp.pprint(webstruct.get_metrics(X_true, y_true, X_true, y_pred))
        _print_metrics(y_pred, y_true)
        save_model(pipe, html_tokenizer)
    else:
        groups = get_groups(trees)
        y_pred, y_true, X_dev = crf_cross_val_predict(pipe, X, y,
            cv=GroupKFold(n_splits=args.cv),
            groups=groups,
            n_folds=args.test_folds,
        )
        # print(X_dev)
        print('measuring metric')
        pp = pprint.PrettyPrinter(2)
        pp.pprint(webstruct.get_metrics(X_dev, y_true, X_dev, y_pred))
        _print_metrics(y_pred, y_true)
        print(len(y_pred))
        # print(y_pred)

    save_explanation(pipe.crf)
