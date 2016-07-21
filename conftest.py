import platform
import os


collect_ignore = []


try:
	__import__('win32api')
except ImportError:
	# pywin32 isn't available, so avoid import errors
	collect_ignore += [
		'jaraco/windows/eventlog.py',
		'jaraco/windows/services.py',
	]


if platform.system() != 'Windows':
	"""
	Ignore everything but 'test_root' on non-Windows systems
	"""
	collect_ignore = [
		os.path.join(root, filename)
		for root, dirs, files in os.walk('.')
		for filename in files
		if filename.endswith('.py')
		and not filename.startswith('test_root')
	]
