# -*- coding: utf-8 -*-
from __future__ import absolute_import
import lxml.html
from webstruct import WebAnnotatorLoader
from webstruct import HtmlTokenizer

HTML = b"""
<html><head>
<meta http-equiv="content-type" content="text/html; charset=windows-1252"></head><body onbeforeunload=""><p><span style="" wa-subtypes="" wa-id="8" wa-type="ORG" class="WebAnnotator_ORG">Scrapin</span><span style="" wa-subtypes="" wa-id="8" wa-type="ORG" class="WebAnnotator_ORG">ghub</span> has an <b>office</b> in <span style="" wa-subtypes="" wa-id="9" wa-type="CITY" class="WebAnnotator_CITY">Montevideo</span></p>
</body><wa-color id="WA-color-0" bg="#33CCFF" fg="#000000" class="WebAnnotator_ORG" type="ORG"></wa-color><wa-color id="WA-color-1" bg="#FF0000" fg="#000000" class="WebAnnotator_PER" type="PER"></wa-color><wa-color id="WA-color-2" bg="#33FF33" fg="#000000" class="WebAnnotator_FUNC" type="FUNC"></wa-color><wa-color id="WA-color-3" bg="#CC66CC" fg="#000000" class="WebAnnotator_TEL" type="TEL"></wa-color><wa-color id="WA-color-4" bg="#FF9900" fg="#000000" class="WebAnnotator_FAX" type="FAX"></wa-color><wa-color id="WA-color-5" bg="#99FFFF" fg="#000000" class="WebAnnotator_EMAIL" type="EMAIL"></wa-color><wa-color id="WA-color-6" bg="#FF6666" fg="#000000" class="WebAnnotator_HOURS" type="HOURS"></wa-color><wa-color id="WA-color-7" bg="#66FF99" fg="#000000" class="WebAnnotator_SUBJ" type="SUBJ"></wa-color><wa-color id="WA-color-8" bg="#3333FF" fg="#FFFFFF" class="WebAnnotator_STREET" type="STREET"></wa-color><wa-color id="WA-color-9" bg="#660000" fg="#FFFFFF" class="WebAnnotator_CITY" type="CITY"></wa-color><wa-color id="WA-color-10" bg="#006600" fg="#FFFFFF" class="WebAnnotator_STATE" type="STATE"></wa-color><wa-color id="WA-color-11" bg="#663366" fg="#FFFFFF" class="WebAnnotator_ZIPCODE" type="ZIPCODE"></wa-color><wa-color id="WA-color-12" bg="#993300" fg="#FFFFFF" class="WebAnnotator_COUNTRY" type="COUNTRY"></wa-color></html>
"""

def test_wa_loader():
    ld = WebAnnotatorLoader(known_tags=('ORG', 'CITY'))
    tree = ld.loadbytes(HTML)
    res = lxml.html.tostring(tree)
    assert "<p> __START_ORG__ Scrapinghub __END_ORG__  has an <b>office</b> in  __START_CITY__ Montevideo __END_CITY__ </p>" in res
    assert "wa-" not in res, res
    assert "WA-" not in res, res

def _assert_entities(fragment, known_tags, expected):

    ld = WebAnnotatorLoader(known_tags=known_tags)
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

    _assert_entities(fragment, ('city', 'state', 'country', 'street'), expected1)
    _assert_entities(fragment, ('addr'), expected2)

    # same as fragment but labeled in different order with WA
    fragment2 = """
    <div class="copyright">Copyright Â© 2013 <span style="color: rgb(0, 0, 0); background-color: rgb(255, 0, 0); text-decoration: none;" wa-subtypes="" wa-id="227" wa-type="org" class="WebAnnotator_org">Weatherseal Spray Foam.</span> All Rights Reserved.<br>
Website Designed by <a wa_temp_href="http://www.western-webs.com" target="_blank" title="www.western-webs.com">Western-Webs</a>,
                <a wa_temp_href="http://tuam.galway-ireland.ie" target="_blank" title="http://tuam.galway-ireland.ie"><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2012" wa-type="addr" class="WebAnnotator_addr"><span style="color: rgb(0, 0, 0); background-color: rgb(51, 204, 255); text-decoration: none;" wa-subtypes="" wa-id="2013" wa-type="city" class="WebAnnotator_city">Tuam</span></span></a><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2012" wa-type="addr" class="WebAnnotator_addr">,
<span style="color: rgb(0, 0, 0); background-color: rgb(255, 0, 0); text-decoration: none;" wa-subtypes="" wa-id="2014" wa-type="state" class="WebAnnotator_state">                </span></span><a wa_temp_href="http://www.galway-ireland.ie" target="_blank" title="www.galway-ireland.ie/"><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2012" wa-type="addr" class="WebAnnotator_addr"><span style="color: rgb(0, 0, 0); background-color: rgb(255, 0, 0); text-decoration: none;" wa-subtypes="" wa-id="2014" wa-type="state" class="WebAnnotator_state">County Galway</span></span></a><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2012" wa-type="addr" class="WebAnnotator_addr">,</span>
                <a wa_temp_href="http://www.ebookireland.com" target="_blank" title="www.ebookireland.com"><span style="color: rgb(255, 255, 255); background-color: rgb(102, 51, 102); text-decoration: none;" wa-subtypes="" wa-id="2012" wa-type="addr" class="WebAnnotator_addr"><span style="color:#000000; background-color:#FF9900;" wa-subtypes="" wa-id="2015" wa-type="country" class="WebAnnotator_country"> Ireland</span></span></a></div>"""

    _assert_entities(fragment2, ('city', 'state', 'country', 'street'), expected1)
    _assert_entities(fragment2, ('addr'), expected2)