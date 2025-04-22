# 🎏 compose-stack

## 📚 About

Ever wondered how to make it more feasible managing multiple **docker compose** stacks at once?

Use `cs` aka docker *compose stack* control tool. 

For the impatient, start with the [Installation](#-installation) and [Quick Start](#-quick-start) chapters below.

## 💾 Installation

Clone the repository.

Follow the instructions in [Development](#-development) section.

## 🎬 Quick Start

✅ After installation, create a configuration file with `cs config --template > ~/compose-stack.yaml` which returns:

```yaml
# compose-stack.yaml

stack:
    website:
        path: ~/website/compose.yaml
    smarthome:
        path: /opt/smarthome/compose.yaml
    nextcloud:
        path: /data/nextcloud/compose.yaml
    test:
        path: /tmp/test-compose-stack/test.yaml
        ignored: True
```

✅ Adjust the respective docker compose stack with nameYAML configuration file paths.

✅ Use `cs --help` or `csctl --help` to identify actions or read further documentation.

## 📄 Documentation

There is only very little coverage on the documentation level.

The main source is to run the commands using the `--help` option.

## 💻 Developing

Please find the source code hosted on [github.com](https://github.com/setempler/compose-stack.py).

For developers, follow this workflow:

* Create a clean python virtual environment via `python3 -m venv cs.pyenv`.
* Load th3 python environment with `source cs.pyenv/bin/actviate`.
* Install developer libraries using `make init`.
* Install the module using `make install`.
* Build the HTML documentation with `make docs`.
* Run tests using `make test`.
* Add issues, pull requests, comments and other contributions to [github](https://github.com/setempler/compose-stack.py/issues).

## © Copying

See file `LICENSE`.
