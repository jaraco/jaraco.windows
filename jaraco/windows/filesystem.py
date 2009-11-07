#!/usr/bin/env python

import os
import sys
import operator
from itertools import imap, ifilter, izip

from jaraco.windows.api.filesystem import *

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
	symlink(target, link, options.directory)
	sys.stdout.write("Symbolic link created: %(link)s --> %(target)s\n" % vars())

def symlink(target, link, target_is_directory = False):
	"""
	An implementation of os.symlink for Windows (Vista and greater)
	"""
	target_is_directory = target_is_directory or os.path.isdir(target)
	handle_nonzero_success(CreateSymbolicLink(link, target, target_is_directory))

def link(target, link):
	"""
	Establishes a hard link between an existing file and a new file.
	"""
	handle_nonzero_success(CreateHardLink(link, target, None))

def is_reparse_point(path):
	"""
	Determine if the given path is a reparse point.
	"""
	FILE_ATTRIBUTE_REPARSE_POINT = 0x400
	INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF
	res = GetFileAttributes(path)
	if res == INVALID_FILE_ATTRIBUTES: raise WindowsError()
	return bool(res & FILE_ATTRIBUTE_REPARSE_POINT)

def islink(path):
	"Determine if the given path is a symlink"
	return is_reparse_point(path) and is_symlink(path)

def is_symlink(path):
	"""
	Assuming path is a reparse point, determine if it's a symlink.
	"""
	return _is_symlink(next(find_files(path)))

def _is_symlink(find_data):
	return find_data.reserved[0] == IO_REPARSE_TAG_SYMLINK

def find_files(spec):
	"""
	A pythonic wrapper around the FindFirstFile/FindNextFile win32 api.
	
	>>> root_files = tuple(find_files(r'c:\*'))
	>>> len(root_files) > 1
	True
	>>> root_files[0].filename == root_files[1].filename
	False
	
	This test might fail on a non-standard installation
	>>> 'Windows' in (fd.filename for fd in root_files)
	True
	"""
	fd = WIN32_FIND_DATA()
	ERROR_NO_MORE_FILES = 0x12
	handle = FindFirstFile(spec, byref(fd))
	while True:
		if handle == INVALID_HANDLE_VALUE:
			raise WindowsError()
		yield fd
		fd = WIN32_FIND_DATA()
		res = FindNextFile(handle, byref(fd))
		if res == 0: # error
			error = WindowsError()
			if error.value == ERROR_NO_MORE_FILES:
				break
			else: raise error
	# todo: how to close handle when generator is destroyed?
	# hint: catch GeneratorExit
	windll.kernel32.FindClose(handle)

def get_final_path(path):
	"""
	For a given path, determine the ultimate location of that path.
	Useful for resolving symlink targets.
	This functions wraps the GetFinalPathNameByHandle from the Windows
	SDK.
	
	Note, this function fails if a handle cannot be obtained (such as
	for C:\Pagefile.sys on a stock windows system). Consider using
	trace_symlink_target instead.
	"""
	hFile = CreateFile(
		path,
		NULL, # desired access
		FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE, # share mode
		LPSECURITY_ATTRIBUTES(), # NULL pointer
		OPEN_EXISTING,
		FILE_FLAG_BACKUP_SEMANTICS,
		NULL,
		)

	if hFile == INVALID_HANDLE_VALUE:
		raise WindowsError()

	VOLUME_NAME_DOS = 0

	buf_size = GetFinalPathNameByHandle(hFile, LPWSTR(), 0, VOLUME_NAME_DOS)
	handle_nonzero_success(buf_size)
	buf = create_unicode_buffer(buf_size)
	result_length = GetFinalPathNameByHandle(hFile, buf, len(buf), VOLUME_NAME_DOS)

	assert result_length < len(buf)
	handle_nonzero_success(result_length)
	handle_nonzero_success(CloseHandle(hFile))

	return buf[:result_length]

