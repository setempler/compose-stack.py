# cs.config


"""Compose stack configuration file parser"""


import re
import os
import yaml
import logging
log = logging.getLogger()


from . import io
from . import console


COMPOSE_STACK_CONFIG = "~/compose-stack.yaml"
COMPOSE_STACK_INFO = f"""
Detection of config file path:
1. if `path` option is given in CLI, use it's value, else
2. if `COMPOSE_STACK_CONFIG` variable is set, use this, else
3. use default path {COMPOSE_STACK_CONFIG}
"""

class Config(object):

    """Compose stack configuration parser"""

    def __init__(self, path=None):
        if path is None:
            path = os.getenv("COMPOSE_STACK_CONFIG")
        if path is None:
            path = COMPOSE_STACK_CONFIG
        path = os.path.expanduser(path)
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise ValueError(f"Cannot find configuration file '{path}'.")
        self.path = path
        self.config = io.read_yaml(path)
        log.debug(f"loaded config from path {self.path}")

    def __str__(self):
        return yaml.dump(self.config)

    def get_root_path(self):
        return os.path.dirname(self.path)

    def get_compose(self, name):
        return self.config.get("compose", None)

    def get_compose_path(self, name):
        """get compose stack's file path
        
        defaults to ${OZAPFTCTL}/services/<name>/compose.yml
        """
        compose = self.get_compose(name)
        if compose is None:
            return
        path = compose.get("path", None)
        if path is None:
            root = self.get_root_path()
            path = os.pathsep.join([root, "services", name, "compose.yml"])
        path = os.path.abspath(path)
        if not os.path.exists(path):
            console.flush(f"error: cannot find compose path '{path}'")
            return None
        #sys.exit(1)
        return path

    def file_exists(self):
        return os.path.exists(self.path)

    def get_init(self, category=None):
        init = self.config.get("init", {})
        if category is not None:
            init = init.get(category, {})
        return init

    def get_init_scripts(self):
        scripts = self.get_init("scripts")
        return scripts

    def get_init_software(self):
        packages = []
        # load software entry
        software = self.get_init("software")
        if not software:
            return packages
        # load apt packages
        apt = software.get("apt", [])
        if apt:
            packages += [Package(name, "apt") for name in apt]
        # load pip packages
        pip = software.get("pip", [])
        if pip:
            packages += [Package(name, "pip") for name in pip]
        # return
        return packages

    def get_systemd_units(self):
        units = []
        for service in self.config.get("services", {}).get("systemd", {}):
            units.append(re.sub(r"\.service$", "", service))
        return units