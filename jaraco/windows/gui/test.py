"""
GUI test support module

Based on watsup and winGuiAuto
"""

import re
from time import sleep
import win32gui

from watsup.launcher import AppThread
from watsup.winGuiAuto import (
	findTopWindow, findTopWindows,
	activateMenuItem, getTopMenu,
	_getMenuInfo, WinGuiAutoError,
	)

class AppWindow(object):
	def __init__(self, handle):
		self._handle = handle

	@classmethod
	def find(cls, *args, **kwargs):
		return cls(findTopWindow(*args, **kwargs))

	def get_menu(self):
		return Menu.get_main(self._handle)

def launch_app(program,wantedText=None,wantedClass=None,verbose=False,delay=0):
	global p
	p=AppThread(program,verbose)
	p.start()
	sleep(delay)
	try:
		return AppWindow.find(wantedText=wantedText,wantedClass=wantedClass)
	except WinGuiAutoError,e:
		pass

def _normalize_control_text(control_text, use_mnemonic=True):
	"""
	Normalize the control text suitable for matching a control.
	
	If use_mnemonic is True (default), remove single ampersands and
	replace double-ampersands with single ampersands.
	
	>>> _normalize_control_text('&Copy && Paste')
	'copy & paste'
	
	If the labels are not using mnemonics, run this with use_mnemonic
	= False
	>>> _normalize_control_text('Copy & Paste', use_mnemonic=False)
	'copy & paste'
	"""
	result = control_text.lower()
	single_amp_pattern = re.compile('&(.)')
	mnemonic_result = single_amp_pattern.sub(r'\1', result)
	return [result, mnemonic_result][use_mnemonic]

class Menu(object):
	def __init__(self, handle):
		self._handle = handle

	@classmethod
	def get_main(cls, wnd):
		"""
		Get the main menu for a window
		"""
		return cls(getTopMenu(wnd))

	@property
	def item_count(self):
		return win32gui.GetMenuItemCount(self._handle)

	def traverse(self, item_path):
		def _find_submenu_or_item(menu_handle, submenu_name):
			"Return the submenu handle (if it is a submenu); otherwise, return the menuinfo"
			res = _find_named_submenu(menu_handle, submenu_name)[1]
			return res.submenu or res
		return reduce(_find_submenu_or_item, item_path, self._handle)

def _find_named_submenu(menu_handle, submenu_name):
	"""
	Find the index number of a menu's submenu with a specific name and
	the submenu itself.
	
	For example,
	>>> index, submenu = _find_named_submenu(hMenu, 'File') #doctest:+SKIP
	"""
	menu_item_count = win32gui.GetMenuItemCount(menu_handle)
	submenus = map(lambda i: _getMenuInfo(menu_handle, i), range(menu_item_count))
	target = _normalize_control_text(submenu_name)
	menu_matches = lambda m: _normalize_control_text(m.name).startswith(target)
	matching_menus = filter(menu_matches, submenus)
	#if len(matching_menus) > 1:
	#	raise WinGuiAutoError("More than one submenu matched %s" % submenu_name)
	if not matching_menus:
		raise WinGuiAutoError("No submenu found for %s" % submenu_name)
	result = matching_menus[0]
	return submenus.index(result), result
