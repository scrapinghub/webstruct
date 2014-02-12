# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re


class WordTokenizer(object):
    """
    This tokenizer is copy-pasted version of TreebankWordTokenizer
    that doesn't split on @ and ':' symbols and doesn't split contractions::

        >>> from nltk.tokenize.treebank import TreebankWordTokenizer
        >>> s = u'''Good muffins cost $3.88\\nin New York. Email: muffins@gmail.com'''
        >>> TreebankWordTokenizer().tokenize(s)
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
    """
    def tokenize(self, text):
        # starting quotes
        text = re.sub(ur'^["“]', r'``', text)               # +unicode quotes
        text = text.replace('``', " `` ")
        text = re.sub(r'([ (\[{<])"', r'\1 `` ', text)

        # punctuation
        text = re.sub(r'(,)(\D|\Z)', r' \1 \2', text)       # CHANGED
        text = text.replace("...", " ... ")
        text = text.replace(u"…", u" ... ")
        text = re.sub(r'[;#$%&|]', r' \g<0> ', text)         # CHANGED @|


        text = re.sub(r'([^\.])(\.)([\]\)}>"\']*)\s*$', r'\1 \2\3 ', text)
        text = re.sub(r'[?!]', r' \g<0> ', text)

        text = re.sub(r"([^'])' ", r"\1 ' ", text)

        # parens, brackets, etc.
        text = re.sub(r'[\]\[\(\)\{\}\<\>]', r' \g<0> ', text)
        text = text.replace("--", " -- ")

        # add extra space to make things easier
        text = " " + text + " "

        # ending quotes
        text = text.replace(u'["”]', " '' ")               # +unicode quotes
        text = re.sub(r'(\S)(\'\')', r'\1 \2 ', text)

        # XXX: contractions handling is removed

        return text.split()


class DefaultTokenizer(WordTokenizer):
    def tokenize(self, text):
        tokens = super(DefaultTokenizer, self).tokenize(text)
        # remove standalone commas and semicolons
        return [t for t in tokens if t not in {',', ';'}]


tokenize = DefaultTokenizer().tokenize
