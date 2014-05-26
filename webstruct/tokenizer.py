# -*- coding: utf-8 -*-
"""
:mod:`webstruct.tokenize` extract the tokens and tags from the annotated data (HTML or text).
"""
import re
import copy

from itertools import groupby
from lxml.etree import XPathEvaluator

from webstruct.token import HtmlToken
from webstruct.word_tokenizers import tokenize as word_tokenize
from webstruct.sequence_encoding import IobEncoder

from webstruct.utils import (
    replace_html_tags,
    kill_html_tags,
    smart_join,
)

class TextTokenizer(object):
    """
    Class for converting annnotated text into list of :class:`Token` instances
    and associated tags.

    Parameters
    ----------

    tagset : set, optional
        A set of entity types to keep. If not passed, all entity types are kept.
        Use this argument to discard some entity types from training data.
    sequence_encoder : object, optional
        Sequence encoder object. If not passed,
        :class:`~webstruct.sequence_encoding.IobEncoder` instance is created.
    text_toknize_func : callable, optional
        Function used for tokenizing text.
        By default, :class:`TextTokenizer` uses
        :func:`webstruct.text_tokenizers.tokenize`.
    """
    def __init__(self, tagset=None, sequence_encoder=None, text_tokenize_func=None):
        # FIXME: don't use shared instance of sequence encoder
        # because sequence encoder is stateful
        self.tagset = set(tagset) if tagset is not None else None
        self.sequence_encoder = sequence_encoder or IobEncoder()
        self.text_tokenize_func = text_tokenize_func or word_tokenize

    def tokenize_single(self, text):
        """
        Return two lists:

        * a list a list of :class:`Token` tokens.
        * a list of associated tags.

        For unannotated text all tags will be "O" - they may be ignored.

        Example:

            >>> from webstruct import GateTextLoader, TextTokenizer
            >>> loader = GateTextLoader()
            >>> tokenizer = TextTokenizer()
            >>> tree = loader.loadbytes(b"hello, <PER>John Doe</PER> <PER>Mary</PER> said")
            >>> tokens, tags = tokenizer.tokenize_single(tree)
            >>> tokens  # doctest: +ELLIPSIS
            [u'hello', u'John', u'Doe', u'Mary', u'said']
            >>> tags
            ['O', u'B-PER', u'I-PER', u'B-PER', 'O']
            >>> for tok, iob_tag in zip(tokens, tags):
            ...     print "%5s" % iob_tag, tok
                O hello
            B-PER John
            I-PER Doe
            B-PER Mary
                O said

        For empty text it returns empty lists::

            >>> tokenizer.tokenize_single(loader.loadbytes(''))
            ([], [])
        """
        tokens, tags = self.tokenize_and_split(text)
        return list(tokens), list(tags)

    def reset(self):
        self.sequence_encoder.reset()

    def tokenize(self, texts):
        X, y = [], []
        for text in texts:
            tokens, tags = self.tokenize_single(text)
            X.append(tokens)
            y.append(tags)
        return X, y

    def tokenize_and_split(self, text):
        input_tokens = self._limit_tags(self.text_tokenize_func(text or ''))
        input_tokens = map(unicode, input_tokens)
        return self.sequence_encoder.encode_split(input_tokens)

    def _limit_tags(self, input_tokens):
        if self.tagset is None:
            return input_tokens

        proc = self.sequence_encoder.token_processor
        token_classes = [proc.classify(tok) for tok in input_tokens]
        return [
            tok for (tok, (typ, value)) in zip(input_tokens, token_classes)
            if not (typ in {'start', 'end'} and value not in self.tagset)
        ]

    def __getstate__(self):
        dct = self.__dict__.copy()
        if self.text_tokenize_func is word_tokenize:
            dct['text_tokenize_func'] = 'DEFAULT'
        return dct

    def __setstate__(self, state):
        if state['text_tokenize_func'] == 'DEFAULT':
            state['text_tokenize_func'] = word_tokenize
        self.__dict__.update(state)


