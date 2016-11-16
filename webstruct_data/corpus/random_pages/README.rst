Here are some random webpages for which model performed bad.

Cleaned data was produced by the following command::

    ./clean_html.py --out corpus/random_pages/cleaned corpus/random_pages/source/*.html

This cleaned data is annotated manually using GATE_ and then saved
to xml files inside 'annotated' folder. 'Save preserving format'
command is used for saving: this mean annotations are saved as custom
HTML tags, like ``<ORG>Microsoft</ORG>``.

FIXME: there are issues with annotation: schema is undocumented, and
some of the annotations are missing. E.g. names in page title are not
annotated. Another issue is that there are no <base> tags, so source
websites are unknown. This data should be converted to WebAnnotator
and cleaned up, or just removed.

.. _GATE: http://gate.ac.uk/
