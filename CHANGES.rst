Changes
=======

0.5 (2017-05-10)
----------------

* webstruct.model.NER now uses ``requests`` library to make HTTP requests;
* changed default headers used by webstruct.model.NER;
* new ``webstruct.infer_domain`` module useful for proper cross-validation;
* webstruct.webannotator.to_webannotator got an option to add ``<base>``
  tag with the original URL to the page;
* fixed a warning in webstruct.gazetteers.geonames.read_geonames;
* add a few more country names to countries.txt list.

0.4.1 (2016-11-28)
------------------

* fixed a bug in NER.extract().

0.4 (2016-11-26)
----------------

* sklearn-crfsuite_ is used as a CRFsuite wrapper, CRFsuiteCRF class
  is removed;
* comments are preserved in HTML trees because recent Firefox puts
  ``<base>`` tags to a comment when saving pages, and this affects
  WebAnnotator;
* fixed 'dont_penalize' argument of webstruct.NER.extract_groups_from_url;
* new webstruct.model.extract_entity_groups utility function;
* HtmlTokenizer and HtmlToken are moved to their own module
  (webstruct.html_tokenizer);
* test improvements;

.. _sklearn-crfsuite: https://github.com/TeamHG-Memex/sklearn-crfsuite

0.3 (2016-09-19)
----------------

There are many changes from previous version: API is changed,
Python 3 is supported, better gazetteers support, CRFsuite support, etc.
