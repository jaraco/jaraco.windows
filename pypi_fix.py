import os
import sys

# a quick little fix for PyPI
if sys.platform in ('win32',):
	if not os.environ.has_key('HOME'):
		drivepath = map(os.environ.get, ('HOMEDRIVE', 'HOMEPATH'))
		os.environ['HOME'] = os.path.join(*drivepath)

