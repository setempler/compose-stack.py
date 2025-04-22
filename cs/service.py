# cs.service


"""Investigate and control services."""


import re
import os
import sys
import datetime
import logging
log = logging.getLogger()


from . import io
from . import sh
from . import config


class Service(object):
    """A service configuration."""
    def __init__(self, **kwargs):
        """Initialize a service configuration.

        Relevant parsing information:

        >>> COMMANDS

        - SYSTEMD:            `systemctl show <unit>.service`
        - DOCKERD/COMPOSE:    `docker inspect <cid>` # only container for the following description!
        - DOCKERS:            `docker stats --no-stream --format json`

        >>> SLOTS (default, if not given it is None)

            >>> identification
            - wanted    (False) whether it is a target of the local configuration or not
            - type              describe the system to which the service's <stack> is associated to:
                                    SYSTEMD: fixed value "systemd"
                                    DOCKERD: fixed value "dockerd"
                                    COMPOSE: fixed value "compose"
            - stack             name of the stack:
                                    SYSTEMD: fixed value "systemd"
                                    DOCKERD: fixed value "dockerd"
                                    COMPOSE: `Config/Labels/com.docker.compose.project`
            - name              name of the service/unit:
                                    SYSTEMD: `Id`; note: `Names` would contain aliases
                                    DOCKERD: `Name`
                                    COMPOSE: <service> from `Name`: <stack>-<service>-<#>
            - pid               the process/container id:
                                    SYSTEMD: `ExecMainPID`; number
                                    DOCKERD: `Id`; a random hash
                                    DOCKERS: `ID`
            - pid6              same as <pid>, shortened to 6 characters:
                                    SYSTEMD: if len > 6: last char replaced by '.'
            >>> status
            - state             the status of the service:
                                    SYSTEMD: `LoadState` & `ActiveState` & `SubState` & `FreezerState`
                                        see SYSTEMD SATES FORMAT below
                                    DOCKERD: `State/Status`
            - created           the date the service was created:
                                    DOCKERD: `Created`
                                    SYSTEMD: ??? undefined, maybe timestamp of unit file generated?
            - started           the date the service was started:
                                    SYSTEMD: `ExecMainStartTimestamp`
                                    DOCKERD: `State/StartedAt`
            - finished          the date the service finished/stopped?:
                                    DOCKERD: `State/FinishedAt`
            - changed           the date of the last status change:
                                    SYSTEMD: `StateChangeTimestamp`
                                    DOCKERD: last one of <created>, <started>, or <finished>
            >>> ressources
            - mem               service memory usage:
                                    SYSTEMD: `MemoryCurrent`
                                    DOCKERS: `MemUsage`
            - cpu               service cpu usage (sum of time or current load):
                                    SYSTEMD: `CPUUsageNSec`; sum of cpu time
                                    DOCKERD: `CPUPerc`; current load
            - blockio           service disk i/o:
                                    DOCKERS: `BlockIO`
            - netio             service network i/o:
                                    DOCKERS: `NetIO`
            >>> network
            - netport   ([])    host exposed ports by service:
                                    DOCKERD: `NetworkSettings/Ports[]/<container-port>/HostPort`,...
            - netmap    ([])    host and service internal ports:
                                    DOCKERD: <per ports>[<container port>],...
            - netmode           network:
                                    DOCKERD: `HostConfig/NetworkMode`
            >>> files
            - mounts            bind or volume mounts of service:
                                    DOCKERD: `Mounts`; format: <n binds>B <n vols>V
            >>> parent
            - image             docker image name:
                                    DOCKERD: `Config/Image`; shorten to 30 chars, if len > 27 add '...'
            - imageid           docker image id:
                                    DOCKERD: 
            - imageid6          shortened docker image id:
                                    DOCKERD: <imageid>'s first 6 chars w/o 'sha256:' prefix
            - imagever          docker image version:
                                    DOCKERD: `Config/Labels/org.opencontainers.image.version`
            - imagedate         docker image creation date:
                                    DOCKERD: `Config/Labels/org.opencontainers.image.created`

        DOCKERD PORTS FORMAT:
            ```
            NetworkSettings
            `-- Ports
                `-- <container port>/<proto>
                    `-- HostPort
            ```

        SYSTEMD STATES FORMAT:
            ```
            if LoadState != loaded
                = LoadState (NOT-FOUND, BAD-SETTING, ERROR, MASKED)
            else
                if FreezerState != running
                    = FreezerState (FROZEN, FREEZING)
                else
                    if ActiveState in (inactive, failed)
                        = ActiveState (INACTIVE, FAILED)
                    else
                        = SubState (RUNNING, EXITED, LISTENING; AUTO-RESTART, START-PRE, START; STOP-PRE, STOP)
            ```
        SYSTEMD STATES
            🔹 Key: LoadState (load)
                Purpose: Indicates whether the service unit file was successfully read and processed by systemd.
                Possible Values:
                    "loaded" → The unit file was successfully found, parsed, and loaded into memory.
                    "not-found" → The unit file does not exist or cannot be found in the usual locations.
                    "bad-setting" → The unit file contains an invalid or unsupported configuration.
                    "error" → There was a general error while loading the unit file.
                    "masked" → The unit is explicitly disabled by linking it to /dev/null, meaning it cannot be started.
            🔹 Key: ActiveState (active)
                Purpose: Represents the high-level activity state of the service.
                Possible Values:
                    "active" → The service is running or is in a valid active state.
                    "inactive" → The service is not running and has not been started.
                    "failed" → The service encountered an error and stopped.
                    "activating" → The service is in the process of starting.
                    "deactivating" → The service is in the process of stopping.
                    "reloading" → The service is reloading its configuration.
            🔹 Key: SubState (sub)
                Purpose: Provides a more detailed state of the service beyond ActiveState.
                Possible Values (depends on ActiveState):
                When ActiveState=active:
                    "running" → The service is running normally.
                    "exited" → The service ran and exited successfully (for one-shot services).
                    "listening" → The service is a socket-based service and is waiting for connections.
                When ActiveState=inactive:
                    "dead" → The service has never been started or has been explicitly stopped.
                When ActiveState=failed:
                    "failed" → The service has stopped due to an error.
                When ActiveState=activating:
                    "auto-restart" → The service is restarting automatically after a failure.
                    "start-pre" → The service is running a pre-start script.
                    "start" → The service is in the main startup phase.
                When ActiveState=deactivating:
                    "stop-pre" → The service is running a pre-stop script.
                    "stop" → The service is in the main stopping phase.
            🔹 Key: FreezerState
                Purpose: Whether the service's processes are paused or running. When systemctl freeze or systemctl thaw is used.
                Possible Values:
                    "running"
                    "freezing"
                    "frozen"
        """
        self.initialize()
        for key, value in kwargs.items():
            if key in ["wanted", "type", "stack", "name", "image", "netport", "netmap"]:
                if value is None or not value:
                    continue
                setattr(self, key, value)

    def initialize(self):
        # identification
        self.wanted = False
        self.type = None
        self.stack = None
        self.name = None
        self.pid = None
        self.pid6 = None
        # status
        self.state = None
        self.created = None
        self.started = None
        self.finished = None
        self.changed = None
        # ressources
        self.mem = None
        self.cpu = None
        self.blockio = None
        self.netio = None
        self.netport = []
        self.netmap = []
        self.netmode = None
        self.mounts = None
        self.image = None
        self.imageid = None
        self.imageid6 = None
        self.imagever = None
        self.imagedate = None

    def __eq__(self, other):
        """Compare two Service items.

        Matches `pid` if not missing.
        Matches `stack` and `name` otherwise.
        """
        if not isinstance(other, Service):
            return False
        if self.pid and other.pid:
            return self.pid == other.pid
        return self.stack == other.stack and self.name == other.name

    def __str__(self):
        state = self.state if self.state else "unknown"
        changed = self.changed if self.changed else "unknown"
        return f"<Service {self.name}@{self.stack} is {state} last changed {changed}>"
        
    def __repr__(self):
        return str(self)
        
    def details(self):        
        name = self.name
        stack = self.stack
        metadata = {k:v for k,v in vars(self).items() if k not in ["name", "stack"]}
        data = [{"NAME": name, "STACK": stack, "PARAMETER": k, "VALUE": v} for k,v in metadata.items()]
        io.print_table(data, output_columns=["NAME", "STACK", "PARAMETER", "VALUE"])
    
    def systemctl_show(self, name):
        """
        """
        # load
        self.initialize()
        vars = sh.Process(["systemctl", "show", name]).lines
        u = {}
        for var in vars:
            key, value = var.split("=", 1)
            u[key] = value
        # identification
        self.wanted = False
        self.type = "systemd"
        self.stack = "systemd"
        self.name = u.get("Id", None)
        if self.name:
            self.name = self.name.replace(".service", "")
        self.pid = u.get("ExecMainPID", None)
        self.pid6 = None
        # status
        def state(u):
            load = u.get("LoadState", None)
            freeze = u.get("FreezerState", None)
            active = u.get("ActiveState", None)
            sub = u.get("SubState", None)
            if not load:
                return None
            if load != "loaded":
                return load
            if not freeze:
                return None
            if freeze != "running":
                return freeze
            if not active:
                return None
            if active in ["inactive", "failed"]:
                return active
            if not sub:
                return None
            if sub == "exited":
                return "finished"
            return sub
        self.state = state(u)
        self.created = None # no solution yet; check unit file creation timestamp?
        def fmt(t):
            log.debug(f"parsing time string: '{t}'")
            if not t:
                return None
            try:
                t = datetime.datetime.strptime(t, "%a %Y-%m-%d %H:%M:%S %Z")
                t = t.strftime("%Y-%m-%d %H:%M:%S")
            except:
                return None
            return t
        self.started = fmt(u.get("ExecMainStartTimestamp", None))
        self.finished = None # no solution yet
        self.changed = fmt(u.get("StateChangeTimestamp", None))
        # ressources
        def fmt(unit):
            mem = None
            try:
                mem = round(int(unit["MEM"]) / 1024 / 1024 / 1024 * 10) / 10
            except:
                pass
            return f"{mem}G" if mem else None
        self.mem = fmt(u.get("MemoryCurrent", None))
        def fmt(nanoseconds):
            if not nanoseconds:
                return None
            result = []
            try:
                total_seconds = int(nanoseconds) / 1e9
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = round((total_seconds % 60), 1)
                if hours > 0:
                    result.append(f"{hours}h")
                if minutes > 0:
                    result.append(f"{minutes}m")
                if seconds > 0 or not result:
                    result.append(f"{seconds}s")
            except:
                pass
            if not result:
                return None
            return " ".join(result)
        self.cpu = fmt(u.get("CPUUsageNSec", None))
        self.blockio = None
        self.netio = None
        self.netport = []
        self.netmap = []
        self.netmode = None
        self.mounts = None
        self.image = None
        self.imageid = None
        self.imageid6 = None
        self.imagever = None
        self.imagedate = None
        return True

    def docker_inspect(self, cid):
        """
        type criteria:
            TYPE/KEY    Image   RepoTag MountPoint
            container   yes     no      no
            image       no      yes     no
            volume      no      no      yes
        """
        # load system info
        self.initialize()
        c = sh.Process(["docker", "inspect", cid]).json[0]
        # check if we pass the type criteria
        if not c.get("Image", False):
            raise Exception("Cannot parse a docker item from other type than container!")
        # identification
        project = c.get("Config", {}).get("Labels", {}).get("com.docker.compose.project", "")
        self.type = "dockerd" if not project else "compose"
        self.stack = self.type if not project else project
        self.name = c.get("Config", {}).get("Labels", {}).get("com.docker.compose.service", None)
        if self.name is None:
            self.name = c.get("Name", None).strip("/")
        self.pid = c.get("Id", cid)
        self.pid6 = self.pid[0:6]
        # status
        notime = "0000-00-00 00:00:00"
        def fmt(dt):
            """YYYY-MM-DDTHH:MM:SS.NNNNNNNZ to YYYY-MM-DD HH:MM:SS"""
            if dt is None:
                return ""
            return dt[:19].replace("T", " ")
        def newer(this, that):
            this = datetime.datetime.strptime(this, '%Y-%m-%d %H:%M:%S')
            that = datetime.datetime.strptime(that, '%Y-%m-%d %H:%M:%S')
            return this > that
        self.state = c.get("State", {}).get("Status", None)
        self.created = fmt(c.get("Created", notime))
        self.started = fmt(c.get("State", {}).get("StartedAt", notime))
        self.finished = fmt(c.get("State", {}).get("FinishedAt", notime))
        self.changed = self.created
        if newer(self.started, self.changed):
            self.changed = self.started
        if newer(self.finished, self.changed):
            self.changed = self.finished
        # ressources
        #self.mem = None
        #self.cpu = None
        #self.blockio = None
        #self.netio = None
        self.netport = []
        self.netmap = []
        for cp, props in c.get("NetworkSettings", {}).get("Ports", {}).items():
            hp = "" if not props else props[0].get("HostPort", "")
            m = f"{hp}({cp})"
            self.netmap.append(m)
            if hp:
                self.netport.append(hp)
        self.netmode = c.get("HostConfig", {}).get("NetworkMode", "")
        def mnt(mounts):
            nv = 0
            nb = 0
            for mount in mounts:
                mtype = mount.get("Type", None)
                nb += int(mtype == "bind")
                nv += int(mtype == "volume")
            nv = f"{nv}V " if nv else ""
            nb = f"{nb}B" if nb else ""
            n = f"{nv}{nb}"
            return n if n else None
        self.mounts = mnt(c.get("Mounts", []))
        self.image = c.get("Config", {}).get("Image", None)
        self.imageid = c.get("Image", None)
        self.imageid6 = self.imageid.replace("sha256:", "")[:6] if self.imageid else None
        self.imagever = c.get("Config", {}).get("Labels", {}).get("org.opencontainers.image.version", "")
        self.imagedate = c.get("Config", {}).get("Labels", {}).get("org.opencontainers.image.created", "")
        return True

    def stop(self):
        log.info(f"stopping {self}")
        if self.stack == "compose":
            pass
        elif self.stack == "dockerd":
            log.critical("stopping a docker container is untested!")
            sh.Process(["docker", "stop", self.name])
        elif self.stack == "systemd":
            pass

    def restart(self, force=False):
        action = "force " if force else ""
        action += "restarting"
        log.info(f"{action} {self}...")
        if not force and self.state != "running":
            log.warning("ignore service which is not running")
            sys.exit(0)
        if self.stack == "compose":
            pass
        elif self.stack == "dockerd":
            pass
        elif self.stack == "systemd":
            pass


