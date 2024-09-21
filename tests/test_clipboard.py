import textwrap

import pytest

import jaraco.windows.clipboard as wc
from jaraco.windows.api import clipboard as api


def test_unicode_clipboard():
    wc.set_unicode_text('foo' * 100)
    assert wc.get_unicode_text() == 'foo' * 100
    wc.set_unicode_text('☃')
    assert wc.get_unicode_text() == '☃'


example_html = textwrap.dedent(
    """
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
    """
).lstrip()
"""
Example taken from
https://msdn.microsoft.com/en-us/library/windows/desktop/ms649015(v=vs.85).aspx#Description
"""


@pytest.fixture
def sample_html():
    with wc.context():
        wc.EmptyClipboard()
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


@pytest.mark.xfail(reason="example is buggy")
def test_html_fragment(sample_html):
    snippet = wc.get_html()
    assert snippet.fragment == '<LI> The Fragment </LI>'


multibyte_example_html = textwrap.dedent(
    """
    Version:0.9
    StartHTML:00000138
    EndHTML:00000215
    StartFragment:00000171
    EndFragment:00000182
    StartSelection:00000174
    EndSelection:00000178
    <html><body>
    <!--StartFragment--><p>😀</p><!--EndFragment-->
    </body></html>
    """
).strip()


@pytest.fixture
def multibyte_sample_html():
    with wc.context():
        wc.EmptyClipboard()
        wc.SetClipboardData(api.CF_HTML, multibyte_example_html.encode('utf-8'))


def test_html_multibyte_characters(multibyte_sample_html):
    res = wc.get_html()
    assert (
        res.html
        == textwrap.dedent(
            """
            <html><body>
            <!--StartFragment--><p>😀</p><!--EndFragment-->
            </body></html>
            """
        ).strip()
    )
    assert res.fragment == '<p>😀</p>'
    assert res.selection == '😀'
