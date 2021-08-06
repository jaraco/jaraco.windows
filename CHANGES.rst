v5.6.0
======

* Added jaraco.windows.msvc, containing a routine for
  installing MSVC in a Docker image. Docker image now
  builds with MSVC support.

v5.5.0
======

* Removed Python 2 compatibility.

v5.4.0
======

* Switch to PEP 420 for namespace package.
* Require Python 3.6 or later.

v5.3.0
======

* ``symlink`` function now supplies the
  ``SYMBOLIC_LINK_FLAG_ALLOW_UNPRIVILEGED_CREATE`` flag
  so that symbolic links can be created without elevated
  privileges as long as developer mode is enabled. See
  `this blog
  <https://blogs.windows.com/windowsdeveloper/2016/12/02/symlinks-windows-10/>`_
  for more details.

v5.2.0
======

* Add ``batch`` module from ``jaraco.develop.environ``.

v5.1.0
======

* #16: Added ability to construct HTMLSnippet from a fragment,
  utilizing that function in set_html. Now ``get/set_html`` are
  tested and work as intended.

v5.0.0
======

* Require Python 3.6 and later.

4.0
===

Switch to `pkgutil namespace technique
<https://packaging.python.org/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages>`_
for the ``jaraco`` namespace.

3.9.2
=====

* #14: Ensure handle is closed in ``filesystem.get_file_info``.

3.9.1
=====

* #13: Fixed TypeError on Python 3 in clipboard.get_html().

3.9
===

* Added new module ``jaraco.windows.filesystem.backports``
  with ``realpath`` backport from `issue9949-v4.patch
  <https://bugs.python.org/issue9949>`_.

3.8.1
=====

* #11: ``jaraco.windows.api.filesystem`` now relies on
  ``ctypes.wintypes.WIN32_FIND_DATAW``, avoiding conflict
  with scandir.

3.8
===

* #10: Added new method to ``jaraco.windows.filesystem``:

  - ``samefile``: backport of os.path.samefile from Python 3.2
    with Windows support for Python 2.7.

3.7.1
=====

* Fixed AttributeError in ``get_final_path``.

3.7
===

* Update reference to ``path.Path`` for compatibility
  with ``path.py 10``.

* Configured project to use `AppVeyor for tests
  <https://ci.appveyor.com/project/jaraco/jaraco-windows>`_.

3.6.3
=====

* Re-release using pypi.org to avoid caching issues.

3.6.2
=====

* Issue #8: Correct argtype to ``c_size_t`` in
  ``GlobalAlloc``. Better aligns with advertised
  API and improves Python version support.

3.6.1
=====

* Issue #7: Added declarations of arguments and result types
  to some ctypes calls, correcting intermittent test failures.

3.6
===

* Moved hosting to Github.

3.5
===

* Issue #6: Fix TypeError in os.readlink.
* Updated project skeleton to include documentation and wheel
  releases.

3.4.1
=====

* Issue #5: Fix ValueError in mmap memory copy routine on 32-bit
  systems.

3.4
===

* Add ``set_html`` function to ``clipboard`` module.

3.3
===

* Backported `Paramiko #193 <https://github.com/paramiko/paramiko/issues/193>`_
  (`change <https://github.com/paramiko/paramiko/commit/d8738b1b0f10e2f70ac69c3e3dbf10e496c8a67f>`_). Use RtlMoveMemory in favor
  of memcpy.
* Fixed AccessViolation on Python 3 in mmap module.
* Fixed AttributeError in security module.

3.2
===

* Dropped dependency on jaraco.util in favor of smaller packages.

3.1.2
=====

