# cs.cli.__init__


"""command line option parsing"""


import argparse
import logging
log = logging.getLogger()

from . import config
from . import help
from . import ls
from . import ps
from ..logger import configure_logging
from ..config import Config
from .. import version


def show_version(args, parser, cfg):
    print(f"{__name__} version {version}")


def main():

    ### global arguments
    s = argparse.ArgumentParser(add_help=False)
    s.add_argument("-c", "--config", dest="config_path", metavar="PATH", default=None, help=f"define main configuration file path; {config.COMPOSE_STACK_INFO}")
    s.add_argument('-v', '--verbose', action='count', default=0, help="enable verbose mode and show warning/info/debug logs")
    p = argparse.ArgumentParser(description="docker compose & other service stack manager", parents=[s])
    psub = p.add_subparsers(dest='command', title="commands", metavar="COMMAND", required=True)
    
    # command: version
    q = psub.add_parser("version", aliases=["--version", "-V"], help="show version")
    q.set_defaults(func=show_version)

    # command: help
    q = psub.add_parser("help", help="show help")
    q.set_defaults(func=help.command)

    # command: config
    q = psub.add_parser("config", parents=[s], help="parse and display configuration collated from --config PATH.")
    q.add_argument("-t", "--template", action="store_true", help="print a template")
    #q.add_argument("mode", default="yaml", nargs="?", help="output mode; supported: yaml")
    # -s, --summarize: count items
    # --check: check if items are available -> check?
    q.set_defaults(func=config.command)
    
    # command: ls
    q = psub.add_parser("ls", parents=[s], help="list inventory")
    q.add_argument('-x', '--extend', action='store_true', help="display full repo name.")
    q.add_argument('-u', '--unknown', action='store_true', help="show unknown (unnamed) docker images.")
    q.set_defaults(func=ls.command)
    
    # command: ps
    q = psub.add_parser("services", parents=[s], aliases=["ps"], help="list services and processes")
    #          extend view
    q.add_argument('-i', '--ids', action="store_true", help="show also container IDs.")
    q.add_argument('-n', '--network', action='store_true', help="display more network details.")
    q.add_argument('-d', '--docker', action='store_true', help="display more docker image details.")
    #q.add_argument('-o', '--compose', action='store_true', help="display only docker processes defined in the stack's compose files; hides generic docker containers.")
    #q.add_argument("-s", "--stats", action="store_true", help="display ressource stats.")
    q.add_argument("-t", "--times", action="store_true", help="display additional times.")
    q.add_argument('-a', '--all', action='store_true', help="display all information.")
    #          filter view
    q.add_argument("-C", "--only-config", action="store_true", help="only list services and information configured.")
    #q.add_argument('-N', '--only-names', action="store_true", help="only list service names.")
    #q.add_argument('-I', '--only-ids', action="store_true", help="only list docker container IDs.")
    q.add_argument("name", nargs="?", help="detailled view on a single service.")
    #q.add_argument("-S", "--stack", default=None, help="name of stack to select service for single view.")
    q.set_defaults(func=ps.command)

    # # command: check
    # q = psub.add_parser("check", help="run system check and print output")
    # q.add_argument("mode", default="yaml", nargs="?", help="output mode; supported: yaml")
    # q.add_argument('-v', '--verbose', action='count', default=0, help="Enable verbose mode and show warning/info/debug logs. More times used, more verbose.")
    # q.set_defaults(func=check.command)
    
    # command: complete
    # q = psub.add_parser("complete", help="generate shell completion output.")
    # q.add_argument("words", nargs="*", help="specify the chain of arguments to identify possible completions.")
    # q.set_defaults(func=complete.command)
    
    # Parse arguments and config
    a = p.parse_args()
    
    # Configure logging
    verbose = getattr(a, "verbose", 0)
    level = logging.ERROR
    if verbose > 0:
        level = logging.WARNING
    if verbose > 1:
        level = logging.INFO
    if verbose > 2:
        level = logging.DEBUG
    configure_logging(level)
        
    # Load configuration
    c = Config(a.config_path)

    # Trigger command process
    a.func(a, p, c)

    # Debug testing
    # log = logging.getLogger()
    # log.debug("test debug")
    # log.info("test info")
    # log.warning("test warning")
    # log.error("test error")
    # log.critical("test critical")