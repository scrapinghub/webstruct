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
* convert these features to the format sequence labelling toolikits accept
  (only Wapiti_ CRF toolkit support it built-in at the moment, but helpers
  for other toolkits like CRFSuite_ and seqlearn_ are planned).

Unlike most NER systems, webstruct works on HTML data, not on text data.
This allows to easily use HTML structure as features, and also
(potentially, not implemented at the moment) to to embed annotation
results back into HTML.

.. _GeoNames: http://www.geonames.org/
.. _wapiti: http://wapiti.limsi.fr
.. _CRFSuite: http://www.chokkan.org/software/crfsuite/
.. _seqlearn: https://github.com/larsmans/seqlearn
.. _WebAnnotator: https://github.com/xtannier/WebAnnotator
.. _GATE: http://gate.ac.uk/


