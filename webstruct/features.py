import re
import ngrams

# steal from NLTK source
def shape(word):
    if re.match('[0-9]+(\.[0-9]*)?|[0-9]*\.[0-9]+$', word):
        return 'number'
    elif re.match('\W+$', word):
        return 'punct'
    elif re.match('[A-Z][a-z]+$', word):
        return 'upcase'
    elif re.match('[a-z]+$', word):
        return 'downcase'
    elif re.match('\w+$', word):
        return 'mixedcase'
    else:
        return 'other'

def generate_word_feature(token):
    return {
        'word': token,
        'shape': shape(token),
        'prefix2': token[:2].lower(),
        'suffix2': token[-2:].lower(),
        'prefix3': token[:3].lower(),
        'suffix3': token[-3:].lower(),
        'prefix4': token[:4].lower(),
        'suffix4': token[-4:].lower(),
        }

def generalize_token_count(count):
    if count == 1:
        return 1
    elif 1 < count < 10:
        return 5
    else:
        return 10

# use all the word feature by default
DEFAULT_TAGS = (
    # word features
    'word',
    'shape',
    'prefix2',
    'suffix2',
    'prefix3',
    'suffix3',
    'prefix4',
    'suffix4',

    # bigrams
    '2grams',

    # token count
    'token-count',
)

def generate_bag_feature(text):
    """
    generate BOW-like features. i.e. position of word doesn't matter

    e.g.
    >>> f= generate_bag_feature("Contact me me")
    >>> f['word']
    ['Contact', 'me', 'me']
    >>> f['shape']
    ['upcase', 'downcase', 'downcase']
    >>> f['2grams']
    ['$START$|contact', 'contact|me', 'me|me', 'me|$STOP$']
    >>> f['token-count']
    [5]

    """
    tokens = ngrams.tokenize(text)
    feature = {}

    for token in tokens:
        for k,v in generate_word_feature(token).iteritems():
            feature.setdefault(k, []).append(v)

    feature.setdefault('2grams', ngrams.bigrams([token.lower() for token in tokens]))
    feature.setdefault('token-count', [generalize_token_count(len(tokens))])
    return feature

def generate_feature(bags, i, label, deftag=DEFAULT_TAGS):

    """
    >>> texts = ['Contact Us  | UCD Earth Institute', 'Hello']
    >>> bags = [generate_bag_feature(text) for text in texts]
    >>> generate_feature(bags, 0, 'O', ('word',))
    ['O', 'word[0]=Contact', 'word[0]=Us', 'word[0]=|', 'word[0]=UCD', 'word[0]=Earth', 'word[0]=Institute', 'word[+1]=Hello', '__BOS__']

    >>> generate_feature(bags, 1, 'O', ('word',))
    ['O', 'word[0]=Hello', 'word[-1]=Contact', 'word[-1]=Us', 'word[-1]=|', 'word[-1]=UCD', 'word[-1]=Earth', 'word[-1]=Institute', '__EOS__']

    """

    feats = [label]
    bag = bags[i]

    prepbag = bags[i-1] if i>0 else {}
    nextbag = bags[i+1] if i<len(bags)-1 else {}

    for k in deftag:

        for v in bag[k]:
            feats.append('%s[0]=%s' %(k, v))

        for v in prepbag.get(k, []):
            feats.append('%s[-1]=%s' %(k, v))

        for v in nextbag.get(k, []):
            feats.append('%s[+1]=%s' %(k, v))

    if i == 0:
        feats.append("__BOS__")

    elif i == len(bags) - 1:
        feats.append("__EOS__")

    return feats

def generate_features(texts, labels):
    items = []
    bags = [generate_bag_feature(text) for text in texts]
    for i in range(len(bags)):
        items.append(generate_feature(bags, i, labels[i]))
    return items

def convert_crfsuite(items):
    # add a line break to indicate the end of a instance.
    return "\n".join(["\t".join(features) for features in items]) + "\n"

if __name__ == '__main__':
    import doctest
    doctest.testmod()
