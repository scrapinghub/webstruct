# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import re


class WordTokenizer(object):
    r"""This tokenizer is copy-pasted version of TreebankWordTokenizer
    that doesn't split on @ and ':' symbols and doesn't split contractions::

    >>> from nltk.tokenize.treebank import TreebankWordTokenizer  # doctest: +SKIP
    >>> s = '''Good muffins cost $3.88\nin New York. Email: muffins@gmail.com'''
    >>> TreebankWordTokenizer().tokenize(s) # doctest: +SKIP
    ['Good', 'muffins', 'cost', '$', '3.88', 'in', 'New', 'York.', 'Email', ':', 'muffins', '@', 'gmail.com']
    >>> WordTokenizer().tokenize(s)
    ['Good', 'muffins', 'cost', '$', '3.88', 'in', 'New', 'York.', 'Email:', 'muffins@gmail.com']
    >>> WordTokenizer().span_tokenize(s)
    [(0, 4), (5, 12), (13, 17), (18, 19), (19, 23), (24, 26), (27, 30), (31, 36), (37, 43), (44, 61)]

    >>> s = '''Shelbourne Road,'''
    >>> WordTokenizer().tokenize(s)
    ['Shelbourne', 'Road', ',']
    >>> WordTokenizer().span_tokenize(s)
    [(0, 10), (11, 15), (15, 16)]

    >>> s = '''population of 100,000'''
    >>> WordTokenizer().tokenize(s)
    ['population', 'of', '100,000']
    >>> WordTokenizer().span_tokenize(s)
    [(0, 10), (11, 13), (14, 21)]

    >>> s = '''Hello|World'''
    >>> WordTokenizer().tokenize(s)
    ['Hello', '|', 'World']
    >>> WordTokenizer().span_tokenize(s)
    [(0, 5), (5, 6), (6, 11)]

    >>> s = '"We beat some pretty good teams to get here," Slocum said.'
    >>> WordTokenizer().tokenize(s)  # doctest: +NORMALIZE_WHITESPACE
    ['``', 'We', 'beat', 'some', 'pretty', 'good',
    'teams', 'to', 'get', 'here', ',', "''", 'Slocum', 'said', '.']
    >>> WordTokenizer().span_tokenize(s)
    [(0, 1), (1, 3), (4, 8), (9, 13), (14, 20), (21, 25), (26, 31), (32, 34),
     (35, 38), (39, 43), (43, 44), (44, 45), (46, 52), (53, 57), (57, 58)]

    >>> s = '''Well, we couldn't have this predictable,
    ... cliche-ridden, \"Touched by an
    ... Angel\" (a show creator John Masius
    ... worked on) wanna-be if she didn't.'''
    >>> WordTokenizer().tokenize(s)  # doctest: +NORMALIZE_WHITESPACE
    ['Well', ',', 'we', "couldn't", 'have', 'this', 'predictable',
     ',', 'cliche-ridden', ',', '``', 'Touched', 'by', 'an',
     'Angel', "''", '(', 'a', 'show', 'creator', 'John', 'Masius',
     'worked', 'on', ')', 'wanna-be', 'if', 'she', "didn't", '.']
    >>> WordTokenizer().span_tokenize(s)
    [(0, 4), (4, 5), (6, 8), (9, 17), (18, 22), (23, 27), (28, 39), (39, 40),
     (41, 54), (54, 55), (56, 57), (57, 64), (65, 67), (68, 70), (71, 76),
     (76, 77), (78, 79), (79, 80), (81, 85), (86, 93), (94, 98), (99, 105),
     (106, 112), (113, 115), (115, 116), (117, 125), (126, 128), (129, 132),
     (133, 139), (139, 140)]

    Some issues:

    >>> WordTokenizer().tokenize("Phone:855-349-1914")  # doctest: +SKIP
    ['Phone', ':', '855-349-1914']

    >>> WordTokenizer().tokenize("Copyright 2014 Foo Bar and Buzz Spam. All Rights Reserved.")   # doctest: +SKIP
    ['Copyright', '2014', 'Foo', 'Bar', 'and', 'Buzz', 'Spam', '.', 'All', 'Rights', 'Reserved', '.']

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
        (re.compile(r'\.(?=[\]\)}>"\']*\s*$)'), None),
        (re.compile(r'[;#$£%&|!?[\](){}<>]'), None),
        (re.compile(r"'(?=\s)|''", re.UNICODE), None),
    ]

    open_quotes = re.compile(r'(^|[\s(\[{<])"')

    def _parse(self, text):
        i = 0
        token_start = 0
        text_length = len(text)
        while 1:
            if i >= text_length:
                yield (token_start, text_length), None
                break
            shift = 1
            partial_text = text[i:]
            for regex, token in self.rules:
                match = regex.match(partial_text)
                if match:
                    yield (token_start, i), None
                    start, shift = match.span()
                    token_start = i + shift
                    yield (i + start, token_start), token
                    break
            i += shift

    def _tokenize(self, text):
        for (start, end), token in self._parse(text):
            # filter empty strings
            if token == '' or start == end:
                continue
            yield (start, end), token

    def tokenize(self, text):
        # this one cannot be placed in the loop because it requires
        # position check (beginning of the string) or previous char value
        text = self.open_quotes.sub(r'\1``', text)
        return [token or text[start:end]
                for (start, end), token in self._tokenize(text)]

    def span_tokenize(self, text):
        return [span for span, _ in self._tokenize(text)]


class DefaultTokenizer(WordTokenizer):
    def tokenize(self, text):
        tokens = super(DefaultTokenizer, self).tokenize(text)
        # remove standalone commas and semicolons
        return [t for t in tokens if t not in {',', ';'}]


tokenize = DefaultTokenizer().tokenize