class Stack(object):
    """Handle a collection of Service objects."""
    def __init__(self, services=[], cfg=None):
        self.reconfigure()
        if services:
            for service in services:
                self.add(service)
        if isinstance(cfg, config.Config):
            f = cfg.get_systemd_units()
            f = {"Id": f} if f else f
            self.load_dockerd()
            self.load_systemd(filter=f)

    def __len__(self):
        return len(self.services)

    def __contains__(self, item):
        return any([item == service for service in self.services])

    def __str__(self):
        return f"<ServiceStack with {len(self.services)} items>"
    
    def __repr__(self):
        return str(self)

    def reconfigure(self):
        self.services = []

    def add(self, item, replace=True):
        if not isinstance(item, Service):
            return False
        if item not in self:
            self.services.append(item)
            return True
        for i in range(len(self)):
            if item == self.services[i]:
                # collect wanted state
                wanted = item.wanted or self.services[i].wanted
                # replace data
                if replace:
                    self.services[i] = item
                # update wanted state even when not replacing
                self.services[i].wanted = wanted
                # exit
                return True
        return False

    def get(self, name, default=None):
        """Get first service item matching a pattern."""
        for service in self.services:
            if service.name == name:
                return service
        return default

    def find(self, name, stack = None):
        """Return all services items matching a pattern."""
        services = []
        for service in self.services:
            if service.name == name:
                services.append(service)
        return services

    def load_dockerd(self, compose_file=None):
        # retrieve ids
        cmd = ["docker", "ps", "--all", "--format", "{{.ID}}"]
        if compose_file is not None:
            cmd = ["docker", "compose", "-f", compose_file, "ps", "--all", "--format", "{{.ID}}"] 
        ids = [i for i in sh.Process(cmd).lines if i]
        # retrieve and add data
        for id in ids:
            s = Service()
            s.docker_inspect(id)
            self.add(s, replace=True)

    def load_systemd(self, filter={}):
        # retrieve unit names
        cmd = ["systemctl", "list-units", "--type=service", "--all", "--no-pager", "--plain", "--no-legend"]
        units = sh.Process(cmd).lines
        units = [line.split(" ")[0].replace(".service", "") for line in units]
        # filter
        if filter:
            if isinstance(filter, config.Config):
                filter = {"Id": filter.get_systemd_units()}
            if "Id" in filter:
                if isinstance(filter["Id"], list):
                    units = [id for id in units if id in filter["Id"]]
                else:
                    units = [id for id in units if id == filter["Id"]]
        # retrieve and add data
        for unit in units:
            s = Service()
            s.systemctl_show(unit)
            s.wanted = filter and "Id" in filter
            self.add(s)

    def load_config(self, cfg):
        # systemd services
        for unit in cfg.get_systemd_units():
            s = Service(wanted=True, type="systemd", stack="systemd", name=unit)
            self.add(s)
        # docker compose stack services
        for compose_name, composed in cfg.config.get("services", {}).get("compose", {}).items():
            stack_ignored = composed.get("ignored", False)
            if stack_ignored:
                continue
            compose_path = composed.get("path", os.path.join("services", compose_name, "compose.yml"))
            compose_path = os.path.join(cfg.get_root_path(), compose_path)
            composed = io.read_yaml(compose_path)
            if composed is None:
                continue
            compose_services = composed.get("services", {})
            for service_name, serviced in compose_services.items():
                ports = " ".join(serviced.get('ports', []))
                portmap = re.sub(r"^0\.0\.0\.0:", "", ports)
                ports = re.sub(r":.*", "", portmap)
                portmap = portmap.split(":", 1)
                if len(portmap) > 1:
                    portmap[1] = f"({portmap[1]})"
                portmap = "".join(portmap)
                s = Service(wanted=True, type="compose", stack=compose_name, name=service_name, image=serviced.get('image', None), netport=ports, netmap=portmap)
                self.add(s)

    def table(self):
        rows = [] #[ s.__dict__ for s in self.services ]
        for s in self.services:
            row = { key.upper(): value for key, value in s.__dict__.items() }
            rows.append(row)
        return rows

    def up(self):
        pass

    def down(self):
        pass
