# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import textwrap

import pytest

import jaraco.windows.clipboard as wc
from jaraco.windows.api import clipboard as api


def test_unicode_clipboard():
	wc.set_unicode_text('foo' * 100)
	assert wc.get_unicode_text() == 'foo' * 100
	wc.set_unicode_text('☃')
	assert wc.get_unicode_text() == '☃'


example_html = textwrap.dedent("""
	Version:0.9
	StartHTML:71
	EndHTML:170
	StartFragment:140
	EndFragment:160
	StartSelection:140
	EndSelection:160
	<!DOCTYPE>
	<HTML>
	<HEAD>
	<TITLE> The HTML Clipboard</TITLE>
	<BASE HREF="http://sample/specs">
	</HEAD>
	<BODY>
	<UL>
	<!--StartFragment -->
	<LI> The Fragment </LI>
	<!--EndFragment -->
	</UL>
	</BODY>
	</HTML>
	""").lstrip()
"""
Example taken from
https://msdn.microsoft.com/en-us/library/windows/desktop/ms649015(v=vs.85).aspx#Description
"""


@pytest.fixture
def sample_html():
	with wc.context():
		wc.SetClipboardData(api.CF_HTML, example_html.encode('utf-8'))


def test_html_paste(sample_html):
	res = wc.get_html()
	assert len(res.html) < len(res.data)
	assert res.headers == dict(
		StartHTML=71,
		Version=0.9,
		EndHTML=170,
		StartFragment=140,
		EndFragment=160,
		StartSelection=140,
		EndSelection=160,
	)
