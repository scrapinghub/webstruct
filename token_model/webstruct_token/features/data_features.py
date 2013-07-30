# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re

__all__ = ['token_looks_like']

EMAIL_RE = re.compile(
        r"([-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?', re.IGNORECASE)  # domain
MONTHS_RE = re.compile('''
    January|February|March|April|May|June|July|August|September|October|November|December
    |Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec
    ''',
    re.VERBOSE | re.IGNORECASE)


def token_looks_like(index, tokens, elem, is_tail):
    token = tokens[0]
    return {
        'looks_like_email': EMAIL_RE.search(token) is not None,
        'looks_like_year': token.isdigit() and len(token)==4 and token[:2] in ['19', '20'],
        'looks_like_month': MONTHS_RE.match(token) is not None,
    }

