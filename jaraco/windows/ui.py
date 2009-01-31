#!/usr/bin/env python

# $Id$

import ctypes

def MessageBox(text, caption=None, handle=None, type=None):
	text = fix_param(text)
	caption = fix_param(caption)
	ctypes.windll.user32.MessageBoxW(handle, text, caption, type)

def fix_param(param):
	import sys
	is_64_bit = 'AMD64' in sys.version
	param_is_string = isinstance(param, basestring)
	param_is_not_unicode = not isinstance(param, unicode)
	if (
		#is_64_bit and # this is not a factor
		param_is_string and
		param_is_string
		):
		param = unicode(param)
	return param

def test_normal_character_parameter():
	MessageBox('simple message', u'message should look like this')

def show_narrow_character_handling_issue():
	# temporarily disable fix_param to illustrate the issue
	global fix_param
	orig_fix_param = fix_param
	fix_param = lambda p: p
	MessageBox('simple message', u'but instead looks like this')
	fix_param = orig_fix_param

if __name__ == '__main__':
	test_normal_character_parameter()
	show_narrow_character_handling_issue()