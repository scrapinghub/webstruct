import unittest

import lxml

import webstruct.annotation_verifier

html_1 = '<span style="abc" class="span">aa</span>'
html_2 = '<span style="abd" class="span">aa</span>'
html_3 = '<span style="abd" class="span">aa<p>s</p></span>'
html_3 = '<span style="abd" class="span">aa<p>s</p><p>ss</p></span>'

class SomethingTest(unittest.TestCase):

    def test_is_node_equal_to_self(self):
        tree_1 = lxml.etree.fromstring(html_1)
        diff = webstruct.annotation_verifier.nodes_difference(tree_1, tree_1)
        self.assertIsNone(diff)

    def test_is_different_nodes_are_diffirent(self):
        tree_1 = lxml.etree.fromstring(html_1)
        tree_2 = lxml.etree.fromstring(html_2)
        diff = webstruct.annotation_verifier.nodes_difference(tree_1, tree_2)
        self.assertIsNotNone(diff)

    def test_is_tree_equal_to_self(self):
        tree_1 = lxml.etree.fromstring(html_3)
        diff = webstruct.annotation_verifier.tree_difference(tree_1, tree_1)
        self.assertIsNone(diff)

    def test_is_different_trees_are_diffirent(self):
        tree_1 = lxml.etree.fromstring(html_2)
        tree_2 = lxml.etree.fromstring(html_3)
        diff = webstruct.annotation_verifier.tree_difference(tree_1, tree_2)
        self.assertIsNotNone(diff)
