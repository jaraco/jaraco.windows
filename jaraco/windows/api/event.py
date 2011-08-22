from ctypes import (
	Structure, windll, POINTER, byref, cast, create_unicode_buffer,
	c_size_t, c_int, create_string_buffer, c_uint64, c_ushort, c_short,
	c_uint,
	)
from ctypes.wintypes import (
	BOOLEAN, LPWSTR, DWORD, LPVOID, HANDLE, FILETIME,
	WCHAR, BOOL, HWND, WORD, UINT,
	)

CreateEvent = windll.kernel32.CreateEventW
CreateEvent.argtypes = (
	LPVOID, # LPSECURITY_ATTRIBUTES
	BOOL,
	BOOL,
	LPWSTR,
)
CreateEvent.restype = HANDLE

_WaitForMultipleObjects = windll.kernel32.WaitForMultipleObjects
_WaitForMultipleObjects.argtypes = DWORD, POINTER(HANDLE), BOOL, DWORD
_WaitForMultipleObjects.restype = DWORD

def WaitForMultipleObjects(handles, wait_all=False, timeout=0):
	n_handles = len(handles)
	handle_array = (HANDLE*n_handles)()
	for index, handle in enumerate(handles):
		handle_array[index] = handle
	return _WaitForMultipleObjects(n_handles, handle_array, wait_all, timeout)

WAIT_OBJECT_0 = 0
