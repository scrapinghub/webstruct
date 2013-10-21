import pkgutil

def get_data(fn):
    return pkgutil.get_data('webstruct.data', fn)

def get_ie_word2vec_classes_data(fn):
    data = get_data(fn)
    return dict([line.split()[0], int(line.split()[1])] for line in data.splitlines())