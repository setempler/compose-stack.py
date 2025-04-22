# cs.cli.ps


"""
SYSTEMD
    SERVICES
DOCKER
    SERVICES
"""


import logging
log = logging.getLogger()


from .. import io
from .. import system
from .. import service

def replace_list(obj, old_value, new_value):
    if not isinstance(obj, list):
        return obj
    return [new_value if x == old_value else x for x in obj]

def command(args, parser, cfg):
    # load stack
    stack = service.Stack()
    stack.load_config(cfg)

    # config info only
    if args.only_config:
        cols = ["TYPE", "STACK", "NAME", "NETPORT"]
        io.print_table(stack.table())
        return
    
    # # include system stats
    # if args.stats:
    #     srv.load_dockers()

    # show single service only
    if args.name:
        log.critical("option `name` not yet supported")
        # services = srv.find(args.name, args.stack)
        # for service in services:
        #     service.details()
        # if not len(services):
        #     Print.flush(f"cannot find service named '{args.name}'")
        return
    
    ### configure output
    cols = ["TYPE", "STACK", "NAME", "STATE", "STARTED", "NETPORT"]
    # if args.stats:
    #     cols += ["CPU", "MEM"]
    if args.network or args.all:
        cols += ["NETMODE"]
        cols = replace_list(cols, "NETPORT", "NETMAP")
    if args.times or args.all:
        cols += ["FINISHED", "CHANGED"]
    # if args.all:
    #     cols += ["CREATED", "MOUNTS.N"]
    if args.docker or args.all:
        cols += ["IMAGE", "IMAGEVER", "IMAGEDATE"]
    

    # load data
    stack.load_dockerd()
    stack.load_systemd(filter=cfg)

    # print output
    io.print_table(stack.table(), output_columns=cols)