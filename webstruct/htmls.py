from lxml.etree import iterwalk


def replace_tags(root, tags, name):
    """
    Replace lxml element's tag.

    >>> from lxml.html import fragment_fromstring, document_fromstring, tostring
    >>> root = fragment_fromstring('<h1>head 1</h1>')
    >>> root = replace_tags(root, ['h1'], 'strong')
    >>> tostring(root)
    '<strong>head 1</strong>'

    >>> root = document_fromstring('<h1>head 1</h1> <h2>head 2</h2>')
    >>> root = replace_tags(root, ['h1','h2','h3','h4'], 'strong')
    >>> tostring(root)
    '<html><body><strong>head 1</strong> <strong>head 2</strong></body></html>'
    """
    for tag in tags:
        for e in root.iter(tag):
            e.tag = name
    return root

def kill_tags(doc, tags, keep_child=True):
    """
    >>> from lxml.html import fragment_fromstring, tostring
    >>> root = fragment_fromstring('<div><h1>head 1</h1></div>')
    >>> root = kill_tags(root, ['h1'])
    >>> tostring(root)
    '<div>head 1</div>'

    >>> root = fragment_fromstring('<div><h1>head 1</h1></div>')
    >>> root = kill_tags(root, ['h1'], False)
    >>> tostring(root)
    '<div></div>'
    """
    for _, elem in iterwalk(doc):
        if elem.tag in tags:
            if keep_child:
                elem.drop_tag()
            else:
                elem.drop_tree()
    return doc


