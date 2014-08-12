import ctypes.wintypes

GetUserName = ctypes.windll.advapi32.GetUserNameW
GetUserName.argtypes = ctypes.wintypes.LPWSTR, ctypes.wintypes.LPDWORD
GetUserName.restype = ctypes.wintypes.DWORD
