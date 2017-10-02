import unittest
import pytest

from webstruct.text_tokenizers import TextToken, WordTokenizer

class TestTokenizerTest(unittest.TestCase):
    def do_tokenize(self, text, result):
        self.assertEqual(result, WordTokenizer().segment_words(text))

    @pytest.mark.xfail
    def test_phone(self):
        return self.do_tokenize(
                "Phone:855-349-1914",
                [TextToken(chars='Phone', position=0, length=5)]
                [TextToken(chars=':', position=5, length=1)]
                [TextToken(chars='855-349-1914', position=6, length=12)]
                )

    @pytest.mark.xfail
    def test_hyphen_mid(self):
        return self.do_tokenize(
                "Powai Campus, Mumbai-400077",
                [TextToken(chars='Powai', position=0, length=5),
                 TextToken(chars='Campus', position=6, length=6),
                 TextToken(chars=',', position=12, length=1),
                 TextToken(chars='Mumbai', position=14, length=6),
                 TextToken(chars='-', position=20, length=1),
                 TextToken(chars='400077', position=21, length=6)]
                )

    @pytest.mark.xfail
    def test_hyphen_end(self):
        return self.do_tokenize(
                "Saudi Arabia-",
                [TextToken(chars='Saudi', position=0, length=5),
                 TextToken(chars='Arabia', position=6, length=6),
                 TextToken(chars='-', position=12, length=1)]
                )

    @pytest.mark.xfail
    def test_hyphen_end(self):
        return self.do_tokenize(
                "1 5858/ 1800",
                [TextToken(chars='1', position=0, length=1),
                 TextToken(chars='5858', position=2, length=4),
                 TextToken(chars='/', position=6, length=1),
                 TextToken(chars='1800', position=8, length=4)]
                )
