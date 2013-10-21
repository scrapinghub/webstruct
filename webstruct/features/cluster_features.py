from webstruct.data import get_ie_word2vec_classes_data

word2vec_classes = get_ie_word2vec_classes_data('ie-classes.txt')

def token_word2vec_class(index, tokens, elem, is_tail):
    token = tokens[index]
    return {'word2vec_class': word2vec_classes.get(token, 1234)}