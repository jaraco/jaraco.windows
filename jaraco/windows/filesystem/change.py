# -*- coding: UTF-8 -*-

"""
FileChange
	Classes and routines for monitoring the file system for changes.

Copyright © 2004, 2011 Jason R. Coombs
"""

import os
import sys
import time
import re
import operator
from threading import Thread
import traceback
from stat import *
import itertools
import logging

from jaraco.util.itertools import consume
import jaraco.util.string

import jaraco.windows.api.filesystem
import jaraco.windows.api.event

log = logging.getLogger(__name__)

class NotifierException(Exception):
	pass

class FileFilter(object):
	def set_root(self, root):
		self.root = root

	def _get_file_path(self, filename):
		try:
			filename = os.path.join(self.root, filename)
		except AttributeError: pass
		return filename

class ModifiedTimeFilter(FileFilter):
	"""
	Returns true for each call where the modified time of the file is after
	the cutoff time.
	"""
	def __init__(self, cutoff):
		# truncate the time to the second.
		self.cutoff = int(cutoff)

	def __call__(self, file):
		filepath = self._get_file_path(file)
		last_mod = os.stat(filepath).st_mtime
		log.debug('%s last modified at %s.', filepath, time.asctime(time.localtime(last_mod)))
		return last_mod >= self.cutoff

class PatternFilter(FileFilter):
	"""
	Filter that returns True for files that match pattern (a regular
	expression).
	"""
	def __init__(self, pattern):
		self.pattern = re.compile(pattern) if isinstance(pattern, basestring) else pattern

	def __call__(self, file):
		return bool(self.pattern.match(file, re.I))

class GlobFilter(PatternFilter):
	"""
	Filter that returns True for files that match the pattern (a glob
	expression.
	"""
	def __init__(self, expression):
		super(GlobFilter, self).__init__(self.convert_file_pattern(expression))

	@staticmethod
	def convert_file_pattern(p):
		r"""
		converts a filename specification (such as c:\*.*) to an equivelent regular expression
		>>> GlobFilter.convert_file_pattern('/*')
		'/.*'
		"""
		subs = (('\\', '\\\\'), ('.', '\\.'), ('*', '.*'), ('?', '.'))
		return jaraco.util.string.multi_substitution(*subs)(p)


class AggregateFilter(FileFilter):
	"""
	This file filter will aggregate the filters passed to it, and when called, will
	  return the results of each filter ANDed together.
	"""
	def __init__(self, *filters):
		self.filters = filters

	def set_root(self, root):
		consume(f.set_root(root) for f in self.filters)

	def __call__(self, file):
		return all(fil(file) for fil in self.filters)

def files_with_path(files, path):
	return (os.path.join(path, file) for file in files)

def get_file_paths(walk_result):
	root, dirs, files = walk_result
	return files_with_path(files, root)

class Notifier(object):
	def __init__(self, root = '.', filters = []):
		# assign the root, verify it exists
		self.root = root
		if not os.path.isdir(self.root):
			raise NotifierException('Root directory "%s" does not exist' % self.root)
		self.filters = filters

		self.watch_subtree = False
		self.quit_event = jaraco.windows.api.event.CreateEvent(None, 0, 0, None)

	def __del__(self):
		try:
			jaraco.windows.api.filesystem.FindCloseChangeNotification(self.hChange)
		except: pass

	def _get_change_handle(self):
		# set up to monitor the directory tree specified
		self.hChange = jaraco.windows.api.filesystem.FindFirstChangeNotification(
			self.root,
			self.watch_subtree,
			jaraco.windows.api.filesystem.FILE_NOTIFY_CHANGE_LAST_WRITE,
		)

		# make sure it worked; if not, bail
		INVALID_HANDLE_VALUE = jaraco.windows.api.filesystem.INVALID_HANDLE_VALUE
		if self.hChange == INVALID_HANDLE_VALUE:
			raise NotifierException('Could not set up directory change notification')

	@staticmethod
	def _filtered_walk(path, file_filter):
		"""
		static method that calls os.walk, but filters out
		anything that doesn't match the filter
		"""
		for root, dirs, files in os.walk(path):
			log.debug('looking in %s', root)
			log.debug('files is %s', files)
			file_filter.set_root(root)
			files = filter(file_filter, files)
			log.debug('filtered files is %s', files)
			yield (root, dirs, files)

	def quit(self):
		SetEvent(self.quit_event)

class BlockingNotifier(Notifier):

	@staticmethod
	def wait_results(*args):
		""" calls WaitForMultipleObjects repeatedly with args """
		return itertools.starmap(
			jaraco.windows.api.event.WaitForMultipleObjects,
			itertools.repeat(args))

	def get_changed_files(self):
		self._get_change_handle()
		check_time = time.time()
		# block (sleep) until something changes in the
		#  target directory or a quit is requested.
		# timeout so we can catch keyboard interrupts or other exceptions
		WAIT_OBJECT_0 = jaraco.windows.api.event.WAIT_OBJECT_0
		for result in BlockingNotifier.wait_results((self.hChange, self.quit_event), False, 1000):
			if result == WAIT_OBJECT_0 + 0:
				# something has changed.
				log.debug('Change notification received')
				next_check_time = time.time()
				jaraco.windows.api.filesystem.FindNextChangeNotification(self.hChange)
				log.debug('Looking for all files changed after %s', time.asctime(time.localtime(check_time)))
				for file in self.find_files_after(check_time):
					yield file
				check_time = next_check_time
			if result == WAIT_OBJECT_0 + 1:
				# quit was received, stop yielding stuff
				return
			else:
				pass # it was a timeout.  ignore it and wait some more.

	def find_files_after(self, cutoff):
		mtf = ModifiedTimeFilter(cutoff)
		af = AggregateFilter(mtf, *self.filters)
		results = Notifier._filtered_walk(self.root, af)
		results = itertools.imap(get_file_paths, results)
		if self.watch_subtree:
			result = itertools.chain(*results)
		else:
			result = next(results)
		return result

class ThreadedNotifier(BlockingNotifier, Thread):
	r"""
	ThreadedNotifier provides a simple interface that calls the handler
	for each file rooted in root that passes the filters.  It runs as its own
	thread, so must be started as such.

	>>> notifier = ThreadedNotifier('c:\\', handler = StreamHandler()) # doctest: +SKIP
	>>> notifier.start() # doctest: +SKIP
	C:\Autoexec.bat changed.
	"""
	def __init__(self, root = '.', filters = [], handler = lambda file: None):
		# init notifier stuff
		BlockingNotifier.__init__(self, root, filters)
		# init thread stuff
		Thread.__init__(self)
		# set it as a daemon thread so that it doesn't block waiting to close.
		#  I tried setting __del__(self) to .quit(), but unfortunately, there are
		#  references to this object in the win32api stuff, so __del__ never gets
		#  called.
		self.setDaemon(True)

		self.handle = handler

	def run(self):
		for file in self.get_changed_files():
			self.handle(file)

class StreamHandler(object):
	"""
	StreamHandler: a sample handler object for use with the threaded
	notifier that will announce by writing to the supplied stream
	(stdout by default) the name of the file.
	"""
	def __init__(self, output = sys.stdout):
		self.output = output

	def __call__(self, filename):
		self.output.write('%s changed.\n' % filename)
