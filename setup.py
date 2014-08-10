# -*- coding: UTF-8 -*-

""" Setup script for building jaraco.windows distribution

Copyright © 2009-2013 Jason R. Coombs
"""

from setuptools import find_packages

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'

name = 'jaraco.windows'

with open('README') as readme:
	long_description = readme.read()

with open('CHANGES') as changes:
	long_description += "\n" + changes.read()

setup_params = dict(
	name = name,
	use_hg_version = dict(increment='0.0.1'),
	description = 'Windows Routines by Jason R. Coombs',
	long_description = long_description,
	author = 'Jason R. Coombs',
	author_email = 'jaraco@jaraco.com',
	url = 'http://pypi.python.org/pypi/' + name,
	packages = find_packages(),
	zip_safe=True,
	namespace_packages = ['jaraco'],
	license = 'MIT',
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 3",
		"Operating System :: Microsoft :: Windows",
	],
	entry_points = dict(
		console_scripts = [
			'xmouse = jaraco.windows.xmouse:Command.invoke',
			'mklink = jaraco.windows.filesystem:mklink',
			'find-symlinks = jaraco.windows.filesystem:find_symlinks_cmd',
			'enver = jaraco.windows.environ:enver',
			'pclip = jaraco.windows.clipboard:paste_stdout',
			'gclip = jaraco.windows.clipboard:stdin_copy',
		],
	),
	install_requires=[
		'jaraco.util>=3.9dev',
		'more_itertools',
		'six',
	],
	extras_require = {
	},
	dependency_links = [
	],
	tests_require=[
		'pytest',
	],
	setup_requires=[
		'hgtools',
		'pytest-runner',
	],
)

if __name__ == '__main__':
	from setuptools import setup
	setup(**setup_params)
