# -*- coding: utf-8 -*-
from __future__ import absolute_import
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
        'title?': token.istitle(),
    }


def parent_tag(index, tokens, elem, is_tail):
    return {'parent_tag': elem.tag if not is_tail else elem.getparent().tag}


def borders(index, tokens, elem, is_tail):
    return {
        'border_at_left': index == 0,
        'border_at_right': index == len(tokens)-1,
    }


DEFAULT = CombinedFeatures(
    token_shape,
    parent_tag,
    borders
)
