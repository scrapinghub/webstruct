# -*- coding: utf-8 -*-
from __future__ import absolute_import


from .block_features import *
from .token_features import *
from .data_features import *
from .utils import CombinedFeatures, JoinFeatures
import functools

DEFAULT_TAGSET = {'ORG', 'PER', 'SUBJ', 'STREET', 'CITY', 'STATE', 'COUNTRY',
                  'ZIPCODE', 'EMAIL', 'TEL', 'FAX', 'SUBJ', 'FUNC', 'HOURS'}

DEFAULT_FEATURES = [
    parent_tag,
    borders,
    block_length,

    # inside certain ancestor tags
    InsideTag('a'),
    InsideTag('strong'),

    functools.partial(token_identity, index=0),
    functools.partial(token_lower, index=0),

    first_upper,
    functools.partial(token_shape, index=0),
    token_endswith_colon,
    token_endswith_dot,
    token_has_copyright,
    number_pattern,
    number_pattern2,
    prefixes_and_suffixes,

    looks_like_year,
    looks_like_month,
    looks_like_email,
    looks_like_street_part,
]

CRFSUITE_FEATURES = DEFAULT_FEATURES + [
    functools.partial(token_identity, index=-1),
    functools.partial(token_identity, index=1),

    functools.partial(token_lower, index=-1),
    functools.partial(token_lower, index=1),

    functools.partial(token_shape, index=-1),
    functools.partial(token_shape, index=1),

    JoinFeatures(functools.partial(token_lower, index=-2), functools.partial(token_lower, index=-1)),
    JoinFeatures(functools.partial(token_lower, index=-1), functools.partial(token_lower, index=0)),

    JoinFeatures(functools.partial(token_lower, index=0), functools.partial(token_lower, index=1)),
    JoinFeatures(functools.partial(token_lower, index=1), functools.partial(token_lower, index=2)),

    JoinFeatures(functools.partial(token_lower, index=-1), functools.partial(token_lower, index=0)),
    JoinFeatures(functools.partial(token_lower, index=0), functools.partial(token_lower, index=1)),
]