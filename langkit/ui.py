import os
import time
from termcolor import cprint
if os.name == 'nt':
    import ctypes
    import struct
import sys

ERROR_COLOR = 'red'
WARNING_COLOR = 'yellow'
PROMPT_COLOR = 'cyan'

def _calc_terminal_size():
    if os.name == 'nt':
        h = ctypes.windll.kernel32.GetStdHandle(-12)  # STD_OUTPUT_HANDLE
        csbi = ctypes.create_string_buffer(22)
        res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

        if res:
            (bufx, bufy, curx, cury, wattr,
            left, top, right, bottom,
            maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
        else:
            sizex, sizey = 80, 25  # can't determine actual size - return default values

        return sizex, sizey
    else:
        rows, columns = os.popen('stty size', 'r').read().split()
        return int(columns), int(rows)

_last_termsize_check = 0
_last_sizex = None
_last_sizey = None
def get_terminal_size(force: bool = False):
    """
    Get the size of the terminal window.

    Args:
        force (bool): If True, force a recalculation of the terminal size.

    Returns:
        Tuple[int, int]: The width and height of the terminal window.
    """
    global _last_termsize_check, _last_sizex, _last_sizey
    now = time.time()
    if force or (now - _last_termsize_check > 10):
        _last_sizex, _last_sizey = _calc_terminal_size()
    return _last_sizex, _last_sizey
    
def wrap_line_with_indent(text: str, width=None):
    """
    Wraps a single line of text to fit within the specified width,
    using the indentation of the first line as the indentation for
    subsequent lines.

    Args:
        text (str): The text to be wrapped.
        width (int): The maximum width of each line.

    Returns:
        str: The wrapped text with indentation.
    """
    if width is None:
        width, _ = get_terminal_size()
    lines = []
    text = text.rstrip()
    if text:
        for i in range(len(text)):
            if text[i] != ' ':
                break
        indent = ' ' * i if i > 0 else ''
        while len(text) > width:
            space_index = text.rfind(' ', len(indent) + 1, width)
            if space_index == -1:
                # If no space found within width, just split at width
                lines.append(text[:width])
                text = indent + text[width:]
            else:
                lines.append(text[:space_index].rstrip())
                text = indent + text[space_index + 1:]
        lines.append(text)
    return '\n'.join(lines)

def wrap_block_with_indent(text: str, width: int=None):
    """
    Wrap the given text (which may consist of multiple lines) to the
    specified width, preserving natural indentation which is already
    present on each line.

    Args:
        text (str): The text to be wrapped.
        width (int): The maximum width of each line.

    Returns:
        str: The wrapped text with preserved indentation.
    """
    wrapped = []
    lines = text.split('\n')
    for line in lines:
        wrapped.append(wrap_line_with_indent(line, width))
    return '\n'.join(wrapped)

def cwrite(text, color):
    cprint(text, color, end='')

def write(text):
    print(text, end='')

def prompt(txt, color=PROMPT_COLOR):
    cwrite(txt + ' ', color)
    return input()

