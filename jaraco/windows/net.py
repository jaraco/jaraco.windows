#!/usr/bin/env python

# $Id$

"""
API hooks for network stuff.
"""

__all__ = ('AddConnection')

import ctypes
import ctypes.wintypes

# TODO: remove dependency on pywin32
import win32api
import win32netcon

# MPR - Multiple Provider Router
mpr = ctypes.windll.mpr

class NETRESOURCE(ctypes.Structure):
	_fields_ = [
		('scope', ctypes.wintypes.DWORD),
		('type', ctypes.wintypes.DWORD),
		('display_type', ctypes.wintypes.DWORD),
		('usage', ctypes.wintypes.DWORD),
		('local_name', ctypes.wintypes.LPWSTR),
		('remote_name', ctypes.wintypes.LPWSTR),
		('comment', ctypes.wintypes.LPWSTR),
		('provider', ctypes.wintypes.LPWSTR),
		]

class WindowsError(Exception):
	"more info about errors at http://msdn.microsoft.com/en-us/library/ms681381(VS.85).aspx"

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return win32api.FormatMessage(self.value)

def make_wide(param):
	"""
	Take a parameter and if it's a narrow string, make it a wide
	string.
	"""
	if isinstance(param, basestring) and not isinstance(param, unicode):
		return unicode(param)
	return param

make_wide = lambda p: p

def AddConnection(
	remote_name,
	type=win32netcon.RESOURCETYPE_ANY,
	local_name=None,
	provider_name=None,
	user=None,
	password=None,
	flags=0):
	resource = NETRESOURCE(
		type=type,
		remote_name=remote_name,
		local_name=local_name,
		provider_name=provider_name,
		# WNetAddConnection2 ignores the other members of NETRESOURCE
		)
	
	result = mpr.WNetAddConnection2W(
		ctypes.byref(resource),
		make_wide(password),
		make_wide(user),
		flags,
		)

	if result != 0:
		raise WindowsError(result)
