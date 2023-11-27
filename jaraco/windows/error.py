import ctypes


__import__('jaraco.windows.api.memory')


def handle_nonzero_success(result):
    if result == 0:
        raise ctypes.WinError()
