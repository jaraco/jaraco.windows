import contextlib
from ctypes import CDLL, c_char_p


def get_libc():
    libnames = ('msvcrt', 'libc.so.6', 'libc.dylib')
    for libname in libnames:
        with contextlib.suppress(OSError):
            return CDLL(libname)
    raise RuntimeError(f"Unable to find a suitable libc (tried {libnames})")


getenv = get_libc().getenv
getenv.argtypes = (c_char_p,)
getenv.restype = c_char_p

if __name__ == '__main__':
    print('FOO is', getenv(b'FOO').decode('utf-8'))
