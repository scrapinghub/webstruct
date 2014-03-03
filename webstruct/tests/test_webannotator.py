# -*- coding: utf-8 -*-
from __future__ import absolute_import

from webstruct import webannotator
from webstruct.utils import html_document_fromstring
from webstruct.tests.utils import HtmlTest


class WaTitleTest(HtmlTest):
    def test_wa_title(self):
        tree = html_document_fromstring(b"""
        <html>
            <head><title>Foo</title></head>
            <body>contents</body>
            <wa-title><b>hello</b>, world</wa-title>
        </html>
        """)
        webannotator.apply_wa_title(tree)

        self.assertHtmlTreeEqual(tree, html_document_fromstring(b"""
        <html>
            <head><title><b>hello</b>, world</title></head>
            <body>contents</body>
        </html>
        """))


