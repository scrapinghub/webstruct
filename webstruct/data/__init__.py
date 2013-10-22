import pkgutil

def get_data(fn):
    return pkgutil.get_data('webstruct.data', fn)