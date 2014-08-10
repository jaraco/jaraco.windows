import ctypes.wintypes

GMEM_MOVEABLE = 0x2

GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
GlobalAlloc.argtypes = ctypes.wintypes.UINT, ctypes.c_ssize_t
GlobalAlloc.restype = ctypes.wintypes.HANDLE

GlobalLock = ctypes.windll.kernel32.GlobalLock
GlobalLock.argtypes = ctypes.wintypes.HGLOBAL,
GlobalLock.restype = ctypes.wintypes.LPVOID

GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock
GlobalUnlock.argtypes = ctypes.wintypes.HGLOBAL,
GlobalUnlock.restype = ctypes.wintypes.BOOL

GlobalSize = ctypes.windll.kernel32.GlobalSize
GlobalSize.argtypes = ctypes.wintypes.HGLOBAL,
GlobalSize.restype = ctypes.c_size_t
