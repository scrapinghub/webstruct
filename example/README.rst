Contact extraction using Webstruct
==================================

This folder contains code to train a model for contact and address
extraction. The result is a .joblib file with pickled webstruct.NER object.

Python packages from requirements.txt file are needed; install them using

::

    pip install -r requirements.txt

Currently the example requires Python 3.5+.

Training
--------

To train a model, first build gazetteers using built_gazetteers script::

    python3 -m ner.build_gazetteers

It will create "_data" folder with city/state geonames data. The script uses
several GBs or RAM.

To train a CRF model run::

    python3 -m ner.train

The model uses training data from opensource webstruct package
(mostly contact pages of US, CA and GB small business websites)
and provides 'ORG', 'TEL', 'FAX', 'HOURS', 'STREET', 'CITY', 'STATE',
'ZIPCODE', 'COUNTRY', and 'SUBJ' entities.

Script should produce "contact-extractor.joblib" file with a saved
webstruct.NER object and "crf-features.html" file with debugging
information about the model.

Usage
-----

To use the saved model code in this folder is not needed.
Make sure joblib, sklearn-crfsuite and webstruct are installed,
then load the model::

    import joblib
    ner = joblib.load('contact-extractor.joblib')
    print(ner.extract_groups_from_url('<some URL>'))

See https://webstruct.readthedocs.io/en/latest/ref/model.html#webstruct.model.NER
for the API.
