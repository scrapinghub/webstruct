# -*- coding: utf-8 -*-
"""
:mod:`webstruct.feature_extraction` contains classes that help
with:

- converting HTML pages into lists of feature dicts and
- extracting annotations.

Usually, the approach is the following:

1. Extract text from the webpage and tokenize it, preserving information
   about token position in original HTML tree
   (token + its tree position = :class:`HtmlToken`).
   Information about annotations (if present) is split from the rest
   of data at this stage. :class:`HtmlTokenizer` is used for extracting
   HTML tokens and annotation tags.

2. Run a number of "token feature functions" that return bits of information
   about each token: token text, token shape (uppercased/lowercased/...),
   whether token is in ``<a>`` HTML element, etc. For each token information
   is combined into a single feature dictionary.

   Use :class:`HtmlFeatureExtractor` at this stage. There is a number of
   predefined token feature functions in :mod:`webstruct.features`.

3. Run a number of "global feature functions" that can modify token feature
   dicts inplace (insert new features, change, remove them) using "global"
   information - information about all other tokens in a document and their
   existing token-level feature dicts. Global feature functions are applied
   sequentially: subsequent global feature functions get feature dicts updated
   by previous feature functions.

   This is also done by :class:`HtmlFeatureExtractor`.

   :class:`~webstruct.features.utils.LongestMatchGlobalFeature` can be used
   to create features that capture multi-token patterns. Some predefined
   global feature functions can be found in :mod:`webstruct.gazetteers`.


"""
from __future__ import absolute_import
import re
import copy
from itertools import chain, groupby
from collections import namedtuple, Counter

from lxml.etree import XPathEvaluator
from sklearn.base import BaseEstimator, TransformerMixin
from webstruct.sequence_encoding import IobEncoder
from webstruct.text_tokenizers import tokenize
from webstruct.utils import (
    replace_html_tags,
    kill_html_tags,
    smart_join,
    merge_dicts
)

_HtmlToken = namedtuple('HtmlToken', 'index tokens elem is_tail')

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

    tagset : set, optional
        A set of entity types to keep. If not passed, all entity types are kept.
        Use this argument to discard some entity types from training data.
    sequence_encoder : object, optional
        Sequence encoder object. If not passed,
        :class:`~webstruct.sequence_encoding.IobEncoder` instance is created.
    text_toknize_func : callable, optional
        Function used for tokenizing text inside HTML elements.
        By default, :class:`HtmlTokenizer` uses
        :func:`webstruct.text_tokenizers.tokenize`.
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
        self.tagset = set(tagset) if tagset is not None else None
        self.text_tokenize_func = text_tokenize_func or tokenize
        self.kill_html_tags = kill_html_tags
        self.replace_html_tags = replace_html_tags

        if ignore_html_tags is not None:
            self.ignore_html_tags = set(ignore_html_tags)
        else:
            self.ignore_html_tags = {'script', 'style'}

        # FIXME: don't use shared instance of sequence encoder
        # because sequence encoder is stateful
        self.sequence_encoder = sequence_encoder or IobEncoder()

        tag_pattern = self.sequence_encoder.token_processor.tag_re.pattern.strip()
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
        self.sequence_encoder.reset()
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
        token_groups = self.sequence_encoder.group(zip(html_tokens, tags))
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

        head_tokens, head_tags = self._tokenize_and_split(tree.text)
        for index, (token, tag) in enumerate(zip(head_tokens, head_tags)):
            yield HtmlToken(index, head_tokens, tree, False), tag

        for child in tree:  # where is my precious "yield from"?
            for html_token, tag in self._process_tree(child):
                yield html_token, tag

        tail_tokens, tail_tags = self._tokenize_and_split(tree.tail)
        for index, (token, tag) in enumerate(zip(tail_tokens, tail_tags)):
            yield HtmlToken(index, tail_tokens, tree, True), tag

        self._cleanup_elem(tree)

    def _cleanup_elem(self, elem):
        """ Remove special tokens from elem """
        if elem.text:
            elem.text = self._tag_re.sub("", elem.text)
        if elem.tail:
            elem.tail = self._tag_re.sub("", elem.tail)

    def _tokenize_and_split(self, text):
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
        if self.text_tokenize_func is tokenize:
            dct['text_tokenize_func'] = 'DEFAULT'
        return dct

    def __setstate__(self, state):
        if state['text_tokenize_func'] == 'DEFAULT':
            state['text_tokenize_func'] = tokenize
        self.__dict__.update(state)


class HtmlFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    This class extracts features from lists of :class:`HtmlToken` instances
    (:class:`HtmlTokenizer` can be used to create such lists).

    :meth:`fit` / :meth:`transform` / :meth:`fit_transform` interface
    may look familiar to you if you ever used scikit-learn_:
    :class:`HtmlFeatureExtractor` implements sklearn's
    Transformer interface. But there is one twist: usually for sequence
    labelling tasks the whole sequences are considered observations.
    So in our case a single observation is a tokenized document
    (a list of tokens), not an individual token:
    :meth:`fit` / :meth:`transform` / :meth:`fit_transform` methods accept
    lists of documents (lists of lists of tokens), and return lists
    of documents' feature dicts (lists of lists of feature dicts).

    .. _scikit-learn: http://scikit-learn.org

    Parameters
    ----------

    token_features : list of callables
        List of "token" feature functions. Each function accepts
        a single ``html_token`` parameter and returns a dictionary
        wich maps feature names to feature values. Dicts from all
        token feature functions are merged by HtmlFeatureExtractor.
        Example token feature (it just returns token text)::

            >>> def current_token(html_token):
            ...     return {'tok': html_token.token}

        :mod:`webstruct.features` module provides some predefined feature
        functions, e.g. :func:`parent_tag <webstruct.features.block_features.parent_tag>`
        which returns token's parent tag.

        Example::

            >>> from webstruct import GateLoader, HtmlTokenizer, HtmlFeatureExtractor
            >>> from webstruct.features import parent_tag

            >>> loader = GateLoader(known_entities={'PER'})
            >>> html_tokenizer = HtmlTokenizer()
            >>> feature_extractor = HtmlFeatureExtractor(token_features=[parent_tag])

            >>> tree = loader.loadbytes(b"<p>hello, <PER>John <b>Doe</b></PER> <br> <PER>Mary</PER> said</p>")
            >>> html_tokens, tags = html_tokenizer.tokenize_single(tree)
            >>> feature_dicts = feature_extractor.transform_single(html_tokens)
            >>> for token, tag, feat in zip(html_tokens, tags, feature_dicts):
            ...     print("%s %s %s" % (token.token, tag, feat))
            hello O {'parent_tag': 'p'}
            John B-PER {'parent_tag': 'p'}
            Doe I-PER {'parent_tag': 'b'}
            Mary B-PER {'parent_tag': 'p'}
            said O {'parent_tag': 'p'}

    global_features : list of callables, optional
        List of "global" feature functions. Each "global" feature function
        should accept a single argument - a list
        of ``(html_token, feature_dict)`` tuples.
        This list contains all tokens from the document and
        features extracted by previous feature functions.

        "Global" feature functions are applied after "token" feature
        functions in the order they are passed.

        They should change feature dicts ``feature_dict`` inplace.

    min_df : integer or Mapping, optional
        Feature values that have a document frequency strictly
        lower than the given threshold are removed.
        If ``min_df`` is integer, its value is used as threshold.

        TODO: if ``min_df`` is a dictionary, it should map feature names
        to thresholds.

    """
    def __init__(self, token_features, global_features=None, min_df=1):
        self.token_features = token_features
        self.global_features = global_features or []
        self.min_df = min_df

    def fit(self, html_token_lists, y=None):
        self.fit_transform(html_token_lists)
        return self

    def fit_transform(self, html_token_lists, y=None, **fit_params):
        X = [self.transform_single(html_tokens) for html_tokens in html_token_lists]
        return self._pruned(X, low=self.min_df)

    def transform(self, html_token_lists):
        return [self.transform_single(html_tokens) for html_tokens in html_token_lists]

    def transform_single(self, html_tokens):
        feature_func = _CombinedFeatures(*self.token_features)
        token_data = list(zip(html_tokens, map(feature_func, html_tokens)))

        for feat in self.global_features:
            feat(token_data)

        return [{k: fd[k] for k in fd if not k.startswith('_')}
                for tok, fd in token_data]

    def _pruned(self, X, low=None):
        if low is None or low <= 1:
            return X
        cnt = self._document_frequency(X)
        keep = {k for (k, v) in cnt.items() if v >= low}
        del cnt
        return [
            [{k: v for k, v in fd.items() if (k, v) in keep} for fd in doc]
            for doc in X
        ]

    def _document_frequency(self, X):
        cnt = Counter()
        for doc in X:
            seen_features = set(chain.from_iterable(fd.items() for fd in doc))
            cnt.update(seen_features)
        return cnt


class _CombinedFeatures(object):
    """
    Utility for combining several feature functions::

        >>> from pprint import pprint
        >>> def f1(tok): return {'upper': tok.isupper()}
        >>> def f2(tok): return {'len': len(tok)}
        >>> features = _CombinedFeatures(f1, f2)
        >>> pprint(features('foo'))
        {'len': 3, 'upper': False}

    """
    def __init__(self, *feature_funcs):
        self.feature_funcs = list(feature_funcs)

    def __call__(self, *args, **kwargs):
        features = [f(*args, **kwargs) for f in self.feature_funcs]
        return merge_dicts(*features)
