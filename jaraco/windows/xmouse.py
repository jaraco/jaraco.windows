#!python

# $Id$

import sys
import ctypes
import ctypes.wintypes
from jaraco.windows.error import handle_nonzero_success

SystemParametersInfo = ctypes.windll.user32.SystemParametersInfoW
SystemParametersInfo.argtypes = (
	ctypes.wintypes.UINT,
	ctypes.wintypes.UINT,
	ctypes.c_void_p,
	ctypes.wintypes.UINT,
	)

SPI_GETACTIVEWINDOWTRACKING = 0x1000
SPI_SETACTIVEWINDOWTRACKING = 0x1001
SPI_GETACTIVEWNDTRKTIMEOUT = 0x2002
SPI_SETACTIVEWNDTRKTIMEOUT = 0x2003
set_constant = SPI_SETACTIVEWINDOWTRACKING
get_constant = SPI_GETACTIVEWINDOWTRACKING

def set(value):
	handle_nonzero_success(
		SystemParametersInfo(
			set_constant, 0, ctypes.cast(value, ctypes.c_void_p), 0
	)	)
	if value and hasattr(options, 'delay'):
		set_delay(options.delay)

def get():
	value = ctypes.wintypes.BOOL()
	handle_nonzero_success(
		SystemParametersInfo(get_constant, 0, ctypes.byref(value), 0)
	)
	return bool(value)

def set_delay(milliseconds):
	handle_nonzero_success(
		SystemParametersInfo(
			SPI_SETACTIVEWNDTRKTIMEOUT,
			0,
			ctypes.cast(milliseconds, ctypes.c_void_p),
			0,
	)	)

def get_delay():
	value = ctypes.wintypes.DWORD()
	handle_nonzero_success(
		SystemParametersInfo(
			SPI_GETACTIVEWNDTRKTIMEOUT,
			0,
			ctypes.byref(value),
			0,
			)
		)
	return int(value.value)

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
	enabled = get()
	delay = get_delay()
	msg = "xmouse: {enabled} (delay {delay}ms)".format(**vars())
	print(msg)

def get_options():
	"""
	%prog [<command>] [<options>]
	
		command: show, enable, disable, toggle (defaults to toggle)
	"""
	from textwrap import dedent
	usage = dedent(get_options.__doc__).strip()
	from optparse import OptionParser
	parser = OptionParser(usage=usage)
	parser.add_option('-d', '--delay', type="int",
		help="Delay in milliseconds for active window tracking")
	options, args = parser.parse_args()
	try:
		options.action = args.pop()
	except IndexError:
		options.action = 'toggle'
	if not options.action in globals():
		parser.error("Unrecognized command {0}".format(options.action))
	if args: parser.error("Too many arguments specified")
	return options

def run():
	global options
	options = get_options()
	globals()[options.action]()

if __name__ == '__main__':
	run()