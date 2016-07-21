collect_ignore = []

try:
	__import__('win32api')
except ImportError:
	# pywin32 isn't available, so avoid import errors
	collect_ignore += [
		'jaraco/windows/eventlog.py',
		'jaraco/windows/services.py',
	]
