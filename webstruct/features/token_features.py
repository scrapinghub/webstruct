# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
import re

__all__ = [
    'token_identity',
    'token_lower',
    'token_shape',
    'first_upper',
    'token_endswith_dot',
    'token_endswith_colon',
    'token_has_copyright',
    'number_pattern',
    'number_pattern2',
    'prefixes_and_suffixes',
    'PrefixFeatures',
    'SuffixFeatures',
]

def _make_key(prefix, index):
    return '{}_{}'.format(prefix, index) if index else prefix


def token_identity(html_token, index, default='?'):
    k = _make_key('token', index)
    if 0 < index < len(html_token.tokens):
        return {k : html_token.tokens[index]}
    else:
        return {k : default}


def token_lower(html_token, index, default='?'):
    k = _make_key('lower', index)
    if 0 < index < len(html_token.tokens):
        return {k : html_token.tokens[index].lower()}
    else:
        return {k : default}


def token_shape(html_token, index):
    k = _make_key('shape', index)
    try:
        token = html_token.tokens[index]
        return {
            k: _shape(token),
        }
    except IndexError:
        return {}


def first_upper(html_token):
    return {'first_upper': html_token.token.isupper()}


def token_endswith_dot(html_token):
    token = html_token.token
    return {'endswith_dot': token.endswith('.') and token != '.'}


def token_endswith_colon(html_token):
    token = html_token.token
    return {'endswith_colon': token.endswith(':') and token != ':'}


def token_has_copyright(html_token):
    return {'has_copyright': u'©' in html_token.token}


def number_pattern(html_token):
    token = html_token.token
    digit_ratio = sum(1 for ch in token if ch.isdigit()) / len(token)

    if digit_ratio >= 0.3:
        num_pattern = re.sub('\d', 'X', token)
        return {
            'num_pattern': num_pattern,
        }
    else:
        return {}


def number_pattern2(html_token):
    token = html_token.token
    digit_ratio = sum(1 for ch in token if ch.isdigit()) / len(token)

    if digit_ratio >= 0.3:
        num_pattern = re.sub('\d', 'X', token)
        num_pattern2 = re.sub('[^X\W]', 'C', num_pattern)
        return {
            'num_pattern2': num_pattern2,
        }
    else:
        return {}


class PrefixFeatures(object):
    def __init__(self, lenghts=(2,3,4), featname="prefix", lower=True):
        self.lower = lower
        self.featname = featname
        self.sizes = dict(
            zip(["%s%s" % (featname, i) for i in lenghts], lenghts)
        )

    def __call__(self, html_token):
        token = html_token.token if not self.lower else html_token.token.lower()
        return {key: token[:size] for key, size in self.sizes.items()}


class SuffixFeatures(object):
    def __init__(self, lenghts=(2,3,4), featname="suffix", lower=True):
        self.lower = lower
        self.sizes = dict(
            zip(["%s%s" % (featname, i) for i in lenghts], lenghts)
        )

    def __call__(self, html_token):
        token = html_token.token if not self.lower else html_token.token.lower()
        return {key: token[-size:] for key, size in self.sizes.items()}


def prefixes_and_suffixes(html_token):
    token = html_token.token.lower()
    return {
        'prefix2': token[:2],
        'suffix2': token[-2:],
        'prefix3': token[:3],
        'suffix3': token[-3:],
        'prefix4': token[:4],
        'suffix4': token[-4:],
    }


# stolen from NLTK source (nltk.tag.sequential.ClassifierBasedPOSTagger)
def _shape(token):
    if re.match('[-+]?[0-9]+(\.[0-9]*)?|[0-9]*\.[0-9]+$', token):
        return 'number'
    elif re.match('\W+$', token):
        return 'punct'
    elif re.match("[A-Z][a-z'`]+$", token):
        return 'upcase'
    elif re.match("[A-Z][A-Z'`]+$", token):
        return 'caps'
    elif re.match("[a-z]+$", token):
        return 'downcase'
    elif re.match('\w+$', token):
        return 'mixedcase'
    else:
        return 'other'

