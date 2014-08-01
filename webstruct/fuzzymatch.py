"""
This class help to generate the training data from partially labelled data with fuzzymatch_.

.. _fuzzywuzzy: https://github.com/seatgeek/fuzzywuzzy

"""
import re
import warnings
from webstruct.sequence_encoding import IobEncoder

from .base import BaseSequenceClassifier

# from http://en.wikipedia.org/wiki/Space_(punctuation)#Spaces_in_Unicode
SPACES_SRE = ur'[\s\u0020\u00a0\u1680\u18e0\u2000-\u200d\u202f\u205f\u2060\u3000\ufeff]+'


class FuzzyMatchClassifier(BaseSequenceClassifier):
    """
    Class for predicting the labels by matching with fuzzymatch_.

    It first finds the candidates using the given regex pattern and then
    compare similarity of the matched text to the text in ``choices``,

    if the any one of the similarities larger than the ``threshold``,
    assign the ``BIO`` tags to corresponding input.

    Parameters
    ----------
    entity : string
        the entitiy type (e.g. ADDR or ORG).

    pattern: string
        a regex pattern used to find the matched string from ``html_tokens``.

    choices : list of string
        a list of string to calculate the similarity to the matched string.

    threshold: float
        a float to decide if matched text should assign to given tag.

    postprocess: function
        a function to process the matched text before compare to ``choices``.

    References
    ----------
    .. _fuzzywuzzy: https://github.com/seatgeek/fuzzywuzzy

    Notes
    -----
    the ``pattern`` should include the whitespaces, see ``SPACES_SRE``.

    """
    def __init__(self, entity, pattern, choices, threshold=0.9, \
                postprocess=lambda x: x, verbose=False):
        self.entity = entity
        self.pattern = pattern
        self.choices = choices
        self.threshold = threshold
        self.postprocess = postprocess
        self.verbose = verbose

    def predict(self, X):
        """
        Make a prediction.

        Parameters
        ----------
        X : list of lists of ``HtmlToken``

        Returns
        -------
        y : list of lists
            predicted labels

        """
        from fuzzywuzzy import process

        y = []
        for html_tokens in X:
            tokens = [html_token.token for html_token in html_tokens]
            iob_encoder = IobEncoder()

            def repl(m):
                extracted = self.postprocess(m.group(0))
                if self.verbose:
                    print extracted, choices

                if process.extractBests(extracted, self.choices, score_cutoff=self.threshold * 100):
                    return u' __START_{0}__ {1} __END_{0}__ '.format(self.entity, m.group(0))
                return m.group(0)

            text = re.sub(self.pattern, repl, u" ".join(tokens), flags=re.I | re.U | re.DOTALL)
            tags = [tag for _, tag in iob_encoder.encode(text.split())]
            assert len(html_tokens) == len(tags), 'len(html_tokens): %s and len(tags): %s are not matched' % \
                        (len(html_tokens), len(tags))
            y.append(tags)

        return y

def merge_bio_tags(*tag_list):
    """Merge BIO tags"""
    def select_tag(x, y):

        if x != 'O' and y != 'O' and x[2:] != y[2:]:
            warnings.warn('conflict BIO tag: %s %s' % (x, y))

        # later one wins
        if y != 'O':
            return y
        if x != 'O':
            return x
        return 'O'
    return [reduce(select_tag, i) for i in zip(*tag_list)]
