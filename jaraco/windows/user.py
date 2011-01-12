import ctypes
from .constants import ERROR_INSUFFICIENT_BUFFER
from .error import WindowsError, handle_nonzero_success

LPDWORD = ctypes.POINTER(ctypes.wintypes.DWORD)
GetUserName = ctypes.windll.advapi32.GetUserNameW
GetUserName.argtypes = (ctypes.wintypes.LPWSTR, LPDWORD)
GetUserName.restype = ctypes.wintypes.DWORD

def get_user_name():
	size = ctypes.wintypes.DWORD()
	try:
		handle_nonzero_success(GetUserName(None, size))
	except WindowsError, e:
		if e.code != ERROR_INSUFFICIENT_BUFFER:
			raise
	buffer = ctypes.create_unicode_buffer(size.value)
	handle_nonzero_success(GetUserName(buffer, size))
	return buffer.value
