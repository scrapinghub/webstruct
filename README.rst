Contact extraction library
==========================

This package contains a library for extracting contact information from
HTML pages.

Installation
------------

Clone the repository, then install package requirements
(package requires lxml, scikit-learn and python-wapiti)::

    $ pip install -r requirements.txt

then install package itself::

    $ python setup.py install


Usage
-----

::

    >>> import wapiti
    >>> from webstruct_token.wapiti import WapitiChunker
    >>> from sklearn.externals import joblib

Load trained model ('wfe.joblib' and 'model.wapiti' files must exitsts)::

    >>> feature_encoder = joblib.load('wfe.joblib')
    >>> wapiti_model = wapiti.Model(model='model.wapiti')
    >>> ner = WapitiChunker(wapiti_model, feature_encoder)

Get a HTML page somewhere::

    >>> import requests
    >>> page = requests.get(some_url)

and extract information::

    >>> for text, label in ner.transform(page.text, page.encoding):
    ...     if label != 'O':
    ...         print("%6s %s" % (label, text))
         TEL 800-4-Altman ( 425-8626 )
       EMAIL sales@altmanlighting.com
         ORG Altman Lighting Co. Inc.
      STREET 57 Alexander Street
        CITY Yonkers
       STATE NY
     ZIPCODE 10701
         TEL 1-800-4-ALTMAN ( 425-8626 )

Training
--------

Model should be trained before usage.
See '../notebooks/train-token-model.ipynb' IPython_ notebook for an example.

Unit Testing
------------

Make sure nose_ is installed, then run ``runtests.sh`` script.

.. _nose: https://github.com/nose-devs/nose
.. _IPython: https://github.com/ipython/ipython
