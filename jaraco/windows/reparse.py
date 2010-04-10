from __future__ import division
import ctypes
from ctypes import wintypes
from jaraco.windows.error import handle_nonzero_success

FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
IO_REPARSE_TAG_SYMLINK = 0xA000000C
FSCTL_GET_REPARSE_POINT = 0x900a8

LPDWORD = ctypes.POINTER(wintypes.DWORD)
LPOVERLAPPED = wintypes.LPVOID

_DeviceIoControl = ctypes.windll.kernel32.DeviceIoControl
_DeviceIoControl.argtypes = [
	wintypes.HANDLE,
	wintypes.DWORD,
	wintypes.LPVOID,
	wintypes.DWORD,
	wintypes.LPVOID,
	wintypes.DWORD,
	LPDWORD,
	LPOVERLAPPED,
	]
_DeviceIoControl.restype = wintypes.BOOL

def DeviceIoControl(device, io_control_code, in_buffer, out_buffer, overlapped=None):
	if overlapped is not None:
		raise NotImplementedError("overlapped handles not yet supported")
	
	if isinstance(out_buffer, int):
		out_buffer = ctypes.create_string_buffer(out_buffer)
	
	in_buffer_size = len(in_buffer) if in_buffer is not None else 0
	out_buffer_size = len(out_buffer)
	assert isinstance(out_buffer, ctypes.Array)

	returned_bytes = wintypes.DWORD()

	res = _DeviceIoControl(
		device,
		io_control_code,
		in_buffer, in_buffer_size,
		out_buffer, out_buffer_size,
		returned_bytes,
		overlapped,
		)

	handle_nonzero_success(res)
	handle_nonzero_success(returned_bytes)
	
	return out_buffer[:returned_bytes.value]

wchar_size = ctypes.sizeof(wintypes.WCHAR)

class REPARSE_DATA_BUFFER(ctypes.Structure):
	_fields_ = [
		('tag', ctypes.c_ulong),
		('data_length', ctypes.c_ushort),
		('reserved', ctypes.c_ushort),
		('substitute_name_offset', ctypes.c_ushort),
		('substitute_name_length', ctypes.c_ushort),
		('print_name_offset', ctypes.c_ushort),
		('print_name_length', ctypes.c_ushort),
		('flags', ctypes.c_ulong),
		('path_buffer', ctypes.c_byte*1),
	]
	def get_print_name(self):
		arr_typ = wintypes.WCHAR*(self.print_name_length//wchar_size)
		data = ctypes.byref(self.path_buffer, self.print_name_offset)
		return ctypes.cast(data, ctypes.POINTER(arr_typ)).contents.value

	def get_substitute_name(self):
		arr_typ = wintypes.WCHAR*(self.substitute_name_length//wchar_size)
		data = ctypes.byref(self.path_buffer, self.substitute_name_offset)
		return ctypes.cast(data, ctypes.POINTER(arr_typ)).contents.value


'''
typedef struct _REPARSE_DATA_BUFFER {
  ULONG  ReparseTag;
  USHORT  ReparseDataLength;
  USHORT  Reserved;
  union {
    struct {
      USHORT  SubstituteNameOffset;
      USHORT  SubstituteNameLength;
      USHORT  PrintNameOffset;
      USHORT  PrintNameLength;
      ULONG  Flags;
      WCHAR  PathBuffer[1];
      } SymbolicLinkReparseBuffer;
    struct {
      USHORT  SubstituteNameOffset;
      USHORT  SubstituteNameLength;
      USHORT  PrintNameOffset;
      USHORT  PrintNameLength;
      WCHAR  PathBuffer[1];
      } MountPointReparseBuffer;
    struct {
      UCHAR  DataBuffer[1];
    } GenericReparseBuffer;
  };
} REPARSE_DATA_BUFFER, *PREPARSE_DATA_BUFFER;

#define REPARSE_DATA_BUFFER_HEADER_SIZE  FIELD_OFFSET(REPARSE_DATA_BUFFER, GenericReparseBuffer)

#define MAXIMUM_REPARSE_DATA_BUFFER_SIZE  ( 16 * 1024 )
'''
