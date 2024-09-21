"""
Script illustrates the surprising behaviors around set/get on the environment
with various APIs.
"""

import ctypes
from jaraco.windows import environ  # noqa: F401
import os  # noqa: F401

getenv = ctypes.cdll.msvcrt.getenv
getenv.restype = ctypes.c_char_p
putenv = ctypes.cdll.msvcrt._putenv


def do_putenv(*pair):
    return putenv("=".join(pair))


def print_environment_variable(key):
    methods = (
        'os.environ.get',
        'os.getenv',
        'environ.GetEnvironmentVariable',
        'getenv',
    )
    for method in methods:
        func = eval(method)
        print(method, end=': ')
        try:
            print(repr(func(key)))
        except Exception as e:
            print(e)
    print()


def do_test():
    key = 'TEST_PYTHON_ENVIRONMENT'
    print('Before setting anything', end=':\n')
    print_environment_variable(key)
    methods = (
        'os.environ.__setitem__',
        'os.putenv',
        'environ.SetEnvironmentVariable',
        'do_putenv',
    )
    for method in methods:
        print('Setting with', method, end=':\n')
        func = eval(method)
        func(key, f'value when using method {method}')
        print_environment_variable(key)


if __name__ == '__main__':
    do_test()
