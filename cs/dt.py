# cs.dt


"""date and time methods.

For convenience, wrap a simpler date/time format to retrieve standardized strings from
a pythone datetime object, or directly from the current system time.
"""


import datetime
import logging
log = logging.getLogger()


def now(fmt = "dt", simplified = True):
    """Obtain the current time as string.

    Args:
        fmt (str): A date/time format defined in :func:`format`.
        simplified (bool): See :func:`format`.

    Returns:
        str: The current time formatted as string.
    
    .. exec_code::
        :caption: Example code:
        :caption_output: Result:

        import miscset
        now = miscset.dt.now()
        print(now)
    """
    dt = datetime.datetime.now()
    return format(dt, fmt, simplified)


def format(dt, fmt = "dt", simplified = True):
    """Format a datetime object.

    Use a python :py:class:`datetime.datetime` object and convert it to a string,
    wrapping the :py:meth:`datetime.datetime.strftime` method.
    For convenience, enable the interpretation of a simpler syntax for common and
    default string formatted system time.

    Args:
        dt (datetime.datetime): A datetime object to format to a string.
        fmt (str): A datetime string format to apply, one of:

            - "dt" aka date and time -> YYYY-MM-DD HH:MM:SS
            - "d"  aka date          -> YYYY-MM-DD
            - "t"  aka time          -> HH:MM:SS
            - "f"  aka file name     -> YYYY-MM-DD_HH-MM-SS
            - "n"  aka numbers       -> YYYYMMDDHHMMSS

        simplified (bool): True to expand the `fmt` from a simplified encoding;
            otherwise use the formats supported by the :py:meth:`datetime.datetime.strftime` method,
            see details at the documentation for
            `format codes <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_.

    Returns:
        str: The datetime object converted to a string.
    
    .. exec_code::
        :caption: Example code:
        :caption_output: Result:

        import datetime
        now = datetime.datetime.now()
        print(f"from:  {repr(now)}")

        import miscset
        nowstr = miscset.dt.format(now)
        print(f"to:    {nowstr}")
        nowstr = miscset.dt.format(now, "n")
        print(f"or to: {nowstr}")
    """
    if simplified:
        fmt = fmt.lower()
        if fmt == "dt":
            fmt = "%Y-%m-%d %H:%M:%S"
        elif fmt == "d":
            fmt = "%Y-%m-%d"
        elif fmt == "t":
            fmt = "%H:%M:%S"
        elif fmt == "f":
            fmt = "%Y-%m-%d_%H-%M-%S"
        elif fmt == "n":
            fmt = "%Y%m%d%H%M%S"
        else:
            fmt = ""
    return dt.strftime(fmt)


def simplify_systemd(dt):
    """Simplify systemd timestamp formats.
    
    Convert from:   YYYY-MM-DDTHH:MM:SS.NNNNNNNZ
    to:             YYYY-MM-DD HH:MM:SS
    """
    return dt[:19].replace("T", " ")


def get_time_elapsed(dt, unit_short=True):
    """Get human readable time difference to now."""
    now = datetime.datetime.now()
    diff = now - dt
    minutes = diff.total_seconds() / 60
    hours = minutes / 60
    days = hours / 24
    months = days / 30
    if minutes < 121:
        unit = "m" if unit_short else "minutes"
        return f"{int(minutes)} {unit}"
    elif hours < 49:
        unit = "h" if unit_short else "hours"
        return f"{int(minutes)} {unit}"
    elif days < 91:
        unit = "d" if unit_short else "days"
        return f"{int(minutes)} {unit}"
    else:
        unit = "M" if unit_short else "months"
        return f"{int(minutes)} {unit}"