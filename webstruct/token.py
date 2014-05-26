# -*- coding: utf-8 -*-
from collections import namedtuple

_HtmlToken = namedtuple('_HtmlToken', 'index tokens elem is_tail')

class HtmlToken(_HtmlToken):
    """
    HTML token info.

    Attributes:

    * :attr:`index` is a token index (in the :attr:`tokens` list)
    * :attr:`tokens` is a list of all tokens in current html block
    * :attr:`elem` is the current html block (as lxml's Element) - most
      likely you want :attr:`parent` instead of it
    * :attr:`is_tail` flag indicates that token belongs to element tail

    Computed properties:

    * :attr:`token` is the current token (as text);
    * :attr:`parent` is token's parent HTML element (as lxml's Element);
    * :attr:`root` is an ElementTree this token belongs to.

    """
    @property
    def token(self):
        return self.tokens[self.index]

    @property
    def parent(self):
        if not self.is_tail:
            return self.elem
        return self.elem.getparent()

    @property
    def root(self):
        return self.elem.getroottree()

    def __repr__(self):
        return "HtmlToken(token=%r, parent=%r, index=%s)" % (
            self.token, self.parent, self.index
        )
