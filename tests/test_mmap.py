import jaraco.windows.mmap as mmap


def test_mmap_simple():
	map = mmap.MemoryMap('foo', 50)
	with map:
		map.write(b'abc')
		map.write(b'def')
		map.seek(0)
		assert map.read(4) == b'abcd'
		assert map.read(2) == b'ef'


def test_mmap_null_bytes():
	map = mmap.MemoryMap('foo', 50)
	with map:
		map.write(b'abcdef')
		map.seek(0)
		assert map.read(10) == b'abcdef\x00\x00\x00\x00'
