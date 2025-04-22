# cs.cli.help


import logging
log = logging.getLogger()


def command(args, parser, cfg):
    parser.parse_args(["--help"])