# -*- coding: utf-8 -*-
from __future__ import absolute_import
from lxml.html import tostring
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


class WaConvertTest(HtmlTest):
    def test_wa_convert(self):
        tree = html_document_fromstring(b"""
        <html>
          <head>
            <title> __START_PER__ Hello! __END_PER__  world!</title>
          </head>
          <body>
            <p>
              __START_ORG__ Scrapinghub
                <b>Inc __END_ORG__  has</b>an
                <b>__START_CITY__office</b>in Montevideo __END_CITY__   __START_ORG__ SH __END_ORG__
            </p>
          </body>
        </html>
        """)
        wa_tree = webannotator.to_webannotator(tree)
        wa_tree_str = tostring(wa_tree)

        self.assertHtmlEqual(wa_tree_str, br"""
        <html>
          <head>
            <title>Hello! world!</title>
          </head>
          <body>
            <p>
              <span class="WebAnnotator_ORG" style="color:#000000; background-color:#FF0000;" wa-id="1" wa-subtypes="" wa-type="ORG">Scrapinghub</span>
              <b><span class="WebAnnotator_ORG" style="color:#000000; background-color:#FF0000;" wa-id="1" wa-subtypes="" wa-type="ORG">Inc</span> has</b>an
              <b><span class="WebAnnotator_CITY" style="color:#000000; background-color:#33FF33;" wa-id="2" wa-subtypes="" wa-type="CITY">office</span></b>
              <span class="WebAnnotator_CITY" style="color:#000000; background-color:#33FF33;" wa-id="2" wa-subtypes="" wa-type="CITY">in Montevideo</span>
              <span class="WebAnnotator_ORG" style="color:#000000; background-color:#FF0000;" wa-id="3" wa-subtypes="" wa-type="ORG">SH</span>
            </p>
          </body>
          <wa-color id="WA-color-0" bg="#33CCFF" fg="#000000" class="WebAnnotator_PER" type="PER"></wa-color>
          <wa-color id="WA-color-1" bg="#FF0000" fg="#000000" class="WebAnnotator_ORG" type="ORG"></wa-color>
          <wa-color id="WA-color-2" bg="#33FF33" fg="#000000" class="WebAnnotator_CITY" type="CITY"></wa-color>
          <wa-title style="box-shadow:0 0 1em black;border:2px solid blue;padding:0.5em;">
            <span class="WebAnnotator_PER" style="color:#000000; background-color:#33CCFF;" wa-id="0" wa-subtypes="" wa-type="PER">Hello!</span> world!
          </wa-title>
        </html>
        """)

