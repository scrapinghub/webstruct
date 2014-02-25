Webstruct
=========

Installation
------------

Overview
--------

To develop a statistical NER system the following steps are needed:

1) define what entities you are interested in;
2) get some training/testing data (annotated webpages);
3) define what features should be extracted;
4) develop a statistical model that uses these features to produce the output.

Webstruct can:

* read annotated HTML data produced by WebAnnotator_ or GATE_;
* transform HTML trees into "HTML tokens", i.e. text tokens with information
  about their position in HTML tree preserved;
* extract various features from these HTML tokens, including text-based
  features, html-based features and gazetteer-based features
  (GeoNames_ support is built-in);
* convert these features to the format sequence labelling toolikits accept
  (only Wapiti_ CRF toolkit support it built-in at the moment, but support
  for other toolkits like CRFSuite_ and seqlearn_ is planned).

.. _GeoNames: http://www.geonames.org/
.. _wapiti: http://wapiti.limsi.fr
.. _CRFSuite: http://www.chokkan.org/software/crfsuite/
.. _seqlearn: https://github.com/larsmans/seqlearn


High-Level Example
------------------

1. Load webpages annotated using WebAnnotator_:

   >>> import webstruct
   >>> trees = webstruct.load_trees([
   ...    ("train/*.html", webstruct.WebAnnotatorLoader())
   ... ])

2. Transform HTML trees into labels and "HTML tokens":

   >>> html_tokenizer = webstruct.HtmlTokenizer()
   >>> X, y = html_tokenizer.tokenize(trees)

   For each tree HtmlTokenizer extracts two arrays: a list of HtmlToken
   instances and a list of tags encoded using IOB2_ encoding. So ``X``
   is a list of lists of HtmlToken instances, and ``y`` is a list of lists
   of strings.

3. Define some feature functions. There are some predefined functions
   in ``webstruct.features``, but let's define a couple of functions
   ourselves for clarity:

   >>> def token_identity(html_token):
   ...     token_text = html_token.token
   ...     return {
   ...         'token': token_text,
   ...         'token_lower': token_text.lower()
   ...     }

   >>> def token_isupper(html_token):
   ...     return {'isupper': html_token.token.isupper()}

   >>> def parent_tag(html_token):
   ...     return {'parent_tag': html_token.parent.tag}


4. To extract richer features we can use Wapiti_ templates (assuming we're
   using Wapiti_ as a labelling toolkit). Template format is described
   `here <http://wapiti.limsi.fr/manual.html#patterns>`__; webstruct allows
   to use feature names instead of numbers in these templates.

   The following template will make wapiti use first-order transition features,
   plus ``token_lower`` values in a +-2 window near the current token.

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

   ``webstruct.create_wapiti_pipeline`` includes all feature for the current
   token by default, so we don't need to define them in our template.

5. Create a model and train it:

   >>> import webstruct
   >>> model = webstruct.create_wapiti_pipeline('mymodel.wapiti',
   ...     token_features = [token_identity, token_isupper, parent_tag],
   ...     feature_template = feature_template,
   ...     train_args = '--algo l-bfgs --maxiter 50 --compact'
   ... )
   >>> model.fit(X, y)

   Model uses command-line wapiti tool; check its
   `manual <http://wapiti.limsi.fr/manual.html>`__ for ``train_args``
   description.

   Under the hood ``model`` is a ``sklearn.pipeline.Pipeline`` that combines
   ``webstruct.HtmlFeatureExtractor`` and ``webstruct.wapiti.WapitiCRF``.

6. To use the model you need to


.. _IOB2: http://en.wikipedia.org/wiki/Inside_Outside_Beginning

Annotation
----------

Webstruct supports WebAnnotator_ and GATE_ annotation formats;
WebAnnotator_ is recommended.

.. _WebAnnotator: https://github.com/xtannier/WebAnnotator
.. _GATE: http://gate.ac.uk/

