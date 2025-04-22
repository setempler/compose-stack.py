# cs.logger


"""The module specific logger construction."""


import sys
import logging
log = logging.getLogger()

from . import console


EMOJIS = {
    # NOTSET
    logging.DEBUG:      "🛠️ ",
    logging.INFO:       "ℹ️ ",
    logging.WARNING:    "⚠️ ",
    logging.ERROR:      "❌",
    logging.CRITICAL:   "🔥",
}

COLORS = {
    #NOTSET
    #DEBUG
    logging.INFO: console.Color.cyan,
    logging.WARNING: console.Color.yellow,
    logging.ERROR: console.Color.red,
    logging.CRITICAL: console.Color.magenta,
}

fmt = f"[%(emoji)s  %(color)s%(levelname)-8s{console.Color.none}]: %(message)s"
fmtx = f"{fmt} @[%(filename)s#%(lineno)s %(asctime)s]"
FORMATS = {
    "default":      fmt,
    logging.DEBUG:  fmtx 
}

FORMATTERS = {
    level: logging.Formatter(format, datefmt="%Y-%m-%d %H:%M:%S") for level, format in FORMATS.items()
}

class EmojiFormatter(logging.Formatter):
    """Define a log format using emojis."""
    
    def __init__(self):
        super().__init__()        

    def format(self, record):
        emoji = EMOJIS.get(record.levelno, "")
        color = COLORS.get(record.levelno, "")
        formatter = FORMATTERS.get(record.levelno, FORMATTERS["default"])
        record.emoji = emoji
        record.color = color
        #record.filename = "x"
        return formatter.format(record)


def configure_logging(level=logging.INFO, out=sys.stderr):
    """Configure the logger.
    
    Args:
        level (int): A logging level such as DEBUG, INFO, WARNING, etc.
    """
    # get root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    # clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    # create a stream handler
    handler = logging.StreamHandler(out)
    handler.setLevel(level)
    # create a formatter
    formatter = EmojiFormatter()
    # update the logger
    handler.setFormatter(formatter)
    logger.addHandler(handler)
