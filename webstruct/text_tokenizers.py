# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import re
import collections

TextToken = collections.namedtuple('TextToken', 'token, position, length')


class WordTokenizer(object):
    r"""This tokenizer is copy-pasted version of TreebankWordTokenizer
    that doesn't split on @ and ':' symbols and doesn't split contractions::

    >>> from nltk.tokenize.treebank import TreebankWordTokenizer  # doctest: +SKIP
    >>> s = '''Good muffins cost $3.88\nin New York. Email: muffins@gmail.com'''
    >>> TreebankWordTokenizer().tokenize(s) # doctest: +SKIP
    ['Good', 'muffins', 'cost', '$', '3.88', 'in', 'New', 'York.', 'Email', ':', 'muffins', '@', 'gmail.com']
    >>> WordTokenizer().tokenize(s)
    [TextToken(token='Good', position=0, length=4),
     TextToken(token='muffins', position=5, length=7),
     TextToken(token='cost', position=13, length=4),
     TextToken(token='$', position=0, length=1),
     TextToken(token='3.88', position=19, length=4),
     TextToken(token='in', position=24, length=2),
     TextToken(token='New', position=27, length=3),
     TextToken(token='York.', position=31, length=5),
     TextToken(token='Email:', position=37, length=6),
     TextToken(token='muffins@gmail.com', position=44, length=17)]

    >>> s = '''Shelbourne Road,'''
    >>> WordTokenizer().tokenize(s)
    [TextToken(token='Shelbourne', position=0, length=10),
     TextToken(token='Road', position=11, length=4),
     TextToken(token=',', position=0, length=1)]

    >>> s = '''population of 100,000'''
    >>> WordTokenizer().tokenize(s)
    [TextToken(token='population', position=0, length=10),
     TextToken(token='of', position=11, length=2),
     TextToken(token='100,000', position=14, length=7)]

    >>> s = '''Hello|World'''
    >>> WordTokenizer().tokenize(s)
    [TextToken(token='Hello', position=0, length=5),
     TextToken(token='|', position=0, length=1),
     TextToken(token='World', position=6, length=5)]

    >>> s2 = '"We beat some pretty good teams to get here," Slocum said.'
    >>> WordTokenizer().tokenize(s2)  # doctest: +NORMALIZE_WHITESPACE
    [TextToken(token='``', position=0, length=2),
     TextToken(token='We', position=2, length=2),
     TextToken(token='beat', position=5, length=4),
     TextToken(token='some', position=10, length=4),
     TextToken(token='pretty', position=15, length=6),
     TextToken(token='good', position=22, length=4),
     TextToken(token='teams', position=27, length=5),
     TextToken(token='to', position=33, length=2),
     TextToken(token='get', position=36, length=3),
     TextToken(token='here', position=40, length=4),
     TextToken(token=',', position=0, length=1),
     TextToken(token="''", position=0, length=1),
     TextToken(token='Slocum', position=47, length=6),
     TextToken(token='said', position=54, length=4),
     TextToken(token='.', position=0, length=1)]
    >>> s3 = '''Well, we couldn't have this predictable,
    ... cliche-ridden, \"Touched by an
    ... Angel\" (a show creator John Masius
    ... worked on) wanna-be if she didn't.'''
    >>> WordTokenizer().tokenize(s3)  # doctest: +NORMALIZE_WHITESPACE
    [TextToken(token='Well', position=0, length=4),
     TextToken(token=',', position=0, length=1),
     TextToken(token='we', position=6, length=2),
     TextToken(token="couldn't", position=9, length=8),
     TextToken(token='have', position=18, length=4),
     TextToken(token='this', position=23, length=4),
     TextToken(token='predictable', position=28, length=11),
     TextToken(token=',', position=0, length=1),
     TextToken(token='cliche-ridden', position=41, length=13),
     TextToken(token=',', position=0, length=1),
     TextToken(token='``', position=0, length=2),
     TextToken(token='Touched', position=58, length=7),
     TextToken(token='by', position=66, length=2),
     TextToken(token='an', position=69, length=2),
     TextToken(token='Angel', position=72, length=5),
     TextToken(token="''", position=0, length=1),
     TextToken(token='(', position=0, length=1),
     TextToken(token='a', position=80, length=1),
     TextToken(token='show', position=82, length=4),
     TextToken(token='creator', position=87, length=7),
     TextToken(token='John', position=95, length=4),
     TextToken(token='Masius', position=100, length=6),
     TextToken(token='worked', position=107, length=6),
     TextToken(token='on', position=114, length=2),
     TextToken(token=')', position=0, length=1),
     TextToken(token='wanna-be', position=118, length=8),
     TextToken(token='if', position=127, length=2),
     TextToken(token='she', position=130, length=3),
     TextToken(token="didn't", position=134, length=6),
     TextToken(token='.', position=0, length=1)]

    Some issues:

    >>> WordTokenizer().tokenize("Phone:855-349-1914")  # doctest: +SKIP
    ['Phone', ':', '855-349-1914']

    >>> WordTokenizer().tokenize("Copyright © 2014 Foo Bar and Buzz Spam. All Rights Reserved.")  # doctest: +SKIP
    ['Copyright', '\xc2\xa9', '2014', 'Wall', 'Decor', 'and', 'Home', 'Accents', '.', 'All', 'Rights', 'Reserved', '.']

    >>> WordTokenizer().tokenize("Powai Campus, Mumbai-400077")  # doctest: +SKIP
    ['Powai', 'Campus', ',', 'Mumbai", "-", "400077']

    >>> WordTokenizer().tokenize("1 5858/ 1800")  # doctest: +SKIP
    ['1', '5858', '/', '1800']

    >>> WordTokenizer().tokenize("Saudi Arabia-")  # doctest: +SKIP
    ['Saudi', 'Arabia', '-']

    """

    # regex, token
    # if token is None - regex match group is taken
    rules = [
        (re.compile(r'\s+', re.UNICODE), ''),
        (re.compile(r'“'), "``"),
        (re.compile(r'["”]'), "''"),
        (re.compile(r'``'), None),
        (re.compile(r'…|\.\.\.'), '...'),
        (re.compile(r'--'), None),
        (re.compile(r',(?=\D|$)'), None),
        (re.compile(r'\.$'), None),
        (re.compile(r'[;#$£%&|!?[\](){}<>]'), None),
        (re.compile(r"'(?=\s)|''", re.UNICODE), None),
    ]

    open_quotes = re.compile(r'(^|[\s(\[{<])"')

    def _tokenize(self, text):
        # this one cannot be placed in the loop because it requires
        # position check (beginning of the string) or previous char value
        text = self.open_quotes.sub(r'\1``', text)

        i = 0
        token_start = 0
        while 1:
            if i >= len(text):
                yield TextToken(token=text[token_start:],
                                position=token_start,
                                length=len(text) - token_start)
                break
            shift = 1
            partial_text = text[i:]
            for regex, token in self.rules:
                match = regex.match(partial_text)
                if match:
                    yield TextToken(token=text[token_start:i],
                                    position=token_start,
                                    length=i - token_start)
                    shift = match.end() - match.start()
                    token_start = i + shift
                    if token is None:
                        yield TextToken(token=match.group(),
                                        position=match.start(),
                                        length=shift)
                    else:
                        yield TextToken(token=token,
                                        position=match.start(),
                                        length=shift)
                    break
            i += shift

    def tokenize(self, text):
        return [t for t in self._tokenize(text) if t.token]


class DefaultTokenizer(WordTokenizer):
    def tokenize(self, text):
        tokens = super(DefaultTokenizer, self).tokenize(text)
        # remove standalone commas and semicolons
        # as they broke tag sets, e.g. PERSON->FUNCTION in case "PERSON, FUNCTION"

        # but it has negative consequences, e.g.
        # etalon:    [PER-B, PER-I, FUNC-B]
        # predicted: [PER-B, PER-I, PER-I ]
        # because we removed punctuation

        # FIXME: remove as token, but save as feature left/right_punct:","
        return [t for t in tokens if t.token not in {',', ';'}]


tokenize = DefaultTokenizer().tokenize
