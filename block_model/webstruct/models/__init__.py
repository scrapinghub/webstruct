from os.path import join, dirname


def get_data_path(fn):
    return join(dirname(__file__), fn)