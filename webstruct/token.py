# -*- coding: utf-8 -*-
from collections import namedtuple

_Token = namedtuple('_Token', 'index tokens')

class Token(_Token):
    """
    Basic token info.

    Attributes:

    * :attr:`index` is a token index (in the :attr:`tokens` list)
    * :attr:`tokens` is a list of all tokens in current html block

    Computed properties:

    * :attr:`token` is the current token (as text);

    """
    @property
    def token(self):
        return self.tokens[self.index]

    def __repr__(self):
        return "Token(token=%r, index=%s)" % (
            self.token, self.index
        )

class HtmlToken(Token):
    """
    HTML token info.

    Attributes besides basic token:

    * :attr:`elem` is the current html block (as lxml's Element) - most
      likely you want :attr:`parent` instead of it
    * :attr:`is_tail` flag indicates that token belongs to element tail

    Computed properties:

    * :attr:`parent` is token's parent HTML element (as lxml's Element);
    * :attr:`root` is an ElementTree this token belongs to.

    """
    def __new__(cls, index, tokens, elem, is_tail):
        self = super(cls, HtmlToken).__new__(cls, index, tokens)
        self.elem = elem
        self.is_tail = is_tail
        return self

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
