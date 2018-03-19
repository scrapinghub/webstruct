import unittest
from webstruct.features import (looks_like_ordinal_en,
                                looks_like_date_pattern,
                                number_looks_like_day,
                                number_looks_like_month)


class HtmlToken():
    def __init__(self, token):
        self.token = token


def test_looks_like_ordinal_en():

    assert looks_like_ordinal_en(HtmlToken('1st')) == {'looks_like_ordinal_en': True}
    assert looks_like_ordinal_en(HtmlToken('2nd')) == {'looks_like_ordinal_en': True}
    assert looks_like_ordinal_en(HtmlToken('33rd')) == {'looks_like_ordinal_en': True}
    assert looks_like_ordinal_en(HtmlToken('14th')) == {'looks_like_ordinal_en': True}
    assert looks_like_ordinal_en(HtmlToken('12th')) == {'looks_like_ordinal_en': True}
    assert looks_like_ordinal_en(HtmlToken('2th')) == {'looks_like_ordinal_en': False}
    assert looks_like_ordinal_en(HtmlToken('42th')) == {'looks_like_ordinal_en': False}
    assert looks_like_ordinal_en(HtmlToken('123th')) == {'looks_like_ordinal_en': False}


def test_looks_like_date_pattern():
    assert looks_like_date_pattern(HtmlToken('12/12/1989')) == {'looks_like_date_pattern': True}
    assert looks_like_date_pattern(HtmlToken('12.1.1989')) == {'looks_like_date_pattern': True}
    assert looks_like_date_pattern(HtmlToken('1-12-1989')) == {'looks_like_date_pattern': True}
    assert looks_like_date_pattern(HtmlToken('1-2-89')) == {'looks_like_date_pattern': True}
    assert looks_like_date_pattern(HtmlToken('12-12-989')) == {'looks_like_date_pattern': False}
    assert looks_like_date_pattern(HtmlToken('12/12-1989')) == {'looks_like_date_pattern': False}
    assert looks_like_date_pattern(HtmlToken('nottadate')) == {'looks_like_date_pattern': False}
    assert looks_like_date_pattern(HtmlToken('340-493-0000')) == {'looks_like_date_pattern': False}


def test_number_looks_like_day():
    assert number_looks_like_day(HtmlToken('12')) == {'number_looks_like_day': True}
    assert number_looks_like_day(HtmlToken('32')) == {'number_looks_like_day': False}


def test_number_looks_like_month():
    assert number_looks_like_month(HtmlToken('12')) == {'number_looks_like_month': True}
    assert number_looks_like_month(HtmlToken('32')) == {'number_looks_like_month': False}
