import ctypes.wintypes

from jaraco.windows.error import handle_nonzero_success

class TokenInformationClass:
	TokenUser = 1

class TOKEN_USER(ctypes.Structure):
	num = 1
	_fields_ = [
		('SID', ctypes.c_void_p),
		('ATTRIBUTES', ctypes.wintypes.DWORD),
	]


class SECURITY_DESCRIPTOR(ctypes.Structure):
	"""
	typedef struct _SECURITY_DESCRIPTOR
		{
		UCHAR Revision;
		UCHAR Sbz1;
		SECURITY_DESCRIPTOR_CONTROL Control;
		PSID Owner;
		PSID Group;
		PACL Sacl;
		PACL Dacl;
		}   SECURITY_DESCRIPTOR;
	"""
	SECURITY_DESCRIPTOR_CONTROL = ctypes.wintypes.USHORT
	REVISION = 1

	_fields_ = [
		('Revision', ctypes.c_ubyte),
		('Sbz1', ctypes.c_ubyte),
		('Control', SECURITY_DESCRIPTOR_CONTROL),
		('Owner', ctypes.c_void_p),
		('Group', ctypes.c_void_p),
		('Sacl', ctypes.c_void_p),
		('Dacl', ctypes.c_void_p),
	]

class SECURITY_ATTRIBUTES(ctypes.Structure):
	"""
	typedef struct _SECURITY_ATTRIBUTES {
		DWORD  nLength;
		LPVOID lpSecurityDescriptor;
		BOOL   bInheritHandle;
	} SECURITY_ATTRIBUTES;
	"""
	_fields_ = [
		('nLength', ctypes.wintypes.DWORD),
		('lpSecurityDescriptor', ctypes.c_void_p),
		('bInheritHandle', ctypes.wintypes.BOOL),
	]

	def __init__(self, *args, **kwargs):
		super(SECURITY_ATTRIBUTES, self).__init__(*args, **kwargs)
		self.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)

	def _get_descriptor(self):
		return self._descriptor
	def _set_descriptor(self, descriptor):
		self._descriptor = descriptor
		self.lpSecurityDescriptor = ctypes.addressof(descriptor)
	descriptor = property(_get_descriptor, _set_descriptor)

def GetTokenInformation(token, information_class):
	"""
	Given a token, get the token information for it.
	"""
	data_size = ctypes.wintypes.DWORD()
	ctypes.windll.advapi32.GetTokenInformation(token, information_class.num,
		0, 0, ctypes.byref(data_size))
	data = ctypes.create_string_buffer(data_size.value)
	handle_nonzero_success(ctypes.windll.advapi32.GetTokenInformation(token,
		information_class.num,
		ctypes.byref(data), ctypes.sizeof(data),
		ctypes.byref(data_size)))
	return ctypes.cast(data, ctypes.POINTER(TOKEN_USER)).contents

class TokenAccess:
	TOKEN_QUERY = 0x8

def OpenProcessToken(proc_handle, access):
	result = ctypes.wintypes.HANDLE()
	proc_handle = ctypes.wintypes.HANDLE(proc_handle)
	handle_nonzero_success(ctypes.windll.advapi32.OpenProcessToken(
		proc_handle, access, ctypes.byref(result)))
	return result

def get_current_user():
	"""
	Return a TOKEN_USER for the owner of this process.
	"""
	process = OpenProcessToken(
		ctypes.windll.kernel32.GetCurrentProcess(),
		TokenAccess.TOKEN_QUERY,
	)
	return GetTokenInformation(process, TOKEN_USER)

def get_security_attributes_for_user(user=None):
	"""
	Return a SECURITY_ATTRIBUTES structure with the SID set to the
	specified user (uses current user if none is specified).
	"""
	if user is None:
		user = get_current_user()

	assert isinstance(user, TOKEN_USER), "user must be TOKEN_USER instance"

	SD = SECURITY_DESCRIPTOR()
	SA = SECURITY_ATTRIBUTES()
	# by attaching the actual security descriptor, it will be garbage-
	# collected with the security attributes
	SA.descriptor = SD
	SA.bInheritHandle = 1

	ctypes.windll.advapi32.InitializeSecurityDescriptor(ctypes.byref(SD),
		SECURITY_DESCRIPTOR.REVISION)
	ctypes.windll.advapi32.SetSecurityDescriptorOwner(ctypes.byref(SD),
		user.SID, 0)
	return SA
