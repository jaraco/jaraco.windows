import os

import pytest

from jaraco.windows import filesystem


def test_islink_on_nonexistent_target():
	assert filesystem.islink('/doesnotexist') is False


def test_is_symlink(tmpdir):
	with tmpdir.as_cwd():
		filesystem.symlink('foobaz', 'foobar')
		assert filesystem.is_symlink('foobar')


def test_FileAttributes():
	attrs = filesystem.FileAttributes.get(__file__)
	assert not attrs.hidden


@pytest.mark.skip('sys.version_info < (3, 2)')
def test_compat_stat():
	"""
	Ensure compat stat produces comparable results to
	normal stat on Python 3.2 and later.
	"""
	assert filesystem.compat_stat(__file__) == os.stat(__file__)


def test_samefile():
	assert filesystem.samefile(__file__, __file__)
	assert not filesystem.samefile(__file__, filesystem.__file__)
