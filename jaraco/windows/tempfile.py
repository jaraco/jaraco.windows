import tempfile

from tempora.timing import BackoffDelay

from jaraco.functools import retry


class TemporaryDirectory(tempfile.TemporaryDirectory):
    """
    A temp directory that attempts to be more
    resilient to PermissionErrors on Windows when deleting files
    that might be held open.

    It tries to delete files/directories multiple times with a short delay.

    >>> with TemporaryDirectory() as td:
    ...     getfixture('slow_closer')(td)
    """

    @retry(
        retries=3,
        trap=PermissionError,
        cleanup=BackoffDelay(delay=0.5, factor=2),
    )
    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
