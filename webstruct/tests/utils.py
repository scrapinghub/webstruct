# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import unittest
from itertools import islice
from doctest import Example

import lxml.html
from lxml.doctestcompare import LXMLOutputChecker

import webstruct
from webstruct.utils import html_document_fromstring


DATA_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..', '..', 'webstruct_data', 'corpus', 'us_contact_pages', 'wa'
    )
)


def get_trees(*slice_args):
    pattern = os.path.join(DATA_PATH, '*.html')
    loader = webstruct.WebAnnotatorLoader()
    _trees_iter = webstruct.load_trees(pattern, loader)
    return list(islice(_trees_iter, *slice_args))


class HtmlOutputChecker(LXMLOutputChecker):
    def get_parser(self, want, got, optionflags):
        # by default LXMLOutputChecker uses HtmlParser
        # with recover=False option; it doesn't work for wa-color tags
        # after body.
        return html_document_fromstring


class HtmlTest(unittest.TestCase):

    def assertHtmlEqual(self, got, want):
        checker = HtmlOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(Example("", want), got, 0)
            raise AssertionError(message)

    def assertHtmlTreeEqual(self, got, want):
        self.assertHtmlEqual(lxml.html.tostring(got), lxml.html.tostring(want))
