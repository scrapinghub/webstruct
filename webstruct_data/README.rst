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

    * ORG - organization, company name - e.g. "University of Massachusetts Amherst"
    * PER - person name, e.g. "John Doe"
    * FUNC - person's function, title, role, etc. - e.g. "Director" or "Sales"
    * TEL - phone
    * FAX - fax
    * EMAIL - email
    * HOURS - open hours, e.g. "Monday-Friday, 10AM - 3PM PST"
    * SUBJ - subject of the contact data, e.g. "Admissions" or "Customer Service"
    * STREET - street address
    * CITY - city
    * STATE - state, province, county, etc.
    * ZIPCODE - zipcode, postcode
    * COUNTRY - country
    * O - "outside entity"

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
    * Open Hours


Annotation Guidelines
---------------------

The distinction between SUBJ and ORG is somewhat unclear.
If "subject" of the contact data is an organization, label it as ORG,
if not then label it as SUBJ. "ORG + contact data" should be unambiguous;
"SUBJ + contact data" should probably require ORG for understanding.
Example: "Indian Office" is most likely SUBJ, but "Food Corp. Indian Office"
is ORG.

If something is a part of mailing address, it is unlikely SUBJ.

These rules are not strict; prefer consistency within a single document, e.g.
if some of the office names are unambigous and some are not, mark them
all as SUBJ or ORG.


Do not annotate website vendors as ORG (leave them unannotated).
Do not annotate unrelated persons (e.g. review authors) as PER.

Facility/building and P.O. box / post address should be a part of STREET.

"Fancy" phones should be annotated as a single entity, e.g. ::

    <TEL>1-800 ROYAL 5-3 (1-800-769-2553)</TEL>
