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

# TODO: remove dependency on pywin32
import win32gui, win32con

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
	path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
	hklm = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
	key = winreg.OpenKey(hklm, path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
	
	@classmethod
	def show(class_):
		for name, value, type in registry_key_values(class_.key):
			sys.stdout.write('='.join((name, value)) + '\n')
			
	@classmethod
	def set(class_, name, value):
		# consider opening the key read-only except for here
		# key = winreg.OpenKey(class_.key, None, 0, winreg.KEY_WRITE)
		# and follow up by closing it.
		if not value:
			return class_.delete(name)
		if name.upper() in ('PATH', 'PATHEXT'):
			existing_value = class_.get(name)
			value = ';'.join(existing_value, value)
		winreg.SetValueEx(class_.key, name, 0, winreg.REG_EXPAND_SZ, value)
		class_.notify()
	
	@classmethod
	def delete(class_, name):
		winreg.DeleteValue(class_.key, name)
		class_.notify()
	
	@classmethod
	def notify(class_):
		win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')

def enver():
	from optparse import OptionParser
	usage = """
Usage:

Show all environment variables - %prog
Add/Modify/Delete environment variable - %prog <name>=[value]

If <name> is PATH or PATHEXT, %prog will append the value prefixed with ;

If there is no value, %prog will delete the <name> environment variable

Note that %prog does not affect the current running environment, and can
only affect new command windows.
"""
	parser = OptionParser(usage=usage)
	options, args = parser.parse_args()
	try:
		param = args.pop()
		if args:
			parser.parser_error("Too many parameters specified")
			raise Exception("need to exit here")
		if not '=' in param:
			parser.parser_error("Expected <name>= or <name>=<value>")
			raise Exception("need to exit here")
		RegisteredEnvironment.set(*param.split('='))
	except IndexError:
		RegisteredEnvironment.show()
