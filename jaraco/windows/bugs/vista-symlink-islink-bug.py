import os
import sys

try:
    from jaraco.windows.filesystem import symlink
except ImportError:
    # a dirty reimplementation of symlink from jaraco.windows
    from ctypes import windll
    from ctypes.wintypes import BOOLEAN, DWORD, LPWSTR

    CreateSymbolicLink = windll.kernel32.CreateSymbolicLinkW
    CreateSymbolicLink.argtypes = (LPWSTR, LPWSTR, DWORD)
    CreateSymbolicLink.restype = BOOLEAN

    def symlink(target, link, target_is_directory=False):
        """
        An implementation of os.symlink for Windows (Vista and greater)
        """
        target_is_directory = target_is_directory or os.path.isdir(target)
        CreateSymbolicLink(link, target, target_is_directory)


assert sys.platform in ('win32',)
os.makedirs(r'.\foo')
assert os.path.isdir(r'.\foo')

symlink(r'.\foo', r'.\foo_sym')
assert os.path.isdir(r'.\foo_sym')
assert os.path.islink(r'.\foo_sym')  # fails
