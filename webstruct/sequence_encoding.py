# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re

class IobEncoder(object):
    """
    Utility class for encoding tagged token streams using IOB2 encoding.

    Encode input tokens using ``encode`` method::

        >>> iob_encoder = IobEncoder()
        >>> input_tokens = ["__START_PER__", "John", "__END_PER__", "said"]
        >>> def encode(encoder, tokens): return [p for p in IobEncoder.from_indices(encoder.encode(tokens), tokens)]
        >>> encode(iob_encoder, input_tokens)
        [('John', 'B-PER'), ('said', 'O')]


        >>> input_tokens = ["hello", "__START_PER__", "John", "Doe", "__END_PER__", "__START_PER__", "Mary", "__END_PER__", "said"]
        >>> tokens = encode(iob_encoder, input_tokens)
        >>> tokens, tags = iob_encoder.split(tokens)
        >>> tokens, tags
        (['hello', 'John', 'Doe', 'Mary', 'said'], ['O', 'B-PER', 'I-PER', 'B-PER', 'O'])

    Note that IobEncoder is stateful. This means you can encode incomplete
    stream and continue the encoding later::

        >>> iob_encoder = IobEncoder()
        >>> input_tokens_partial = ["__START_PER__", "John"]
        >>> encode(iob_encoder, input_tokens_partial)
        [('John', 'B-PER')]
        >>> input_tokens_partial = ["Mayer", "__END_PER__", "said"]
        >>> encode(iob_encoder, input_tokens_partial)
        [('Mayer', 'I-PER'), ('said', 'O')]

    To reset internal state, use ``reset method``::

        >>> iob_encoder.reset()

    Group results to entities::

        >>> iob_encoder.group(encode(iob_encoder, input_tokens))
        [(['hello'], 'O'), (['John', 'Doe'], 'PER'), (['Mary'], 'PER'), (['said'], 'O')]

    Input token stream is processed by ``InputTokenProcessor()`` by default;
    you can pass other token processing class to customize which tokens
    are considered start/end tags.
    """

    def __init__(self, token_processor=None):
        self.token_processor = token_processor or InputTokenProcessor()
        self.reset()

    def reset(self):
        """ Reset the sequence """
        self.tag = 'O'

    def iter_encode(self, input_tokens):
        # the easiest way would be to check the following token and check if it is a token or end however this is not possible with generators
        # second option is to keep a prev_tag in memory and modify it depending the current value but I am not suere it's possible to do given that previous tag has been yielded already
        for number, token in enumerate(input_tokens):
            token_type, value = self.token_processor.classify(token)

            if token_type == 'start':
                self.tag = "B-" + value

            elif token_type == 'end':
                if value != self.tag[2:]:
                    raise ValueError(
                        "Invalid tag sequence: close tag '%s' "
                        "doesn't match open tag '%s'." % (value, self.tag)
                    )
                self.tag = "O"

            elif token_type == 'token':
                yield number, self.tag
                if self.tag[0] == 'B':
                    self.tag = "I" + self.tag[1:]

            elif token_type == 'drop':
                continue

            else:
                raise ValueError("Unknown token type '%s' for token '%s'" % (token_type, token))

    def encode(self, input_tokens):
        return list(self.iter_encode(input_tokens))

    def split(self, tokens):
        """ split ``[(token, tag)]`` to ``([token], [tags])`` tuple """
        return [t[0] for t in tokens], [t[1] for t in tokens]

    @classmethod
    def from_indices(cls, indices, input_tokens):
        for idx, tag in indices:
            yield input_tokens[idx], tag

    @classmethod
    def group(cls, data, strict=False):
        """
        Group IOB2-encoded entities. ``data`` should be an iterable
        of ``(info, iob_tag)`` tuples. ``info`` could be any Python object,
        ``iob_tag`` should be a string with a tag.

        Example::

            >>>
            >>> data = [("hello", "O"), (",", "O"), ("John", "B-PER"),
            ...         ("Doe", "I-PER"), ("Mary", "B-PER"), ("said", "O")]
            >>> for items, tag in IobEncoder.iter_group(data):
            ...     print("%s %s" % (items, tag))
            ['hello', ','] O
            ['John', 'Doe'] PER
            ['Mary'] PER
            ['said'] O

        By default, invalid sequences are fixed::

            >>> data = [("hello", "O"), ("John", "I-PER"), ("Doe", "I-PER")]
            >>> for items, tag in IobEncoder.iter_group(data):
            ...     print("%s %s" % (items, tag))
            ['hello'] O
            ['John', 'Doe'] PER

        Pass 'strict=True' argument to raise an exception for
        invalid sequences::

            >>> for items, tag in IobEncoder.iter_group(data, strict=True):
            ...     print("%s %s" % (items, tag))
            Traceback (most recent call last):
            ...
            ValueError: Invalid sequence: I-PER tag can't start sequence
        """
        return list(cls.iter_group(data, strict))

    @classmethod
    def iter_group(cls, data, strict=False):
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

