#-*- coding: utf-8 -*-

from __future__ import print_function

import itertools
import contextlib
import ctypes

from ctypes import Structure, windll, POINTER
from ctypes.wintypes import BYTE, DWORD, BOOL

try:
	import wmi as wmilib
except ImportError:
	pass

import jaraco.util.itertools as jiter
from jaraco.windows.error import handle_nonzero_success

class SYSTEM_POWER_STATUS(Structure):
	_fields_ = (
		('ac_line_status', BYTE),
		('battery_flag', BYTE),
		('battery_life_percent', BYTE),
		('reserved', BYTE),
		('battery_life_time', DWORD),
		('battery_full_life_time', DWORD),
		)

	@property
	def ac_line_status_string(self):
		return {0:'offline', 1: 'online', 255: 'unknown'}[self.ac_line_status]

LPSYSTEM_POWER_STATUS = POINTER(SYSTEM_POWER_STATUS)
def GetSystemPowerStatus():
	GetSystemPowerStatus = windll.kernel32.GetSystemPowerStatus
	GetSystemPowerStatus.argtypes = (LPSYSTEM_POWER_STATUS,)
	GetSystemPowerStatus.restype = BOOL
	stat = SYSTEM_POWER_STATUS()
	handle_nonzero_success(GetSystemPowerStatus(stat))
	return stat

def _init_power_watcher():
	global power_watcher
	if 'power_watcher' not in globals():
		wmi = wmilib.WMI()
		query = 'SELECT * from Win32_PowerManagementEvent'
		power_watcher = wmi.ExecNotificationQuery(query)

def get_power_management_events():
	_init_power_watcher()
	while True:
		yield power_watcher.NextEvent()

def wait_for_power_status_change():
	EVT_POWER_STATUS_CHANGE = 10
	def not_power_status_change(evt):
		return evt.EventType != EVT_POWER_STATUS_CHANGE
	events = get_power_management_events()
	jiter.consume(itertools.takewhile(not_power_status_change, events))

def get_unique_power_states():
	"""
	Just like get_power_states, but ensures values are returned only
	when the state changes.
	"""
	return jiter.unique_justseen(get_power_states())

def get_power_states():
	"""
	Continuously return the power state of the system when it changes.
	This function will block indefinitely if the power state never
	changes.
	"""
	while True:
		state = GetSystemPowerStatus()
		yield state.ac_line_status_string
		wait_for_power_status_change()

SetThreadExecutionState = ctypes.windll.kernel32.SetThreadExecutionState
SetThreadExecutionState.argtypes = [ctypes.c_uint]
SetThreadExecutionState.restype = ctypes.c_uint

class ES:
	"""
	Execution state constants
	"""
	continuous = 0x80000000
	system_required = 1
	display_required = 2
	awaymode_required = 0x40


@contextlib.contextmanager
def no_sleep():
	"""
	Context that prevents the computer from going to sleep.
	"""
	mode = ES.continuous | ES.system_required
	handle_nonzero_success(SetThreadExecutionState(mode))
	try:
		yield
	finally:
		handle_nonzero_success(SetThreadExecutionState(ES.continuous))
