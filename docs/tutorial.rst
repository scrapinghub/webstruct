Tutorial
========

This tutorial assumes you are familiar with machine learning.


Get annotated data
------------------

First, you need the training/development data. We suggest to use
WebAnnotator_ Firefox extension to annotate HTML pages. Follow WebAnnotator
docs to define named entities and annotate some web pages.

After that you can load annotated webpages as lxml trees:

>>> import webstruct
>>> trees = webstruct.load_trees([
...    ("train/*.html", webstruct.WebAnnotatorLoader())
... ])

See :ref:`html-loaders` for more info.

.. _WebAnnotator: https://github.com/xtannier/WebAnnotator


From HTML to Tokens
-------------------

To convert HTML trees to a format suitable for sequence prediction algorithms
(like CRF, MEMM or Structured Perceptron) the following approach is used:

1. Text is extracted from HTML and split into tokens.
2. For each token a special :class:`~.HtmlToken` instance is created. It
   contains information not only about the text token itself, but also about
   its position in HTML tree.

A single HTML page corresponds to a single sequence (a list of HtmlTokens).

:class:`~.HtmlTokenizer` can transform trees loaded by one of the WebStruct
loaders into labels and HTML tokens:

>>> html_tokenizer = webstruct.HtmlTokenizer()
>>> X, y = html_tokenizer.tokenize(trees)

For each tree :class:`~.HtmlTokenizer` extracts two arrays: a list of
:class:`~.HtmlToken` instances ``X`` and a list of tags encoded
using IOB2_ encoding (also known as BIO encoding) ``y``.
So in our example ``X`` is a list of lists of :class:`~.HtmlToken`
instances, and  ``y`` is a list of lists of strings.

Feature Extraction
------------------

For supervised machine learning algorithms to work we need to extract
`features <http://en.wikipedia.org/wiki/Features_%28pattern_recognition%29>`_.

In WebStruct feature vectors are Python dicts
``{"feature_name": "feature_value"}``; a dict is computed for
each HTML token. How to convert these dicts into representation required
by a sequence labelling toolkit depends on a toolkit used; we will cover
that later.

To compute feature dicts use :class:`~.HtmlFeatureExtractor`.
First, define your feature functions. A feature function should take
an :class:`~.HtmlToken` instance and return a feature dict;
feature dicts from individual feature functions will be merged
into the final feature dict for a token. Such functions can ask questions
about token itself, its neighbours (in the same HTML element),
its position in HTML.

There are predefined feature functions in :mod:`webstruct.features`,
but for this tutorial let's create some functions ourselves::

    def token_identity(html_token):
        return {'token': html_token.token}

    def token_isupper(html_token):
        return {'isupper': html_token.token.isupper()}

    def parent_tag(html_token):
        return {'parent_tag': html_token.parent.tag}

    def border_at_left(html_token):
        return {'border_at_left': html_token.index == 0}


Next, create :class:`~.HtmlFeatureExtractor` and use it to extract
feature dicts:

>>> feature_extractor = HtmlFeatureExtractor(
...     token_features = [
...         token_identity,
...         token_isupper,
...         parent_tag,
...         border_at_left
...     ]
... )
>>> features = feature_extractor.fit_transform(X)

WebStruct supports another kind of feature functions that work on multiple
tokens; we don't cover them in this tutorial.

See :ref:`feature-extraction` for more info about HTML tokenization and
feature extraction.

Using a Sequence Labelling Toolkit
----------------------------------

WebStruct doesn't provide a CRF or Structured Perceptron implementation;
learning and prediction is supposed to be handled by an external
sequence labelling toolkit like Wapiti_, CRFSuite_ or seqlearn_.
Once feature dicts are extracted from HTML you should convert them to
a format required by your sequence labelling tooklit and use this toolkit
to train a model and do the prediction.

.. _wapiti: http://wapiti.limsi.fr
.. _CRFSuite: http://www.chokkan.org/software/crfsuite/
.. _seqlearn: https://github.com/larsmans/seqlearn

Wapiti Support
--------------

Currently WebStruct has helpers only for Wapiti_ sequence labelling toolkit.
To use them, you'll need

* wapiti C++ library itself, including ``wapiti`` command-line utility;
* `python-wapiti <https://github.com/adsva/python-wapiti>`_ wrapper (github version).

Extracting Features using Wapiti Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wapiti_ has "templates" support which allows to define richer features
from the basic features, and to specify what to do with labels.
Template format is described in Wapiti
`manual <http://wapiti.limsi.fr/manual.html#patterns>`__; you may also
check `CRF++ docs <http://crfpp.googlecode.com/svn/trunk/doc/index.html#templ>`__
to get the templates idea - CRF++ and Wapiti template formats are very similar.

Let's define a template that will make wapiti use first-order transition
features, plus ``token`` text values in a +-2 window near the current token.

