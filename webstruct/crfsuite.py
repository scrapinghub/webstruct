# -*- coding: utf-8 -*-
"""
CRFsuite_ backend for webstruct.

.. _CRFsuite: http://www.chokkan.org/software/crfsuite/
"""
from __future__ import absolute_import
import re
import itertools
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from webstruct import HtmlFeatureExtractor
from webstruct.base import BaseCRF
from webstruct.features import DEFAULT_FEATURES
from webstruct.utils import get_combined_keys, tostr


CRFPP_MACRO_PATTERN = re.compile(r'''
    (?P<macro>%[xX])
    \[
    \s*(?P<offset>[\d-]+),
    \s*(?P<column>[^\],\s]+)\s*
    (?P<rest>[\],])
    ''', re.VERBOSE | re.UNICODE)


def parse_crfpp_template(template):
    """
    parse a CRF++ compatible template into the list of templates in form of (name, offset)

    >>> parse_crfpp_template("U22:%x[0,tag]")
    [(('tag', 0),)]

    >>> parse_crfpp_template("U22:%x[0,tag]/%x[-1,tag]")
    [(('tag', 0), ('tag', -1))]
    """
    templates = []
    for line in template.splitlines():
        line = line.strip()
        tuples = []
        if line.startswith('#'):
            continue
        if line.startswith('u') or line.startswith('U'):
            tuples = [(m.groupdict()['column'], int(m.groupdict()['offset']))
                      for m in CRFPP_MACRO_PATTERN.finditer(line) if m]
        if line == 'B' or line == 'b':
            continue
        if line.startswith('b') or line.startswith('B'):
            import warnings

            warnings.warn("bigram templates: %s not supported in CRFsuite" % line)
        if len(tuples):
            templates.append(tuple(tuples))
    return templates


def create_crfsuite_pipeline(model_filename,
                             token_features=None,
                             global_features=None,
                             feature_template=None,
                             min_df=1,
                             **crfsuite_kwargs):
    """
    Create a scikit-learn Pipeline for HTML tagging using CRFsuite.
    This pipeline expects data produced by
    :class:`~.HtmlTokenizer` as an input and produces
    sequences of IOB2 tags as output.

    Example of training, with all parameters default::

        >>> import webstruct
        >>> trees = webstruct.load_trees([
        ...    ("train/*.html", webstruct.WebAnnotatorLoader())
        ... ])  # doctest: +SKIP
        >>> X, y = webstruct.HtmlTokenizer().tokenize(trees)  # doctest: +SKIP
        >>> model = webstruct.create_crfsuite_pipeline('model.crfsuite')  # doctest: +SKIP
        >>> model.fit(X, y)  # doctest: +SKIP

    """

    if token_features is None:
        token_features = DEFAULT_FEATURES

    return Pipeline([
        ('fe', HtmlFeatureExtractor(token_features, global_features, min_df=min_df)),
        ('encoder', CRFsuiteFeatureEncoder(feature_template)),
        ('crf', CRFsuite(model_filename, **crfsuite_kwargs)),
    ])


