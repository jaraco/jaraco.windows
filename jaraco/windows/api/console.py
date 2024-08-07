import ctypes
import types
from ctypes import wintypes


kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

HISTORY_NO_DUP_FLAG = 1


class HISTORY_INFO(ctypes.Structure):
    _fields_ = (
        ('cbSize', wintypes.UINT),
        ('HistoryBufferSize', wintypes.UINT),
        ('NumberOfHistoryBuffers', wintypes.UINT),
        ('dwFlags', wintypes.DWORD),
    )

    def __init__(self, *args, **kwds):
        super().__init__(ctypes.sizeof(self), *args, **kwds)


def get_history_info():
    info = HISTORY_INFO()
    if not kernel32.GetConsoleHistoryInfo(ctypes.byref(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    return types.SimpleNamespace(
        bufsize=info.HistoryBufferSize,
        nbuf=info.NumberOfHistoryBuffers,
        flags=info.dwFlags,
    )


def set_history_info(bufsize=512, nbuf=32, flags=HISTORY_NO_DUP_FLAG):
    info = HISTORY_INFO(bufsize, nbuf, flags)
    if not kernel32.SetConsoleHistoryInfo(ctypes.byref(info)):
        raise ctypes.WinError(ctypes.get_last_error())