>>> feature_template = '''
... # Label unigram & bigram
... *
...
... # Nearby token unigrams (lower)
... uLL:%x[-2,token_lower]
... u-L:%x[-1,token_lower]
... u-R:%x[ 1,token_lower]
... uRR:%x[ 2,token_lower]
... '''

Note that WebStruct allows to use feature names instead of numbers
in Wapiti templates.

Training
~~~~~~~~

Let's define a CRF model:

>>> crf = webstruct.WapitiCRF('mymodel.wapiti',
...     train_args = '--algo l-bfgs --maxiter 50 --compact',
...     feature_template = feature_template,
... )

:class:`~.WapitiCRF` uses command-line ``wapiti`` tool from C++ library;
make sure it is installed. First :class:`~.WapitiCRF` constructor
argument is a file name the model will be save to after training.
For ``train_args`` description check the Wapiti
`manual <http://wapiti.limsi.fr/manual.html>`__.

.. note::

    :class:`~.WapitiCRF` includes all feature for the current
    token by default, so we haven't defined them in our template.

To train the model use :meth:`.WapitiCRF.fit` method:

>>> crf.fit(features, y)

:meth:`.WapitiCRF.fit` accepts 2 lists: a list of lists of feature dicts for
all documents, and a list of lists of tags for all documents.

Prediction
~~~~~~~~~~

Once you got a trained model you can use it to extract entities from
unseen webpages. To do it, you need:

1. Load data using :class:`~.HtmlLoader` loader. If a custom HTML cleaner
   was used for loading training data make sure to apply it here as well.
2. Use the same ``html_tokenizer`` as used for training to extract HTML tokens
   and labels from loaded trees. All labels would be "O" here;
   ``y`` can be discarded.
3. Use the same ``feature_extractor`` as used for training to extract
   features.
4. Run :meth:`.WapitiCRF.transform` method on features extracted in (3)
   to get the prediction - a list of IOB2-encoded tags for each input document.
5. Group input tokens to entities based on predicted tags
   (check :meth:`.IobEncoder.group` and :func:`.smart_join`).

We won't go into details here because usually you don't have to write
all the steps above manually - there are helpers in :mod:`webstruct.model`
that make the whole process easier.

Putting It All Together
~~~~~~~~~~~~~~~~~~~~~~~



When you got a trained model, to extract named entities from unannotated data
you can use :class:`~.HtmlLoader` to load input HTML tree,
:class:`~.HtmlTokenizer` to create a list of HTML tokens for these trees,
then use model's ``transform`` method to get IOB2 labels for them,
then use :meth:`.IobEncoder.group` to convert IOB2 labels to simple labels,
and then use :func:`.smart_join` to get entities as text.

5. Create a model and train it:

   >>> import webstruct
   >>> model = webstruct.create_wapiti_pipeline('mymodel.wapiti',
   ...     token_features = [token_identity, token_isupper, parent_tag],
   ...     feature_template = feature_template,
   ...     train_args = '--algo l-bfgs --maxiter 50 --compact'
   ... )
   >>> model.fit(X, y)


   Under the hood ``model`` is a ``sklearn.pipeline.Pipeline`` that combines
   :class:`~.HtmlFeatureExtractor` and :class:`~.WapitiCRF`.

Extracting Named Entities
~~~~~~~~~~~~~~~~~~~~~~~~~

When you got a trained model, to extract named entities from unannotated data
you can use :class:`~.HtmlLoader` to load input HTML tree,
:class:`~.HtmlTokenizer` to create a list of HTML tokens for these trees,
then use model's ``transform`` method to get IOB2 labels for them,
then use :meth:`.IobEncoder.group` to convert IOB2 labels to simple labels,
and then use :func:`.smart_join` to get entities as text.

:class:`~.NER` class combines all of these steps:

>>> import urllib2
>>> html = urllib2.urlopen("http://scrapinghub.com/contact").read()
>>> ner = webstruct.NER(model)
>>> ner.extract(html)
[('Scrapinghub', 'ORG'), ..., ('Iturriaga 3429 ap. 1', 'STREET'), ...]



.. _IOB2: http://en.wikipedia.org/wiki/Inside_Outside_Beginning


Training and Prediction
-----------------------

WebStruct doesn't have CRF or MEMM or Averaged Perceptron implementation
built-in; it relies on external libraries to do actual training and
prediction. Once feature dicts are extracted from HTML you can convert them to
a format required by your sequence labelling tooklit and use this toolkit
to train a model and do the prediction.

Currently WebStruct provides some utilities for using Wapiti_ as a sequence
labelling toolkit. There is ``webstruct.wapiti.WapitiFeatureEncoder`` class
for encoding feature dictionaries to Wapiti format, and
``webstruct.wapiti.WapitiChunker`` class for prediction.
Training is currently should be done using command-line utilities.

TODO: more docs for ``webstruct.wapiti``
