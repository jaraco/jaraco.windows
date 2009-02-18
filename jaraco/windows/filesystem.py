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
	is_directory = options.directory or os.path.isdir(target)
	handle_nonzero_success(CreateSymbolicLink(link, target, is_directory))
	sys.stdout.write("Symbolic link created: %(link)s --> %(target)s\n" % vars())