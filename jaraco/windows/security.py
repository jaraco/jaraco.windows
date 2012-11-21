import ctypes.wintypes


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
	info = information_class()
	ctypes.windll.advapi32.GetTokenInformation(token, information_class.num,
		ctypes.by_ref(info), ctypes.sizeof(information_class),
		ctypes.by_ref(data_size))
	return info
