# -*- coding: UTF-8 -*-

""" Setup script for building jaraco.windows distribution

Copyright © 2009-2010 Jason R. Coombs
"""

import os
import functools
from setuptools import setup, find_packages, Distribution

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'

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

setup (
		name = name,
		use_hg_version = True,
		description = 'Windows Routines by Jason R. Coombs',
		long_description = open('README').read(),
		author = 'Jason R. Coombs',
		author_email = 'jaraco@jaraco.com',
		url = 'http://pypi.python.org/pypi/'+name,
		packages = find_packages(),
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
				'pclip = jaraco.windows.clipboard:paste_stdout',
				'gclip = jaraco.windows.clipboard:stdin_copy',
			],
		),
		install_requires=[
			'jaraco.util>=3.5.2dev',
		],
		extras_require = {
		},
		dependency_links = [
		],
		tests_require=[
			'nose>=0.10',
		],
		setup_requires=[
			'hgtools >= 0.4.7',
		],
		test_suite = "nose.collector",
		cmdclass=dict(build_py=build_py),
	)
