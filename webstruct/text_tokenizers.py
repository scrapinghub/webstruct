# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import re
import collections

TextToken = collections.namedtuple('TextToken', 'chars, position, length')


class WordTokenizer(object):
    r"""This tokenizer is copy-pasted version of TreebankWordTokenizer
    that doesn't split on @ and ':' symbols and doesn't split contractions::

    >>> from nltk.tokenize.treebank import TreebankWordTokenizer  # doctest: +SKIP
    >>> s = '''Good muffins cost $3.88\nin New York. Email: muffins@gmail.com'''
    >>> TreebankWordTokenizer().tokenize(s) # doctest: +SKIP
    ['Good', 'muffins', 'cost', '$', '3.88', 'in', 'New', 'York.', 'Email', ':', 'muffins', '@', 'gmail.com']
    >>> WordTokenizer().tokenize(s)
    [TextToken(chars='Good', position=0, length=4),
     TextToken(chars='muffins', position=5, length=7),
     TextToken(chars='cost', position=13, length=4),
     TextToken(chars='$', position=0, length=1),
     TextToken(chars='3.88', position=19, length=4),
     TextToken(chars='in', position=24, length=2),
     TextToken(chars='New', position=27, length=3),
     TextToken(chars='York.', position=31, length=5),
     TextToken(chars='Email:', position=37, length=6),
     TextToken(chars='muffins@gmail.com', position=44, length=17)]

    >>> s = '''Shelbourne Road,'''
    >>> WordTokenizer().tokenize(s)
    [TextToken(chars='Shelbourne', position=0, length=10),
     TextToken(chars='Road', position=11, length=4),
     TextToken(chars=',', position=0, length=1)]

    >>> s = '''population of 100,000'''
    >>> WordTokenizer().tokenize(s)
    [TextToken(chars='population', position=0, length=10),
     TextToken(chars='of', position=11, length=2),
     TextToken(chars='100,000', position=14, length=7)]

    >>> s = '''Hello|World'''
    >>> WordTokenizer().tokenize(s)
    [TextToken(chars='Hello', position=0, length=5),
     TextToken(chars='|', position=0, length=1),
     TextToken(chars='World', position=6, length=5)]

    >>> s2 = '"We beat some pretty good teams to get here," Slocum said.'
    >>> WordTokenizer().tokenize(s2)  # doctest: +NORMALIZE_WHITESPACE
    [TextToken(chars='``', position=0, length=2),
     TextToken(chars='We', position=2, length=2),
     TextToken(chars='beat', position=5, length=4),
     TextToken(chars='some', position=10, length=4),
     TextToken(chars='pretty', position=15, length=6),
     TextToken(chars='good', position=22, length=4),
     TextToken(chars='teams', position=27, length=5),
     TextToken(chars='to', position=33, length=2),
     TextToken(chars='get', position=36, length=3),
     TextToken(chars='here', position=40, length=4),
     TextToken(chars=',', position=0, length=1),
     TextToken(chars="''", position=0, length=1),
     TextToken(chars='Slocum', position=47, length=6),
     TextToken(chars='said', position=54, length=4),
     TextToken(chars='.', position=0, length=1)]
    >>> s3 = '''Well, we couldn't have this predictable,
    ... cliche-ridden, \"Touched by an
    ... Angel\" (a show creator John Masius
    ... worked on) wanna-be if she didn't.'''
    >>> WordTokenizer().tokenize(s3)  # doctest: +NORMALIZE_WHITESPACE
    [TextToken(chars='Well', position=0, length=4),
     TextToken(chars=',', position=0, length=1),
     TextToken(chars='we', position=6, length=2),
     TextToken(chars="couldn't", position=9, length=8),
     TextToken(chars='have', position=18, length=4),
     TextToken(chars='this', position=23, length=4),
     TextToken(chars='predictable', position=28, length=11),
     TextToken(chars=',', position=0, length=1),
     TextToken(chars='cliche-ridden', position=41, length=13),
     TextToken(chars=',', position=0, length=1),
     TextToken(chars='``', position=0, length=2),
     TextToken(chars='Touched', position=58, length=7),
     TextToken(chars='by', position=66, length=2),
     TextToken(chars='an', position=69, length=2),
     TextToken(chars='Angel', position=72, length=5),
     TextToken(chars="''", position=0, length=1),
     TextToken(chars='(', position=0, length=1),
     TextToken(chars='a', position=80, length=1),
     TextToken(chars='show', position=82, length=4),
     TextToken(chars='creator', position=87, length=7),
     TextToken(chars='John', position=95, length=4),
     TextToken(chars='Masius', position=100, length=6),
     TextToken(chars='worked', position=107, length=6),
     TextToken(chars='on', position=114, length=2),
     TextToken(chars=')', position=0, length=1),
     TextToken(chars='wanna-be', position=118, length=8),
     TextToken(chars='if', position=127, length=2),
     TextToken(chars='she', position=130, length=3),
     TextToken(chars="didn't", position=134, length=6),
     TextToken(chars='.', position=0, length=1)]

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
                yield TextToken(chars=text[token_start:],
                                position=token_start,
                                length=len(text) - token_start)
                break
            shift = 1
            partial_text = text[i:]
            for regex, token in self.rules:
                match = regex.match(partial_text)
                if match:
                    yield TextToken(chars=text[token_start:i],
                                    position=token_start,
                                    length=i - token_start)
                    shift = match.end() - match.start()
                    token_start = i + shift
                    if token is None:
                        yield TextToken(chars=match.group(),
                                        position=match.start(),
                                        length=shift)
                    else:
                        yield TextToken(chars=token,
                                        position=match.start(),
                                        length=shift)
                    break
            i += shift

    def tokenize(self, text):
        return [t for t in self._tokenize(text) if t.chars]


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
        return [t for t in tokens if t.chars not in {',', ';'}]


tokenize = DefaultTokenizer().tokenize