* Correct typo in jaraco.windows.api.filesystem (Issue #4).

3.1.1
=====

* Correct invocation of enver.

3.1
===

* Added clipboard.get_image helper.

3.0.1
=====

* Substantial fixes on Python 3.
* Fixed regression in clipboard module.
* Restored changes from 2.16, unintentionally omitted from 3.0.

3.0
===

* Moved many of the API definitions to the ``jaraco.windows.api`` package.

2.16
====

* Allow enver to be invoked with python -m jaraco.windows.environ
* Add nominal support for credential vault.

2.15.1
======

* Fixed constants around ``power.no_sleep``.

2.15
====

* Improved Python 3 support including working gclip and pclip commands.

2.14
====

* Added py2exe support to the package.

2.13.2
======

* Improvements to file change handling, reducing duplicates.

2.13
====

* Added `no_sleep` context manager to the power module.

2.12
====

* Added `add` method to the environ RegisteredEnvironments. Use it to add
  a value to a list of values but only if it's not already present.

2.11.1
======

* Fixed issue in set_unicode_text.

2.11
====

* Add `clipboard.set_unicode_text`.

2.10
====

* Fixed issue where MemoryMap wouldn't read null bytes.
* Added security.get_security_attributes_for_user.

2.9
===

* Added mmap module with MemoryMap class. This class allows the client to
  specify SECURITY_ATTRIBUTES, which the Python mmap module does not.
* Added security module with support for security descriptors and security
  attributes.

2.8
===

* Added vpn module with support for creating PPTP connections.

2.7
===

* Added filesystem.SetFileAttributes

2.6
===

* Fixed import issue in jaraco.windows.filesystem on Python 3.
* Added cookie module from jaraco.net.
* Fixed issue in filesystem.islink() where a call against a nonexistent
  file could raise an Exception.

2.5
===

* Moved timers module from jaraco.util.
* Added jaraco.windows.cred with initial support for Windows Credential
  Manager.

2.4
===

* Moved filechange notification from jaraco.util.

2.3
===

* Added filesystem.GetFileAttributes.
* Added services module for working with Windows Services (currently uses
  pywin32).

2.2
===

* Fixes by wkornewald for issue #1 - Symlink relative path deficiencies.
* Added jaraco.windows.message.SendMessageTimeout.
* Fixed issue where environment changes would stall on SendMessage.
* SendMessage now uses the correct type for lParam, but will still accept
  string types.

2.1
===

* Added jaraco.windows.user module (with get_user_name function).
* Added get_unicode_text to clipboard module.

2.0
===

* Added clipboard.set_text function for a simple routine for setting
  clipboard text.
* Added support for editing environment variables in a text-editor.
* Added clipboard.get_html and clipboard.HTMLSnippet for supporting
  the HTML format from the clipboard.

1.9.1
=====

* Fixed issue with clipboard handling of null-terminated strings

1.9
===

* Added eventlog utility
* Added support for other clipboard formats (including DIB and DIBV5), and now clipboards to proper memory locking while reading the resource
* Added registry module
* Moved office module to jaraco.office project

1.8
===

* Added 2to3 build support - now installs on Python 3
* Removed default import of jaraco.windows.net into jaraco.windows
* Fixed division operator issue in jaraco.windows.reparse.

1.7
===

* Added option to enver to remove values from a path or other semi-
  colon-separated value.
* Added privilege module.
* Made `jaraco.windows.error.WindowsError` a subclass of
  `__builtin__.WindowsError`.
* Added office module with MS Word based PDF Converter.
* Added early implementation of clipboard support.
* Added delay option to xmouse.

1.6
===

* Added monkeypatch for os.symlink and os.readlink.
* Added find-symlinks command.

1.5
===

* NB!! Switched the order of the parameters for symlink and link to match the
  signature found in the ``os`` module. This will absolutely break any implementations
  that worked with ``jaraco.windows`` prior to 1.5.

1.4
===

* Added more robust support for symlink support (including a symlink traversal
  routine that works even when the target is locked). This method uses explicit
  reparse point parsing, using the new reparse module.
* Added support for hardlinks.
* Added jaraco.windows.lib for locating loaded modules.
* Added command line parameters to environ to allow override of default
  append/replace behavior.
* Added power monitoring utilities.
* Began work on GUI testing objects in jaraco.windows.gui.test, based on watsup.
* Added filesystem.GetBinaryType
* Added filesystem.SHFileOperation (useful for sending items to a Recycle Bin).
* Updated enver to support appending to a non-existent variable.
* Added a 'show' option to xmouse
* Added routines to support the Microsoft Data Protection API (DPAPI).

1.3
===

* Added -U option to enver

1.2
===

* Added this documentation
* Updated the project website to use PYPI directly.
* Improved deployment support (fixes issues with easy_install)
* Fixed issue with PATH and PATHEXT handling in enver.

1.1
===

* Added support for persistent environment variable setting (inspired by
  enver.py)

1.0
===

* Initial release
* Includes xmouse script for enabling/disabling focus-follows-mouse
