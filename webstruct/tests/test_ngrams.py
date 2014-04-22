# -*- coding: utf-8 -*-
from __future__ import absolute_import
from webstruct import GateLoader, HtmlTokenizer, HtmlFeatureExtractor
from webstruct.features import token_lower, token_identity
from webstruct.features import Ngram

def _load_document():
    loader = GateLoader(known_entities=['PER'])
    html_tokenizer = HtmlTokenizer(replace_html_tags={'b': 'strong'})
    tree = loader.loadbytes(b"<p>hello, <PER>John <b>Doe</b></PER> <br> <PER>Mary</PER> said</p>")
    html_tokens, _ = html_tokenizer.tokenize_single(tree)
    return html_tokens

def test_ngrams():
    X = _load_document()
    featextracotr = HtmlFeatureExtractor([token_lower, token_identity], global_features=[Ngram([-2, -1], ['lower'])])
    X2 = featextracotr.transform_single(X)
    assert '?/?' == X2[0].get('lower_-2/lower_-1')
    assert '?/hello' == X2[1].get('lower_-2/lower_-1')
    assert 'hello/john' == X2[2].get('lower_-2/lower_-1')
    assert 'doe/mary' == X2[-1].get('lower_-2/lower_-1')

def test_ngrams_feature_names():
    X = _load_document()
    featextracotr = HtmlFeatureExtractor([token_lower, token_identity], global_features=[
        Ngram([-2, -1], ['lower', 'token'])
    ])
    X2 = featextracotr.transform_single(X)

    assert '?/?' == X2[0].get('lower_-2/token_-1')
    assert '?/hello' == X2[1].get('lower_-2/token_-1')
    assert 'hello/John' == X2[2].get('lower_-2/token_-1')
    assert 'doe/Mary' == X2[-1].get('lower_-2/token_-1')

    featextracotr = HtmlFeatureExtractor([token_lower, token_identity], global_features=[
        Ngram([0, 1], ['lower', 'token'])
    ])
    X2 = featextracotr.transform_single(X)
    assert 'hello/John' == X2[0].get('lower_0/token_1')
    assert 'said/?' == X2[-1].get('lower_0/token_1')
