#!/usr/bin/env python

# $Id$

import sys
from itertools import count

import ctypes
import ctypes.wintypes

try:
	import winreg
except ImportError:
	import _winreg as winreg

from jaraco.windows import error
from jaraco.windows.message import SendMessage, HWND_BROADCAST, WM_SETTINGCHANGE

_SetEnvironmentVariable = ctypes.windll.kernel32.SetEnvironmentVariableW
_SetEnvironmentVariable.restype = ctypes.wintypes.BOOL
_SetEnvironmentVariable.argtypes = [ctypes.wintypes.LPCWSTR]*2

_GetEnvironmentVariable = ctypes.windll.kernel32.GetEnvironmentVariableW
_GetEnvironmentVariable.restype = ctypes.wintypes.BOOL
_GetEnvironmentVariable.argtypes = [
	ctypes.wintypes.LPCWSTR,
	ctypes.wintypes.LPWSTR, ctypes.wintypes.DWORD,
	]

def SetEnvironmentVariable(name, value):
	error.handle_nonzero_success(_SetEnvironmentVariable(name, value))

def ClearEnvironmentVariable(name):
	error.handle_nonzero_success(_SetEnvironmentVariable(name, None))

def GetEnvironmentVariable(name):
	max_size = 2**15-1
	buffer = ctypes.create_unicode_buffer(max_size)
	error.handle_nonzero_success(_GetEnvironmentVariable(name, buffer, max_size))
	return buffer.value

### 

def registry_key_values(key):
	for index in count():
		try:
			yield winreg.EnumValue(key, index)
		except WindowsError:
			break

class RegisteredEnvironment(object):
	"""
	Manages the environment variables as set in the Windows Registry.
	"""
	
	@classmethod
	def show(class_):
		for name, value, type in registry_key_values(class_.key):
			sys.stdout.write('='.join((name, value)) + '\n')

	NoDefault = type('NoDefault', (object,), dict())

	@classmethod
	def get(class_, name, default=NoDefault):
		try:
			value, type = winreg.QueryValueEx(class_.key, name)
			return value
		except WindowsError:
			if default is not class_.NoDefault:
				return default
			raise ValueError("No such key", name)

	@classmethod
	def get_values_list(class_, name, sep):
		res = class_.get(name.upper(), [])
		if isinstance(res, basestring):
			res = res.split(sep)
		return res
		

			
	@classmethod
	def set(class_, name, value, options):
		# consider opening the key read-only except for here
		# key = winreg.OpenKey(class_.key, None, 0, winreg.KEY_WRITE)
		# and follow up by closing it.
		if not value:
			return class_.delete(name)
		do_append = options.append or (
			name.upper() in ('PATH', 'PATHEXT') and not options.replace
			)
		if do_append:
			sep = ';'
			values = class_.get_values_list(name, sep) + [value]
			value = ';'.join(values)
		winreg.SetValueEx(class_.key, name, 0, winreg.REG_EXPAND_SZ, value)
		class_.notify()
	
	@classmethod
	def delete(class_, name):
		winreg.DeleteValue(class_.key, name)
		class_.notify()
	
	@classmethod
	def notify(class_):
		# TODO: Implement Microsoft UIPI (User Interface Privilege Isolation) to
		#  elevate privilege to system level so the system gets this notification
		# for now, this must be run as admin to work as expected
		SendMessage(HWND_BROADCAST, WM_SETTINGCHANGE, 0, u'Environment')

class MachineRegisteredEnvironment(RegisteredEnvironment):
	path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
	hklm = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
	key = winreg.OpenKey(hklm, path, 0, winreg.KEY_READ | winreg.KEY_WRITE)

class UserRegisteredEnvironment(RegisteredEnvironment):
	hkcu = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
	key = winreg.OpenKey(hkcu, 'Environment', 0, winreg.KEY_READ | winreg.KEY_WRITE)

def trim(s):
	from textwrap import dedent
	return dedent(s).strip()

def enver(*args):
	"""
	%prog [<name>=[value]]
	
	To show all environment variables, call with no parameters:
	 %prog
	To Add/Modify/Delete environment variable:
	 %prog <name>=[value]

	If <name> is PATH or PATHEXT, %prog will by default append the value using
	a semicolon as a separator. Use -r to disable this behavior or -a to force
	it for variables other than PATH and PATHEXT.

	If append is prescribed, but the value doesn't exist, the value will be
	created.

	If there is no value, %prog will delete the <name> environment variable.
	i.e. "PATH="

	Note that %prog does not affect the current running environment, and can
	only affect subsequently spawned applications.
	"""
	from optparse import OptionParser
	parser = OptionParser(usage=trim(enver.__doc__))
	parser.add_option('-U', '--user-environment',
		action='store_const', const=UserRegisteredEnvironment,
		default=MachineRegisteredEnvironment,
		dest='class_',
		help="Use the current user's environment",
		)
	parser.add_option('-a', '--append',
		action='store_true', default=False,
		help="Append the value to any existing value (default for PATH and PATHEXT)",)
	parser.add_option('-r', '--replace',
		action='store_true', default=False,
		help="Replace any existing value (used to override default append for PATH and PATHEXT)",
		)
	options, args = parser.parse_args(*args)
	
	try:
		param = args.pop()
		if args:
			parser.error("Too many parameters specified")
			raise SystemExit(1)
		if not '=' in param:
			parser.error("Expected <name>= or <name>=<value>")
			raise SystemExit(2)
		name, value = param.split('=')
		options.class_.set(name, value, options)
	except IndexError:
		options.class_.show()
