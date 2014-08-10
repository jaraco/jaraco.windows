import ctypes.wintypes

LPDWORD = ctypes.POINTER(ctypes.wintypes.DWORD)
GetUserName = ctypes.windll.advapi32.GetUserNameW
GetUserName.argtypes = (ctypes.wintypes.LPWSTR, LPDWORD)
GetUserName.restype = ctypes.wintypes.DWORD
