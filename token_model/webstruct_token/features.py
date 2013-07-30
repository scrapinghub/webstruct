# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
import re
from .utils import merge_dicts

class CombinedFeatures(object):
    """
    Utility for combining several feature functions::

        >>> from pprint import pprint
        >>> def f1(tok): return {'upper': tok.isupper()}
        >>> def f2(tok): return {'len': len(tok)}
        >>> features = CombinedFeatures(f1, f2)
        >>> pprint(features('foo'))
        {'len': 3, 'upper': False}
        >>> print(sorted(features.seen_keys))
        ['len', 'upper']

    """
    def __init__(self, *feature_funcs):
        self.feature_funcs = list(feature_funcs)
        self.seen_keys = set()

    def __iadd__(self, other):
        self.feature_funcs.append(other)
        return self

    def __isub__(self, other):
        self.feature_funcs.remove(other)
        return self

    def __call__(self, *args, **kwargs):
        features = (f(*args, **kwargs) for f in self.feature_funcs)
        res = merge_dicts(*features)
        self.seen_keys.update(res.keys())
        return res

    def __repr__(self):
        return "CombinedFeatures(%r)" % (", ".join(map(repr, self.feature_funcs)))

    def copy(self):
        res = CombinedFeatures(*self.feature_funcs)
        res.seen_keys = self.seen_keys.copy()
        return res


def token_shape(index, tokens, elem, is_tail):
    token = tokens[index]
    return {
        'token': token,
        'lower': token.lower(),
        'shape': _shape(token),
        'endswith_dot': token.endswith('.') and token != '.',
        'first_upper': token[0].isupper(),
        'has_copyright': u'©' in token
    }


def parent_tag(index, tokens, elem, is_tail):
    return {'parent_tag': elem.tag if not is_tail else elem.getparent().tag}

def inside_a_tag(index, token, elem, is_tail):
    return {'inside_a_tag': any(e is not None for e in elem.iterancestors('a'))}

def borders(index, tokens, elem, is_tail):
    return {
        'border_at_left': index == 0,
        'border_at_right': index == len(tokens)-1,
    }

def number_pattern(index, tokens, elem, is_tail):
    token = tokens[index]
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


def prefixes_and_suffixes(index, tokens, elem, is_tail):
    token = tokens[index].lower()
    return {
        'prefix2': token[:2],
        'suffix2': token[-2:],
        'prefix3': token[:3],
        'suffix3': token[-3:],
        'prefix4': token[:4],
        'suffix4': token[-4:],
    }


def block_length(index, tokens, elem, is_tail):
    if len(tokens) == 1:
        bl = '1'
    elif 1 < len(tokens) <= 10:
        bl = 'short'
    elif 10 < len(tokens) <= 20:
        bl = 'medium'
    else:
        bl = 'large'
    return {'block_length': bl}


# stolen from NLTK source (nltk.tag.sequential.ClassifierBasedPOSTagger)
def _shape(token):
    if re.match('[0-9]+(\.[0-9]*)?|[0-9]*\.[0-9]+$', token):
        return 'number'
    elif re.match('\W+$', token):
        return 'punct'
    elif re.match('[A-Z][a-z]+$', token):
        return 'upcase'
    elif re.match('[a-z]+$', token):
        return 'downcase'
    elif re.match('\w+$', token):
        return 'mixedcase'
    else:
        return 'other'


EMAIL_RE = re.compile(
        r"([-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?', re.IGNORECASE)  # domain
MONTHS_RE = re.compile('''
    January|February|March|April|May|June|July|August|September|October|November|December
    |Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec
    ''',
    re.VERBOSE | re.IGNORECASE)


def token_looks_like(index, tokens, elem, is_tail):
    token = tokens[0]
    return {
        'looks_like_email': EMAIL_RE.search(token) is not None,
        'looks_like_year': token.isdigit() and len(token)==4 and token[:2] in ['19', '20'],
        'looks_like_month': MONTHS_RE.match(token) is not None,
    }

DEFAULT = CombinedFeatures(
    token_shape,
    parent_tag,
    inside_a_tag,
    borders,
    number_pattern,
    prefixes_and_suffixes,
    block_length,
    token_looks_like,
)
