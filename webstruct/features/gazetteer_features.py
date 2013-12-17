# -*- coding: utf-8 -*-
from __future__ import absolute_import
import csv
import dawg
import marisa_trie
from webstruct.utils import LongestMatch

def load_us_states(fn):
    res = {}
    with open(fn, 'rb') as f:
        reader = csv.DictReader(f)
        for row in reader:
            res[row['names'].decode('utf8')] = row['admin1_code'].decode('utf8')
    return res

firstnames_male = dawg.IntCompletionDAWG().load('/Users/kmike/svn/gazetteers/gazetteers/data/us_firstnames1990_male.intcdawg')
firstnames_female = dawg.IntCompletionDAWG().load('/Users/kmike/svn/gazetteers/gazetteers/data/us_firstnames1990_female.intcdawg')
lastnames = dawg.IntCompletionDAWG().load('/Users/kmike/svn/gazetteers/gazetteers/data/us_lastnames2000.intcdawg')

us_admin = marisa_trie.RecordTrie(str("2s 1s 5s 2s 3s")).load('/Users/kmike/svn/gazetteers/gazetteers/data/us_admin.marisa')
us_all = marisa_trie.RecordTrie(str("2s 1s 5s 2s 3s")).load('/Users/kmike/svn/gazetteers/gazetteers/data/us_all.marisa')
us_ppl = marisa_trie.RecordTrie(str("2s 1s 5s 2s 3s")).load('/Users/kmike/svn/gazetteers/gazetteers/data/us_ppl.marisa')
# us_states = marisa_trie.RecordTrie(str("2s 1s 5s 2s 3s")).load('/Users/kmike/svn/gazetteers/gazetteers/data/us_states.marisa')
us_states = load_us_states('/Users/kmike/svn/gazetteers/gazetteers/data/us_states.csv')
cities15000 = marisa_trie.RecordTrie(str("2s 1s 5s 2s 3s")).load('/Users/kmike/svn/gazetteers/gazetteers/data/cities15000.marisa')
cities5000 = marisa_trie.RecordTrie(str("2s 1s 5s 2s 3s")).load('/Users/kmike/svn/gazetteers/gazetteers/data/cities15000.marisa')


lm_states = LongestMatch(us_states)
lm_ppl = LongestMatch(us_ppl)
lm_cities15000 = LongestMatch(cities15000)
lm_cities5000 = LongestMatch(cities5000)


LASTNAMES_THRESHOLDS = [1000, 500, 250]
FIRSTNAMES_THRESHOLDS = [100, 20, 5]


def us_census(html_token):
    token = html_token.token.upper()
    male_cnt = firstnames_male.get(token, 0)
    female_cnt = firstnames_male.get(token, 0)
    lastname_cnt = lastnames.get(token, 0)

    res = {}

    for th in FIRSTNAMES_THRESHOLDS:
        res['firstname%s' % th] = male_cnt > th or female_cnt > th

    for th in LASTNAMES_THRESHOLDS:
        res['lastname%s' % th] = lastname_cnt > th

    for key, value in res.items():
        res[key+'_title'] = value and html_token.token.istitle()

    return res


def us_states_info(doc):
    token_strings = [tok.token for tok, feat in doc]
    for start, end, key in lm_states.find_ranges(token_strings):
        match = lm_states.known[key]
        doc[start][1]['B-US-STATE'] = True
        for idx in range(start+1, end):
            doc[idx][1]['I-US-STATE'] = True
        for idx in range(start, end):
            doc[idx][1]['US-STATE'] = True
            doc[idx][1]['_US-STATE-%s' % match] = True


def us_populated_places_info(doc):
    token_strings = [tok.token for tok, feat in doc]
    for start, end, key in lm_ppl.find_ranges(token_strings):

        doc[start][1]['B-US-PPL'] = True
        for idx in range(start+1, end):
            doc[idx][1]['I-US-PPL'] = True

        match = lm_ppl.known[key]
        for idx in range(start, end):
            doc[idx][1]['US-PPL'] = True
            for country, cls, cls2, state, county in match:
                doc[idx][1]['_US-STATE-%s' % state] = True
                # doc[idx][1]['US-COUNTY-%s'] = state


def cities15000_info(doc):
    token_strings = [tok.token for tok, feat in doc]
    for start, end, key in lm_cities15000.find_ranges(token_strings):

        doc[start][1]['B-CITY15000'] = True
        for idx in range(start+1, end):
            doc[idx][1]['I-CITY15000'] = True

        match = lm_cities15000.known[key]
        for idx in range(start, end):
            doc[idx][1]['CITY15000'] = True
            for country, cls, cls2, state, county in match:
                doc[idx][1]['_COUNTRY-%s' % country.strip()] = True
                # doc[idx][1]['GEONAMES-%s' % cls2.strip()] = True


def cities5000_info(doc):
    token_strings = [tok.token for tok, feat in doc]
    for start, end, key in lm_cities15000.find_ranges(token_strings):

        doc[start][1]['B-CITY5000'] = True
        for idx in range(start+1, end):
            doc[idx][1]['I-CITY5000'] = True

        match = lm_cities5000.known[key]
        for idx in range(start, end):
            doc[idx][1]['CITY5000'] = True
            for country, cls, cls2, state, county in match:
                doc[idx][1]['_COUNTRY-%s' % country.strip()] = True
