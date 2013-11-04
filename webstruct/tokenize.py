# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re


class WordTokenizer(object):
    """
    This tokenizer is copy-pasted version of TreebankWordTokenizer
    that doesn't split on @ and ':' symbols and doesn't split contractions::

        >>> from nltk.tokenize.treebank import TreebankWordTokenizer
        >>> s = '''Good muffins cost $3.88\\nin New York. Email: muffins@gmail.com'''
        >>> TreebankWordTokenizer().tokenize(s)
        ['Good', 'muffins', 'cost', '$', '3.88', 'in', 'New', 'York.', 'Email', ':', 'muffins', '@', 'gmail.com']
        >>> WordTokenizer().tokenize(s)
        ['Good', 'muffins', 'cost', '$', '3.88', 'in', 'New', 'York.', 'Email:', 'muffins@gmail.com']

        >>> s = '''Shelbourne Road,'''
        >>> WordTokenizer().tokenize(s)
        ['Shelbourne', 'Road', ',']

        >>> s = '''Shelbourne Road,1000'''
        >>> WordTokenizer().tokenize(s)
        ['Shelbourne', 'Road', ',', '1000']

        >>> s = '''population of 100,000'''
        >>> WordTokenizer().tokenize(s)
        ['population', 'of', '100,000']

    """
    def tokenize(self, text):
        #starting quotes
        text = re.sub(r'^\"', r'``', text)
        text = re.sub(r'(``)', r' \1 ', text)
        text = re.sub(r'([ (\[{<])"', r'\1 `` ', text)

        #punctuation
        text = re.sub(r'(?<!\d)([,])', r' \1 ', text)     # CHANGED :
        text = re.sub(r'\.\.\.', r' ... ', text)
        text = re.sub(r'[;#$%&]', r' \g<0> ', text)         # CHANGED @


        text = re.sub(r'([^\.])(\.)([\]\)}>"\']*)\s*$', r'\1 \2\3 ', text)
        text = re.sub(r'[?!]', r' \g<0> ', text)

        text = re.sub(r"([^'])' ", r"\1 ' ", text)

        #parens, brackets, etc.
        text = re.sub(r'[\]\[\(\)\{\}\<\>]', r' \g<0> ', text)
        text = re.sub(r'--', r' -- ', text)

        #add extra space to make things easier
        text = " " + text + " "

        #ending quotes
        text = re.sub(r'"', " '' ", text)
        text = re.sub(r'(\S)(\'\')', r'\1 \2 ', text)

        # CHANGED:

        # text = re.sub(r"([^' ])('[sS]|'[mM]|'[dD]|') ", r"\1 \2 ", text)
        # text = re.sub(r"([^' ])('ll|'LL|'re|'RE|'ve|'VE|n't|N'T) ", r"\1 \2 ",
        #               text)
        #
        # for regexp in self.CONTRACTIONS2:
        #     text = regexp.sub(r' \1 \2 ', text)
        # for regexp in self.CONTRACTIONS3:
        #     text = regexp.sub(r' \1 \2 ', text)

        # We are not using CONTRACTIONS4 since
        # they are also commented out in the SED scripts
        # for regexp in self.CONTRACTIONS4:
        #     text = regexp.sub(r' \1 \2 \3 ', text)

        return text.split()


word_tokenizer = WordTokenizer()

def default_tokenizer(text):
    for tok in word_tokenizer.tokenize(text):
        if tok in ',;':
            continue
        yield tok

