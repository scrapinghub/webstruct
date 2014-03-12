# -*- coding: utf-8 -*-
from __future__ import absolute_import
from copy import deepcopy
from lxml.html import tostring
from webstruct.feature_extraction import HtmlTokenizer
from webstruct.loaders import GateLoader, HtmlLoader
from webstruct.utils import html_document_fromstring
from .utils import HtmlTest


GATE_HTML = b"""
<html>
  <body>
    <p>
      <ORG>Scrapinghub
      <b>Inc</ORG> has</b> an
      <b>office</b> in <CITY>Montevideo</CITY>
    </p>
  </body>
</html>"""

UNANNOTATED_HTML = b"""
<html>
  <body>
    <p>Scrapinghub <b>Inc has</b> an <b>office</b> in Montevideo</p>
  </body>
</html>
"""

ANNOTATED_HTML = b"""
<html>
  <body>
    <p>
      __START_ORG__ Scrapinghub
        <b>Inc __END_ORG__  has</b>an
        <b>office</b>in  __START_CITY__ Montevideo __END_CITY__
    </p>
  </body>
</html>"""


class HtmlTokenizerTest(HtmlTest):

    def _load(self):
        return GateLoader(known_tags=['ORG', 'CITY']).loadbytes(GATE_HTML)

    def test_tokenization_doesnt_alter_tree(self):
        src_tree = self._load()
        orig_src_tree = deepcopy(src_tree)
        HtmlTokenizer().tokenize_single(src_tree)

        # original tree is not changed
        self.assertHtmlTreeEqual(src_tree, orig_src_tree)

    def assertTokenizationWorks(self, tree):
        html_tokens, tags = HtmlTokenizer().tokenize_single(tree)

        # data is correct
        self.assertListEqual(
            [t.token for t in html_tokens],
            [u'Scrapinghub', u'Inc', u'has', u'an', u'office', u'in', u'Montevideo'],
        )
        self.assertListEqual(
            tags,
            [u'B-ORG', u'I-ORG', 'O', 'O', 'O', 'O', u'B-CITY']
        )

        tree = html_tokens[0].root
        self.assertNotIn('__', tostring(tree))

    def test_tokenize_single(self):
        self.assertTokenizationWorks(self._load())

    def test_tokenize_single_lineends(self):
        self.assertTokenizationWorks(HtmlLoader().loadbytes(ANNOTATED_HTML))

    def test_detokenize_single(self):
        src_tree = self._load()
        orig_src_tree = deepcopy(src_tree)

        tokenizer = HtmlTokenizer()
        html_tokens, tags = tokenizer.tokenize_single(src_tree)
        new_tree = html_tokens[0].root
        self.assertIn('__START_ORG__', tostring(src_tree))
        self.assertNotIn('__START_ORG__', tostring(new_tree))

        self.assertHtmlTreeEqual(
            new_tree,
            html_document_fromstring(UNANNOTATED_HTML)
        )

        detokenized_tree = tokenizer.detokenize_single(html_tokens, tags)
        self.assertIn('__START_ORG__', tostring(detokenized_tree))

        self.assertHtmlTreeEqual(
            detokenized_tree,
            html_document_fromstring(ANNOTATED_HTML)
        )
        self.assertHtmlTreeEqual(detokenized_tree, orig_src_tree)
        self.assertHtmlTreeEqual(detokenized_tree, src_tree)

    def test_detokenize_single_empty(self):
        self.assertIs(HtmlTokenizer().detokenize_single([], []), None)

    def test_tokenize_scripts_and_styles(self):
        html = b"""
        <html>
          <head>
            <script>function foo(){}</script>
            <style>
              body {
                color: "red"
              }
            </style>
          </head>
          <body>hello</body>
        </html>
        """

        tree = HtmlLoader().loadbytes(html)
        tree2 = html_document_fromstring(html)

        # tokenizer doesn't produce tokens for <script> and <style> contents
        tokenizer = HtmlTokenizer()
        html_tokens, tags = tokenizer.tokenize_single(tree)
        self.assertEqual(len(html_tokens), 1)
        self.assertEqual(html_tokens[0].tokens, ['hello'])
        self.assertEqual(html_tokens[0].elem.tag, 'body')

        # but it preserves <script> and <style> elements
        self.assertHtmlTreeEqual(tree, tree2)

        # and restores the tree if needed
        detokenized_tree = tokenizer.detokenize_single(html_tokens, tags)
        self.assertHtmlTreeEqual(tree, detokenized_tree)



