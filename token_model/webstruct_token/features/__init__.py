# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .block_features import *
from .token_features import *
from .data_features import *
from .utils import CombinedFeatures


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
