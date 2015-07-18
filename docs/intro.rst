Webstruct
=========

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
* convert these features to the format sequence labelling toolkits accept;
* use Wapiti_ or CRFSuite_ CRF toolkit for entity extraction (helpers for other
  toolkits like seqlearn_ are planned);
* group extracted entites using an unsupervised algorithm;
* embed annotation results back into HTML files (using WebAnnotator_ format),
  allowing to view them in a web browser and fix using visual tools.

Unlike most NER systems, webstruct works on HTML data, not only
on text data. This allows to define features that use HTML structure,
and also to embed annotation results back into HTML.

.. _GeoNames: http://www.geonames.org/
.. _CRFSuite: http://www.chokkan.org/software/crfsuite/
.. _GATE: http://gate.ac.uk/


Installation
------------

Webstruct requires Python 2.7 or Python 3.3+.

To install Webstruct, use pip::

    $ pip install webstruct

Webstruct depends on the following Python packages:

* lxml_ for parsing HTML;
* `scikit-learn`_ >= 0.14.

Note that these dependencies are not installed automatically
when ``pip install webstruct`` is executed.

There are also some optional dependencies:

* Webstruct has support for Wapiti_ sequence labelling toolkit;
  you'll need both the ``wapiti`` binary and `python-wapiti`_ wrapper
  (from github master) for the tutorial.
* For training data annotation you may use WebAnnotator_ Firefox extension.
* Code for preparing GeoNames gazetteers uses `marisa-trie`_ and `pandas`_.

.. _lxml: https://github.com/lxml/lxml
.. _scikit-learn: https://github.com/scikit-learn/scikit-learn
.. _seqlearn: https://github.com/larsmans/seqlearn
.. _python-wapiti: https://github.com/adsva/python-wapiti
.. _Wapiti: http://wapiti.limsi.fr
.. _WebAnnotator: https://github.com/xtannier/WebAnnotator
.. _marisa-trie: https://github.com/kmike/marisa-trie
.. _pandas: http://pandas.pydata.org/
