# -*- coding: UTF-8 -*-

"""FileChange
	Classes and routines for monitoring the file system for changes.

Copyright © 2004 Jason R. Coombs
"""

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'
__version__ = '$Rev$'[6:-2]
__svnauthor__ = '$Author$'[9:-2]
__date__ = '$Date$'[7:-2]

import os, sys, time, re, operator
from threading import Thread
import traceback
from stat import *
import itertools
from jaraco.util.itertools import consume
import jaraco.util.string

import logging
log = logging.getLogger(__name__)

# win32* requires ActivePython by Mark Hammond (thanks Mark!)
from win32file import *
from win32api import *
from win32event import *
from win32con import FILE_NOTIFY_CHANGE_LAST_WRITE

class NotifierException(Exception):
	pass

class FileFilter(object):
	def SetRoot(self, root):
		self.root = root

	def _GetFilePath(self, filename):
		try:
			filename = os.path.join(self.root, filename)
		except AttributeError: pass
		return filename

class ModifiedTimeFilter(FileFilter):
	""" Returns true for each call where the modified time of the file is after the cutoff time """
	def __init__(self, cutoff):
		# truncate the time to the second.
		self.cutoff = int(cutoff)

	def __call__(self, file):
		filepath = self._GetFilePath(file)
		last_mod = os.stat(filepath).st_mtime
		log.debug('%s last modified at %s.', filepath, time.asctime(time.localtime(last_mod)))
		return last_mod >= self.cutoff

class PatternFilter(FileFilter):
	"""
	This file filter when called will return True for those files that match the pattern.
	  When initialized, exactly one of filePattern or rePattern must be supplied.

	filePattern is a DOS-like file name with wildcards (*,?)
	rePattern is a regular expression.
	"""
	def __init__(self, filePattern = None, rePattern = None):
		if filePattern and rePattern:
			raise TypeError('PatternFilter() takes exactly 1 argument (2 given).')
		if not filePattern and not rePattern:
			raise TypeError('PatternFilter() takes exactly 1 argument (0 given).')
		if filePattern:
			self.pattern = PatternFilter.ConvertFilePattern(filePattern)
		if rePattern:
			self.pattern = rePattern

	@staticmethod
	def ConvertFilePattern(p):
		r"""
		converts a filename specification (such as c:\*.*) to an equivelent regular expression
		>>> PatternFilter.ConvertFilePattern('c:\*')
		'c:\\\\.*'
		"""
		subs = (('\\', '\\\\'), ('.', '\\.'), ('*', '.*'), ('?', '.'))
		return jaraco.util.string.multi_substitution(*subs)(p)

	def __call__(self, file):
		return bool(re.match(self.pattern, file, re.I))

class AggregateFilter(FileFilter):
	"""
	This file filter will aggregate the filters passed to it, and when called, will
	  return the results of each filter ANDed together.
	"""
	def __init__(self, *filters):
		self.filters = filters

	def SetRoot(self, root):
		consume(f.SetRoot(root) for f in self.filters)

	def __call__(self, file):
		results = (fil(file) for fil in self.filters)
		result = reduce(operator.and_, results)
		return result

def filesWithPath(files, path):
	for file in files:
		yield os.path.join(path, file)

def GetFilePaths(walkResult):
	root, dirs, files = walkResult
	return filesWithPath(files, root)

class Notifier(object):
	def __init__(self, root = '.', filters = []):
		# assign the root, verify it exists
		self.root = root
		if not os.path.isdir(self.root):
			raise NotifierException('Root directory "%s" does not exist' % self.root)
		self.filters = filters

		self.watchSubtree = False
		self.QuitEvent = CreateEvent(None, 0, 0, None)

	def __del__(self):
		try:
			FindCloseChangeNotification(self.hChange)
		except: pass

	def _GetChangeHandle(self):
		# set up to monitor the directory tree specified
		self.hChange = FindFirstChangeNotification(
			self.root,
			self.watchSubtree,
			FILE_NOTIFY_CHANGE_LAST_WRITE
		)

		# make sure it worked; if not, bail
		if self.hChange == INVALID_HANDLE_VALUE:
			raise NotifierException('Could not set up directory change notification')

	def _FilteredWalk(path, fileFilter):
		"""
		static method that calls os.walk, but filters out
		anything that doesn't match the filter
		"""
		for root, dirs, files in os.walk(path):
			log.debug('looking in %s', root)
			log.debug('files is %s', files)
			fileFilter.SetRoot(root)
			files = filter(fileFilter, files)
			log.debug('filtered files is %s', files)
			yield (root, dirs, files)
	_FilteredWalk = staticmethod(_FilteredWalk)

	def Quit(self):
		SetEvent(self.QuitEvent)

class BlockingNotifier(Notifier):

	def WaitResults(*args):
		""" calls WaitForMultipleObjects repeatedly with args """
		return itertools.starmap(WaitForMultipleObjects, itertools.repeat(args))
	WaitResults = staticmethod(WaitResults)

	def GetChangedFiles(self):
		self._GetChangeHandle()
		checkTime = time.time()
		# block (sleep) until something changes in the
		#  target directory or a quit is requested.
		# timeout so we can catch keyboard interrupts or other exceptions
		for result in BlockingNotifier.WaitResults((self.hChange, self.QuitEvent), False, 1000):
			if result == WAIT_OBJECT_0 + 0:
				# something has changed.
				log.debug('Change notification received')
				nextCheckTime = time.time()
				FindNextChangeNotification(self.hChange)
				log.debug('Looking for all files changed after %s', time.asctime(time.localtime(checkTime)))
				for file in self.FindFilesAfter(checkTime):
					yield file
				checkTime = nextCheckTime
			if result == WAIT_OBJECT_0 + 1:
				# quit was received, stop yielding stuff
				return
			else:
				pass # it was a timeout.  ignore it and wait some more.

	def FindFilesAfter(self, cutoff):
		mtf = ModifiedTimeFilter(cutoff)
		af = AggregateFilter(mtf, *self.filters)
		results = Notifier._FilteredWalk(self.root, af)
		results = itertools.imap(GetFilePaths, results)
		if self.watchSubtree:
			result = itertools.chain(*results)
		else:
			result = results.next()
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
		#  I tried setting __del__(self) to .Quit(), but unfortunately, there are
		#  references to this object in the win32api stuff, so __del__ never gets
		#  called.
		self.setDaemon(True)

		self.Handle = handler

	def run(self):
		for file in self.GetChangedFiles():
			self.Handle(file)

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
