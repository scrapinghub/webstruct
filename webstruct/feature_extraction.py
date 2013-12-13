# -*- coding: utf-8 -*-
from __future__ import absolute_import
import copy
from collections import namedtuple
from .sequence_encoding import IobEncoder
from .tokenizers import tokenize
from webstruct.features import CombinedFeatures
from webstruct.utils import replace_tags, kill_tags

_HtmlToken = namedtuple('HtmlToken', 'index tokens elem is_tail label')

class HtmlToken(_HtmlToken):
    """
    HTML token info.

    * ``index`` is a token index (in the ``tokens`` list);
    * ``tokens`` is a list of all tokens in current html block;
    * ``elem`` is the current html block (as lxml's Element) - most likely
      you want ``HtmlToken.parent`` instead of it;
    * ``is_tail`` flag that indicates that token belongs to element tail
    * ``label`` is a NER tag for this token. For unannotated HTML
      it is always "O". Feature functions shouldn't access this attribute.

    Computed properties:

    * ``token`` is the current token (as text);
    * ``parent`` is token's parent HTML element (as lxml's Element).

    """
    @property
    def token(self):
        return self.tokens[self.index]

    @property
    def parent(self):
        if not self.is_tail:
            return self.elem
        return self.elem.getparent()


class HtmlTokenizer(object):
    """
    Use ``HtmlTokenizer.tokenize`` to convert HTML tree (returned by one
    of the webstruct loaders) to a list of HtmlToken instances::

        >>> from webstruct import GateLoader, HtmlTokenizer
        >>> loader = GateLoader(known_tags=['PER'])
        >>> html_tokenizer = HtmlTokenizer(replace_tags={'b': 'strong'})

        >>> tree = loader.loadbytes(b"<p>hello, <PER>John <b>Doe</b></PER> <br> <PER>Mary</PER> said</p>")
        >>> for tok in html_tokenizer.tokenize(tree):
        ...     print tok.token, tok.label, tok.elem.tag, tok.parent.tag
        hello O p p
        John B-PER p p
        Doe I-PER strong strong
        Mary B-PER br p
        said O br p

    For HTML without text it returns empty list::

        >>> html_tokenizer.tokenize(loader.loadbytes(b'<p></p>'))
        []

    """
    def __init__(self, tagset=None, sequence_encoder=None, text_tokenize=None,
                 kill_tags=None, replace_tags=None):
        self.tagset_ = set(tagset) if tagset is not None else None
        self.sequence_encoder_ = sequence_encoder or IobEncoder()
        self.text_tokenize_ = text_tokenize or tokenize
        self.kill_tags_ = kill_tags
        self.replace_tags_ = replace_tags

    def tokenize(self, tree):
        """
        Return a list of HtmlToken tokens.

        For unannotated HTML tags list will contain "O" tags and may be ignored.
        """
        tree = copy.deepcopy(tree)
        self.sequence_encoder_.reset()
        self._prepare_tree(tree)
        return list(self._process_tree(tree))

    def _prepare_tree(self, tree):
        if self.kill_tags_:
            kill_tags(tree, self.kill_tags_, keep_child=True)

        if self.replace_tags_:
            replace_tags(tree, self.replace_tags_)

    def _process_tree(self, tree):
        head_tokens, head_tags = self._tokenize_and_split(tree.text)
        for index, (token, tag) in enumerate(zip(head_tokens, head_tags)):
            yield HtmlToken(index, head_tokens, tree, False, tag)

        for child in tree:  # where is my precious "yield from"?
            for token in self._process_tree(child):
                yield token

        tail_tokens, tail_tags = self._tokenize_and_split(tree.tail)
        for index, (token, tag) in enumerate(zip(tail_tokens, tail_tags)):
            yield HtmlToken(index, tail_tokens, tree, True, tag)

    def _tokenize_and_split(self, text):
        input_tokens = self._limit_tags(self.text_tokenize_(text or ''))
        return self.sequence_encoder_.encode_split(input_tokens)

    def _limit_tags(self, input_tokens):
        if self.tagset_ is None:
            return input_tokens

        proc = self.sequence_encoder_.token_processor_
        token_classes = [proc.classify(tok) for tok in input_tokens]
        return [
            tok for (tok, (typ, value)) in zip(input_tokens, token_classes)
            if not (typ in {'start', 'end'} and value not in self.tagset_)
        ]


class HtmlFeatureExtractor(object):
    """
    This class extracts features from a list of HtmlTokens (html tree tokenized
    using HtmlTokenizer).

    To create HtmlFeatureExtractor, pass a list of feature functions
    to the constructor. Each feature function must accept 3 parameters:
    ``html_token``, ``index`` and ``html_tokens`` and return a dictionary
    wich maps feature names to feature values.

    ``html_token`` always equals to ``html_tokens[index]``. ``html_tokens``
    is a list of all html tokens from this tree.

    Example feature that returns token text::

        >>> def current_token(html_token, index, html_tokens):
        ...     return {'tok': html_token.token}

    ``webstruct.features`` module provides some predefined feature functions,
    e.g. ``parent_tag`` which returns token's parent tag.

    Example::

        >>> from webstruct import GateLoader, HtmlTokenizer, HtmlFeatureExtractor
        >>> from webstruct.features import parent_tag

        >>> loader = GateLoader(known_tags=['PER'])
        >>> html_tokenizer = HtmlTokenizer()
        >>> feature_extractor = HtmlFeatureExtractor([parent_tag])

        >>> tree = loader.loadbytes(b"<p>hello, <PER>John <b>Doe</b></PER> <br> <PER>Mary</PER> said</p>")
        >>> html_tokens = html_tokenizer.tokenize(tree)
        >>> feature_dicts = feature_extractor.transform(html_tokens)
        >>> for token, feat in zip(html_tokens, feature_dicts):
        ...     print("%s %s %s" % (token.token, token.label, feat))
        hello O {'parent_tag': 'p'}
        John B-PER {'parent_tag': 'p'}
        Doe I-PER {'parent_tag': 'b'}
        Mary B-PER {'parent_tag': 'p'}
        said O {'parent_tag': 'p'}

    """
    def __init__(self, feature_functions):
        self.feature_func_ = CombinedFeatures(*feature_functions)

    def transform(self, html_tokens):
        return [
            self.feature_func_(tok, index, html_tokens)
            for index, tok in enumerate(html_tokens)
        ]

