import re

_RE_SEP = re.compile(ur'[\s,]+', re.U)

def tokenize(text):
    return [token for token in re.split(_RE_SEP, text) if len(token)]

def join_tokens(tokens, sep=' '):
    return sep.join(tokens)

def normalize(text):
    return join_tokens(tokenize(text))

def bigrams(tokens, sep='|'):
    """
    generate bigrams (2grams) with $START$ and $STOP$

    for example:
    >>> bigrams(tokenize("this is a test"), sep='/')
    ['$START$/this', 'this/is', 'is/a', 'a/test', 'test/$STOP$']
    """
    tokens = ["$START$"] + tokens + ["$STOP$"]
    return ['%s%s%s' %(tokens[i], sep, tokens[i+1]) for i in xrange(0, len(tokens)-1)]