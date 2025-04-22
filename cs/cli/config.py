# cs.cli.config


import logging
log = logging.getLogger()


from .. import config


COMPOSE_STACK_INFO = config.COMPOSE_STACK_INFO


TEMPLATE = """# compose-stack.yaml

stack:
    website:
        path: ~/website/compose.yaml
    smarthome:
        path: /opt/smarthome/compose.yaml
    nextcloud:
        path: /data/nextcloud/compose.yaml
"""

def command(args, parser, cfg):
    if args.template:
        log.info("show a template only")
        print(TEMPLATE)
        return
    log.info(f"show config file '{cfg.path}'")
    print(cfg)