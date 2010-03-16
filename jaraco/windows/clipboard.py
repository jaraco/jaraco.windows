import ctypes
from ctypes import windll
from ctypes.wintypes import UINT, HANDLE

from jaraco.windows.error import handle_nonzero_success, WindowsError

__all__ = (
	'CF_TEXT', 'GetClipboardData', 'CloseClipboard',
	'SetClipboardData', 'OpenClipboard',
	)

CF_TEXT = 1

def OpenClipboard(owner=None):
	"""
	Open the clipboard.
	
	owner
	[in] Handle to the window to be associated with the open clipboard.
	If this parameter is None, the open clipboard is associated with the
	current task.
	"""
	handle_nonzero_success(windll.user32.OpenClipboard(owner))

CloseClipboard = lambda: handle_nonzero_success(windll.user32.CloseClipboard())

_GetClipboardData = windll.user32.GetClipboardData
_GetClipboardData.argtypes = (UINT,)
_GetClipboardData.restype = HANDLE

def GetClipboardData(type):
	if not type == CF_TEXT:
		raise NotImplementedError("No support for data of type %d" % type)
	handle = _GetClipboardData(type)
	if handle is None:
		raise ValueError("No clipboard data of type %d" % type)
	return ctypes.string_at(handle)

EmptyClipboard = lambda: handle_nonzero_success(windll.user32.EmptyClipboard())

_SetClipboardData = windll.user32.SetClipboardData
_SetClipboardData.argtypes = (UINT, HANDLE)
_SetClipboardData.restype = HANDLE

GMEM_MOVEABLE = 0x2

def SetClipboardData(type, content):
	"""
	Modeled after http://msdn.microsoft.com/en-us/library/ms649016%28VS.85%29.aspx#_win32_Copying_Information_to_the_Clipboard
	"""
	if not type == CF_TEXT and not isinstance(content, basestring):
		raise NotImplementedError("Only text type is supported at this time")
	# allocate the memory for the data
	content = ctypes.create_string_buffer(content)
	flags = GMEM_MOVEABLE
	size = len(content)
	handle_to_copy = windll.kernel32.GlobalAlloc(flags, size)
	ptr = windll.kernel32.GlobalLock(handle_to_copy)
	ctypes.memmove(ptr, content, size)
	windll.kernel32.GlobalUnlock(handle_to_copy)
	result = _SetClipboardData(type, handle_to_copy)
	if result is None:
		raise WindowsError()
