from jaraco.windows import filesystem

def test_islink_on_nonexistent_target():
	assert filesystem.islink('/doesnotexist') == False

def test_is_symlink(tmpdir):
	with tmpdir.as_cwd():
		filesystem.symlink('foobaz', 'foobar')
		assert filesystem.is_symlink('foobar')
