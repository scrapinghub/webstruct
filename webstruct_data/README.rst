Development data for WebStruct
==============================

This package contains development (train/test) data for WebStruct
and some utilities for working with it.

What is annotated
-----------------

Cleaned HTML pages are annotated. Cleaning is conservative: only
script/style/embed tags are removed.

If we annotate other blocks of data (e.g. text extracted from HTML
page, or page regions) then the training/test data could become
obsolete if prediction pipeline changes. If full HTML pages are
annotated, data could be used regardless of prediction algorithm.

NER Label Set
-------------

Possible labels are:

    * ORG
    * PER
    * TEL
    * FAX
    * EMAIL
    * STREET
    * CITY
    * STATE
    * ZIPCODE
    * COUNTRY
    * O

EMAIL (and maybe TEL, FAX and ZIPCODE) could be easy to extract using
regexpes, but they are still included in label set because
it could be much easier to combine extracted data to records this way
(i.e. to determine that this email belongs to this person).

Sometimes customers want STREET1 / STREET2 separation.
This separation looks rather arbitrary, so STREET1 / STREET2 tags
are not included.

For non-US addresses province, county, etc. should be marked as STATE.

'O' label means 'token is not a part of named entity' (in other words,
'token is outside entity').

Ideas for extra labels:

    * P.O. box / post address
    * Facility/building
    * Department/office/branch

Annotation Guidelines
---------------------

Website vendors shouldn't be annotated as ORG.

Office/department/branch names should be annotated as ORG.

Facility/building and P.O. box / post address should be a part of STREET.

"Fancy" phones should be annotated as a single entity, e.g. ::

    <TEL>1-800 ROYAL 5-3 (1-800-769-2553)</TEL>
