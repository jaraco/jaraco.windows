#!/usr/bin/env python

# $Id$

import ctypes

def ensure_unicode(param):
	try:
		param = ctypes.create_unicode_buffer(param)
	except TypeError:
		pass # just return the param as is
	return param
