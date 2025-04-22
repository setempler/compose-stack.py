# console.py


"""Console escape code based shell colors, print methods, cursor operations.

Note on escape code operators:
* `\\r`      : carriage return, move cursor to column 1
* `\\033[nG` : move cursor to column n
* `\\033[nC` : move cursor BY n columns to the right
* `\\033[K`  : short for \033[0K
* `\\033[0K` : erase from cursor to end of line
* `\\033[1K` : erase from beginning of line to cursor
* `\\033[2K` : erase entire line
"""


import os
import sys
import logging
log = logging.getLogger()


class Color:
    """ANSI shell color escape codes."""
    none = "\033[0m"
    white = "\033[1;37m"
    cyan = "\033[1;36m"
    magenta = "\033[1;35m"
    blue = "\033[1;34m"
    yellow = "\033[1;33m"
    green = "\033[1;32m"
    red = "\033[1;31m"
    bold = "\033[1m"
    dim  = "\033[2m"


def flush(msg, clear=False):
    """rapid print to stdout
    
    Args:
        msg (str): A text to send to stdout immediately.
        clear (bool): before sending to stdout, clear current line.
    """
    lines = [msg]
    #out = sys.stdout if not err else sys.stderr
    if isinstance(msg, list):
        lines = msg
    for line in lines:
        if clear:
            move_left()
            clear_line() # clear lines? use `clear` (int) for number, convert bool by `int(clear)`
        line = str(line).rstrip()
        line += os.linesep
        sys.stdout.write(line)
    sys.stdout.flush()


def move_to(n=1):
    """move curser to column n"""
    sys.stdout.write(f"\033[{n}G")


def move_left():
    """move cursor left to first column"""
    move_to(1)


def move_right(n=1):
    """move cursor right by n columns"""
    sys.stdout.write(f"\033[{n}C")


def move_up(n=1):
    """move cursor up n lines"""
    sys.stdout.write(f"\033[{n}A")


def move_up_left(n=1):
    """move curser up n lines and left to first column"""
    move_up(n)
    move_left()


def clear_line_right():
    """erase from cursor to end of line"""
    sys.stdout.write(f"\033[0K")


def clear_line_left():
    """erase from beginning of line to cursor"""
    sys.stdout.write(f"\033[1K")


def clear_line():
    """erase entire line"""
    sys.stdout.write(f"\033[2K")


def clear_lines(n=1):
    """erase n entire lines"""
    for i in range(n):
        move_up()
        clear_line()
    move_left()


def replace_lines(lines=[""]):
    """erase and replace lines"""
    n = len(lines)
    clear_lines(n)
    flush(lines)
