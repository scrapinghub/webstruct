# -*- coding: utf-8 -*-
from __future__ import absolute_import

from webstruct.infer_domain import guess_domain, get_tree_domain, get_base_href
from webstruct.loaders import HtmlLoader


def _load(html_bytes):
    ld = HtmlLoader()
    return ld.loadbytes(html_bytes)


def test_guess_domain():
    tree = _load(b"""
    <html>
        <body>
            <a href="https://twitter.com/">share</a>
            <a href="http://example2.com/baz">baz</a>
            <a href="http://example.com/foo">foo</a>
            <a href="http://foo.example.com/bar">bar</a>
        </body>
    </html>
    """)
    assert guess_domain(tree) == "example.com"
    assert get_tree_domain(tree) == "example.com"
    assert get_base_href(tree) is None


def test_baseurl():
    tree = _load(b"""
    <html>
        <head>
            <base  href="http://example.org/foo"/>
        </head>
        <body>
            <a href="https://twitter.com/">share</a>
            <a href="http://example2.com/baz">baz</a>
            <a href="http://example.com/foo">foo</a>
            <a href="http://foo.example.com/bar">bar</a>
        </body>
    </html>
    """)
    assert guess_domain(tree) == "example.com"
    assert get_base_href(tree) == "http://example.org/foo"
    assert get_tree_domain(tree) == "example.org"


def test_commented_baseurl():
    tree = _load(b"""
    <html>
        <head>
            <!--base  href="http://example.org/foo"/-->
        </head>
        <body>
            <a href="https://twitter.com/">share</a>
            <a href="http://example2.com/baz">baz</a>
            <a href="http://example.com/foo">foo</a>
            <a href="http://foo.example.com/bar">bar</a>
        </body>
    </html>
    """)
    assert guess_domain(tree) == "example.com"
    assert get_base_href(tree) == "http://example.org/foo"
    assert get_tree_domain(tree) == "example.org"


def test_no_links():
    tree = _load(b"""<html><body><p>empty</p></body></html>""")
    assert guess_domain(tree) == ""
    assert get_base_href(tree) is None
    assert get_tree_domain(tree) == ""
