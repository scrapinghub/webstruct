# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import lxml.html
from webstruct import WebAnnotatorLoader
from webstruct import HtmlTokenizer


def test_wa_loader():
    ld = WebAnnotatorLoader()
    tree = ld.load(os.path.join(os.path.dirname(__file__), 'data', 'wa1.html'))
    res = lxml.html.tostring(tree)
    assert "<p> __START_ORG__ Scrapinghub __END_ORG__  has an <b>office</b> in  __START_CITY__ Montevideo __END_CITY__ </p>" in res, res
    assert "wa-" not in res, res
    assert "WA-" not in res, res


def test_wa_loader_with_known_entities():

    loader = WebAnnotatorLoader(known_entities={'ORG'})
    html = b"<html><body><p><span wa-subtypes='' wa-id='227' wa-type='ORG' class='WebAnnotator_org'>Scrapinghub</span> has an <b>office</b> in <span wa-subtypes='' wa-id='228' wa-type='CITY' class='WebAnnotator_org'>Montevideo</span></p></body></html>"
    tree = loader.loadbytes(html)
    res = lxml.html.tostring(tree)
    assert '<html><body><p> __START_ORG__ Scrapinghub __END_ORG__  has an <b>office</b> in Montevideo</p></body></html>' in res


def _assert_entities(fragment, known_entities, expected):

    ld = WebAnnotatorLoader(known_entities=known_entities)
    tree = ld.loadbytes(fragment)
    tokenizer = HtmlTokenizer()

    html_tokens, tags = tokenizer.tokenize_single(tree)
    tokens = [html_token.token for html_token in html_tokens]
    assert expected == dict([(token, tag) for token, tag in zip(tokens, tags) if tag != 'O'])

def test_wa_nested_fragment():
    fragment = """
<div class="copyright">Copyright Â© 2013 <span style="color: rgb(0, 0, 0); background-color: rgb(255, 0, 0); text-decoration: none;" wa-subtypes="" wa-id="227" wa-type="org" class="WebAnnotator_org">Weatherseal Spray Foam.</span> All Rights Reserved.<br>
Website Designed by <a wa_temp_href="http://www.western-webs.com" target="_blank" title="www.western-webs.com">Western-Webs</a>,
                <a wa_temp_href="http://tuam.galway-ireland.ie" target="_blank" title="http://tuam.galway-ireland.ie"><span style="color: rgb(0, 0, 0); background-color: rgb(51, 204, 255); text-decoration: none;" wa-subtypes="" wa-id="2010" wa-type="city" class="WebAnnotator_city"><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2011" wa-type="addr" class="WebAnnotator_addr">Tuam</span></span></a><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2011" wa-type="addr" class="WebAnnotator_addr">,
                </span><a wa_temp_href="http://www.galway-ireland.ie" target="_blank" title="www.galway-ireland.ie/"><span style="color: rgb(0, 0, 0); background-color: rgb(255, 0, 0); text-decoration: none;" wa-subtypes="" wa-id="2009" wa-type="state" class="WebAnnotator_state"><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2011" wa-type="addr" class="WebAnnotator_addr">County Galway</span></span></a><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2011" wa-type="addr" class="WebAnnotator_addr">,</span>
                <a wa_temp_href="http://www.ebookireland.com" target="_blank" title="www.ebookireland.com"><span style="color: rgb(0, 0, 0); background-color: rgb(255, 153, 0); text-decoration: none;" wa-subtypes="" wa-id="2008" wa-type="country" class="WebAnnotator_country"><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2011" wa-type="addr" class="WebAnnotator_addr"> Ireland</span></span></a></div>
"""
    expected1 = {'Tuam': 'B-city', 'County': 'B-state', 'Galway': 'I-state', 'Ireland': 'B-country'}
    expected2 = {'Tuam': 'B-addr', 'County': 'I-addr', 'Galway': 'I-addr', 'Ireland': 'I-addr'}

    _assert_entities(fragment, {'city', 'state', 'country', 'street'}, expected1)
    _assert_entities(fragment, {'addr'}, expected2)

    # same as fragment but labeled in different order with WA
    fragment2 = """
    <div class="copyright">Copyright Â© 2013 <span style="color: rgb(0, 0, 0); background-color: rgb(255, 0, 0); text-decoration: none;" wa-subtypes="" wa-id="227" wa-type="org" class="WebAnnotator_org">Weatherseal Spray Foam.</span> All Rights Reserved.<br>
Website Designed by <a wa_temp_href="http://www.western-webs.com" target="_blank" title="www.western-webs.com">Western-Webs</a>,
                <a wa_temp_href="http://tuam.galway-ireland.ie" target="_blank" title="http://tuam.galway-ireland.ie"><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2012" wa-type="addr" class="WebAnnotator_addr"><span style="color: rgb(0, 0, 0); background-color: rgb(51, 204, 255); text-decoration: none;" wa-subtypes="" wa-id="2013" wa-type="city" class="WebAnnotator_city">Tuam</span></span></a><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2012" wa-type="addr" class="WebAnnotator_addr">,
<span style="color: rgb(0, 0, 0); background-color: rgb(255, 0, 0); text-decoration: none;" wa-subtypes="" wa-id="2014" wa-type="state" class="WebAnnotator_state">                </span></span><a wa_temp_href="http://www.galway-ireland.ie" target="_blank" title="www.galway-ireland.ie/"><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2012" wa-type="addr" class="WebAnnotator_addr"><span style="color: rgb(0, 0, 0); background-color: rgb(255, 0, 0); text-decoration: none;" wa-subtypes="" wa-id="2014" wa-type="state" class="WebAnnotator_state">County Galway</span></span></a><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2012" wa-type="addr" class="WebAnnotator_addr">,</span>
                <a wa_temp_href="http://www.ebookireland.com" target="_blank" title="www.ebookireland.com"><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2012" wa-type="addr" class="WebAnnotator_addr"><span style="color:#000000; background-color:#FF9900;" wa-subtypes="" wa-id="2015" wa-type="country" class="WebAnnotator_country"> Ireland</span></span></a></div>"""

    _assert_entities(fragment2, {'city', 'state', 'country', 'street'}, expected1)
    _assert_entities(fragment2, {'addr'}, expected2)
