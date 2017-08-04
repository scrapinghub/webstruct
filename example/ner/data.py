#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from itertools import chain
from pathlib import Path
from typing import List, Tuple, Any, Set

import webstruct

from .utils import pages_progress


WEBSTRUCT_DATA = Path(__name__).parent / ".." / "webstruct_data"
GAZETTEER_DATA = Path(__name__).parent / "_data"


KNOWN_ENTITIES = [
    'ORG', 'TEL', 'FAX', 'HOURS',
    'STREET', 'CITY', 'STATE', 'ZIPCODE', 'COUNTRY',
    'EMAIL', 'PER', 'FUNC', 'SUBJ'
]
CONTACT_ENTITIES = [
    'ORG', 'TEL', 'FAX', 'HOURS',
    'STREET', 'CITY', 'STATE', 'ZIPCODE', 'COUNTRY',
    'SUBJ',
]
ADDRESS_ENTITIES = [
    'STREET', 'CITY', 'STATE', 'ZIPCODE', 'COUNTRY',
]


def load_webstruct_data() -> List:
    """
    Load training data from webstruct repository.

    It is a mess: there are two folders which have OK data, one
    is stored in WebAnnotator format, another is stored in GATE format.
    """
    wa_loader = webstruct.WebAnnotatorLoader(known_entities=KNOWN_ENTITIES)
    gate_loader = webstruct.GateLoader(known_entities=KNOWN_ENTITIES)

    trees1 = webstruct.load_trees(
        str(WEBSTRUCT_DATA / "corpus/business_pages/wa/*.html"),
        loader=wa_loader,
    )

    trees2 = webstruct.load_trees(
        str(WEBSTRUCT_DATA / "corpus/us_contact_pages/annotated/*.xml"),
        loader=gate_loader
    )
    trees = chain(trees1, trees2)
    return list(pages_progress(trees, desc="Loading webstruct default annotated data"))


def load_countries() -> Set[str]:
    countries_path = WEBSTRUCT_DATA / 'gazetteers/countries/countries.txt'
    return set(countries_path.read_text().splitlines())
