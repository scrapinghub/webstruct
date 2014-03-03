# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from doctest import Example
import lxml.html
from lxml.doctestcompare import LXMLOutputChecker


class HtmlTest(unittest.TestCase):

    def assertHtmlEqual(self, got, want):
        checker = LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(Example("", want), got, 0)
            raise AssertionError(message)

    def assertHtmlTreeEqual(self, got, want):
        self.assertHtmlEqual(lxml.html.tostring(got), lxml.html.tostring(want))
