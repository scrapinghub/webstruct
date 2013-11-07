# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = ['parent_tag', 'inside_tag', 'borders', 'block_length']

def parent_tag(index, tokens, elem, is_tail):
    return {'parent_tag': elem.tag if not is_tail else elem.getparent().tag}

def inside_tag(tag, index, token, elem, is_tail):
    """
    >>> from lxml.html import fragment_fromstring
    >>> root = fragment_fromstring('<div><strong><p>head 1</p></strong></div>')
    >>> elem = list(root.iter('p'))[0]
    >>> inside_tag('strong', 0, None, elem, False)
    {'inside_tag_strong': True}

    >>> root = fragment_fromstring('<div><strong>head 1</strong></div>')
    >>> elem = list(root.iter('strong'))[0]
    >>> inside_tag('strong', 0, None, elem, False)
    {'inside_tag_strong': True}

    """
    return {'inside_tag_{}'.format(tag): any(e is not None for e in elem.iterancestors(tag)) or elem.tag == tag}

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

