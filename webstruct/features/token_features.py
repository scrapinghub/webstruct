# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
import re

__all__ = ['token_shape', 'number_pattern', 'prefixes_and_suffixes']

def token_shape(html_token):
    token = html_token.token
    return {
        'token': token,
        'lower': token.lower(),
        'shape': _shape(token),
        'endswith_dot': token.endswith('.') and token != '.',
        'endswith_colon': token.endswith(':') and token != ':',
        'first_upper': token[0].isupper(),
        'has_copyright': u'©' in token
    }


def number_pattern(html_token):
    token = html_token.token
    digit_ratio = sum(1 for ch in token if ch.isdigit()) / len(token)

    if digit_ratio >= 0.3:
        num_pattern = re.sub('\d', 'X', token)
        num_pattern2 = re.sub('[^X\W]', 'C', num_pattern)
        return {
            'num_pattern': num_pattern,
            'num_pattern2': num_pattern2,
        }
    else:
        return {}


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

