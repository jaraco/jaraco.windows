import ctypes.wintypes

from jaraco.windows.error import handle_nonzero_success

class TokenInformationClass:
	TokenUser = 1

class TOKEN_USER(ctypes.Structure):
	num = 1
	_fields_ = [
		('SID', ctypes.c_void_p),
		('ATTRIBUTES', ctypes.wintypes.DWORD),
	]

def GetTokenInformation(token, information_class):
	"""
	Given a token, get the token information for it.
	"""
	data_size = ctypes.wintypes.DWORD()
	ctypes.windll.advapi32.GetTokenInformation(token, information_class.num,
		0, 0, ctypes.byref(data_size))
	data = ctypes.create_string_buffer(data_size.value)
	handle_nonzero_success(ctypes.windll.advapi32.GetTokenInformation(token,
		information_class.num,
		ctypes.byref(data), ctypes.sizeof(data),
		ctypes.byref(data_size)))
	return ctypes.cast(data, ctypes.POINTER(TOKEN_USER)).contents

class TokenAccess:
	TOKEN_QUERY = 0x8

def OpenProcessToken(proc_handle, access):
	result = ctypes.wintypes.HANDLE()
	proc_handle = ctypes.wintypes.HANDLE(proc_handle)
	handle_nonzero_success(ctypes.windll.advapi32.OpenProcessToken(
		proc_handle, access, ctypes.byref(result)))
	return result

def get_current_user():
	process = OpenProcessToken(
		ctypes.windll.kernel32.GetCurrentProcess(),
		TokenAccess.TOKEN_QUERY,
	)
	return GetTokenInformation(process, TOKEN_USER)
