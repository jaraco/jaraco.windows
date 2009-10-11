from win32file import CreateFile
from jaraco.windows.reparse import DeviceIoControl
from win32con import *
import ctypes, ctypes.wintypes
import winioctlcon

from optparse import OptionParser

def get_args():
	parser = OptionParser()
	options, args = parser.parse_args()
	try:
		options.filename = args.pop(0)
	except IndexError:
		parser.error('filename required')
	return options

def main():
	options = get_args()
	print trace_symlink_target(options.filename)

FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000

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
		arr_typ = ctypes.wintypes.WCHAR*(self.print_name_length/2)
		data = ctypes.byref(self.path_buffer, self.print_name_offset)
		return ctypes.cast(data, ctypes.POINTER(arr_typ)).contents.value

	def get_substitute_name(self):
		arr_typ = ctypes.wintypes.WCHAR*(self.substitute_name_length/2)
		data = ctypes.byref(self.path_buffer, self.substitute_name_offset)
		return ctypes.cast(data, ctypes.POINTER(arr_typ)).contents.value

def trace_symlink_target(link):
	try:
		hnd = CreateFile(
			link,
			0,
			FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,
			None,
			OPEN_EXISTING,
			FILE_FLAG_OPEN_REPARSE_POINT|FILE_FLAG_BACKUP_SEMANTICS,
			None,
			)
	except:
		return link
		
	try:
		handle = hnd.handle
		res = DeviceIoControl(handle, winioctlcon.FSCTL_GET_REPARSE_POINT, None, 10240)
	except:
		return link

	bytes = ctypes.create_string_buffer(res)
	p_rdb = ctypes.cast(bytes, ctypes.POINTER(REPARSE_DATA_BUFFER))
	rdb = p_rdb.contents
	if not rdb.tag == 0xa000000c:
		return link
	pn = rdb.get_print_name()
	return trace_symlink_target(pn)

if __name__ == '__main__':
	main()