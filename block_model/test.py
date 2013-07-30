import sys

from pyquery import PyQuery as pq
from webstruct.tagger import Tagger

tagger = Tagger('webstruct.model')

html = pq(url=sys.argv[1]).html()
texts, labels, address = tagger.tag(html)
for i, text in enumerate(texts):
    print >> sys.stderr, '[%s] [%s]: %s' %(i, labels[i], text)
print 'ADDR:', address
