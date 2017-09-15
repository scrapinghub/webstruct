# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import string
from lxml.html import tostring
from webstruct import webannotator
from webstruct.utils import html_document_fromstring
from webstruct.tests.utils import HtmlTest


class WaTitleTest(HtmlTest):

    def assertApplyWaTitle(self, source, result):
        tree = html_document_fromstring(source)
        webannotator.apply_wa_title(tree)
        self.assertHtmlTreeEqual(tree, html_document_fromstring(result))

    def test_wa_title_no_attributes(self):
        self.assertApplyWaTitle(
            b"""
            <html>
                <head><title>Foo</title></head>
                <body>contents</body>
                <wa-title class="classy"><b>hello</b>, world</wa-title>
            </html>
            """,

            b"""
            <html>
                <head><title><b>hello</b>, world</title></head>
                <body>contents</body>
            </html>
            """
        )

    def test_wa_title(self):
        self.assertApplyWaTitle(
            b"""
            <html>
                <head><title>Foo</title></head>
                <body>contents</body>
                <wa-title><b>hello</b>, world</wa-title>
            </html>
            """,

            b"""
            <html>
                <head><title><b>hello</b>, world</title></head>
                <body>contents</body>
            </html>
            """
        )

    def test_wa_title_no_title(self):
        self.assertApplyWaTitle(
            b"""
            <html>
                <head><title>Foo</title></head>
                <body>contents</body>
            </html>
            """,

            b"""
            <html>
                <head><title>Foo</title></head>
                <body>contents</body>
            </html>
            """
        )

    def test_wa_title_no_invalid(self):
        self.assertApplyWaTitle(
            b"""
            <html>
                <body>contents</body>
                <wa-title><b>hello</b>, world</wa-title>
            </html>
            """,
            b"<html><body>contents</body></html>"
        )


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

    def test_wa_convert_no_title(self):
        tree = html_document_fromstring(b"""
        <html><body><p> __START_ORG__ Scrapinghub __END_ORG__ </p></body></html>
        """)
        wa_tree = webannotator.to_webannotator(tree)
        wa_tree_str = tostring(wa_tree)

        self.assertHtmlEqual(wa_tree_str, br"""
        <html>
          <body>
            <p>
              <span class="WebAnnotator_ORG" style="color:#000000; background-color:#33CCFF;" wa-id="0" wa-subtypes="" wa-type="ORG">Scrapinghub</span>
            </p>
          </body>
          <wa-color bg="#33CCFF" class="WebAnnotator_ORG" fg="#000000" id="WA-color-0" type="ORG"></wa-color>
        </html>
        """)

    def test_handle_nonxml_attributes(self):
        html = b"""
        <html>
          <body>
            <a class="addthis_button_facebook_like" like:layout="button_count">
          </body>
        </html>
        """
        tree = html_document_fromstring(html)
        wa_tree = webannotator.to_webannotator(tree)
        wa_tree_str = tostring(wa_tree)
        self.assertHtmlEqual(wa_tree_str, html)

    def test_baseurl_nohead(self):
        html = b"""<html><body><p>hello</p></body></html>"""
        tree = html_document_fromstring(html)
        wa_tree = webannotator.to_webannotator(tree,
                                               url='http://example.com/foo')
        self.assertHtmlEqual(tostring(wa_tree), """
        <html>
            <head><base href="http://example.com/foo"/></head>
            <body><p>hello</p></body>
        </html>
        """)

    def test_baseurl_head(self):
        html = b"""<html><head><meta/></head><body><p>hello</p></body></html>"""
        tree = html_document_fromstring(html)
        wa_tree = webannotator.to_webannotator(tree,
                                               url='http://example.com/foo')
        self.assertHtmlEqual(tostring(wa_tree), """
        <html>
            <head><base href="http://example.com/foo"/><meta/></head>
            <body><p>hello</p></body>
        </html>
        """)

    def test_baseurl_exists(self):
        html = b"""
        <html>
            <head><base href="http://example.com/foo"/></head>
            <body><p>hello</p></body>
        </html>
        """
        tree = html_document_fromstring(html)
        wa_tree = webannotator.to_webannotator(tree,
                                               url='http://example.com/bar')
        self.assertHtmlEqual(tostring(wa_tree), html)


class EntityColorsTest(HtmlTest):
    def test_entity_colors(self):
        color_dict = webannotator.EntityColors()
        colors = {}
        entities = reversed(string.ascii_letters)
        for entity in entities:
            colors[entity] = color_dict[entity]

        for entity in string.ascii_letters:
            fg, bg, index = color_dict[entity]
            assert (fg, bg, index) == colors[entity]
            assert fg[0] == '#'
            assert bg[0] == '#'
            assert len(fg) == 7
            assert len(bg) == 7

        color_dict2 = webannotator.EntityColors(**dict(color_dict))
        assert color_dict.next_index == color_dict2.next_index

        for entity in string.ascii_letters:
            assert color_dict[entity] == color_dict2[entity]

    def test_html_loading(self):
        color_dict = webannotator.EntityColors.from_htmlfile(
            os.path.join(os.path.dirname(__file__), 'data', 'wa1.html')
        )
        self.assertEqual(color_dict['COUNTRY'], ("#FFFFFF", "#993311", 12))
