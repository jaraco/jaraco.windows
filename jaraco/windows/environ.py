#!/usr/bin/env python

# $Id$

import ctypes
import ctypes.wintypes

from jaraco.windows import error

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
	