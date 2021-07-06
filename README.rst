.. image:: https://img.shields.io/pypi/v/jaraco.windows.svg
   :target: `PyPI link`_

.. image:: https://img.shields.io/pypi/pyversions/jaraco.windows.svg
   :target: `PyPI link`_

.. _PyPI link: https://pypi.org/project/jaraco.windows

.. image:: https://github.com/jaraco/jaraco.windows/workflows/tests/badge.svg
   :target: https://github.com/jaraco/jaraco.windows/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: Black

.. image:: https://readthedocs.org/projects/jaracowindows/badge/?version=latest
   :target: https://jaracowindows.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2021-informational
   :target: https://blog.jaraco.com/skeleton


A pure-python interface to Windows
APIs using ctypes. This package is not designed to be exhaustive, but
rather to supply interfaces as they are needed by the contributors.

Package Contents
================

``jaraco.windows`` contains several modules for different purposes. For now,
read the source. Eventually, I hope to put high-level descriptions of the modules
here.

Installation
============

You should install this module the normal way using pip.

If you want to monkeypatch the os module to include symlink compatibility, you
should add the following to your ``usercustomize`` or ``sitecustomize`` module:

	``import jaraco.windows.filesystem as fs; fs.patch_os_module()``

Thereafter, you should be able to use ``os.symlink`` and ``os.readlink`` in Windows
Vista and later using the same interface as on Unix.

Note that ``jaraco.windows.filesystem.symlink`` takes an additional optional
parameter ``target_is_directory``, which must be specified if the target is not
present and is expected to be a directory once present.

Contribute
==========

If jaraco.windows doesn't supply the interface you require for your
application, consider creating the interface and providing a pull request
to the project.
