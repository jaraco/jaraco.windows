from ctypes import (
	Structure, windll, POINTER, byref, cast, create_unicode_buffer,
	c_size_t, c_int, create_string_buffer, c_uint64, c_ushort, c_short,
	c_uint,
	)
from ctypes.wintypes import (
	BOOLEAN, LPWSTR, DWORD, LPVOID, HANDLE, FILETIME,
	WCHAR, BOOL, HWND, WORD, UINT,
	)
from jaraco.windows.reparse import IO_REPARSE_TAG_SYMLINK, FSCTL_GET_REPARSE_POINT, REPARSE_DATA_BUFFER
from jaraco.windows.reparse import DeviceIoControl

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
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_FLAG_BACKUP_SEMANTICS = 0x2000000
NULL = 0
OPEN_EXISTING = 3
FILE_ATTRIBUTE_READONLY = 0x1
FILE_ATTRIBUTE_DIRECTORY = 0x10
FILE_ATTRIBUTE_NORMAL = 0x80
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
GENERIC_READ = 0x80000000
FILE_READ_ATTRIBUTES = 0x80
INVALID_HANDLE_VALUE = HANDLE(-1).value

INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF

ERROR_NO_MORE_FILES = 0x12

VOLUME_NAME_DOS = 0

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

SCS_32BIT_BINARY = 0 # A 32-bit Windows-based application
SCS_64BIT_BINARY = 6 # A 64-bit Windows-based application
SCS_DOS_BINARY = 1 # An MS-DOS-based application
SCS_OS216_BINARY = 5 # A 16-bit OS/2-based application
SCS_PIF_BINARY = 3 # A PIF file that executes an MS-DOS-based application
SCS_POSIX_BINARY = 4 # A POSIX-based application
SCS_WOW_BINARY = 2 # A 16-bit Windows-based application

_GetBinaryType = windll.kernel32.GetBinaryTypeW
_GetBinaryType.argtypes = (LPWSTR, POINTER(DWORD))
_GetBinaryType.restype = BOOL

FILEOP_FLAGS = WORD
class SHFILEOPSTRUCT(Structure):
	_fields_ = [
		('status_dialog', HWND),
		('operation', UINT),
		('from_', LPWSTR),
		('to', LPWSTR),
		('flags', FILEOP_FLAGS),
		('operations_aborted', BOOL),
		('name_mapping_handles', LPVOID),
		('progress_title', LPWSTR),
	]
_SHFileOperation = windll.shell32.SHFileOperationW
_SHFileOperation.argtypes = [POINTER(SHFILEOPSTRUCT)]
_SHFileOperation.restype = c_int

FOF_ALLOWUNDO = 64
FOF_NOCONFIRMATION = 16
FO_DELETE = 3

ReplaceFile = windll.kernel32.ReplaceFileW
ReplaceFile.restype = BOOL
ReplaceFile.argtypes = [
	LPWSTR,
	LPWSTR,
	LPWSTR,
	DWORD,
	LPVOID,
	LPVOID,
	]

REPLACEFILE_WRITE_THROUGH = 0x1
REPLACEFILE_IGNORE_MERGE_ERRORS = 0x2
REPLACEFILE_IGNORE_ACL_ERRORS = 0x4

class STAT_STRUCT(Structure):
	_fields_ = [
		('dev', c_uint),
		('ino', c_ushort),
		('mode', c_ushort),
		('nlink', c_short),
		('uid', c_short),
		('gid', c_short),
		('rdev', c_uint),
		# the following 4 fields are c_uint64 for _stat64
		('size', c_uint),
		('atime', c_uint),
		('mtime', c_uint),
		('ctime', c_uint),
	]

_wstat = windll.msvcrt._wstat
_wstat.argtypes = [LPWSTR, POINTER(STAT_STRUCT)]
_wstat.restype = c_int

GetFileAttributes = windll.kernel32.GetFileAttributesW
GetFileAttributes.argtypes = LPWSTR,
GetFileAttributes.restype = DWORD

FILE_NOTIFY_CHANGE_LAST_WRITE = 0x10

FindFirstChangeNotification = windll.kernel32.FindFirstChangeNotificationW
FindFirstChangeNotification.argtypes = LPWSTR, BOOL, DWORD
FindFirstChangeNotification.restype = HANDLE

FindCloseChangeNotification = windll.kernel32.FindCloseChangeNotification
FindCloseChangeNotification.argtypes = HANDLE,
FindCloseChangeNotification.restype = BOOL

FindNextChangeNotification = windll.kernel32.FindNextChangeNotification
FindNextChangeNotification.argtypes = HANDLE,
FindNextChangeNotification.restype = BOOL
