# cs.cli.ls


"""
DOCKER
    IMAGES
    VOLUMES
"""


import logging
log = logging.getLogger()


from .. import system
from .. import io

def command(args, parser, cfg):
    print("# DOCKER IMAGES")
    images = system.get_docker_images()
    io.print_table(images, output_columns=["ID", "TAG", "VERSION", "CREATED"])
    volumes = system.get_docker_volumes()
    io.print_table(volumes, output_columns=["ID", "CREATED", "MOUNT_PATH"])
    pass