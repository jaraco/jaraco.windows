import ctypes.wintypes

from . import error

_CredDeleteW = ctypes.windll.advapi32.CredDeleteW
_CredDeleteW.argtypes = (
	ctypes.wintypes.LPCWSTR, # TargetName
	ctypes.wintypes.DWORD, # Type
	ctypes.wintypes.DWORD, # Flags
)
_CredDeleteW.restype = ctypes.wintypes.BOOL

CRED_TYPE_GENERIC=1

def CredDelete(TargetName, Type, Flags=0):
	error.handle_nonzero_success(_CredDeleteW(TargetName, Type, Flags))
