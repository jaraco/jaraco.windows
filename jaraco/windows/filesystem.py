#!/usr/bin/env python

import os
import sys
from ctypes import (
	Structure, windll, POINTER, byref, cast, create_unicode_buffer,
	c_size_t
	)
from ctypes.wintypes import (
	BOOLEAN, LPWSTR, DWORD, LPVOID, HANDLE, FILETIME,
	c_uint64, WCHAR,
	)
from jaraco.windows.error import handle_nonzero_success, WindowsError

CreateSymbolicLink = windll.kernel32.CreateSymbolicLinkW
CreateSymbolicLink.argtypes = (
	LPWSTR,
	LPWSTR,
	DWORD,
	)
CreateSymbolicLink.restype = BOOLEAN

CreateHardLink = windll.kernel32.CreateHardLinkW
CreateHardLink.argtypes = (
	LPWSTR,
	LPWSTR,
	LPVOID, # reserved for LPSECURITY_ATTRIBUTES
	)
CreateHardLink.restype = BOOLEAN

GetFileAttributes = windll.kernel32.GetFileAttributesW
GetFileAttributes.argtypes = (LPWSTR,)
GetFileAttributes.restype = DWORD

MAX_PATH = 260

GetFinalPathNameByHandle = windll.kernel32.GetFinalPathNameByHandleW
GetFinalPathNameByHandle.argtypes = (
	HANDLE, LPWSTR, DWORD, DWORD,
	)
GetFinalPathNameByHandle.restype = DWORD

class SECURITY_ATTRIBUTES(Structure):
	_fields_ = (
		('length', DWORD),
		('p_security_descriptor', LPVOID),
		('inherit_handle', BOOLEAN),
		)
LPSECURITY_ATTRIBUTES = POINTER(SECURITY_ATTRIBUTES)

CreateFile = windll.kernel32.CreateFileW
CreateFile.argtypes = (
	LPWSTR,
	DWORD,
	DWORD,
	LPSECURITY_ATTRIBUTES,
	DWORD,
	DWORD,
	HANDLE,
	)
CreateFile.restype = HANDLE
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2
FILE_SHARE_DELETE = 4
FILE_FLAG_BACKUP_SEMANTICS = 0x2000000
NULL = 0
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80
GENERIC_READ = 0x80000000
INVALID_HANDLE_VALUE = HANDLE(-1).value

CloseHandle = windll.kernel32.CloseHandle
CloseHandle.argtypes = (HANDLE,)
CloseHandle.restype = BOOLEAN

class WIN32_FIND_DATA(Structure):
	_fields_ = [
		('file_attributes', DWORD),
		('creation_time', FILETIME),
		('last_access_time', FILETIME),
		('last_write_time', FILETIME),
		('file_size_words', DWORD*2),
		('reserved', DWORD*2),
		('filename', WCHAR*MAX_PATH),
		('alternate_filename', WCHAR*14),
	]
	
	@property
	def file_size(self):
		return cast(self.file_size_words, POINTER(c_uint64)).contents

LPWIN32_FIND_DATA = POINTER(WIN32_FIND_DATA)

FindFirstFile = windll.kernel32.FindFirstFileW
FindFirstFile.argtypes = (LPWSTR, LPWIN32_FIND_DATA)
FindFirstFile.restype = HANDLE
FindNextFile = windll.kernel32.FindNextFileW
FindNextFile.argtypes = (HANDLE, LPWIN32_FIND_DATA)
FindNextFile.restype = BOOLEAN

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

def link(link, target):
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
	IO_REPARSE_TAG_SYMLINK = 0xA000000C
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

def GetFinalPath(path):
	"""
	For a given path, determine the ultimate location of that path.
	Useful for resolving symlink targets.
	This functions wraps the GetFinalPathNameByHandle from the Windows
	SDK.
	"""
	hFile = CreateFile(
		path,
		NULL, # desired access
		FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE, # share mode
		LPSECURITY_ATTRIBUTES(), # NULL pointer
		OPEN_EXISTING,
		FILE_ATTRIBUTE_NORMAL|FILE_FLAG_BACKUP_SEMANTICS,
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
