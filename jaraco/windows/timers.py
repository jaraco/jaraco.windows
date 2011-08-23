# -*- coding: UTF-8 -*-

"""
timers
	In particular, contains a waitable timer.

Copyright © 2004,2011 Jason R. Coombs
"""

import time
import win32event
import threading

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'

class WaitableTimer:
	def __init__(self):
		self.SignalEvent = win32event.CreateEvent(None, 0, 0, None)
		self.StopEvent = win32event.CreateEvent(None, 0, 0, None)

	def Set(self, dueTime, period):
		threading.start_new_thread(self._SignalLoop_, (dueTime, period))

	def Stop(self):
		win32event.SetEvent(self.StopEvent)

	def WaitForSignal(self, timeoutSeconds = None):
		if not timeoutSeconds:
			timeoutMilliseconds = win32event.INFINITE
		else:
			timeoutMilliseconds = int(timeoutSeconds * 1000)
		win32event.WaitForSingleObject(self.SignalEvent, timeoutMilliseconds)

	def _SignalLoop_(self, dueTime, period):
		if not dueTime and not period:
			raise ValueError("dueTime or period must be non-zero")
		try:
			if not dueTime:
				dueTime = time.time() + period
			if dueTime:
				self._Wait_(dueTime - time.time())
			while period:
				dueTime += period
				self._Wait_(dueTime - time.time())
		except Exception:
			pass

		#we're done here, just quit

	def _Wait_(self, seconds):
		milliseconds = int(seconds*1000)
		if milliseconds > 0:
			res = win32event.WaitForSingleObject(self.StopEvent, milliseconds)
			if res == win32event.WAIT_OBJECT_0: raise Exception
			if res == win32event.WAIT_TIMEOUT: pass
		win32event.SetEvent(self.SignalEvent)

	def getEvenDueTime(self, period):
		now = time.time()
		return now - (now % period)
