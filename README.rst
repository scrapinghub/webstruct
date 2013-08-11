WebStruct
=========

This repository contains two different libraries for extracting contact
information from HTML pages + training data.

* block_model - extracts contact information from HTML pages;
  works on HTML "block" level; uses CRFSuite_ CRF implementation
  (via pyCRFsuite_).
* token_model - extracts contact information from HTML pages;
  works on word level; uses Wapiti_ CRF implementation.
* webstruct_data - annotated training/dev data (currently for token_model).

.. _Wapiti: http://wapiti.limsi.fr/
.. _CRFsuite: http://www.chokkan.org/software/crfsuite/
.. _pyCRFsuite: https://github.com/jakevdp/pyCRFsuite

See README files inside these folders for more info.