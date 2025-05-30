import collections
import ctypes
import io
import itertools
import re
import sys
import textwrap
from contextlib import contextmanager
from ctypes import windll

from jaraco.windows.api import clipboard, memory
from jaraco.windows.error import handle_nonzero_success
from jaraco.windows.memory import LockedMemory

__all__ = ('GetClipboardData', 'CloseClipboard', 'SetClipboardData', 'OpenClipboard')


def OpenClipboard(owner=None):
    """
    Open the clipboard.

    owner
    [in] Handle to the window to be associated with the open clipboard.
    If this parameter is None, the open clipboard is associated with the
    current task.
    """
    handle_nonzero_success(windll.user32.OpenClipboard(owner))


def CloseClipboard():
    handle_nonzero_success(windll.user32.CloseClipboard())


data_handlers = dict()


def handles(*formats):
    def register(func):
        for format in formats:
            data_handlers[format] = func
        return func

    return register


def nts(buffer):
    """
    Null Terminated String
    Get the portion of bytestring buffer up to a null character.
    """
    result, null, rest = buffer.partition('\x00')
    return result


@handles(clipboard.CF_DIBV5, clipboard.CF_DIB)
def raw_data(handle):
    return LockedMemory(handle).data


@handles(clipboard.CF_TEXT)
def text_string(handle):
    return nts(raw_data(handle))


@handles(clipboard.CF_UNICODETEXT)
def unicode_string(handle):
    return nts(raw_data(handle).decode('utf-16'))


@handles(clipboard.CF_BITMAP)
def as_bitmap(handle):
    # handle is HBITMAP
    raise NotImplementedError("Can't convert to DIB")
    # todo: use GetDIBits http://msdn.microsoft.com
    # /en-us/library/dd144879%28v=VS.85%29.aspx


@handles(clipboard.CF_HTML)
class HTMLSnippet(object):
    """
    HTML Snippet representing the Microsoft `HTML snippet format
    <https://docs.microsoft.com/en-us/windows/win32/dataxchg/html-clipboard-format>`_.
    """

    # The non-normative grammar defines markers with a space before "-->",
    # but the body text defines them without spaces and states "with no
    # whitespace chars within each comment itself".
    # Actually, Edge and Firefox don't include spaces, so we also don't include
    # a space.
    START_FRAGMENT_MARKER = b'<!--StartFragment-->'
    END_FRAGMENT_MARKER = b'<!--EndFragment-->'

    def __init__(self, handle):
        self.data = nts(raw_data(handle).decode('utf-8'))
        self.headers = self.parse_headers(self.data)

    @property
    def html(self):
        start_html = self.headers['StartHTML']
        end_html = self.headers['EndHTML']
        if start_html == -1:
            start_html = self.headers['StartFragment'] - len(
                HTMLSnippet.START_FRAGMENT_MARKER
            )
        if end_html == -1:
            end_html = self.headers['EndFragment'] + len(
                HTMLSnippet.END_FRAGMENT_MARKER
            )
        return self.__slice_data(start_html, end_html)

    @property
    def fragment(self):
        start_fragment = self.headers['StartFragment']
        end_fragment = self.headers['EndFragment']
        return self.__slice_data(start_fragment, end_fragment)

    @property
    def selection(self):
        start_selection = (
            self.headers.get('StartSelection') or self.headers['StartFragment']
        )
        end_selection = self.headers.get('EndSelection') or self.headers['EndFragment']
        return self.__slice_data(start_selection, end_selection)

    def __slice_data(self, start, end):
        return self.data.encode('utf-8')[start:end].decode('utf-8')

    @staticmethod
    def parse_headers(data):
        d = io.StringIO(data, None)

        if not re.match(r'Version:(?:0\.9|1\.0)\n', d.readline()):
            raise ValueError('Unsupported format')

        d.seek(0)

        def header_line(line):
            return re.match(r'(\w+):(.*)\n', line)

        headers = map(header_line, d)
        # grab headers until they no longer match
        headers = itertools.takewhile(bool, headers)

        def best_type(value):
            try:
                return int(value)
            except ValueError:
                pass
            try:
                return float(value)
            except ValueError:
                pass
            return value

        pairs = ((header.group(1), best_type(header.group(2))) for header in headers)
        return dict(pairs)

    @classmethod
    def from_string(cls, source):
        """
        Construct an HTMLSnippet with all the headers, modeled after
        https://docs.microsoft.com/en-us/troubleshoot/cpp/add-html-code-clipboard
        """
        tmpl = textwrap.dedent(
            """
            Version:0.9
            StartHTML:{start_html:08d}
            EndHTML:{end_html:08d}
            StartFragment:{start_fragment:08d}
            EndFragment:{end_fragment:08d}
            <html><body>
            <!--StartFragment-->{source}<!--EndFragment-->
            </body></html>
            """
        ).strip()
        zeros = collections.defaultdict(lambda: 0, locals())
        pre_value = tmpl.format_map(zeros).encode('utf-8')
        start_html = pre_value.find(b'<html>')
        end_html = len(pre_value)
        assert end_html < 100000000
        start_fragment = pre_value.find(HTMLSnippet.START_FRAGMENT_MARKER) + len(
            HTMLSnippet.START_FRAGMENT_MARKER
        )
        end_fragment = pre_value.rfind(HTMLSnippet.END_FRAGMENT_MARKER)
        snippet = cls.__new__(cls)
        snippet.data = tmpl.format_map(locals())
        snippet.headers = cls.parse_headers(snippet.data)
        return snippet


