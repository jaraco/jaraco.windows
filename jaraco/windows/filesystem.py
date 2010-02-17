#!/usr/bin/env python

from __future__ import print_function

import os
import sys
import operator
from itertools import imap, ifilter, izip
from ctypes import (POINTER, byref, cast, create_unicode_buffer,
	create_string_buffer, windll)
from jaraco.windows.error import WindowsError, handle_nonzero_success
import jaraco.windows.api.filesystem as api

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
	handle_nonzero_success(api.CreateSymbolicLink(link, target, target_is_directory))

def link(target, link):
	"""
	Establishes a hard link between an existing file and a new file.
	"""
	handle_nonzero_success(api.CreateHardLink(link, target, None))

def is_reparse_point(path):
	"""
	Determine if the given path is a reparse point.
	"""
	res = api.GetFileAttributes(path)
	if res == api.INVALID_FILE_ATTRIBUTES: raise WindowsError()
	return bool(res & api.FILE_ATTRIBUTE_REPARSE_POINT)

def islink(path):
	"Determine if the given path is a symlink"
	return is_reparse_point(path) and is_symlink(path)

def is_symlink(path):
	"""
	Assuming path is a reparse point, determine if it's a symlink.
	
	>>> symlink('foobaz', 'foobar')
	>>> is_symlink('foobar')
	True
	>>> os.remove('foobar')
	"""
	return _is_symlink(next(find_files(path)))

def _is_symlink(find_data):
	return find_data.reserved[0] == api.IO_REPARSE_TAG_SYMLINK

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
	fd = api.WIN32_FIND_DATA()
	handle = api.FindFirstFile(spec, byref(fd))
	while True:
		if handle == api.INVALID_HANDLE_VALUE:
			raise WindowsError()
		yield fd
		fd = api.WIN32_FIND_DATA()
		res = api.FindNextFile(handle, byref(fd))
		if res == 0: # error
			error = WindowsError()
			if error.code == api.ERROR_NO_MORE_FILES:
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
	hFile = api.CreateFile(
		path,
		api.NULL, # desired access
		api.FILE_SHARE_READ|api.FILE_SHARE_WRITE|api.FILE_SHARE_DELETE, # share mode
		api.LPSECURITY_ATTRIBUTES(), # NULL pointer
		api.OPEN_EXISTING,
		api.FILE_FLAG_BACKUP_SEMANTICS,
		api.NULL,
		)

	if hFile == api.INVALID_HANDLE_VALUE:
		raise WindowsError()

	buf_size = api.GetFinalPathNameByHandle(hFile, api.LPWSTR(), 0, api.VOLUME_NAME_DOS)
	handle_nonzero_success(buf_size)
	buf = create_unicode_buffer(buf_size)
	result_length = api.GetFinalPathNameByHandle(hFile, buf, len(buf), api.VOLUME_NAME_DOS)

	assert result_length < len(buf)
	handle_nonzero_success(result_length)
	handle_nonzero_success(api.CloseHandle(hFile))

	return buf[:result_length]

def GetBinaryType(filepath):
	res = api.DWORD()
	handle_nonzero_success(api._GetBinaryType(filepath, res))
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
	params = api.SHFILEOPSTRUCT(0, operation, from_, to, flags)
	res = api._SHFileOperation(params)
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

def resolve_path(target, start=os.path.curdir):
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

findpath = resolve_path

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
		link = resolve_path(link, orig)
	return link

def readlink(link):
	"""
	readlink(link) -> target
	Return a string representing the path to which the symbolic link points.
	"""
	handle = api.CreateFile(
		link,
		0,
		0,
		None,
		api.OPEN_EXISTING,
		api.FILE_FLAG_OPEN_REPARSE_POINT|api.FILE_FLAG_BACKUP_SEMANTICS,
		None,
		)
	
	if handle == api.INVALID_HANDLE_VALUE:
		raise WindowsError()

	res = api.DeviceIoControl(handle, api.FSCTL_GET_REPARSE_POINT, None, 10240)

	bytes = create_string_buffer(res)
	p_rdb = cast(bytes, POINTER(api.REPARSE_DATA_BUFFER))
	rdb = p_rdb.contents
	if not rdb.tag == api.IO_REPARSE_TAG_SYMLINK:
		raise RuntimeError("Expected IO_REPARSE_TAG_SYMLINK, but got %d" % rdb.tag)
	return rdb.get_print_name()

def patch_os_module():
	if not hasattr(os, 'symlink'):
		os.symlink = symlink
		os.path.islink = islink
	if not hasattr(os, 'readlink'):
		os.readlink = readlink

def find_symlinks(root):
	for dirpath, dirnames, filenames in os.walk(root):
		for name in dirnames+filenames:
			pathname = os.path.join(dirpath, name)
			if is_symlink(pathname): yield pathname

def find_symlinks_cmd():
	"""
	%prog [start-path]
	Search the specified path (defaults to the current directory) for symlinks,
	printing the source and target on each line.
	"""
	from optparse import OptionParser
	from textwrap import dedent
	parser = OptionParser(usage=dedent(find_symlinks_cmd.__doc__).strip())
	options, args = parser.parse_args()
	if not args: args = ['.']
	root = args.pop()
	if args:
		parser.error("unexpected argument(s)")
	try:
		for symlink in find_symlinks(root):
			target = readlink(symlink)
			dir = ['', 'D'][os.path.isdir(symlink)]
			msg = '{dir:2}{symlink} --> {target}'.format(**vars())
			print(msg)
	except KeyboardInterrupt:
		pass
