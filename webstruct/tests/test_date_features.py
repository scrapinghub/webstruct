from webstruct.features import (looks_like_day_ordinal,
                                looks_like_date_pattern,
                                number_looks_like_day,
                                number_looks_like_month)


class HtmlToken():
    def __init__(self, token):
        self.token = token


def test_looks_like_day_ordinal():

    def assert_looks_like_day_ordinal(token, expected):
        assert looks_like_day_ordinal(token) == expected

    assert_looks_like_day_ordinal(HtmlToken('1st'),
                                  {'looks_like_day_ordinal': True})

    assert_looks_like_day_ordinal(HtmlToken('2nd'), 
                                  {'looks_like_day_ordinal': True})

    assert_looks_like_day_ordinal(HtmlToken('3rd'),
                                  {'looks_like_day_ordinal': True})

    assert_looks_like_day_ordinal(HtmlToken('14th'),
                                  {'looks_like_day_ordinal': True})

    assert_looks_like_day_ordinal(HtmlToken('12th'),
                                  {'looks_like_day_ordinal': True})

    # grammatically wrong but should not add too much noise
    assert_looks_like_day_ordinal(HtmlToken('2th'),
                                  {'looks_like_day_ordinal': True})

    assert_looks_like_day_ordinal(HtmlToken('123th'),
                                  {'looks_like_day_ordinal': False})


def test_looks_like_date_pattern():

    def assert_looks_like_date_pattern(token, expected):
        assert looks_like_date_pattern(token) == expected

    assert_looks_like_date_pattern(HtmlToken('12/12/1989'),
                                   {'looks_like_date_pattern': True})

    assert_looks_like_date_pattern(HtmlToken('12.12.1989'),
                                   {'looks_like_date_pattern': True})

    assert_looks_like_date_pattern(HtmlToken('12-12-1989'),
                                   {'looks_like_date_pattern': True})

    assert_looks_like_date_pattern(HtmlToken('12-12-89'),
                                   {'looks_like_date_pattern': True})

    # TODO make this false
    assert_looks_like_date_pattern(HtmlToken('12-12-989'),
                                   {'looks_like_date_pattern': True})

    assert_looks_like_date_pattern(HtmlToken('12/12-1989'),
                                   {'looks_like_date_pattern': False})

    assert_looks_like_date_pattern(HtmlToken('nottadate'),
                                   {'looks_like_date_pattern': False})

    assert_looks_like_date_pattern(HtmlToken('340-493-0000'),
                                   {'looks_like_date_pattern': False})


def test_number_looks_like_day():
    token = HtmlToken('12')
    assert number_looks_like_day(token) == {'number_looks_like_day': True}

    token = HtmlToken('32')
    assert number_looks_like_day(token) == {'number_looks_like_day': False}


def test_number_looks_like_month():
    token = HtmlToken('12')
    assert number_looks_like_month(token) == {'number_looks_like_month': True}

    token = HtmlToken('32')
    assert number_looks_like_month(token) == {'number_looks_like_month': False}
