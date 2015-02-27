import six


# These two utilities are needed to overcome repr differencies in doctests

def bprint(data):
     if not isinstance(data, str):
         data = data.decode()
     print(data.strip())

def bformat(data):
    if isinstance(data, (list, tuple)):
        return data.__class__(map(bformat, data))
    elif six.PY2 and isinstance(data, unicode):
        return data.encode('utf-8')
    else:
        return data
