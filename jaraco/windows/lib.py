import ctypes
from ctypes.wintypes import HANDLE, LPWSTR, DWORD

GetModuleFileName = ctypes.windll.kernel32.GetModuleFileNameW
GetModuleFileName.argtypes = (HANDLE, LPWSTR, DWORD)
GetModuleFileName.restype = DWORD

def find_lib(lib):
	r"""
	Find the DLL for a given library.
	
	Accepts a string or loaded module
	
	>>> find_lib('kernel32').lower()
	u'c:\\windows\\system32\\kernel32.dll'
	"""
	if isinstance(lib, str):
		lib = getattr(ctypes.windll, lib)

	size = 1024
	result = ctypes.create_unicode_buffer(size)
	GetModuleFileName(lib._handle, result, size)
	return result.value
