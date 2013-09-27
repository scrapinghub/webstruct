# -*- coding: utf-8 -*-
from __future__ import absolute_import

from ..utils import merge_dicts

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


def substrings(txt, min_length=2, max_length=10, pad=''):
    """
    >>> substrings("abc", 1)
    ['a', 'ab', 'abc', 'b', 'bc', 'c']
    >>> substrings("abc", 2)
    ['ab', 'abc', 'bc']
    >>> substrings("abc", 1, 2)
    ['a', 'ab', 'b', 'bc', 'c']
    >>> substrings("abc", 1, 3, '$')
    ['$a', 'a', '$ab', 'ab', '$abc', 'abc', 'abc$', 'b', 'bc', 'bc$', 'c', 'c$']
    """
    res = []
    for start in range(len(txt)):
        remaining_length = len(txt) - start
        for length in range(min_length, min(max_length+1, remaining_length+1)):
            token = txt[start:start+length]
            if start == 0 and pad:
                res.append(pad+token)
            res.append(token)
            if length == remaining_length and pad:
                res.append(token+pad)
    return res

def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, (8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        if hasattr(el, "__iter__"):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result
