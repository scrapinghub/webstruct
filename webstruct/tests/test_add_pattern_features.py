from webstruct.features.global_features import _add_pattern_features


def test_add_pattern_features():
    feature_dicts = [{'bias': 1,
                      'looks_like_ordinal_day': 'False',
                      'looks_like_range': False,
                      'looks_like_year': False,
                      },
                     {'bias': 1,
                      'looks_like_ordinal_day': 'False',
                      'looks_like_range': False,
                      'looks_like_year': False,
                      },
                     {'bias': 1,
                      'looks_like_ordinal_day': 'False',
                      'looks_like_range': False,
                      'looks_like_year': False,
                      },]

    expected = [{ 'bias': 1,
                  'looks_like_ordinal_day': 'False',
                  'looks_like_range': False,
                  'looks_like_year': False,
                  'looks_like_ordinal_day/looks_like_year[-1]/looks_like_range[-2]': 'False/?/?'},
                { 'bias': 1,
                  'looks_like_ordinal_day': 'False',
                  'looks_like_range': False,
                  'looks_like_year': False,
                  'looks_like_ordinal_day/looks_like_year[-1]/looks_like_range[-2]':  'False/False/?'},
                { 'bias': 1,
                  'looks_like_ordinal_day': 'False',
                  'looks_like_range': False,
                  'looks_like_year': False,
                  'looks_like_ordinal_day/looks_like_year[-1]/looks_like_range[-2]': 'False/False/False'}]

    pattern = ((0, 'looks_like_ordinal_day'),(-1, 'looks_like_year'),(-2, 'looks_like_range'))

    _add_pattern_features(feature_dicts, pattern, '?', '_NA_', '/')
    assert feature_dicts == expected