class HtmlTokenizer(object):
    """
    Class for converting HTML trees (returned by one of the
    :mod:`webstruct.loaders`) into lists of :class:`HtmlToken` instances
    and associated tags. Also, it can do the reverse conversion.

    Use :meth:`tokenize_single` to convert a single tree and :meth:`tokenize`
    to convert multiple trees.

    Use :meth:`detokenize_single` to get an annotated tree out of a list
    of :class:`HtmlToken` instances and a list of tags.

    Parameters
    ----------

    tagset, sequence_encoder, text_toknize_func : see :class:`TextTokenizer`
    kill_html_tags: set, optional
        A set of HTML tags which should be removed. Contents inside
        removed tags is not removed. See :func:`webstruct.utils.kill_html_tags`
    replace_html_tags: dict, optional
        A mapping ``{'old_tagname': 'new_tagname'}``. It defines how tags
        should be renamed. See :func:`webstruct.utils.replace_html_tags`
    ignore_html_tags: set, optional
        A set of HTML tags which won't produce :class:`HtmlToken` instances,
        but will be kept in a tree. Default is ``{'script', 'style'}``.
    """
    def __init__(self, tagset=None, sequence_encoder=None, text_tokenize_func=None,
                 kill_html_tags=None, replace_html_tags=None, ignore_html_tags=None):
        self.text_tokenizer = TextTokenizer(tagset, sequence_encoder, text_tokenize_func)
        self.kill_html_tags = kill_html_tags
        self.replace_html_tags = replace_html_tags

        if ignore_html_tags is not None:
            self.ignore_html_tags = set(ignore_html_tags)
        else:
            self.ignore_html_tags = {'script', 'style'}

        tag_pattern = self.text_tokenizer.sequence_encoder.token_processor.tag_re.pattern.strip()
        self._tag_re = re.compile(r"(^|\s)%s(\s|$)" % tag_pattern)

    def tokenize_single(self, tree):
        """
        Return two lists:

        * a list a list of HtmlToken tokens;
        * a list of associated tags.

        For unannotated HTML all tags will be "O" - they may be ignored.

        Example:

            >>> from webstruct import GateLoader, HtmlTokenizer
            >>> loader = GateLoader(known_entities={'PER'})
            >>> html_tokenizer = HtmlTokenizer(replace_html_tags={'b': 'strong'})
            >>> tree = loader.loadbytes(b"<p>hello, <PER>John <b>Doe</b></PER> <br> <PER>Mary</PER> said</p>")
            >>> html_tokens, tags = html_tokenizer.tokenize_single(tree)
            >>> html_tokens  # doctest: +ELLIPSIS
            [HtmlToken(token=u'hello', parent=<Element p at ...>, index=0), HtmlToken...]
            >>> tags
            ['O', u'B-PER', u'I-PER', u'B-PER', 'O']
            >>> for tok, iob_tag in zip(html_tokens, tags):
            ...     print "%5s" % iob_tag, tok.token, tok.elem.tag, tok.parent.tag
                O hello p p
            B-PER John p p
            I-PER Doe strong strong
            B-PER Mary br p
                O said br p

        For HTML without text it returns empty lists::

            >>> html_tokenizer.tokenize_single(loader.loadbytes(b'<p></p>'))
            ([], [])

        """
        tree = copy.deepcopy(tree)
        self.text_tokenizer.reset()
        self._prepare_tree(tree)
        res = zip(*(self._process_tree(tree)))
        if not res:
            return ([], [])
        return list(res[0]), list(res[1])

    def tokenize(self, trees):
        X, y = [], []
        for tree in trees:
            html_tokens, tags = self.tokenize_single(tree)
            X.append(html_tokens)
            y.append(tags)
        return X, y

    def detokenize_single(self, html_tokens, tags):
        """
        Build annotated ``lxml.etree.ElementTree`` from
        ``html_tokens`` (a list of :class:`.HtmlToken` instances)
        and ``tags`` (a list of their tags).

        Annotations are encoded as ``__START_TAG__`` and ``__END_TAG__``
        text tokens (this is the format :mod:`webstruct.loaders` use).
        """
        if len(html_tokens) != len(tags):
            raise ValueError("len(html_tokens) must be equal to len(tags)")

        if not html_tokens:
            return None

        orig_tree = html_tokens[0].root
        tree = copy.deepcopy(orig_tree)
        xpatheval = XPathEvaluator(tree)

        # find starts/ends of token groups
        token_groups = self.text_tokenizer.sequence_encoder.group(zip(html_tokens, tags))
        starts, ends = set(), set()
        pos = 0
        for gr_tokens, gr_tag in token_groups:
            n_tokens = len(gr_tokens)
            if gr_tag != 'O':
                starts.add(pos)
                ends.add(pos + n_tokens - 1)
            pos += n_tokens

        # mark starts/ends with special tokens
        data = zip(html_tokens, tags, range(len(html_tokens)))
        keyfunc = lambda rec: (rec[0].elem, rec[0].is_tail)

        for (orig_elem, is_tail), g in groupby(data, keyfunc):
            g = list(g)
            fix = False
            tokens = g[0][0].tokens[:]
            for token, tag, token_idx in g:
                if token_idx in starts:
                    tokens[token.index] = ' __START_%s__ %s' % (tag[2:], tokens[token.index])
                    fix = True
                if token_idx in ends:
                    tokens[token.index] = '%s __END_%s__ ' % (tokens[token.index], tag[2:])
                    fix = True

            if fix:
                xpath = orig_tree.getpath(orig_elem)
                elem = xpatheval(xpath)[0]
                if is_tail:
                    elem.tail = smart_join(tokens)
                else:
                    elem.text = smart_join(tokens)

        return tree

    def _prepare_tree(self, tree):
        if self.kill_html_tags:
            kill_html_tags(tree, self.kill_html_tags, keep_child=True)

        if self.replace_html_tags:
            replace_html_tags(tree, self.replace_html_tags)

    def _process_tree(self, tree):
        if tree.tag in self.ignore_html_tags:
            return

        head_tokens, head_tags = self.text_tokenizer.tokenize_and_split(tree.text)
        for index, (token, tag) in enumerate(zip(head_tokens, head_tags)):
            yield HtmlToken(index, head_tokens, tree, False), tag

        for child in tree:  # where is my precious "yield from"?
            for html_token, tag in self._process_tree(child):
                yield html_token, tag

        tail_tokens, tail_tags = self.text_tokenizer.tokenize_and_split(tree.tail)
        for index, (token, tag) in enumerate(zip(tail_tokens, tail_tags)):
            yield HtmlToken(index, tail_tokens, tree, True), tag

        self._cleanup_elem(tree)

    def _cleanup_elem(self, elem):
        """ Remove special tokens from elem """
        if elem.text:
            elem.text = self._tag_re.sub("", elem.text)
        if elem.tail:
            elem.tail = self._tag_re.sub("", elem.tail)
