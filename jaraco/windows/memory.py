import ctypes
from ctypes import windll
from ctypes import c_size_t
from ctypes.wintypes import HGLOBAL, LPVOID, BOOL, WinError

GlobalLock = windll.kernel32.GlobalLock
GlobalLock.argtypes = HGLOBAL,
GlobalLock.restype = LPVOID

GlobalUnlock = windll.kernel32.GlobalUnlock
GlobalUnlock.argtypes = HGLOBAL,
GlobalUnlock.restype = BOOL

GlobalSize = windll.kernel32.GlobalSize
GlobalSize.argtypes = HGLOBAL,
GlobalSize.restype = c_size_t

class LockedMemory(object):
	def __init__(self, handle):
		self.handle = handle

	def __enter__(self):
		self.data_ptr = GlobalLock(self.handle)
		if not self.data_ptr:
			del self.data_ptr
			raise WinError()

	def __exit__(self, *args):
		GlobalUnlock(self.handle)
		del self.data_ptr

	@property
	def data(self):
		with self:
			return ctypes.string_at(self.data_ptr, self.size)

	@property
	def size(self):
		return GlobalSize(self.data_ptr)

