# -*- coding: utf-8 -*-
from __future__ import absolute_import


from .block_features import *
from .token_features import *
from .data_features import *
from .utils import CombinedFeatures

DEFAULT_TAGSET = {'ORG', 'PER', 'SUBJ', 'STREET', 'CITY', 'STATE', 'COUNTRY',
                  'ZIPCODE', 'EMAIL', 'TEL', 'FAX', 'SUBJ', 'FUNC', 'HOURS'}

DEFAULT_FEATURES = [
    parent_tag,
    borders,
    block_length,

    # inside certain ancestor tags
    InsideTag('a'),
    InsideTag('strong'),

    token_shape,
    number_pattern,
    prefixes_and_suffixes,

    looks_like_year,
    looks_like_month,
    looks_like_email,
    looks_like_street_part,
]

OPEN_HOURS_TAGSET = {'HOURS'}

OPEN_HOURS_FEATURES = [
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
]
