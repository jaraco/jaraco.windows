import ctypes.wintypes
from ctypes.wintypes import LPDWORD

GetUserName = ctypes.windll.advapi32.GetUserNameW
GetUserName.argtypes = ctypes.wintypes.LPWSTR, LPDWORD
GetUserName.restype = ctypes.wintypes.DWORD
