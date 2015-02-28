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
    >>> WordTokenizer().tokenize(s) # doctest: +IGNORE_UNICODE
    ['Good', 'muffins', 'cost', '$', '3.88', 'in', 'New', 'York.', 'Email:', 'muffins@gmail.com']

    >>> s = '''Shelbourne Road,'''
    >>> WordTokenizer().tokenize(s) # doctest: +IGNORE_UNICODE
    ['Shelbourne', 'Road', ',']

    >>> s = '''population of 100,000'''
    >>> WordTokenizer().tokenize(s) # doctest: +IGNORE_UNICODE
    ['population', 'of', '100,000']

    >>> s = '''Hello|World'''
    >>> WordTokenizer().tokenize(s) # doctest: +IGNORE_UNICODE
    ['Hello', '|', 'World']

    >>> s2 = '"We beat some pretty good teams to get here," Slocum said.'
    >>> WordTokenizer().tokenize(s2)  # doctest: +NORMALIZE_WHITESPACE +IGNORE_UNICODE
    ['``', 'We', 'beat', 'some', 'pretty', 'good',
    'teams', 'to', 'get', 'here', ',', "''", 'Slocum', 'said', '.']
    >>> s3 = '''Well, we couldn't have this predictable,
    ... cliche-ridden, \"Touched by an
    ... Angel\" (a show creator John Masius
    ... worked on) wanna-be if she didn't.'''
    >>> WordTokenizer().tokenize(s3)  # doctest: +NORMALIZE_WHITESPACE +IGNORE_UNICODE
    ['Well', ',', 'we', "couldn't", 'have', 'this', 'predictable',
     ',', 'cliche-ridden', ',', '``', 'Touched', 'by', 'an',
     'Angel', "''", '(', 'a', 'show', 'creator', 'John', 'Masius',
     'worked', 'on', ')', 'wanna-be', 'if', 'she', "didn't", '.']

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
                yield text[token_start:]
                break
            shift = 1
            partial_text = text[i:]
            for regex, token in self.rules:
                match = regex.match(partial_text)
                if match:
                    yield text[token_start:i]
                    shift = match.end() - match.start()
                    token_start = i + shift
                    if token is None:
                        yield match.group()
                    else:
                        yield token
                    break
            i += shift

    def tokenize(self, text):
        return [t for t in self._tokenize(text) if t]


class DefaultTokenizer(WordTokenizer):
    def tokenize(self, text):
        tokens = super(DefaultTokenizer, self).tokenize(text)
        # remove standalone commas and semicolons
        return [t for t in tokens if t not in {',', ';'}]


tokenize = DefaultTokenizer().tokenize
