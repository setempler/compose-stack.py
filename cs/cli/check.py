# cs.cli.check


"""check the system"""


import logging
log = logging.getLogger()


from .. import system
from .. import sh


def command(args, parser, cfg):
    print(f"CHECK (verbosity:{args.verbose})")
    passed = 0
    total = 0
    # perform checks
    for tool in ["docker", "systemctl", "foobar"]:
        total += 1
        path = system.which(tool)
        log.debug(f"check tool={tool} on path={path}")
        if not path:
            log.error(f"system tool not found: '{tool}'")
        else:
            passed += 1
            log.info(f"system tool found: '{tool}'")
    cmds = [
       ["docker", "--version"], 
       ["systemctl", "--version"],
       ["floppaxa"]
    ]
    for cmd in cmds:
        total += 1
        x = sh.Process(cmd)
        if x.is_done:
            passed += 1
            log.info(f"version tested: '{x.lines[0]}'")
        else:
            log.error(f"version test failed with: '{cmd}'")
    if passed < total:
        log.warning(f"only {passed} of {total} tests passed")