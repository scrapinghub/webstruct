# -*- coding: utf-8 -*-
from __future__ import absolute_import

import functools

from .block_features import *
from .token_features import *
from .data_features import *
from .utils import CombinedFeatures

DEFAULT_TAGSET = {'org', 'per', 'subj', 'street', 'city', 'state', 'country',
                  'zipcode', 'email', 'tel', 'fax', 'subj', 'func', 'hours'}

DEFAULT = CombinedFeatures(
    parent_tag,
    borders,
    block_length,

    # inside certain ancestor tags
    functools.partial(inside_tag, 'a'),
    functools.partial(inside_tag, 'strong'),

    token_shape,
    number_pattern,
    prefixes_and_suffixes,

    looks_like_year,
    looks_like_month,
    looks_like_email,
    looks_like_street_part,
)

OPEN_HOURS_TAGSET = {'hours'}

OPEN_HOURS_FEATURES = CombinedFeatures(
    parent_tag,
    borders,
    block_length,

    token_shape,
    number_pattern,
    prefixes_and_suffixes,
    looks_like_email,

    # datetime
    looks_like_year,
    looks_like_time,
    looks_like_month,
    looks_like_weekday,
    looks_like_range
)