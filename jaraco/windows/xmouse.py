#!python

# $Id$

import sys
import ctypes
import ctypes.wintypes
from jaraco.windows.error import WindowsError

"""
Usage: %s {enable, disable, toggle}
"""

SystemParametersInfo = ctypes.windll.user32.SystemParametersInfoW
SystemParametersInfo.argtypes = (
	ctypes.wintypes.UINT,
	ctypes.wintypes.UINT,
	ctypes.c_void_p,
	ctypes.wintypes.UINT,
	)

SPI_GETACTIVEWINDOWTRACKING = 0x1000
SPI_SETACTIVEWINDOWTRACKING = 0x1001

set_constant = SPI_SETACTIVEWINDOWTRACKING
get_constant = SPI_GETACTIVEWINDOWTRACKING

def handle_result(result):
	if result == 0:
		raise WindowsError()

def set(value):
	handle_result(
		SystemParametersInfo(
			set_constant, 0, ctypes.cast(value, ctypes.c_void_p), 0
	)	)

def get():
	value = ctypes.wintypes.BOOL()
	handle_result(
		SystemParametersInfo(get_constant, 0, ctypes.byref(value), 0)
	)
	return bool(value)

def enable():
	print "enabling xmouse"
	set(True)
	
def disable():
	print "disabling xmouse"
	set(False)

def toggle():
	value = get()
	print "xmouse: %s -> %s" % (value, not value)
	set(not value)

def show():
	print "xmouse: %s" % get()

def run():
	try:
		action = sys.argv[1]
	except IndexError:
		action = 'toggle'

	try:
		globals()[action]()
	except KeyError:
		print >> sys.stderr, usage

if __name__ == '__main__':
	run()