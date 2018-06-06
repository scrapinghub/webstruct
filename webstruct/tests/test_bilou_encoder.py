from copy import deepcopy

from webstruct.sequence_encoding import bilou_encoder, bilou_group


def test_encode():
    input_tokens = [['O', 'O', 'B-TITLE', 'I-TITLE', 'I-TITLE', 'I-TITLE',
                    'I-TITLE', 'I-TITLE', 'O', 'O', 'O', 'B-CITY'],
                    ['B-ORG', 'I-ORG'], ['I-ORG'], ['O'], ['B-TEL']]
    expected = [['O', 'O', 'B-TITLE', 'I-TITLE', 'I-TITLE', 'I-TITLE',
                 'I-TITLE', 'L-TITLE', 'O', 'O', 'O', 'U-CITY'],
                ['B-ORG', 'I-ORG'], ['L-ORG'], ['O'], ['U-TEL']]
    assert bilou_encoder(input_tokens) == expected

    input_tokens = [['O']]
    expected = [['O']]
    assert bilou_encoder(input_tokens) == expected

    input_tokens = []
    expected = []
    assert bilou_encoder(input_tokens) == expected


def test_group():
    data = [('Detail', 'O'), ('-', 'O'), ('Rodin', 'B-TITLE'),
            ('-', 'I-TITLE'), ('Rilke', 'I-TITLE'), ('-', 'I-TITLE'),
            ('Hofmannsthal.', 'L-TITLE'), ('Staatliche', 'O'),
            ('Museen', 'O'), ('zu', 'O'), ('Berlin', 'U-CITY'),
            ('Technik', 'B-ORG'), ('Museum', 'I-ORG'), ('Speyer', 'L-ORG'),
            ('Tel', 'O'), ('123454321', 'U-TEL')]
    expected = [(['Detail', '-'], 'O'),
                (['Rodin','-', 'Rilke', '-', 'Hofmannsthal.'], 'TITLE'),
                (['Staatliche', 'Museen', 'zu'], 'O'),
                (['Berlin'], 'CITY'),
                (['Technik', 'Museum', 'Speyer'], 'ORG'),
                (['Tel'], 'O'),
                (['123454321'], 'TEL')]
    assert bilou_group(data) == expected


def test_group_bad_labels():
    correct_data = [("hello", "O"), (",", "O"), ("John", "B-PER"),
                    ("Doe", "L-PER"), ("Mary", "U-PER"), ("said", "O")]
    expected = [(['hello', ',' ], 'O'), (['John', 'Doe'], 'PER'),
                (['Mary'], 'PER'), (['said'], 'O')]
    ilu_data = deepcopy(correct_data)
    ilu_data[2] = ("John", "I-PER")
    llu_data = deepcopy(correct_data)
    llu_data[2] = ("John", "L-PER")
    iiu_data = deepcopy(correct_data)
    iiu_data[2] = ("John", "I-PER")
    iiu_data[3] = ("Doe", "I-PER")
    bbu_data = deepcopy(correct_data)
    bbu_data[3] = ("Doe", "B-PER")
    biu_data = deepcopy(correct_data)
    biu_data[3] = ("Doe", "I-PER")
    blb_data = deepcopy(correct_data)
    blb_data[4] = ("Mary", "B-PER")
    bli_data = deepcopy(correct_data)
    bli_data[4] = ("Mary", "I-PER")
    bll_data = deepcopy(correct_data)
    bll_data[4] = ("Mary", "L-PER")

    bbu_expected = deepcopy(expected)
    bbu_expected[1:2] = ((['John'], 'PER'), (['Doe'], 'PER'))
    bli_expected = deepcopy(expected)
    bli_expected[1] = (['John', 'Doe', 'Mary'], 'PER')
    del bli_expected[-2]
    bll_expected = bli_expected

    assert bilou_group(ilu_data) == expected
    assert bilou_group(llu_data) == expected
    assert bilou_group(iiu_data) == expected
    assert bilou_group(bbu_data) == bbu_expected
    assert bilou_group(biu_data) == expected
    assert bilou_group(blb_data) == expected
    assert bilou_group(bli_data) == bli_expected
    assert bilou_group(bll_data) == bll_expected
