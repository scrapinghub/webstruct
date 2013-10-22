from gzip import GzipFile
from webstruct.data import get_data
from cStringIO import StringIO

def get_ie_word2vec_classes_data(fn):
    data = get_data(fn)
    stream = GzipFile(fileobj=StringIO(data))
    return dict([line.split()[0], int(line.split()[1])] for line in stream)

word2vec_classes = get_ie_word2vec_classes_data('ie-6k-classes-500.txt.gz')

def token_word2vec_class(index, tokens, elem, is_tail):
    token = tokens[index]
    return {'word2vec_class': word2vec_classes.get(token, 1234)}