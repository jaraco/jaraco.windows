#!/usr/bin/env python

import os
import sys
from ctypes import Structure, windll
from ctypes.wintypes import BOOLEAN, LPWSTR, DWORD
from jaraco.windows.error import handle_nonzero_success

CreateSymbolicLink = windll.kernel32.CreateSymbolicLinkW
CreateSymbolicLink.argtypes = (
	LPWSTR,
	LPWSTR,
	DWORD,
	)
CreateSymbolicLink.restype = BOOLEAN

def mklink():
	"""
	Like cmd.exe's mklink except it will infer directory status of the
	target.
	"""
	from optparse import OptionParser
	parser = OptionParser(usage="usage: %prog [options] link target")
	parser.add_option('-d', '--directory',
		help="Target is a directory (only necessary if not present)",
		action="store_true")
	options, args = parser.parse_args()
	try:
		link, target = args
	except ValueError:
		parser.error("incorrect number of arguments")
	symlink(link, target, options.directory)
	sys.stdout.write("Symbolic link created: %(link)s --> %(target)s\n" % vars())

def symlink(link, target, target_is_directory = False):
	"""
	An implementation of os.symlink for Windows (Vista and greater)
	"""
	target_is_directory = target_is_directory or os.path.isdir(target)
	handle_nonzero_success(CreateSymbolicLink(link, target, target_is_directory))