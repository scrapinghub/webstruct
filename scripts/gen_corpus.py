"""
Convert the html corpus (in msgpack format) downloaded by businessites to plain text.
"""
from gzip import GzipFile
import msgpack
import sys
import lxml.html.clean

from lxml.html import HTMLParser, document_fromstring, tostring
from webstruct.tokenize import default_tokenizer

parser = HTMLParser(encoding='utf8')

cleaner = lxml.html.clean.Cleaner(
    style=True,
    scripts=True,
    embedded=True,
    links=True,
    page_structure=False,
    remove_unknown_tags=False,
    meta=False,
    safe_attrs_only=False
)

def html2text(html):
    doc = document_fromstring(html, parser=parser)
    doc = cleaner.clean_html(doc)
    return tostring(doc, method='text', encoding='unicode')

# use same tokenizer as the webstruct.
def normalize_text(text):
    return u" ".join(default_tokenizer(text))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: python %s some.msgpack.gz output.txt' %sys.argv[0]
        sys.exit()

    unpacker = msgpack.Unpacker(GzipFile(filename=sys.argv[1]))
    with open(sys.argv[2], 'w') as f:
        for i, item in enumerate(unpacker):
            html = item.get('body', '')
            if html:
                text = html2text(html)
                text = normalize_text(text)
                f.write(text.encode('utf8'))
                f.write('\n')
        print i, 'pages wrote to: %s' %sys.argv[2]
