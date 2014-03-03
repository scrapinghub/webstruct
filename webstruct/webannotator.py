"""
:mod:`webstruct.webannotator` provides functions for working with HTML
pages annotated with WebAnnotator_ Firefox extension.

.. _WebAnnotator: https://github.com/xtannier/WebAnnotator
"""
from __future__ import absolute_import

DEFAULT_COLORS = [
    # background, foreground
    ("#000000", "#33CCFF"),
    ("#000000", "#FF0000"),
    ("#000000", "#33FF33"),
    ("#000000", "#CC66CC"),
    ("#000000", "#FF9900"),
    ("#000000", "#99FFFF"),
    ("#000000", "#FF6666"),
    ("#000000", "#66FF99"),
    ("#FFFFFF", "#3333FF"),
    ("#FFFFFF", "#660000"),
    ("#FFFFFF", "#006600"),
    ("#FFFFFF", "#663366"),
    ("#FFFFFF", "#993300"),
    ("#FFFFFF", "#336666"),
    ("#FFFFFF", "#666600"),
    ("#FFFFFF", "#009900"),
]


def apply_wa_title(tree):
    """
    Replace page's ``<title>`` contents with a contents of
    ``<wa-title>`` element and remove ``<wa-title>`` tag.

    WebAnnotator > 1.14 allows annotation of ``<title>`` contents;
    it is stored after body in ``<wa-title>`` elements.
    """
    for wa_title in tree.xpath('//wa-title'):
        titles = tree.xpath('//title')
        if not titles:
            wa_title.drop_tree()
            return
        title = titles[0]
        head = title.getparent()
        head.insert(head.index(title), wa_title)
        title.drop_tree()
        wa_title.tag = 'title'
        return

