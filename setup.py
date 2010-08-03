# -*- coding: UTF-8 -*-

""" Setup script for building jaraco.windows distribution

Copyright © 2009 Jason R. Coombs
"""

import os
import functools
from setuptools import setup, find_packages, Distribution

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'

class VersionCallableDistribution(Distribution):
	"""
	A Distribution class that allows the version to be a callable, so
	the version can be calculated, and the calculation can be dependent
	on setup-time dependencies specified in setup_requires.
	"""
	def __init__(self, *args, **kwargs):
		parent = self.__class__.__bases__[0]
		parent.__init__(self, *args, **kwargs)
		if hasattr(self.metadata.version, '__call__'):
			self.metadata.version = self.metadata.version()

try:
	from distutils.command.build_py import build_py_2to3 as build_py
	# exclude some fixers that break already compatible code
	from lib2to3.refactor import get_fixers_from_package
	fixers = get_fixers_from_package('lib2to3.fixes')
	for skip_fixer in ['import']:
		fixers.remove('lib2to3.fixes.fix_' + skip_fixer)
	build_py.fixer_names = fixers
except ImportError:
	from distutils.command.build_py import build_py

name = 'jaraco.windows'

def get_version(default='unknown'):
	import hgtools
	os.environ['HGTOOLS_FORCE_CMD'] = 'True'
	mgr = hgtools.get_manager()
	tag = mgr.get_tag()
	if tag and tag != 'tip':
		return tag
	return default

setup (name = name,
		version = '1.9',
		distclass=VersionCallableDistribution,
		description = 'Windows Routines by Jason R. Coombs',
		long_description = open('docs/index.txt').read().strip(),
		author = 'Jason R. Coombs',
		author_email = 'jaraco@jaraco.com',
		url = 'http://pypi.python.org/pypi/'+name,
		packages = find_packages(exclude=['ez_setup', 'tests', 'examples']),
		zip_safe=True,
		namespace_packages = ['jaraco',],
		license = 'MIT',
		classifiers = [
			"Development Status :: 4 - Beta",
			"Intended Audience :: Developers",
			"Programming Language :: Python",
		],
		entry_points = dict(
			console_scripts = [
				'xmouse = jaraco.windows.xmouse:run',
				'mklink = jaraco.windows.filesystem:mklink',
				'find-symlinks = jaraco.windows.filesystem:find_symlinks_cmd',
				'enver = jaraco.windows.environ:enver',
			],
		),
		install_requires=[
			'jaraco.util>=3.0dev-r1143',
		],
		extras_require = {
		},
		dependency_links = [
		],
		tests_require=[
			'nose>=0.10',
		],
		setup_requires=[
			'hgtools',
		],
		test_suite = "nose.collector",
		cmdclass=dict(build_py=build_py),
	)