class CRFsuiteFeatureEncoder(BaseEstimator, TransformerMixin):
    """
    A utility class to expand the features with CRF++ compatible template.
    """

    def __init__(self, template="#"):
        self.template = template
        self.templates_ = parse_crfpp_template(self.template)
        self.feature_names_ = None
        super(CRFsuiteFeatureEncoder, self).__init__()

    def fit(self, X, y=None):
        return self.partial_fit(X)

    def partial_fit(self, X, y=None):
        keys = set(self.feature_names_ or set())
        for feature_dicts in X:
            keys = (keys | get_combined_keys(feature_dicts))

        self.feature_names_ = tuple(keys)
        return self

    def transform(self, X, y=None):
        return [self.transform_single(x) for x in X]

    def transform_single(self, x):
        r"""
        Transform a sequence of dict to a list of ``CRFsuite.Item```

        >>> encoder = CRFsuiteFeatureEncoder("U:token L=%x[0, token]/%x[1, token]")
        >>> seq_features = [{'token': 'the', 'tag': 'DT'}, {'token': 'dog', 'tag': 'NN'}]
        >>> encoder.fit([seq_features])
        CRFsuiteFeatureEncoder(template=None)

        >>> items = encoder.transform_single([{'token': 'the', 'tag': 'DT'}, {'token': 'dog', 'tag': 'NN'}])

        >>> [(attr.attr, attr.value) for attr in items[0]]
        [('token=the', 1.0), ('tag=DT', 1.0), ('token[0]|token[1]=the|dog', 1.0)]

        >>> [(attr.attr, attr.value) for attr in items[1]]
        [('token=dog', 1.0), ('tag=NN', 1.0)]

        Unlike other CRF toolkit, CRFsuite support non-binary feature value. e.g.
        >>> encoder = CRFsuiteFeatureEncoder("U:token L=%x[0, token]/%x[1, token]")
        >>> seq_features = [{'token': 'the', 'tag': 'DT'}, {'token': 'dog', 'tag': 'NN'}]
        >>> encoder.fit([seq_features])
        CRFsuiteFeatureEncoder(template=None)

        >>> items = encoder.transform_single([{'token': ('the', 2.0), 'tag': 'DT'}, {'token': ('dog', 1.5), 'tag': 'NN'}])

        >>> [(attr.attr, attr.value) for attr in items[0]]
        [('token=the', 2.0), ('tag=DT', 1.0), ('token[0]|token[1]=the|dog', 1.0)]

        """
        import crfsuite

        items = [crfsuite.Item() for _ in range(len(x))]

        # each feature convert to a unigram feature
        for t in range(len(x)):
            for key in self.feature_names_:
                v = x[t].get(key)
                if isinstance(v, tuple):
                    items[t].append(crfsuite.Attribute('%s=%s' % (key, tostr(v[0])), v[1]))
                else:
                    items[t].append(crfsuite.Attribute('%s=%s' % (key, tostr(v))))

        # expand bigram features and other unigram features in CRF++ compatible template
        for template in self.templates_:
            name = '|'.join(['%s[%d]' % (f, o) for f, o in template])
            for t in range(len(x)):
                values = []
                for field, offset in template:
                    p = t + offset
                    if p not in range(len(x)):
                        values = []
                        break
                    if field in x[p]:
                        v = x[p][field]
                        if isinstance(v, tuple):
                            # always skip the scale
                            values.append(tostr(v[0]))
                        else:
                            values.append(tostr(v))
                if values:
                    items[t].append(crfsuite.Attribute('%s=%s' % (name, '|'.join(values))))

        return items

class CRFsuite(BaseCRF):
    """Class for training and applying CRFsuite models.

    It relies on CRFsuite's python SWIG package.

    Parameters
    ----------
    algorithm : string,
        'lbfgs' for Gradient descent using the L-BFGS method,
        'l2sgd' for Stochastic Gradient Descent with L2 regularization term
        'ap' for Averaged Perceptron
        'pa' for Passive Aggressive
        'arow' for Adaptive Regularization Of Weight Vector

    c1: float
        the coefficient for L1 regularization.

    c2: float
        The coefficient for L2 regularization.
    """

    def __init__(self, model_filename, algorithm='l2sgd', c1=0.0, c2=1.0, verbose=True):
        self.model_filename = model_filename
        self.verbose = verbose
        self.algorithm = algorithm
        self.c1 = c1
        self.c2 = c2
        super(CRFsuite, self).__init__()

    def fit(self, X, y):
        """
        Train a model.

        Parameters
        ----------
        X : a list of lists of ```crfsuite.Item```

        y : a list of lists of strings
            Labels for several documents.
        """

        import crfsuite

        class Trainer(crfsuite.Trainer):
            def __init__(self, crfsuite):
                self.crfsuite = crfsuite
                super(Trainer, self).__init__()

            def message(self, msg):
                if self.crfsuite.verbose:
                    print msg.strip()

        trainer = Trainer(self)
        trainer.select(self.algorithm, 'crf1d')

        for items, labels in itertools.izip(X, y):
            xseq = self._to_item_sequence(items)
            yseq = self._to_stringlist(labels)
            trainer.append(xseq, yseq, 0)

        if self.algorithm == 'lbfgs':
            trainer.set('c1', str(self.c1))

        trainer.set('c2', str(self.c2))
        trainer.train(self.model_filename, -1)
        return self

    def transform(self, X):
        import crfsuite

        tagger = crfsuite.Tagger()
        tagger.open(self.model_filename)
        xseqs = [self._to_item_sequence(items) for items in X]
        yseqs = []
        for xseq in xseqs:
            tagger.set(xseq)
            yseqs.append(tagger.viterbi())
        return yseqs

    def _to_item_sequence(self, items):
        import crfsuite

        xseq = crfsuite.ItemSequence()
        for item in items:
            xseq.append(item)
        return xseq

    def _to_stringlist(self, labels):
        import crfsuite

        yseq = crfsuite.StringList()
        for label in labels:
            yseq.append(tostr(label))

        return yseq