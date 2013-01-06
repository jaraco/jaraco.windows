# -*- coding: utf-8 -*-

import jaraco.windows.clipboard as wc

def test_unicode_clipboard():
	wc.set_unicode_text('foo'*100)
	assert wc.get_unicode_text() == u'foo'*100
	wc.set_unicode_text(u'☃')
	assert wc.get_unicode_text() == u'☃'