def GetBinaryType(filepath):
	res = DWORD()
	handle_nonzero_success(_GetBinaryType(filepath, res))
	return res

def _make_null_terminated_list(obs):
	obs = _makelist(obs)
	if obs is None: return
	return u'\x00'.join(obs) + u'\x00\x00'

def _makelist(ob):
	if ob is None: return
	if not isinstance(ob, (list, tuple, set)):
		return [ob]
	return ob

def SHFileOperation(operation, from_, to=None, flags=[]):
	flags = reduce(operator.or_, flags, 0)
	from_ = _make_null_terminated_list(from_)
	to = _make_null_terminated_list(to)
	params = SHFILEOPSTRUCT(0, operation, from_, to, flags)
	res = _SHFileOperation(params)
	if res != 0:
		raise RuntimeError("SHFileOperation returned %d" % res)

def join(*paths):
	r"""
	Wrapper around os.path.join that works with Windows drive letters.
	
	>>> join('d:\\foo', '\\bar')
	'd:\\bar'
	"""
	paths_with_drives = imap(os.path.splitdrive, paths)
	drives, paths = zip(*paths_with_drives)
	# the drive we care about is the last one in the list
	drive = next(ifilter(None, reversed(drives)), '')
	return os.path.join(drive, os.path.join(*paths))
	
def findpath(target, start=os.path.curdir):
	r"""
	Find a path from start to target where target is relative to start.
	
	>>> orig_wd = os.getcwd()
	>>> os.chdir('c:\\windows') # so we know what the working directory is

	>>> findpath('d:\\')
	'd:\\'

	>>> findpath('d:\\', 'c:\\windows')
	'd:\\'

	>>> findpath('\\bar', 'd:\\')
	'd:\\bar'

	>>> findpath('\\bar', 'd:\\foo') # fails with '\\bar'
	'd:\\bar'

	>>> findpath('bar', 'd:\\foo')
	'd:\\foo\\bar'

	>>> findpath('\\baz', 'd:\\foo\\bar') # fails with '\\baz'
	'd:\\baz'

	>>> os.path.abspath(findpath('\\bar'))
	'c:\\bar'

	>>> os.path.abspath(findpath('bar'))
	'c:\\windows\\bar'

	>>> findpath('..', 'd:\\foo\\bar')
	'd:\\foo'

	The parent of the root directory is the root directory.
	>>> findpath('..', 'd:\\')
	'd:\\'
	"""
	return os.path.normpath(join(start, target))

def trace_symlink_target(link):
	"""
	Given a file that is known to be a symlink, trace it to its ultimate
	target.
	
	Raises TargetNotPresent when the target cannot be determined.
	Raises ValueError when the specified link is not a symlink.
	"""

	if not is_symlink(link):
		raise ValueError("link must point to a symlink on the system")
	while is_symlink(link):
		orig = os.path.dirname(link)
		link = readlink(link)
		link = findpath(link, orig)
	return link

def readlink(link):
	"""
	readlink(link) -> target
	Return a string representing the path to which the symbolic link points.
	"""
	handle = CreateFile(
		link,
		0,
		0,
		None,
		OPEN_EXISTING,
		FILE_FLAG_OPEN_REPARSE_POINT|FILE_FLAG_BACKUP_SEMANTICS,
		None,
		)

	res = DeviceIoControl(handle, FSCTL_GET_REPARSE_POINT, None, 10240)

	bytes = create_string_buffer(res)
	p_rdb = cast(bytes, POINTER(REPARSE_DATA_BUFFER))
	rdb = p_rdb.contents
	if not rdb.tag == IO_REPARSE_TAG_SYMLINK:
		raise RuntimeError("Expected IO_REPARSE_TAG_SYMLINK, but got %d" % rdb.tag)
	return rdb.get_print_name()

def patch_os_module():
	if not hasattr(os, 'symlink'):
		os.symlink = symlink
		os.path.islink = islink
	if not hasattr(os, 'readlink'):
		os.readlink = readlink
