NER Framework for HTML data
===========================

This is a framework for creating machine-learning-based
NER systems that work on HTML data. Its goals:

1. parse annotations embedded in HTML document;
2. convert start/end annotation tags to IOB format;
3. transform HTML tree into a sequence of tokens;
4. extract features from HTML tokens;
5. TODO: convert these features to formats required by different
   sequence labelling toolkits (like Wapiti_, CRFSuite_ or seqlearn_);
6. TODO: combine results of several NER subsystems into a single annotation.

.. _wapiti: wapiti.limsi.fr
.. _CRFSuite: http://www.chokkan.org/software/crfsuite/
.. _seqlearn: https://github.com/larsmans/seqlearn

Annotation
----------

For training annotated data is needed. There are different tools
for annotating HTML; we support WebAnnotator_ and GATE_ annotation formats
(WebAnnotator_ is recommended).

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
are converted to IOB tag sequences and removed from token stream. IOB tags are
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

Example implementations::

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
updated ``merged_feature_dict``s.

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
