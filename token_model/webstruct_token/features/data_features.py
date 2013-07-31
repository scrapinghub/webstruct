# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re

__all__ = ['looks_like_date', 'looks_like_email', 'looks_like_street_part']

EMAIL_RE = re.compile(
        r"([-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?', re.IGNORECASE)  # domain

MONTHS_RE = re.compile('''
    January|February|March|April|May|June|July|August|September|October|November|December
    |Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec
    ''',
    re.VERBOSE | re.IGNORECASE)

STREET_PART_TOKENS = set('''
avenue ave ave.
boulevard blvd blvd.
street str. st.
road rd rd.
drive dr dr.
lane ln ln.
court
circle
place pl
ridgeway parkway highway
park
'''.split())

COMMON_ADDRESS_PARTS = set('''suite floor p.o. center'''.split())
DIRECTIONS = set('''
north south east west
N S E W N. S. E. W.
NE SE SW NW
northeast southeast southwest northwest
'''.lower().split())


def looks_like_email(index, tokens, elem, is_tail):
    return {
        'looks_like_email': EMAIL_RE.search(tokens[index]) is not None,
    }


def looks_like_date(index, tokens, elem, is_tail):
    token = tokens[0]
    return {
        'looks_like_year': token.isdigit() and len(token)==4 and token[:2] in ['19', '20'],
        'looks_like_month': MONTHS_RE.match(token) is not None,
    }


def looks_like_street_part(index, tokens, elem, is_tail):
    token = tokens[0].lower()
    return {
        'common_street_part': token in STREET_PART_TOKENS,
        'common_address_part': token in COMMON_ADDRESS_PARTS,
        'direction': token in DIRECTIONS,
    }
