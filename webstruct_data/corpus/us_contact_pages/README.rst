Here are webpages collected by querying Google for
'contact us <organization_type> usa' queries, where <business type>
is 'restaurant', 'zoo', 'lawyer', 'car rental', 'church', 'clinic',
'pet store', 'plumber', 'bank', etc.

Cleaned data was produced by the following command::

    ./clean_html.py --out corpus/us_contact_pages/cleaned corpus/us_contact_pages/source/*.html

This cleaned data is annotated manually using GATE_ and then saved
to xml files inside 'annotated' folder. 'Save preserving format'
command is used for saving: this mean annotations are saved as custom
HTML tags, like ``<ORG>Microsoft</ORG>``.

.. _GATE: http://gate.ac.uk/
