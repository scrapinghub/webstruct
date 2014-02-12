# -*- coding: utf-8 -*-
from __future__ import absolute_import

from webstruct.utils import merge_dicts, LongestMatch


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
        features = [f(*args, **kwargs) for f in self.feature_funcs]
        res = merge_dicts(*features)
        self.seen_keys.update(res.keys())
        return res

    def __repr__(self):
        return "CombinedFeatures(%r)" % (", ".join(map(repr, self.feature_funcs)))

    def copy(self):
        res = CombinedFeatures(*self.feature_funcs)
        res.seen_keys = self.seen_keys.copy()
        return res


class LongestMatchGlobalFeature(object):
    def __init__(self, lookup_data, featname):
        """
        Create a global feature function that adds 3 types of features:

        1) B-featname - if current token starts an entity from
           the ``lookup_data``;
        2) I-featname - if current token is inside an entity from
           the ``lookup_data``;
        3) featname - if current token belongs to an entity from the
           ``lookup_data``.

        """
        if hasattr(lookup_data, 'find_ranges'):
            self.lm = lookup_data
        else:
            self.lm = LongestMatch(lookup_data)
        self.b_featname = 'B-' + featname
        self.i_featname = 'I-' + featname
        self.featname = featname

    def __call__(self, doc):
        token_strings = [tok.token for tok, feat in doc]
        for start, end, matched_text in self.lm.find_ranges(token_strings):
            self.process_range(doc, start, end, matched_text)

    def process_range(self, doc, start, end, matched_text):
        doc[start][1][self.b_featname] = True
        doc[start][1][self.featname] = True

        for idx in range(start+1, end):
            doc[idx][1][self.i_featname] = True
            doc[idx][1][self.featname] = True
