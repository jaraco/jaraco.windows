# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import jaraco.windows.clipboard as wc

def test_unicode_clipboard():
	wc.set_unicode_text('foo'*100)
	assert wc.get_unicode_text() == 'foo'*100
	wc.set_unicode_text('☃')
	assert wc.get_unicode_text() == '☃'
