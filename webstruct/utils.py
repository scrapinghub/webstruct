# -*- coding: utf-8 -*-
from __future__ import absolute_import

def merge_dicts(*dicts):
    """
    >>> sorted(merge_dicts({'foo': 'bar'}, {'bar': 'baz'}).items())
    [('bar', 'baz'), ('foo', 'bar')]
    """
    res = {}
    for d in dicts:
        res.update(d)
    return res


def get_combined_keys(dicts):
    """
    >>> sorted(get_combined_keys([{'foo': 'egg'}, {'bar': 'spam'}]))
    ['bar', 'foo']
    """
    seen_keys = set()
    for dct in dicts:
        seen_keys.update(dct.keys())
    return seen_keys


def tostr(val):
    if isinstance(val, basestring):
        return val
    if isinstance(val, bool):
        return str(int(val))
    return str(val)
