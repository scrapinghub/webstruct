Here are some random webpages for which model performed bad.

Cleaned data was produced by the following command::

    ./clean_html.py --out corpus/random_pages/cleaned corpus/random_pages/source/*.html

This cleaned data is annotated manually using GATE_ and then saved
to xml files inside 'annotated' folder. 'Save preserving format'
command is used for saving: this mean annotations are saved as custom
HTML tags, like ``<ORG>Microsoft</ORG>``.

.. _GATE: http://gate.ac.uk/
