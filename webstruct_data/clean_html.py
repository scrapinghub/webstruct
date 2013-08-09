#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTML cleaning script. It:

* strips <script>, <style> and alike tags;
* converts page to UTF-8 (regardless of encoding specified in meta tag,
  without changing that meta tag).

Existing files in output folder are silently overwritten.

Usage:
  clean_html.py [--out=<folder>] <input> ...
  clean_html.py (-h | --help)

Options:
  -h --help           Show this screen.
  -o --out=<folder>   Where to store the results [default: cleaned].

"""

import codecs
import os
import lxml.html.clean
import lxml.etree
from lxml.html import HTMLParser
from w3lib.encoding import html_to_unicode
from docopt import docopt


def clean_html(html, encoding=None):
    cleaner = lxml.html.clean.Cleaner(
        style=True,
        scripts=True,
        embedded=True,
        links=True,
        page_structure=False,
        remove_unknown_tags=False,
        meta=False,
        safe_attrs_only=False
    )
    parser = HTMLParser(encoding=encoding)
    html = lxml.html.document_fromstring(html, parser=parser)
    doc = cleaner.clean_html(html)
    return lxml.etree.tounicode(doc)


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError:
        pass


if __name__ == '__main__':
    args = docopt(__doc__)

    mkdir(args['--out'])
    for in_name in args['<input>']:
        path, fname = os.path.split(in_name)
        out_name = os.path.join(args['--out'], fname)

        with open(in_name, 'rb') as f:
            encoding, html = html_to_unicode(None, f.read())

        cleaned = clean_html(html.encode(encoding), encoding)

        with codecs.open(out_name, 'w', encoding='utf8') as out:
            out.write(cleaned)
