# -*- coding: utf-8 -*-
from __future__ import absolute_import
import subprocess
from lxml.etree import iterwalk


def merge_dicts(*dicts):
    """
    >>> sorted(merge_dicts({'foo': 'bar'}, {'bar': 'baz'}).items())
    [('bar', 'baz'), ('foo', 'bar')]
    """
    res = {}
    for d in dicts:
        res.update(d)
    return res


def get_combined_keys(dicts):
    """
    >>> sorted(get_combined_keys([{'foo': 'egg'}, {'bar': 'spam'}]))
    ['bar', 'foo']
    """
    seen_keys = set()
    for dct in dicts:
        seen_keys.update(dct.keys())
    return seen_keys


def tostr(val):
    if isinstance(val, basestring):
        return val
    if isinstance(val, bool):
        return str(int(val))
    return str(val)


def flatten(x):
    """flatten(sequence) -> list

    Return a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples::

        >>> [1, 2, [3,4], (5,6)]
        [1, 2, [3, 4], (5, 6)]
        >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, (8,9,10)])
        [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]
    """

    result = []
    for el in x:
        if hasattr(el, "__iter__"):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


def replace_html_tags(root, tag_replaces):
    """
    Replace lxml elements' tag.

    >>> from lxml.html import fragment_fromstring, document_fromstring, tostring
    >>> root = fragment_fromstring('<h1>head 1</h1>')
    >>> replace_html_tags(root, {'h1': 'strong'})
    >>> tostring(root)
    '<strong>head 1</strong>'

    >>> root = document_fromstring('<h1>head 1</h1> <H2>head 2</H2>')
    >>> replace_html_tags(root, {'h1': 'strong', 'h2': 'strong', 'h3': 'strong', 'h4': 'strong'})
    >>> tostring(root)
    '<html><body><strong>head 1</strong> <strong>head 2</strong></body></html>'
    """
    for _, elem in iterwalk(root):
        if elem.tag in tag_replaces:
            elem.tag = tag_replaces[elem.tag]


def kill_html_tags(doc, tagnames, keep_child=True):
    """
    >>> from lxml.html import fragment_fromstring, tostring
    >>> root = fragment_fromstring('<div><h1>head 1</h1></div>')
    >>> kill_html_tags(root, ['h1'])
    >>> tostring(root)
    '<div>head 1</div>'

    >>> root = fragment_fromstring('<div><h1>head 1</h1></div>')
    >>> kill_html_tags(root, ['h1'], False)
    >>> tostring(root)
    '<div></div>'
    """
    tagnames = set(tagnames)
    for _, elem in iterwalk(doc):
        if elem.tag in tagnames:
            if keep_child:
                elem.drop_tag()
            else:
                elem.drop_tree()


def run_command(args, verbose=True):
    """
    Execute a command in a subprocess, terminate it if exception occurs,
    raise CalledProcessError exception if command returned non-zero exit code.

    If ``verbose == True`` then print output as it appears using "print".
    Unlike ``subprocess.check_call`` it doesn't assume that stdout
    has a file descriptor - this allows printing to works in IPython notebook.
    """
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = []
    try:
        while True:
            line = p.stdout.readline()
            if not line:
                break
            if verbose:
                print(line.rstrip("\n\r"))
            output.append(line)
        p.wait()
        if p.returncode != 0:
            cmd = subprocess.list2cmdline(args)
            raise subprocess.CalledProcessError(p.returncode, cmd, "\n".join(output))
    finally:
        # kill a process if exception occurs
        if p.returncode is None:
            p.terminate()

