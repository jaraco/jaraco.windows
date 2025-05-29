import builtins
import sys

PermissionError = (
    # workaround for python/cpython#87319
    (builtins.PermissionError, NotADirectoryError)
    if sys.version_info < (3, 11)
    else builtins.PermissionError
)