Both GATE and WebAnnotator embed annotations into HTML using special tags:
GATE uses custom tags like ``<ORG>`` while WebAnnotator uses tags like
``<span wa-type="ORG">``.

WebStruct loader classes convert GATE and WebAnnotator tags into
``__START_TAGNAME__`` and ``__END_TAGNAME__`` tokens, clean the HTML
and return the result as a tree parsed by lxml::

    >>> from webstruct import WebAnnotatorLoader
    >>> loader = WebAnnotatorLoader()
    >>> loader.load('0.html')
    <Element html at ...>

From HTML to Tokens
-------------------

To convert HTML Tree to a format suitable for sequence prediction algorithms
(like CRF, MEMM or Averaged Perceptron) the following approach is used:

1. Text is extracted from HTML and split into tokens.
2. For each token a special HtmlToken instance is created. It
   contains information not only about the text token itself, but also about
   its position in HTML tree.

A single HTML page corresponds to a single sequence (a list of HtmlTokens).

HtmlTokenizer class can convert a tree (loaded by one of the WebStruct loaders)
to a list of HtmlTokens::

    >>> from webstruct import HtmlTokenizer
    >>> html_tokenizer = HtmlTokenizer()
    >>> tree = loader.load('0.html')
    >>> html_tokens = html_tokenizer.tokenize(tree)

For annotated data start/end tokens (e.g. ``__START_ORG__`` and ``__END_ORG__``)
are converted to IOB2 tag sequences and removed from token stream. IOB2 tags are
available as ``tag`` attribute of HtmlTokens.

Feature extraction
------------------

To extract features, user-defined feature functions are applied to HTML tokens.
There are 2 types of feature functions: "token" feature functions and "global"
feature functions.

Token feature functions take 'html_token' argument which is a current
HtmlToken instance. Such features can ask questions about token itself,
its neighbours (in the same HTML element) and its position in HTML.

Example features:

* lower-cased token text;
* "1" if token consists of lower-cased letters, "0" otherwise;
* "1" if token at the left of this token is uppercased, "0" otherwise;
* "1" if ``<p>`` tag opens just before this token, "0" otherwise;
* "1" if this token is inside ``<a>`` tag, "0" otherwise;
* "1" if there are more than 100 tokens in this HTML element, "0" otherwise.

Example implementations:

    >>> def token_lower(html_token):
    ...     return {'token_lower': html_token.token.lower()}

    >>> def token_isupper(html_token):
    ...     return {'isupper': html_token.token.isupper()}


Token feature function must return a dictionary with a
{feature_name: feature_value} mapping. The results of individual
feature functions are merged into a single dictionary.

Second type of feature function is a "global" feature function.
Global feature functions also take a single argument: a list of
``(html_token, merged_feature_dict)`` tuples. This argument contains
all tokens from this document and all features extracted by token
feature functions.

Global feature functions should modify feature dicts inplace. They are applied
sequentially; subsequent global feature functions get
updated ``merged_feature_dict``\s.

There are some predefined feature functions in ``webstruct.features`` package.

To extract features from a list of HtmlTokens, pass feature functions
to ``HtmlFeatureExtractor`` constructor and then call its ``transform()``
method::

    >>> from webstruct import HtmlFeatureExtractor
    >>> from webstruct.features import token_shape
    >>> feature_extractor = HtmlFeatureExtractor(
    ...     token_features = [token_lower, token_shape],
    ...     global_features = [],
    ... )
    >>> feature_dicts = feature_extractor.transform(html_tokens)


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

Combining Results of NER Subsystems
-----------------------------------

TODO: this is not implemented

Sequence tagging algorithms like CRF often have O(N^2) time and memory
complexity regarding the number of possible out tags. That's why it is often
a good idea not to try to predict all tags at the same time, but to split
a NER system into several smaller independent NER subsystems and merge the
results after prediction.
