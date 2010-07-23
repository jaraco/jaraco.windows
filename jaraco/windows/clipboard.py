import ctypes
from ctypes import windll
from ctypes.wintypes import UINT, HANDLE

from jaraco.windows.error import handle_nonzero_success, WindowsError
from jaraco.windows.memory import LockedMemory

__all__ = (
	'CF_TEXT', 'GetClipboardData', 'CloseClipboard',
	'SetClipboardData', 'OpenClipboard',
	)

CF_TEXT = 1
CF_BITMAP = 2
CF_METAFILEPICT    = 3
CF_SYLK            = 4
CF_DIF             = 5
CF_TIFF            = 6
CF_OEMTEXT         = 7
CF_DIB             = 8
CF_PALETTE         = 9
CF_PENDATA         = 10
CF_RIFF            = 11
CF_WAVE            = 12
CF_UNICODETEXT     = 13
CF_ENHMETAFILE     = 14
CF_HDROP           = 15
CF_LOCALE          = 16
CF_DIBV5           = 17
CF_MAX             = 18
CF_OWNERDISPLAY    = 0x0080
CF_DSPTEXT         = 0x0081
CF_DSPBITMAP       = 0x0082
CF_DSPMETAFILEPICT = 0x0083
CF_DSPENHMETAFILE  = 0x008E
CF_PRIVATEFIRST    = 0x0200
CF_PRIVATELAST     = 0x02FF
CF_GDIOBJFIRST     = 0x0300
CF_GDIOBJLAST      = 0x03FF

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

data_handlers = dict()
def handles(*formats):
	def register(func):
		for format in formats:
			data_handlers[format] = func
		return func
	return register

@handles(CF_TEXT, CF_DIBV5, CF_DIB)
def raw_string(handle):
	return LockedMemory(handle).data

@handles(CF_UNICODETEXT)
def unicode_string(handle):
	return unicode(raw_string(handle))

@handles(CF_BITMAP)
def as_bitmap(handle):
	# handle is HBITMAP
	raise NotImplementedError("Can't convert to DIB")
	# todo: use GetDIBits http://msdn.microsoft.com/en-us/library/dd144879%28v=VS.85%29.aspx

def GetClipboardData(type=CF_UNICODETEXT):
	if not type in data_handlers:
		raise NotImplementedError("No support for data of type %d" % type)
	handle = _GetClipboardData(type)
	if handle is None:
		raise TypeError("No clipboard data of type %d" % type)
	return data_handlers[type](handle)

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
