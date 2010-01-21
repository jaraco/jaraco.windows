#!/usr/bin/env python
#-*- coding: utf-8 -*-

# $Id$

import itertools

try:
	import wmi as wmilib
except ImportError:
	pass

from ctypes import Structure, windll, POINTER
from ctypes.wintypes import BYTE, DWORD, BOOL

from jaraco.windows.error import handle_nonzero_success
from jaraco.util.iter_ import consume

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
	consume(itertools.takewhile(not_power_status_change, events))

def get_unique_power_states():
	"""
	Just like get_power_states, but ensures values are returned only
	when the state changes.
	"""
	from jaraco.util.iter_ import unique_justseen
	return unique_justseen(get_power_states())

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