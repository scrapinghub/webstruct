from copy import deepcopy

from webstruct.sequence_encoding import BilouEncoder

 # Test all wrong combinations II IL LI LL L/IB-something else L/IBsame
            # maybe should deal with UI by changing U to B, maybe not needed because the algorithm right now behaves just as if it was a B

def test_encode():
    input_tokens = ('Detail', '-', '__START_TITLE__', 'Rodin', '-', 
        'Rilke', '-', 'Hofmannsthal.', 'Man', 'and', 'His', 'Genius', 
        '__END_TITLE__', 'Staatliche', 'Museen', 
        'zu', '__START_CITY__', 'Berlin', '__END_CITY__')
    expected = [(0, 'O'), (1, 'O'), (3, 'B-TITLE'), (4, 'I-TITLE'), 
        (5, 'I-TITLE'), (6, 'I-TITLE'), (7, 'I-TITLE'), (8, 'I-TITLE'), 
        (9, 'I-TITLE'), (10, 'I-TITLE'), (11, 'L-TITLE'), (13, 'O'), 
        (14, 'O'), (15, 'O'), (17, 'U-CITY')]
    assert  BilouEncoder().encode(input_tokens) == expected

    input_tokens = ('__START_CITY__', 'Metropolitan', 'City', 
        'of', 'Genoa', '__END_CITY__')
    expected = [(1, 'B-CITY'), (2, 'I-CITY'), (3, 'I-CITY'), (4, 'L-CITY')]
    assert  BilouEncoder().encode(input_tokens) == expected


def test_group():
    data = [('Detail', 'O'), ('-', 'O'), ('Rodin', 'B-TITLE'), ('-', 'I-TITLE'), 
        ('Rilke', 'I-TITLE'), ('-', 'I-TITLE'), ('Hofmannsthal.', 'I-TITLE'), 
        ('Man', 'I-TITLE'), ('and', 'I-TITLE'), ('His', 'I-TITLE'), 
        ('Genius', 'L-TITLE'), ('Staatliche', 'O'), ('Museen', 'O'), 
        ('zu', 'O'), ('Berlin', 'U-CITY')]
    expected = [(['Detail', '-' ], 'O'), 
    (['Rodin', '-', 'Rilke', '-', 'Hofmannsthal.', 'Man', 'and', 'His', 'Genius'], 'TITLE'),
    (['Staatliche', 'Museen', 'zu'], 'O'), (['Berlin'], 'CITY')]
    assert BilouEncoder().group(data) == expected


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

    assert BilouEncoder().group(ilu_data) == expected
    assert BilouEncoder().group(llu_data) == expected
    assert BilouEncoder().group(iiu_data) == expected
    assert BilouEncoder().group(bbu_data) == bbu_expected
    assert BilouEncoder().group(biu_data) == expected
    assert BilouEncoder().group(blb_data) == expected
    assert BilouEncoder().group(bli_data) == bli_expected
    assert BilouEncoder().group(bll_data) == bll_expected
