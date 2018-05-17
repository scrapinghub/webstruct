# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
from webstruct.utils import flatten
from .datetime_format import WEEKDAYS, MONTHS

__all__ = ['looks_like_year', 'looks_like_month', 'looks_like_time',
           'looks_like_weekday', 'looks_like_email', 'looks_like_street_part',
           'looks_like_range', 'looks_like_ordinal_en', 'looks_like_date_pattern',
           'number_looks_like_day', 'number_looks_like_month']

EMAIL_PARTS = dict(
    username_re=r"(?P<username>[\w][\w_.-]*)",
    domain_re=r"(?P<domain>[\w][\w_.-]*)",
    zone_re=r"(?P<zone>[a-z]{2}|aero|asia|biz|cat|com|coop|edu|gov|info|int|jobs|mil|moby|museum|name|net|org|pro|tel|travel|xxx)",
)
EMAIL_SRE = r"(?P<space>(\s|%20|\b)){username_re}@{domain_re}\.{zone_re}\b".format(**EMAIL_PARTS)
EMAIL_RE = re.compile(EMAIL_SRE, re.IGNORECASE)


MONTHS_SRE = '|'.join(set(flatten(MONTHS))).replace('.', '\.')
MONTHS_RE = re.compile(r'^(' + MONTHS_SRE + ')$', re.IGNORECASE)

WEEKDAYS_SRE = '|'.join(set(flatten(WEEKDAYS))).replace('.', '\.')
WEEKDAYS_RE = re.compile(r'^(' + WEEKDAYS_SRE + ')$', re.IGNORECASE)

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
unit
block
'''.split())

COMMON_ADDRESS_PARTS = set('''suite floor p.o. po center'''.split())
DIRECTIONS = set('''
north south east west
N S E W N. S. E. W.
NE SE SW NW
northeast southeast southwest northwest
'''.lower().split())

TIME_RE = re.compile('\d{1,2}[\.:]\d{2}')

RANGES = set('''t/m - van tot from to'''.lower().split())


def looks_like_email(html_token):
    return {
        'looks_like_email': EMAIL_RE.search(html_token.token) is not None,
    }


def looks_like_street_part(html_token):
    token = html_token.token.lower()
    return {
        'common_street_part': token in STREET_PART_TOKENS,
        'common_address_part': token in COMMON_ADDRESS_PARTS,
        'direction': token in DIRECTIONS,
    }


def looks_like_year(html_token):
    token = html_token.token
    return {
        'looks_like_year': token.isdigit() and len(token) == 4 and token[:2] in ['19', '20'],
    }


def looks_like_month(html_token):
    token = html_token.token
    return {
        'looks_like_month': MONTHS_RE.match(token) is not None
    }


def looks_like_time(html_token):
    token = html_token.token
    return {
        'looks_like_time': TIME_RE.match(token) is not None
    }


def looks_like_weekday(html_token):
    token = html_token.token
    return {
        'looks_like_weekday': WEEKDAYS_RE.match(token) is not None
    }


def looks_like_range(html_token):
    token = html_token.token.lower()
    return {
        'looks_like_range': token in RANGES
    }


def looks_like_ordinal_en(html_token):
    if len(html_token.token) < 3:
        return {'looks_like_ordinal_en': False}
    if re.search('\d*1st', html_token.token):
        return {'looks_like_ordinal_en': True}
    if re.search('\d*2nd', html_token.token):
        return {'looks_like_ordinal_en': True}
    if re.search('\d*3rd', html_token.token):
        return {'looks_like_ordinal_en': True}
    if re.search('11th|12th|13th', html_token.token):
        return {'looks_like_ordinal_en': True}
    if re.search('\d*[4,5,6,7,8,9,0]th', html_token.token):
        return {'looks_like_ordinal_en': True}
    return {'looks_like_ordinal_en': False}


def looks_like_date_pattern(html_token):
    nchars = len(html_token.token)
    if 6 <= nchars <= 8:
        if re.match('\d{1,2}\/\d{1,2}\/\d{2}$', html_token.token):
            # XX/XX/XX X/XX/XX X/X/XX XX/X/XX
            return {'looks_like_date_pattern': True}
        if re.match('\d{2}\/\d{1,2}\/\d{1,2}$', html_token.token):
            # XX/XX/XX XX/XX/X XX/X/X XX/X/XX
            return {'looks_like_date_pattern': True}

        if re.match('\d{1,2}\.\d{1,2}\.\d{2}$', html_token.token):
            # XX.XX.XX X.XX.XX X.X.XX XX.X.XX
            return {'looks_like_date_pattern': True}
        if re.match('\d{2}\.\d{1,2}\.\d{1, 2}$', html_token.token):
            # XX.XX.XX XX.XX.X XX.X.X XX.X.XX
            return {'looks_like_date_pattern': True}

        if re.match('\d{1,2}-\d{1,2}-\d{2}$', html_token.token):
            # XX-XX-XX X-XX-XX X-X-XX XX-X-XX
            return {'looks_like_date_pattern': True}
        if re.match('\d{2}-\d{1,2}-\d{1, 2}$', html_token.token):
            # XX-XX-XX XX-XX-X XX-X-X XX-X-XX
            return {'looks_like_date_pattern': True}

    elif 8 <= nchars <= 10:
        if re.match('\d{1,2}\/\d{1,2}\/\d{4}$', html_token.token):
            # XX/XX/XXXX X/XX/XXXX X/X/XXXX XX/X/XXXX
            return {'looks_like_date_pattern': True}
        if re.match('\d{4}\/\d{1,2}\/\d{1,2}$', html_token.token):
            # XXXX/XX/XX XXXX/XX/X XXXX/X/X XXXX/X/XX
            return {'looks_like_date_pattern': True}

        if re.match('\d{1,2}\.\d{1,2}\.\d{4}$', html_token.token):
            # XX.XX.XXXX X.XX.XXXX X.X.XXXX XX.X.XXXX
            return {'looks_like_date_pattern': True}
        if re.match('\d{4}\.\d{1,2}\.\d{1, 2}$', html_token.token):
            # XXXX.XX.XX XXXX.XX.X XXXX.X.X XXXX.X.XX
            return {'looks_like_date_pattern': True}

        if re.match('\d{1,2}-\d{1,2}-\d{4}$', html_token.token):
            # XX-XXXX-XX X-XX-XXXX X-X-XXXX XX-X-XXXX
            return {'looks_like_date_pattern': True}
        if re.match('\d{4}-\d{1,2}-\d{1, 2}$', html_token.token):
            # XXXX-XX-XX XXXX-XX-X XXXX-X-X XXXX-X-XX
            return {'looks_like_date_pattern': True}
    return {'looks_like_date_pattern': False}


def number_looks_like_day(html_token):
    try:
        number = int(html_token.token)
        if 0 < number < 32:
            return {'number_looks_like_day': True}
        return {'number_looks_like_day': False}
    except ValueError:
        return {'number_looks_like_day': False}


def number_looks_like_month(html_token):
    try:
        number = int(html_token.token)
        if 0 < number < 13:
            return {'number_looks_like_month': True}
        return {'number_looks_like_month': False}
    except ValueError:
        return {'number_looks_like_month': False}
