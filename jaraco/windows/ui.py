#!/usr/bin/env python

# $Id$

import ctypes

def fix_param(param):
	import sys
	if 'AMD64' in sys.version and isinstance(param, basestring) and not isinstance(param, unicode):
		param = unicode(param)
	return param

def MessageBox(text, caption=None, handle=None, type=None):
	text = fix_param(text)
	caption = fix_param(caption)
	ctypes.windll.user32.MessageBoxW(handle, text, caption, type)

def test_normal_character_parameter():
	MessageBox(u'simple message', u'message should look like this')

def show_narrow_character_handling_issue():
	# disable fix_param to illustrate the issue
	global fix_param
	orig_fix_param = fix_param
	fix_param = lambda p: p
	MessageBox('simple message', u'but instead looks like this')
	fix_param = orig_fix_param

if __name__ == '__main__':
	test_normal_character_parameter()
	show_narrow_character_handling_issue()