import contextlib
from ctypes import CDLL, c_char_p


def get_libc():
    libnames = ('msvcrt', 'libc.so.6', 'libc.dylib')
    for libname in libnames:
        with contextlib.suppress(OSError):
            return CDLL(libname)
    raise RuntimeError(f"Unable to find a suitable libc (tried {libnames})")


getenv = get_libc().getenv
getenv.restype = c_char_p

# call into your linked module here

print('FOO is', getenv('FOO'))