class BilouEncoder(object):
    """
    Utility class for encoding tagged token streams using BILOU encoding.

    Encode input tokens using ``encode`` method::

        >>> bilou_encoder = BilouEncoder()
        >>> input_tokens = ["__START_PER__", "John", "__END_PER__", "said"]
        >>> def encode(encoder, tokens): return [p for p in BilouEncoder.from_indices(encoder.encode(tokens), tokens)]
        >>> encode(bilou_encoder, input_tokens)
        [('John', 'U-PER'), ('said', 'O')]


        >>> input_tokens = ["hello", "__START_PER__", "John", "Doe", "__END_PER__", "__START_PER__", "Mary", "__END_PER__", "said"]
        >>> tokens = encode(bilou_encoder, input_tokens)
        >>> tokens, tags = bilou_encoder.split(tokens)
        >>> tokens, tags
        (['hello', 'John', 'Doe', 'Mary', 'said'], ['O', 'B-PER', 'L-PER', 'U-PER', 'O'])

    To reset internal state, use ``reset method``::

        >>> bilou_encoder.reset()

    """
    def __init__(self, token_processor=None):
        self.token_processor = token_processor or InputTokenProcessor()
        self.reset()

    def reset(self):
        """ Reset the sequence """
        self.tag = 'O'

    def encode(self, input_tokens):
        tags = []
        token_type, value = '', ''
        for number, token in enumerate(input_tokens):
            token_type, value = self.token_processor.classify(token)

            if token_type == 'start':
                self.tag = "B-" + value

            elif token_type == 'end':
                if value != tags[-1][1][2:]:
                    raise ValueError(
                        "Invalid tag sequence: close tag '%s' "
                        "doesn't match open tag '%s'." % (value, tags[-1][1])
                    )
                if tags[-1][1][0] == 'B':  # check first letter of previous tag
                    tags[-1] = (tags[-1][0], 'U' + self.tag[1:])
                else:
                    tags[-1] = (tags[-1][0], 'L' + self.tag[1:])
                self.tag = 'O'

            elif token_type == 'token':
                tags.append((number, self.tag))
                if len(tags) > 0 and tags[-1][1][0] == 'B':
                    self.tag = 'I' + self.tag[1:]

            elif token_type == 'drop':
                continue
            else:
                raise ValueError("Unknown token type '%s' for token '%s'" % (token_type, token))
        return tags

    def split(self, tokens):
        """ split ``[(token, tag)]`` to ``([token], [tags])`` tuple """
        return [t[0] for t in tokens], [t[1] for t in tokens]

    @classmethod
    def from_indices(cls, indices, input_tokens):
        for idx, tag in indices:
            yield input_tokens[idx], tag

    @classmethod
    def group(cls, data, strict=False):
        """
        Group BILOU-encoded entities. ``data`` should be an iterable
        of ``(info, bilou_tag)`` tuples. ``info`` could be any Python object,
        ``bilou_tag`` should be a string with a tag.

        Example::

            >>>
            >>> data = [("hello", "O"), (",", "O"), ("John", "B-PER"),
            ...         ("Doe", "L-PER"), ("Mary", "U-PER"), ("said", "O")]
            >>> for items, tag in BilouEncoder.iter_group(data):
            ...     print("%s %s" % (items, tag))
            ['hello', ','] O
            ['John', 'Doe'] PER
            ['Mary'] PER
            ['said'] O

        By default, invalid sequences are fixed::

            >>> data = [("hello", "O"), ("John", "I-PER"), ("Doe", "I-PER")]
            >>> for items, tag in IobEncoder.iter_group(data):
            ...     print("%s %s" % (items, tag))
            ['hello'] O
            ['John', 'Doe'] PER

        Pass 'strict=True' argument to raise an exception for
        invalid sequences::

            >>> for items, tag in BilouEncoder.iter_group(data, strict=True):
            ...     print("%s %s" % (items, tag))
            Traceback (most recent call last):
            ...
            ValueError: Invalid sequence: I-PER tag can't start sequence
        """
        return list(cls.iter_group(data, strict))

    @classmethod
    def iter_group(cls, data, strict=False):
        buf, tag = [], 'O'
        n = len(data)
        for i, (info, bilou_tag) in enumerate(data):
           
            i_or_l = bilou_tag.startswith('I-') or bilou_tag.startswith('L-')
            if i_or_l and tag != bilou_tag[2:]: 
                if strict:
                    raise ValueError("Invalid sequence: %s tag can't start sequence" % bilou_tag)
                elif i < n and data[i + 1][1][0] != 'B' and data[i + 1][1][2:] == tag[2:]:
                    bilou_tag = 'B-' + bilou_tag[2:]
                else:
                    bilou_tag = 'U-' + bilou_tag[2:]
               

            if bilou_tag.startswith('B-') or bilou_tag.startswith('U-'):
                if buf:
                    yield buf, tag 
                buf = []

            elif bilou_tag == 'O':
                if buf and tag != 'O':
                    yield buf, tag
                    buf = []

            tag = 'O' if bilou_tag == 'O' else bilou_tag[2:]
            buf.append(info)

        if buf:
            yield buf, tag


# FIXME: this hook is incomplete: __START_TAG__ tokens are assumed everywhere.
class InputTokenProcessor(object):
    def __init__(self, tagset=None):
        if tagset is not None:
            tag_re = '|'.join(tagset)
        else:
            tag_re = '\w+?'
        self.tag_re = re.compile('__(START|END)_(%s)__' % tag_re)

    def classify(self, token):
        """
        >>> tp = InputTokenProcessor()
        >>> tp.classify('foo')
        ('token', 'foo')
        >>> tp.classify('__START_ORG__')
        ('start', 'ORG')
        >>> tp.classify('__END_ORG__')
        ('end', 'ORG')
        """

        # start/end tags
        m = self.tag_re.match(token)
        if m:
            return m.group(1).lower(), m.group(2)

        # # drop standalone commas and semicolons by default?
        # if token in {',', ';'}:
        #     return 'drop', token

        # regular token
        return 'token', token
