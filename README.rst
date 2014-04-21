Webstruct
=========

Webstruct is a library for creating statistical NER_ systems that work
on HTML data, i.e. a library for building tools that extract named
entities (addresses, organization names, open hours, etc) from webpages.

Unlike most NER systems, webstruct works on HTML data, not only
on text data. This allows to define features that use HTML structure,
and also to embed annotation results back into HTML.

The license is MIT.

Read the docs_ for more info.

.. _docs: http://webstruct.readthedocs.org/en/latest/
.. _NER: http://en.wikipedia.org/wiki/Named-entity_recognition

Contributing
------------

* Source code: https://github.com/scrapinghub/webstruct
* Bug tracker: https://github.com/scrapinghub/webstruct/issues

To run tests, make sure nose_ is installed, then run ``runtests.sh`` script.

.. _nose: https://github.com/nose-devs/nose
