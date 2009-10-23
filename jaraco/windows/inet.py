"""
Some routines for retrieving the addresses from the local
network config.
"""

import ipaddr
import itertools
import ctypes
from ctypes.wintypes import DWORD, BYTE, WCHAR, BOOL

# from mprapi.h
MAX_INTERFACE_NAME_LEN = 2**8

# from iprtrmib.h
MAXLEN_PHYSADDR = 2**3
MAXLEN_IFDESCR = 2**8

# from error.h
NO_ERROR = 0
ERROR_INSUFFICIENT_BUFFER = 122
ERROR_INVALID_PARAMETER = 87
ERROR_NOT_SUPPORTED = 50

class MIB_IFROW(ctypes.Structure):
	_fields_ = (
			('name', WCHAR*MAX_INTERFACE_NAME_LEN),
			('index', DWORD),
			('type', DWORD),
			('MTU', DWORD),
			('speed', DWORD),
			('physical_address_length', DWORD),
			('physical_address_raw', BYTE*MAXLEN_PHYSADDR),
			('admin_status', DWORD),
			('operational_status', DWORD),
			('last_change', DWORD),
			('octets_received', DWORD),
			('unicast_packets_received', DWORD),
			('non_unicast_packets_received', DWORD),
			('incoming_discards', DWORD),
			('incoming_errors', DWORD),
			('incoming_unknown_protocols', DWORD),
			('octets_sent', DWORD),
			('unicast_packets_sent', DWORD),
			('non_unicast_packets_sent', DWORD),
			('outgoing_discards', DWORD),
			('outgoing_errors', DWORD),
			('outgoing_queue_length', DWORD),
			('description_length', DWORD),
			('description_raw', ctypes.c_char*MAXLEN_IFDESCR),
	)

	def _get_binary_property(self, name):
		val_prop = '{0}_raw'.format(name)
		val = getattr(self, val_prop)
		len_prop = '{0}_length'.format(name)
		length = getattr(self, len_prop)
		return str(buffer(val))[:length]

	@property
	def physical_address(self):
		return self._get_binary_property('physical_address')

	@property
	def description(self):
		return self._get_binary_property('description')

class MIB_IFTABLE(ctypes.Structure):
	_fields_ = (
		('num_entries', DWORD),	  # dwNumEntries
		('entries', MIB_IFROW*0), # table
	)

class MIB_IPADDRROW(ctypes.Structure):
	_fields_ = (
		('address_num', DWORD),
		('index', DWORD),
		('mask', DWORD),
		('broadcast_address', DWORD),
		('reassembly_size', DWORD),
		('unused', ctypes.c_ushort),
		('type', ctypes.c_ushort),
	)
	
	@property
	def address(self):
		# Convert from little-endian to big-endian
		import struct
		_ = struct.pack('L', self.address_num)
		address_num = struct.unpack('!L', _)[0]
		return ipaddr.IPv4Address(address_num)

class MIB_IPADDRTABLE(ctypes.Structure):
	_fields_ = (
		('num_entries', DWORD),
		('entries', MIB_IPADDRROW*0),
	)

# define some parameters to the API Functions
ip_helper = ctypes.windll.iphlpapi
ip_helper.GetIfTable.argtypes = [
	ctypes.POINTER(MIB_IFTABLE),
	ctypes.POINTER(ctypes.c_ulong),
	BOOL,
	]
ip_helper.GetIfTable.restype = DWORD

ip_helper.GetIpAddrTable.argtypes = [
	ctypes.POINTER(MIB_IPADDRTABLE),
	ctypes.POINTER(ctypes.c_ulong),
	BOOL,
	]
ip_helper.GetIpAddrTable.restype = DWORD

class AllocatedTable(object):
	"""
	Both the interface table and the ip address table use the same
	technique to store arrays of structures of variable length. This
	base class captures the functionality to retrieve and access those
	table entries.
	
	The subclass needs to define three class attributes:
		method: a callable that takes three arguments - a pointer to
				the structure, the length of the data contained by the
				structure, and a boolean of whether the result should
				be sorted.
		structure: a C structure defininition that describes the table
				format.
		row_structure: a C structure definition that describes the row
				format.
	"""
	def __get_table_size(self):
		"""
		Retrieve the size of the buffer needed by calling the method
		with a null pointer and length of zero. This should trigger an
		insufficient buffer error and return the size needed for the
		buffer.
		"""
		length = DWORD()
		res = self.method(None, length, False)
		if res != ERROR_INSUFFICIENT_BUFFER:
			raise RuntimeError("Error getting table length (%d)" % res)
		return length.value

	def get_table(self):
		"""
		Get the table
		"""
		buffer_length = self.__get_table_size()
		returned_buffer_length = DWORD(buffer_length)
		buffer = ctypes.create_string_buffer(buffer_length)
		pointer_type = ctypes.POINTER(self.structure)
		table_p = ctypes.cast(buffer, pointer_type)
		res = self.method(table_p, returned_buffer_length, False)
		if res != NO_ERROR:
			raise RuntimeError("Error retrieving table (%d)" % res)
		return table_p.contents

	@property
	def entries(self):
		"""
		Using the table structure, return the array of entries based
		on the table size.
		"""
		table = self.get_table()
		entries_array = self.row_structure*table.num_entries
		pointer_type = ctypes.POINTER(entries_array)
		return ctypes.cast(table.entries, pointer_type).contents

class InterfaceTable(AllocatedTable):
	method = ip_helper.GetIfTable
	structure = MIB_IFTABLE
	row_structure = MIB_IFROW

class AddressTable(AllocatedTable):
	method = ip_helper.GetIpAddrTable
	structure = MIB_IPADDRTABLE
	row_structure = MIB_IPADDRROW

class AddressManager(object):
	@staticmethod
	def hardware_address_to_string(addr):
		hex_bytes = (byte.encode('hex') for byte in addr)
		return ':'.join(hex_bytes)

	def get_host_mac_address_strings(self):
		return (self.hardware_address_to_string(addr)
			for addr in self.get_host_mac_addresses())

	def get_host_ip_address_strings(self):
		return itertools.imap(str, self.get_host_ip_addresses())

	def get_host_mac_addresses(self):
		return (
			entry.physical_address
			for entry in InterfaceTable().entries
			)

	def get_host_ip_addresses(self):
		return (
			entry.address
			for entry in AddressTable().entries
			)
