# cs.system


"""operating system interactions"""


import yaml
import logging
log = logging.getLogger()


from . import sh
from . import dt


def which(bin):
    """Get path to file of a command.

    Uses system's `which` tool.
    Returns the path to the tool or `None` if not found.
    """
    path = sh.Process(["which", bin]).stdoutstripped
    if not len(path):
        return None
    return path[0]
    

def get_os():
    try:
        # linux
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("ID="):
                    # debian, ubuntu, ...
                    return line.strip().split("=", 1)[1].replace('"', '')
    except FileNotFoundError:
        return None
    return None


def get_docker_containers():
    cmd = ["docker", "ps", "-a", "--format", "{{.ID}}"]
    ids = sh.Process(cmd).lines
    containers = []
    for id in ids:
        image = sh.Process(["docker", "inspect", id]).json[0]
        tag = image.get("RepoTags", [])
        conf = image.get("Config", {})
        conf_labs = conf.get("Labels", {})
        entry = {}
        entry["ID"] = id
        entry["TAG"] = "" if not len(tag) else tag[0]
        entry["CREATED"] = f"{dt.simplify_systemd(image.get('Created', ''))}"
        entry["VERSION"] = None if conf_labs is None else conf_labs.get("org.opencontainers.image.version", "")
        containers.append(entry)
    return containers


def get_docker_images():
    cmd = ["docker", "images", "--format", "{{.ID}}"]
    ids = sh.Process(cmd).lines
    images = []
    for id in ids:
        image = sh.Process(["docker", "inspect", id]).json[0]
        tag = image.get("RepoTags", [])
        conf = image.get("Config", {})
        conf_labs = conf.get("Labels", {})
        entry = {}
        entry["ID"] = id
        entry["TAG"] = "" if not len(tag) else tag[0]
        entry["CREATED"] = f"{dt.simplify_systemd(image.get('Created', ''))}"
        entry["VERSION"] = None if conf_labs is None else conf_labs.get("org.opencontainers.image.version", "")
        images.append(entry)
    return images


def get_docker_volumes():
    cmd = ["docker", "volume", "ls", "-q"]
    ids = sh.Process(cmd).lines
    volumes = []
    for id in ids:
        volume = sh.Process(["docker", "inspect", id]).json[0]
        log.debug(f"volume={volume}")
        labels = volume.get("Labels", {})
        if labels is None:
            labels = {}
        compose_project = labels.get("com.docker.compose.project", None)
        compose_volume = labels.get("com.docker.compose.volume", None)
        mount_path = volume.get("Mountpoint", None)
        created = volume.get("CreatedAt", None)
        entry = {
            "ID": id,
            "COMPOSE_PROJECT": compose_project,
            "COMPOSE_VOLUME": compose_volume,
            "CREATED": dt.simplify_systemd(created),
            "MOUNT_PATH": mount_path,
        }
        volumes.append(entry)
    return volumes



def get_dockerd_stats():
    cmd = ["docker", "stats", "--no-stream", "--format", "json"]
    stats = sh.Process(cmd).json_lines
    services = []
    for s in stats:
        entry = {}
        entry["CONTAINER.ID"] = s.get("ID", None)
        if entry["CONTAINER.ID"] is None:
            continue
        entry["MEM"] = s.get("MemUsage", "").split(" / ")[0].rstrip("GMKiB")
        entry["CPU"] = s.get("CPUPerc", "")
        entry["IO.BLK"] = s.get("BlockIO", "")
        entry["IO.NET"] = s.get("NetIO", "")
    return services


def get_dockerd_df():
    cmd = ["docker", "system", "df", "--format", "json"]
    lines = sh.Process(cmd).lines
    lines = ",".join(lines)
    lines = f"[{lines}]"
    df = yaml.safe_load(lines)
    return df