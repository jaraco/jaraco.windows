import ctypes.wintypes

GMEM_MOVEABLE = 0x2

GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
GlobalAlloc.argtypes = ctypes.wintypes.UINT, ctypes.c_ssize_t
GlobalAlloc.restype = ctypes.wintypes.HANDLE
