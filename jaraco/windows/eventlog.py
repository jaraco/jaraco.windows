import functools
from contextlib import contextmanager
from itertools import imap

import win32api, win32con, winerror, win32evtlog, win32evtlogutil

from jaraco.util.iter_ import consume

error = win32api.error # The error the evtlog module raises.

class EventLog(object):
	def __init__(self, name="Application", machine_name=None):
		self.machine_name = machine_name
		self.name = name
		self.formatter = functools.partial(win32evtlogutil.FormatMessage, logType=self.name)

	def __enter__(self):
		if hasattr(self, 'handle'):
			raise ValueError("Overlapping attempts to use this log context")
		self.handle = win32evtlog.OpenEventLog(self.machine_name, self.name)
		return self

	def __exit__(self, *args):
		win32evtlog.CloseEventLog(self.handle)
		del self.handle
		
	def get_records(self, flags=win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ):
		with self:
			while True:
				objects = win32evtlog.ReadEventLog(self.handle, flags, 0)
				if not objects:
					break
				for item in objects:
					yield item

	def __iter__(self):
		return self.get_records()

	def format_record(self, record):
		return self.formatter(record)

	def format_records(self, records=None):
		if records is None:
			records = self.get_records()
		return imap(self.format_record, records)