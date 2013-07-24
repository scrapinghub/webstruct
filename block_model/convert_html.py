"""
utils to convert a HTML page to pure text.
"""
import sys
from webstruct.htmls import get_lines

html = open(sys.argv[1]).read().decode('utf8')
for line in get_lines(html):
    if line:
        print line.encode('utf8')
        print 'O'
