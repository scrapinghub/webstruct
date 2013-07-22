import re
from scrapy.selector import XPathSelector
from w3lib.html import unquote_markup

_TAG_RE = re.compile(ur'\s*</?([a-z0-9]+).*?>\s*', re.I | re.DOTALL)
_SCRIPTS_RE = re.compile(ur'<script.*?/script>|<style.*?/style>', re.I | re.DOTALL)
_SPACING_RE = re.compile(ur'\n[\n\s]+', re.DOTALL)
_TAG_ALIAS = {
    u'div': u'table',
    u'p': u'h1,h2,h3,h4,h5,h6,address',
    }
_TAG_INVALIAS = dict((t, a) for a, s in _TAG_ALIAS.items() for t in s.split(','))
def _clean_html(html):
    '''Only keep some structure and anchor tags'''
    html = _SPACING_RE.sub(u'\n', html)
    html = _SCRIPTS_RE.sub(u' ', html)
    html = _TAG_RE.sub(_clean_html_tag, html)
    html = unquote_markup(html).replace(u'\u00a0', ' ').replace(u'\u2013', '-')
    return _SPACING_RE.sub(u'\n', html)

def _clean_html_tag(m):
    isclosing = u'/' if m.group(0).startswith('</') else u''
    tagname = m.group(1).lower()
    tagname = _TAG_INVALIAS.get(tagname, tagname)
    # if tagname in (u'a', u'area', 'meta'):
    #     return '\n'+m.group(0)+'\n'
    if tagname in (u'div', u'html', u'body', u'title'):
        return '\n<{0}{1}>\n'.format(isclosing, tagname)
    elif tagname in (u'br', u'tr', u'p', u'li', u'td', u'dt', u'dd'):
        return u'\n'
    else:
        return u' '

def tidy_html(body):
    html = _clean_html(body)
    hxs = XPathSelector(text=html)
    text = u'\n'.join(txt.strip() for txt in hxs.select('//text()').extract())
    return html, text