# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re


class WordTokenizer(object):
    r"""This tokenizer is copy-pasted version of TreebankWordTokenizer
    that doesn't split on @ and ':' symbols and doesn't split contractions::

    TODO: move test to separate module


    >>> from nltk.tokenize.treebank import TreebankWordTokenizer  # doctest: +SKIP
    >>> s = u'''Good muffins cost $3.88\nin New York. Email: muffins@gmail.com'''
    >>> TreebankWordTokenizer().tokenize(s)  # doctest: +SKIP
    [u'Good', u'muffins', u'cost', u'$', u'3.88', u'in', u'New', u'York.', u'Email', u':', u'muffins', u'@', u'gmail.com']
    >>> WordTokenizer().tokenize(s)
    [u'Good', u'muffins', u'cost', u'$', u'3.88', u'in', u'New', u'York.', u'Email:', u'muffins@gmail.com']
    >>> WordTokenizer().span_tokenize(s)
    [(0, 4), (5, 12), (13, 17), (18, 19), (19, 23), (24, 26), (27, 30), (31, 36), (37, 43), (44, 61)]

    >>> s = u'''Shelbourne Road,'''
    >>> WordTokenizer().tokenize(s)
    [u'Shelbourne', u'Road', u',']
    >>> WordTokenizer().span_tokenize(s)
    [(0, 10), (11, 15), (15, 16)]

    >>> s = u'''population of 100,000'''
    >>> WordTokenizer().tokenize(s)
    [u'population', u'of', u'100,000']
    >>> WordTokenizer().span_tokenize(s)
    [(0, 10), (11, 13), (14, 21)]

    >>> s = u'''Hello|World'''
    >>> WordTokenizer().tokenize(s)
    [u'Hello', u'|', u'World']
    >>> WordTokenizer().span_tokenize(s)
    [(0, 5), (5, 6), (6, 11)]

    >>> s = u'"We beat some pretty good teams to get here," Slocum said.'
    >>> WordTokenizer().tokenize(s)  # doctest: +NORMALIZE_WHITESPACE
    [u'``', u'We', u'beat', u'some', u'pretty', u'good',
    u'teams', u'to', u'get', u'here', u',', u"''", u'Slocum', u'said', u'.']
    >>> WordTokenizer().span_tokenize(s)  # doctest: +NORMALIZE_WHITESPACE
    [(0, 1), (1, 3), (4, 8), (9, 13), (14, 20), (21, 25), (26, 31), (32, 34),
     (35, 38), (39, 43), (43, 44), (44, 45), (46, 52), (53, 57), (57, 58)]
    >>> s = u'''Well, we couldn't have this predictable,
    ... cliche-ridden, \"Touched by an
    ... Angel\" (a show creator John Masius
    ... worked on) wanna-be if she didn't.'''
    >>> WordTokenizer().tokenize(s)  # doctest: +NORMALIZE_WHITESPACE
    [u'Well', u',', u'we', u"couldn't", u'have', u'this', u'predictable',
     u',', u'cliche-ridden', u',', u'``', u'Touched', u'by', u'an',
     u'Angel', u"''", u'(', u'a', u'show', u'creator', u'John', u'Masius',
     u'worked', u'on', u')', u'wanna-be', u'if', u'she', u"didn't", u'.']
    >>> WordTokenizer().span_tokenize(s)  # doctest: +NORMALIZE_WHITESPACE
    [(0, 4), (4, 5), (6, 8), (9, 17), (18, 22), (23, 27), (28, 39), (39, 40),
     (41, 54), (54, 55), (56, 57), (57, 64), (65, 67), (68, 70), (71, 76),
     (76, 77), (78, 79), (79, 80), (81, 85), (86, 93), (94, 98), (99, 105),
     (106, 112), (113, 115), (115, 116), (117, 125), (126, 128), (129, 132),
     (133, 139), (139, 140)]

    Some issues:

    >>> WordTokenizer().tokenize("Phone:855-349-1914")  # doctest: +SKIP
    [u'Phone', u':', u'855-349-1914']

    >>> WordTokenizer().tokenize(u"Copyright © 2014 Foo Bar and Buzz Spam. All Rights Reserved.")  # doctest: +SKIP
    [u'Copyright', u'\xc2\xa9', u'2014', u'Wall', u'Decor', u'and', u'Home', u'Accents', u'.', u'All', u'Rights', u'Reserved', u'.']

    >>> WordTokenizer().tokenize(u"Powai Campus, Mumbai-400077")  # doctest: +SKIP
    [u'Powai', u'Campus', u',', u'Mumbai", "-", "400077']

    >>> WordTokenizer().tokenize(u"1 5858/ 1800")  # doctest: +SKIP
    [u'1', u'5858', u'/', u'1800']

    >>> WordTokenizer().tokenize(u"Saudi Arabia-")  # doctest: +SKIP
    [u'Saudi', u'Arabia', u'-']

    """

    # regex, token
    # if token is None - regex match group is taken
    rules = [
        (re.compile(ur'\s+', re.U), ''),
        (re.compile(ur'“'), u"``"),
        (re.compile(ur'["”]'), u"''"),
        (re.compile(ur'``'), None),
        (re.compile(ur'…|\.\.\.'), u'...'),
        (re.compile(ur'--'), None),
        (re.compile(ur',(?=\D|$)'), None),
        (re.compile(ur'\.(?=[\]\)}>"\']*\s*$)'), None),
        (re.compile(ur'[;#$£%&|!?[\](){}<>]'), None),
        (re.compile(ur"'(?=\s)|''", re.U), None),
    ]

    open_quotes = re.compile(ur'(^|[\s(\[{<])"', re.U)

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
        text = self.open_quotes.sub(ur'\1``', text)
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
