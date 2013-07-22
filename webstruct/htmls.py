from lxml import etree
from lxml.html import document_fromstring, HTMLParser, tostring
from lxml.html.clean import Cleaner
import re
from webstruct.tidy import tidy_html

_TAG_RE = re.compile(ur'\s*</?([a-z]+).*?>\s*', re.I | re.DOTALL)

def clean_tag(html, tag, replacement):
    """
    >>> html = u"<p>UCD Earth Institute,<br>UCD Science Centre South,<br>University College Dublin</p>"
    >>> clean_tag(html, 'br', '\\n')
    u'<p>UCD Earth Institute,\\nUCD Science Centre South,\\nUniversity College Dublin</p>'

    >>> html = u"<p>UCD Earth Institute,<br>UCD Science Centre South,<br>University College Dublin</p>"
    >>> clean_tag(html, 'br', ' ')
    u'<p>UCD Earth Institute, UCD Science Centre South, University College Dublin</p>'

    """
    def _clean_br_hook(m):
        t = m.group(1).lower()
        if t == tag:
            return replacement
        return m.group(0)

    return _TAG_RE.sub(_clean_br_hook, html)

def clean_html(html):
    cleaner = Cleaner(style=True,
                      page_structure=False,
                      remove_unknown_tags=True,
                      meta=False,
                      safe_attrs_only=True)
    return cleaner.clean_html(html)

def parse_html(html, encoding='utf-8'):
    parser = HTMLParser(encoding=encoding)
    return document_fromstring(html, parser=parser)

def replace_tags(root, _from_set, _to):
    """
    >>> from lxml.html import fragment_fromstring, document_fromstring, tostring
    >>> root = fragment_fromstring('<h1>head 1</h1>')
    >>> root = replace_tags(root, 'h1', 'strong')
    >>> tostring(root)
    '<strong>head 1</strong>'

    >>> root = document_fromstring('<h1>head 1</h1> <h2>head 2</h2>')
    >>> root = replace_tags(root, ('h1','h2','h3','h4'), 'strong')
    >>> tostring(root)
    '<html><body><strong>head 1</strong> <strong>head 2</strong></body></html>'
    """

    _from_set = (_from_set, )
    if isinstance(_to, basestring):
        _to = (_to, )
    for tags, _target in zip(_from_set, _to):
        for e in root.iter(tags):
            e.tag = _target
    return root

def get_lines(html):
    html = clean_html(html)
    html, texts = tidy_html(html)
    return [line.strip() for line in texts.splitlines() if line]

if __name__ == '__main__':
    import doctest
    doctest.testmod()