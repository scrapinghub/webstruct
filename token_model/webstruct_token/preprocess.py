# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re

DEFAULT_TAGSET = {'org', 'per', 'subj', 'street', 'city', 'state', 'country',
                  'zipcode', 'email', 'tel', 'fax'}


def to_features_and_labels(elem, tokenize_func, label_encoder, feature_func):
    """
    Convert HTML element or document (parsed by lxml) to a sequence of
    (features_dict, label) pairs.

        >>> html = "<p>hello <PER>John <b>Doe</b></PER> <br> <PER>Mary</PER> said</p>"

    First, define a tagset and encode NER labels in the original HTML::

        >>> tagset = Tagset({"ORG", "PER"})
        >>> html = tagset.encode_tags(html)

    Then parse the document using lxml::

        >>> import lxml.html
        >>> doc = lxml.html.fromstring(html)

    Then define text tokenizer, label encoder and feature functions::

        >>> tokenize_func = lambda text: text.split()
        >>> label_encoder = IobSequence(tagset)
        >>> def get_features(index, tokens, elem, is_tail):
        ...     return {
        ...         'tok': tokens[index],
        ...         'is_tail': int(is_tail),
        ...         'tag': elem.tag,
        ...     }

    Then use to_features_and_labels to extract features and labels::

        >>> for features, label in to_features_and_labels(doc, tokenize_func, label_encoder, get_features):
        ...     print("{1:5} {0[tok]:5} {0[is_tail]:2} {0[tag]}".format(features, label))
        O     hello  0 p
        B-PER John   0 p
        I-PER Doe    0 b
        B-PER Mary   1 br
        O     said   1 br

    """
    def tokenize_and_split(text):
        tokens = tokenize_func(text or '')
        return label_encoder.encode_split(tokens)

    # head
    head_tokens, head_labels = tokenize_and_split(elem.text)
    for index, (token, label) in enumerate(zip(head_tokens, head_labels)):
        yield feature_func(index, head_tokens, elem, False), label

    # children
    for child in elem:
        # where is my precious "yield from"?
        for features, label in to_features_and_labels(child, tokenize_func, label_encoder, feature_func):
            yield features, label

    # tail
    tail_tokens, tail_labels = tokenize_and_split(elem.tail)
    for index, (token, label) in enumerate(zip(tail_tokens, tail_labels)):
        yield feature_func(index, tail_tokens, elem, True), label


class Tagset(object):
    """
    Utility class for working with tags and converting between
    ``<TAG>`` and internal tag representation.
    """
    def __init__(self, tagset):
        self.tagset = tagset
        self.patterns = self._patterns()

    def encode_tags(self, text):
        """
        Replace <tag> and </tag> with __TAG_START and __TAG_END.

        This is needed to simplify parsing of HTML that has NER <tags>
        embedded (e.g. GATE outputs such HTML).

        >>> tagset = Tagset({'org', 'city'})
        >>> tagset.encode_tags('<p>Go to <CITY>Montevideo</city></p>')
        '<p>Go to  __CITY_START Montevideo __city_END </p>'

        """
        text = re.sub(self.patterns['html_open_tag'], r' __\1_START ', text)
        text = re.sub(self.patterns['html_close_tag'], r' __\1_END ', text)
        return text

    def start_tag_or_none(self, token):
        """
        >>> tagset = Tagset({'org'})
        >>> tagset.start_tag_or_none('foo')
        >>> tagset.start_tag_or_none('__ORG_START')
        'ORG'
        """
        if self.patterns['start_tag'].match(token):
            return token[2:-6].upper()

    def end_tag_or_none(self, token):
        """
        >>> tagset = Tagset({'org'})
        >>> tagset.start_tag_or_none('foo')
        >>> tagset.end_tag_or_none('__ORG_END')
        'ORG'
        """
        if self.patterns['end_tag'].match(token):
            return token[2:-4].upper()

    def _patterns(self):
        tags_pattern = '|'.join(self.tagset)
        return {
            'html_open_tag': re.compile('<(%s)>' % tags_pattern, re.I),
            'html_close_tag': re.compile('</(%s)>' % tags_pattern, re.I),
            'start_tag': re.compile('__(%s)_START' % tags_pattern, re.I),
            'end_tag': re.compile('__(%s)_END' % tags_pattern, re.I)
        }


