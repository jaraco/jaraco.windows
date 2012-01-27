import py.test

from jaraco.windows import filesystem

def test_islink_on_nonexistent_target():
	assert filesystem.islink('/doesnotexist') == False
