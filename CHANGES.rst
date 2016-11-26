Changes
=======

0.4 (2016-11-26)
----------------

* sklearn-crfsuite_ is used as a CRFsuite wrapper, CRFsuiteCRF class
  is removed;
* comments are preserved in HTML trees because recent Firefox puts
  ``<base>`` tags to a comment when saving pages, and this affects
  WebAnnotator;
* fixed 'dont_penalize' argument of webstruct.NER.extract_groups_from_url;
* new webstruct.model.extract_entity_groups utility function;
* HtmlTokenizer and HtmlToken are modev to their own module
  (webstruct.html_tokenizer);
* test improvements;

.. _sklearn-crfsuite: https://github.com/TeamHG-Memex/sklearn-crfsuite

0.3 (2016-09-19)
----------------

There are many changes from previous version; API is changes,
Python 3 is supported, better gazetteers upport, CRFsuite support, etc.