class IobSequence(object):
    """
    By default, IobSequence outputs 'O' tags:

        >>> seq = IobSequence(Tagset({'ORG', 'PER'}))
        >>> seq.tag
        'O'
        >>> next(seq), next(seq), next(seq)
        ('O', 'O', 'O')

    Use ``begin`` method to start a new sequence:

        >>> seq.begin('PER')
        >>> seq.tag
        'PER'

    When the tag is not 'O', first item is encoded as B-TAG and
    consequent items are encoded as I-TAG::

        >>> next(seq), next(seq), next(seq)
        ('B-PER', 'I-PER', 'I-PER')
        >>> seq.begin('ORG')
        >>> next(seq), next(seq), next(seq)
        ('B-ORG', 'I-ORG', 'I-ORG')
        >>> seq.tag
        'ORG'

    """

    def __init__(self, tagset):
        self.tagset = tagset
        self.reset()

    def begin(self, tag):
        """ Begin new sequence """
        self.tag = tag
        self.start = True

    def reset(self):
        """ Resets sequence """
        self.begin('O')

    def encode(self, tokens):
        """
        Convert sequence to IOB format;
        return a sequence of (token, label) pairs::

            >>> tagset = Tagset({'PER', 'ORG'})
            >>> text = tagset.encode_tags("hello <PER>John Doe</PER> <PER>Mary</PER> said")
            >>> seq = IobSequence(tagset)
            >>> for token, label in seq.encode(text.split()):
            ...     print("%s %s" % (token, label))
            hello O
            John B-PER
            Doe I-PER
            Mary B-PER
            said O

        """
        return zip(self._process_border_tokens(tokens), self)

    def encode_split(self, tokens):
        """
        Convert sequence to IOB format;
        return 2 lists (tokens and labels)::

            >>> tagset = Tagset({'PER', 'ORG'})
            >>> text = tagset.encode_tags("hello <PER>John Doe</PER> <PER>Mary</PER> said")
            >>> tokens, labels = IobSequence(tagset).encode_split(text.split())
            >>> tokens
            ('hello', 'John', 'Doe', 'Mary', 'said')
            >>> labels
            ('O', 'B-PER', 'I-PER', 'B-PER', 'O')

        """
        res = list(self.encode(tokens))
        if not res:
            return (), ()
        return zip(*res)

    @staticmethod
    def group(data, strict=False):
        """
        Group IOB-encoded entities::

            >>> data = [("hello", "O"), (",", "O"), ("John", "B-PER"),
            ...         ("Doe", "I-PER"), ("Mary", "B-PER"), ("said", "O")]
            >>> for items, label in IobSequence.group(data):
            ...     print("%s %s" % (items, label))
            ['hello', ','] O
            ['John', 'Doe'] PER
            ['Mary'] PER
            ['said'] O

        By default, invalid sequences are fixed::

            >>> data = [("hello", "O"), ("John", "I-PER"), ("Doe", "I-PER")]
            >>> for items, label in IobSequence.group(data):
            ...     print("%s %s" % (items, label))
            ['hello'] O
            ['John', 'Doe'] PER

        Pass 'strict=True' argument to raise an exception for
        invalid sequences::

            >>> for items, label in IobSequence.group(data, strict=True):
            ...     print("%s %s" % (items, label))
            Traceback (most recent call last):
            ...
            ValueError: Invalid sequence: I-PER tag can't start sequence
        """
        buf, tag = [], 'O'

        for info, iob_tag in data:
            if iob_tag.startswith('I-') and tag != iob_tag[2:]:
                if strict:
                    raise ValueError("Invalid sequence: %s tag can't start sequence" % iob_tag)
                else:
                    iob_tag = 'B-' + iob_tag[2:]  # fix bad tag

            if iob_tag.startswith('B-'):
                if buf:
                    yield buf, tag
                buf = []

            elif iob_tag == 'O':
                if buf and tag != 'O':
                    yield buf, tag
                    buf = []

            tag = 'O' if iob_tag == 'O' else iob_tag[2:]
            buf.append(info)

        if buf:
            yield buf, tag


    def _process_border_tokens(self, tokens):
        for token in tokens:
            if self._handle_border_token(token):  # pseudo-token
                continue
            yield token

    def _handle_border_token(self, token):
        """
        Handle start/end tokens. Return True if token was start or end tag.

        >>> seq = IobSequence(Tagset(['ORG', 'PER', 'LOC']))
        >>> seq._handle_border_token('hello')
        >>> seq.tag
        'O'
        >>> seq._handle_border_token('__ORG_START')
        True
        >>> seq.tag
        'ORG'
        >>> seq._handle_border_token('__ORG_END')
        True
        >>> seq.tag
        'O'
        >>>
        """
        start_tag = self.tagset.start_tag_or_none(token)
        if start_tag:
            self.begin(start_tag)
            return True

        end_tag = self.tagset.end_tag_or_none(token)
        if end_tag:
            # XXX: nested tags are unsupported
            assert end_tag == self.tag, (end_tag, self.tag)
            self.reset()
            return True

    def __iter__(self):
        return self

    def __next__(self):
        if self.tag == 'O':
            return 'O'

        if self.start:
            self.start = False
            return 'B-' + self.tag

        return 'I-' + self.tag
    next = __next__  # Python 2.x support