def GetClipboardData(type=clipboard.CF_UNICODETEXT):
    if type not in data_handlers:
        raise NotImplementedError("No support for data of type %d" % type)
    handle = clipboard.GetClipboardData(type)
    if handle is None:
        raise TypeError("No clipboard data of type %d" % type)
    return data_handlers[type](handle)


def EmptyClipboard():
    handle_nonzero_success(windll.user32.EmptyClipboard())


def SetClipboardData(type, content):
    """
    Modeled after http://msdn.microsoft.com
    /en-us/library/ms649016%28VS.85%29.aspx
    #_win32_Copying_Information_to_the_Clipboard
    """
    allocators = {
        clipboard.CF_TEXT: ctypes.create_string_buffer,
        clipboard.CF_UNICODETEXT: ctypes.create_unicode_buffer,
        clipboard.CF_HTML: ctypes.create_string_buffer,
    }
    if type not in allocators:
        raise NotImplementedError("Only text and HTML types are supported at this time")
    # allocate the memory for the data
    content = allocators[type](content)
    flags = memory.GMEM_MOVEABLE
    size = ctypes.sizeof(content)
    handle_to_copy = windll.kernel32.GlobalAlloc(flags, size)
    with LockedMemory(handle_to_copy) as lm:
        ctypes.memmove(lm.data_ptr, content, size)
    result = clipboard.SetClipboardData(type, handle_to_copy)
    if result is None:
        raise ctypes.WinError()


def set_text(source):
    with context():
        EmptyClipboard()
        SetClipboardData(clipboard.CF_TEXT, source)


def get_text():
    with context():
        result = GetClipboardData(clipboard.CF_TEXT)
    return result


def set_unicode_text(source):
    with context():
        EmptyClipboard()
        SetClipboardData(clipboard.CF_UNICODETEXT, source)


def get_unicode_text():
    with context():
        return GetClipboardData()


def get_html():
    """
    >>> set_html('<b>foo</b>')
    >>> get_html().html
    '<html><body>...<b>foo</b>...</body></html>'
    >>> get_html().fragment
    '<b>foo</b>'
    """
    with context():
        result = GetClipboardData(clipboard.CF_HTML)
    return result


def set_html(source):
    """
    >>> set_html('<b>foo</b>')
    """
    snippet = HTMLSnippet.from_string(source)
    with context():
        EmptyClipboard()
        SetClipboardData(clipboard.CF_HTML, snippet.data.encode('utf-8'))


def get_image():
    with context():
        return GetClipboardData(clipboard.CF_DIB)


def paste_stdout():
    sys.stdout.write(get_unicode_text())


def stdin_copy():
    set_unicode_text(sys.stdin.read())


@contextmanager
def context():
    OpenClipboard()
    try:
        yield
    finally:
        CloseClipboard()


def get_formats():
    with context():
        format_index = 0
        while True:
            format_index = clipboard.EnumClipboardFormats(format_index)
            if format_index == 0:
                break
            yield format_index
