import os
import pathlib
import platform
import random
import threading
import time

import pytest

collect_ignore = ['jaraco/windows/incubator']


try:
    __import__('win32api')
except ImportError:
    # pywin32 isn't available, so avoid import errors
    collect_ignore += ['jaraco/windows/eventlog.py', 'jaraco/windows/services.py']


if platform.system() != 'Windows':
    """
    Ignore everything but specifically cross-platform safe modules.
    """
    safe = 'test_root.py', 'tempfile.py'
    collect_ignore = [
        os.path.join(root, filename)
        for root, dirs, files in os.walk('.')
        for filename in files
        if filename.endswith('.py') and filename not in safe
    ]


@pytest.fixture
def tmpdir_as_cwd(tmpdir):
    with tmpdir.as_cwd():
        yield tmpdir


@pytest.fixture
def slow_closer():
    def close_slowly(handle):
        """
        Sleep for .1 to 2.1 seconds and then attempt to close the handle.
        """
        time.sleep(2 * random.random() + 0.1)
        handle.close()

    def prepare(directory):
        excl_file = pathlib.Path(directory, 'somefile')
        handle = excl_file.open('w', encoding='utf-8')
        threading.Thread(target=close_slowly, args=(handle,)).start()

    return prepare
