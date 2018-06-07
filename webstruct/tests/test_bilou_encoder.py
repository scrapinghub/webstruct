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
    html_tokens = ['Detail', '-', 'Rodin', '-', 'Rilke', '-', 'Hofmannsthal.',
                   'Staatliche', 'Museen', 'zu', 'Berlin', 'Technik', 'Museum',
                   'Speyer', 'Tel', '123454321']
    tags = ['O', 'O', 'B-TITLE', 'I-TITLE', 'I-TITLE', 'I-TITLE', 'L-TITLE',
            'O', 'O', 'O', 'U-CITY', 'B-ORG', 'I-ORG', 'L-ORG', 'O', 'U-TEL']

    expected = [(['Detail', '-'], 'O'),
                (['Rodin','-', 'Rilke', '-', 'Hofmannsthal.'], 'TITLE'),
                (['Staatliche', 'Museen', 'zu'], 'O'),
                (['Berlin'], 'CITY'),
                (['Technik', 'Museum', 'Speyer'], 'ORG'),
                (['Tel'], 'O'),
                (['123454321'], 'TEL')]

    assert bilou_group(html_tokens, tags) == expected


def test_group_bad_labels():
    html_tokens = ['hello', ',', 'John', 'Doe', 'Mary', 'said']
    tags = ['O', 'O', 'B-PER', 'L-PER', 'U-PER', 'O']

    expected = [(['hello', ',' ], 'O'), (['John', 'Doe'], 'PER'),
                (['Mary'], 'PER'), (['said'], 'O')]
    ilu_tags = deepcopy(tags)
    ilu_tags[2] = "I-PER"
    llu_tags = deepcopy(tags)
    llu_tags[2] = "L-PER"
    iiu_tags = deepcopy(tags)
    iiu_tags[2] = "I-PER"
    iiu_tags[3] = "I-PER"
    bbu_tags = deepcopy(tags)
    bbu_tags[3] = "B-PER"
    biu_tags = deepcopy(tags)
    biu_tags[3] = "I-PER"
    blb_tags = deepcopy(tags)
    blb_tags[4] = "B-PER"
    bli_tags = deepcopy(tags)
    bli_tags[4] = "I-PER"
    bll_tags = deepcopy(tags)
    bll_tags[4] = "L-PER"

    bbu_expected = deepcopy(expected)
    bbu_expected[1:2] = ((['John'], 'PER'), (['Doe'], 'PER'))
    bli_expected = deepcopy(expected)
    bli_expected[1] = (['John', 'Doe', 'Mary'], 'PER')
    del bli_expected[-2]
    bll_expected = bli_expected

    assert bilou_group(html_tokens, ilu_tags) == expected
    assert bilou_group(html_tokens, llu_tags) == expected
    assert bilou_group(html_tokens, iiu_tags) == expected
    assert bilou_group(html_tokens, bbu_tags) == bbu_expected
    assert bilou_group(html_tokens, biu_tags) == expected
    assert bilou_group(html_tokens, blb_tags) == expected
    assert bilou_group(html_tokens, bli_tags) == bli_expected
    assert bilou_group(html_tokens, bll_tags) == bll_expected
