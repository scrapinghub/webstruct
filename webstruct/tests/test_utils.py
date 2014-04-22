# -*- coding: utf-8 -*-
from __future__ import absolute_import
from webstruct.utils import human_sorted


def test_human_sorted():
    assert human_sorted(['5', '10', '7', '100']) == ['5', '7', '10', '100']
    assert human_sorted(['foo1', 'foo10', 'foo2']) == ['foo1', 'foo2', 'foo10']
