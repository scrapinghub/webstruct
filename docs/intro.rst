Webstruct
=========

Installation
------------

TODO

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
* convert these features to the format sequence labelling toolikits accept;
* use Wapiti_ CRF toolkit for entity extraction (helpers for other
  toolkits like CRFSuite_ and seqlearn_ are planned);
* group extracted entites using an unsupervised algorithm;
* embed annotation results back into HTML files (using WebAnnotator_ format),
  allowing to view them in a web browser and fix using visual tools.

Unlike most NER systems, webstruct works on HTML data, not only
on text data. This allows to define features that use HTML structure,
and also to embed annotation results back into HTML.


.. _GeoNames: http://www.geonames.org/
.. _wapiti: http://wapiti.limsi.fr
.. _CRFSuite: http://www.chokkan.org/software/crfsuite/
.. _seqlearn: https://github.com/larsmans/seqlearn
.. _WebAnnotator: https://github.com/xtannier/WebAnnotator
.. _GATE: http://gate.ac.uk/
