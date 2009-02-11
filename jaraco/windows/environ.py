#!/usr/bin/env python

# $Id

import ctypes
import ctypes.wintypes

from jaraco.windows import error

_SetEnvironmentVariable = ctypes.windll.kernel32.SetEnvironmentVariableW
_SetEnvironmentVariable.restype = ctypes.wintypes.BOOL
_SetEnvironmentVariable.argtypes = [ctypes.wintypes.LPCWSTR]*2

def SetEnvironmentVariable(name, value):
	error.handle_nonzero_success(_SetEnvironmentVariable(name, value))

def ClearEnvironmentVariable(name):
	error.handle_nonzero_success(_SetEnvironmentVariable(name, None))