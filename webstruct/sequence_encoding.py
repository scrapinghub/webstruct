# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re


class IobEncoder(object):
    """
    Utility class for encoding tagged token streams using IOB2 encoding.

    Encode input tokens using ``encode`` method::
        >>> input_tokens = ['__START_PER__', 'John', '__END_PER__', 'said']
        >>> iob_encoder = IobEncoder()
        >>> def encode(encoder, tokens): return [p for p in IobEncoder.from_indices(encoder.iter_encode(tokens), tokens)]
        >>> encode(iob_encoder, input_tokens)
        [('John', 'B-PER'), ('said', 'O')]

        >>> input_tokens = ['hello', '__START_PER__', 'John', 'Doe',
        ...                 '__END_PER__', '__START_PER__', 'Mary',
        ...                 '__END_PER__', 'said']
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

        >>> tokens, tags = iob_encoder.split(encode(iob_encoder, input_tokens))
        >>> iob_encoder.group(tokens, tags)
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
                raise ValueError("Unknown token type '%s' for token '%s'" % (
                                                      token_type, token.chars))

    def encode(self, input_tokens):
        chains, tags = [], []
        for node_tokens, tree, is_tail in input_tokens:
            c = list(self.iter_encode([t.chars for t in node_tokens]))
            c = [l for l in self.from_indices(c, node_tokens)]
            if not c:
                continue
            c, tg = self.split(c)
            chains.append((c, tree, is_tail))
            tags.append(tg)

        return chains, tags

    def split(self, tokens):
        """ split ``[(token, tag)]`` to ``([token], [tags])`` tuple """
        return [t[0] for t in tokens], [t[1] for t in tokens]

    @classmethod
    def from_indices(cls, indices, input_tokens):
        for idx, tag in indices:
            yield input_tokens[idx], tag

    @classmethod
    def group(cls, tokens, tags, strict=False):
        """
        Group IOB2-encoded entities. ``tokens`` could be any Python object,
        ``tags`` should be a list of iob tags.

        Example::

            >>>
            >>> tokens = ["hello", ",", "John", "Doe", "Mary", "said"]
            >>> tags = ["O", "O", "B-PER", "I-PER", "B-PER", "O"]
            >>> for items, tag in IobEncoder.iter_group(tokens, tags):
            ...     print("%s %s" % (items, tag))
            ['hello', ','] O
            ['John', 'Doe'] PER
            ['Mary'] PER
            ['said'] O

        By default, invalid sequences are fixed::
            >>> tokens = ["hello", ",", "John", "Doe"]
            >>> tags = ["O", "O", "I-PER", "I-PER"]
            >>> for items, tag in IobEncoder.iter_group(tokens, tags):
            ...     print("%s %s" % (items, tag))
            ['hello', ','] O
            ['John', 'Doe'] PER

        Pass 'strict=True' argument to raise an exception for
        invalid sequences
        """
            #
            # >>> for items, tag in IobEncoder.iter_group(tokens, tags, strict=True):
            # ...     print("%s %s" % (items, tag))
            # Traceback (most recent call last):
            # ...
            # ValueError: Invalid sequence: I-PER tag can't start sequence

        return list(cls.iter_group(tokens, tags, strict))

    @classmethod
    def iter_group(cls, tokens, tags, strict=False):
        buf, tag = [], 'O'
        for info, iob_tag in zip(tokens, tags):
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


class BilouEncoder(object):
    """
    Utility class for encoding tagged token streams using BILOU encoding.
    Same behavior as IobEncoder.
   """

    def __init__(self, token_processor=None):
        self.token_processor = token_processor or InputTokenProcessor()
        self.iob_encoder = IobEncoder()
        self.reset()

    def reset(self):
        """ Reset the sequence """
        self.iob_encoder.reset()

    def encode(self, input_tokens):
        chains, tags = self.iob_encoder.encode(input_tokens)
        tags = self.iob_to_bilou(tags)
        return chains, tags

    def iob_to_bilou(self, iob_tags):
        bilou_tags = []
        n_tags_lists = len(iob_tags)
        for i, text_tags in enumerate(iob_tags):
            tags = []
            n_tags = len(text_tags)
            for n, tag in enumerate(text_tags):
                tags.append(tag)
                if tag[0] != 'O':
                    if n + 1 < n_tags and not text_tags[n + 1][0].startswith('I'):
                        # if the next tag is not I this entity ends here
                        self.update_end_of_entity(tags)
            if i + 1 < n_tags_lists:
                if not iob_tags[i + 1][0].startswith('I'):  # peek next tag list
                    # if the first tag of the next list is not I entity ends here
                    self.update_end_of_entity(tags)
            else:
                self.update_end_of_entity(tags)
            bilou_tags.append(tags)
        return bilou_tags

    def update_end_of_entity(self, tags):
        last_tag = tags[-1]
        if last_tag.startswith('B'):
            tags[-1] = 'U' + last_tag[1:]
        elif last_tag.startswith('I'):
            tags[-1] = 'L' + last_tag[1:]

    @classmethod
    def from_indices(cls, indices, input_tokens):
        for idx, tag in indices:
            yield input_tokens[idx], tag

    @classmethod
    def group(cls, tokens, tags, strict=False):
        """
        Group BILOU-encoded entities. ``tokens`` could be any Python object,
        ``tags`` should be a list of bilou tags.

        Example::

           >>> tokens = ["hello", ",", "John", "Doe", "Mary", "said"]
           >>> tags = ["O", "O", "B-PER", "L-PER", "U-PER", "O"]
           >>> for items, tag in BilouEncoder.iter_group(tokens, tags):
           ...     print("%s %s" % (items, tag))
           ['hello', ','] O
           ['John', 'Doe'] PER
           ['Mary'] PER
           ['said'] O

        By default, invalid sequences are fixed::

           >>> tokens = ["hello", "John", "Doe"]
           >>> tags = ["O", "I-PER", "I-PER"]
           >>> for items, tag in IobEncoder.iter_group(tokens, tags):
           ...     print("%s %s" % (items, tag))
           ['hello'] O
           ['John', 'Doe'] PER

        Pass 'strict=True' argument to raise an exception for
        invalid sequences::

            >>> for items, tag in BilouEncoder.iter_group(tokens, tags, strict=True):
            ...     print("%s %s" % (items, tag))
            Traceback (most recent call last):
            ...
            ValueError: Invalid sequence: I-PER tag can't start sequence
        """
        return list(cls.iter_group(tokens, tags, strict))

    @classmethod
    def iter_group(cls, tokens, tags, strict=False):
        buf, tag = [], 'O'
        n = len(tags)
        for i, (info, bilou_tag) in enumerate(zip(tokens, tags)):
            i_or_l = bilou_tag.startswith('I-') or bilou_tag.startswith('L-')
            if i_or_l and tag != bilou_tag[2:]:
                if strict:
                    raise ValueError("Invalid sequence: %s tag can't start"
                                     "sequence" % bilou_tag)
                elif (i < n and not tags[i + 1].startswith('B')
                      and tags[i + 1][2:] == tag[2:]):
                    bilou_tag = 'B-' + bilou_tag[2:]
                else:
                    bilou_tag = 'U-' + bilou_tag[2:]

            if bilou_tag.startswith('B-') or bilou_tag.startswith('U-'):
                if buf:
                    yield (buf, tag)
                buf = []

            elif bilou_tag == 'O':
                if buf and tag != 'O':
                    yield (buf, tag)
                    buf = []

            tag = 'O' if bilou_tag == 'O' else bilou_tag[2:]
            buf.append(info)
            if i == n - 1 and buf:
                yield (buf, tag)
