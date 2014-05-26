# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re

class WordTokenizer(object):
    r"""This tokenizer is copy-pasted version of TreebankWordTokenizer
    that doesn't split on @ and ':' symbols and doesn't split contractions::

    >>> from nltk.tokenize.treebank import TreebankWordTokenizer  # doctest: +SKIP
    >>> s = u'''Good muffins cost $3.88\nin New York. Email: muffins@gmail.com'''
    >>> TreebankWordTokenizer().tokenize(s)  # doctest: +SKIP
    [u'Good', u'muffins', u'cost', u'$', u'3.88', u'in', u'New', u'York.', u'Email', u':', u'muffins', u'@', u'gmail.com']
    >>> WordTokenizer().tokenize(s)
    [u'Good', u'muffins', u'cost', u'$', u'3.88', u'in', u'New', u'York.', u'Email:', u'muffins@gmail.com']

    >>> s = u'''Shelbourne Road,'''
    >>> WordTokenizer().tokenize(s)
    [u'Shelbourne', u'Road', u',']

    >>> s = u'''population of 100,000'''
    >>> WordTokenizer().tokenize(s)
    [u'population', u'of', u'100,000']

    >>> s = u'''Hello|World'''
    >>> WordTokenizer().tokenize(s)
    [u'Hello', u'|', u'World']

    >>> s2 = u'"We beat some pretty good teams to get here," Slocum said.'
    >>> WordTokenizer().tokenize(s2)  # doctest: +NORMALIZE_WHITESPACE
    [u'``', u'We', u'beat', u'some', u'pretty', u'good',
    u'teams', u'to', u'get', u'here', u',', u"''", u'Slocum', u'said', u'.']
    >>> s3 = u'''Well, we couldn't have this predictable,
    ... cliche-ridden, \"Touched by an
    ... Angel\" (a show creator John Masius
    ... worked on) wanna-be if she didn't.'''
    >>> WordTokenizer().tokenize(s3)  # doctest: +NORMALIZE_WHITESPACE
    [u'Well', u',', u'we', u"couldn't", u'have', u'this', u'predictable',
     u',', u'cliche-ridden', u',', u'``', u'Touched', u'by', u'an',
     u'Angel', u"''", u'(', u'a', u'show', u'creator', u'John', u'Masius',
     u'worked', u'on', u')', u'wanna-be', u'if', u'she', u"didn't", u'.']

    """

    # regex, token
    # if token is None - regex match group is taken
    rules = [
        (re.compile(r'\s+', re.UNICODE), ''),
        (re.compile(ur'“'), u"``"),
        (re.compile(ur'["”]'), u"''"),
        (re.compile(r'``'), None),
        (re.compile(ur'…|\.\.\.'), u'...'),
        (re.compile(r'--'), None),
        (re.compile(r',(?=\D|$)'), None),
        (re.compile(r'\.$'), None),
        (re.compile(ur'[;#$£%&|!?[\](){}<>]'), None),
        (re.compile(r"'(?=\s)|''", re.UNICODE), None),
    ]

    open_quotes = re.compile(r'(^|[\s(\[{<])"')

    def _tokenize(self, text):
        # this one cannot be placed in the loop because it requires
        # position check (beginning of the string) or previous char value
        text = self.open_quotes.sub(ur'\1``', text)

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
