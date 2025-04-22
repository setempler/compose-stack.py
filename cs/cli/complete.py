# cs.cli.complete


import logging
log = logging.getLogger()


def command(args, parser, cfg):
    # use log level debug for 1x -v
    # use debug level for reasoning of completion
    print(parser)
    for item in vars(parser):
        print(item)
    for sub in getattr(parser, "_subparsers", None):
        print(sub)
    pass
