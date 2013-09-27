# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = ['parent_tag', 'inside_a_tag', 'borders', 'block_length']

def parent_tag(index, tokens, elem, is_tail):
    return {'parent_tag': elem.tag if not is_tail else elem.getparent().tag}

def inside_a_tag(index, token, elem, is_tail):
    return {'inside_a_tag': any(e is not None for e in elem.iterancestors('a'))}

def borders(index, tokens, elem, is_tail):
    return {
        'border_at_left': index == 0,
        'border_at_right': index == len(tokens)-1,
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

