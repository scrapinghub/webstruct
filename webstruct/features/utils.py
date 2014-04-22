# -*- coding: utf-8 -*-
from __future__ import absolute_import

import itertools
from webstruct.utils import merge_dicts, LongestMatch


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


class Ngram(object):
    """
    Create a ngram global feature to combine local features.
    """
    def __init__(self, offsets, feature_names, seperator='/', default='?'):
        self.offsets = offsets
        self.feature_names = feature_names
        self.seperator = seperator
        self.default = default

    def __call__(self, doc):
        features = [feat for _, feat in doc]

        # XXX: use index value on HTML element level?
        for i, (html_token, feature) in enumerate(doc):
            keys = []
            values = []
            for offset, name in itertools.izip_longest(self.offsets, self.feature_names, fillvalue=self.feature_names[0]):
                index = offset + i
                keys.append('%s_%s' % (name, offset))
                if 0 <= index < len(features):
                    values.append(features[index][name])
                else:
                    values.append(self.default)
            feature.setdefault(self.seperator.join(keys), self.seperator.join(values))
