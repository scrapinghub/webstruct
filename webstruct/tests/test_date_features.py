from webstruct.features import (looks_like_day_ordinal,
                                looks_like_date_pattern,
                                number_looks_like_day,
                                number_looks_like_month)


class HtmlToken():
    def __init__(self, token):
        self.token = token


def test_looks_like_day_ordinal():
    token = HtmlToken('1st')
    expected = {'looks_like_day_ordinal': True}
    result = looks_like_day_ordinal(token)
    assert result == expected

    token = HtmlToken('2nd')
    expected = {'looks_like_day_ordinal': True}
    result = looks_like_day_ordinal(token)
    assert result == expected

    token = HtmlToken('3rd')
    expected = {'looks_like_day_ordinal': True}
    result = looks_like_day_ordinal(token)
    assert result == expected

    token = HtmlToken('14th')
    expected = {'looks_like_day_ordinal': True}
    result = looks_like_day_ordinal(token)
    assert result == expected

    token = HtmlToken('12th')
    expected = {'looks_like_day_ordinal': True}
    result = looks_like_day_ordinal(token)
    assert result == expected

    # grammatically wrong but should not add too much noise
    token = HtmlToken('2th')
    expected = {'looks_like_day_ordinal': True}
    result = looks_like_day_ordinal(token)
    assert result == expected

    token = HtmlToken('123th')
    expected = {'looks_like_day_ordinal': False}
    result = looks_like_day_ordinal(token)
    assert result == expected


def test_looks_like_date_pattern():
    token = HtmlToken('12/12/1989')
    expected = {'looks_like_date_pattern': True}
    result = looks_like_date_pattern(token)
    assert result == expected

    token = HtmlToken('12.12.1989')
    expected = {'looks_like_date_pattern': True}
    result = looks_like_date_pattern(token)
    assert result == expected

    token = HtmlToken('12-12-1989')
    expected = {'looks_like_date_pattern': True}
    result = looks_like_date_pattern(token)
    assert result == expected

    token = HtmlToken('12-12-89')
    expected = {'looks_like_date_pattern': True}
    result = looks_like_date_pattern(token)
    assert result == expected

    # TODO make this false
    token = HtmlToken('12-12-989')
    expected = {'looks_like_date_pattern': True}
    result = looks_like_date_pattern(token)
    assert result == expected

    token = HtmlToken('12/12-1989')
    expected = {'looks_like_date_pattern': False}
    result = looks_like_date_pattern(token)
    assert result == expected

    token = HtmlToken('nottadate')
    expected = {'looks_like_date_pattern': False}
    result = looks_like_date_pattern(token)
    assert result == expected


def test_number_looks_like_day():
    token = HtmlToken('12')
    expected = {'number_looks_like_day': True}
    result = number_looks_like_day(token)
    assert result == expected

    token = HtmlToken('32')
    expected = {'number_looks_like_day': False}
    result = number_looks_like_day(token)
    assert result == expected


def test_number_looks_like_month():
    token = HtmlToken('12')
    expected = {'number_looks_like_month': True}
    result = number_looks_like_month(token)
    assert result == expected

    token = HtmlToken('32')
    expected = {'number_looks_like_month': False}
    result = number_looks_like_month(token)
    assert result == expected
