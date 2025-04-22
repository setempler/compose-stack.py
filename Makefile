# Makefile

SHELL := /usr/bin/bash
venv := $(shell basename "$$VIRTUAL_ENV")

.PHONY: all
all: init test install docs

.PHONY: init
init:
	@echo -n "virtual environment '$(venv)' ... "
	@[ -z $$VIRTUAL_ENV ] && echo please check && exit 1 || echo ok
	@pip install --upgrade pip
	@pip install -r requirements.txt
	@pip install -r requirements-dev.txt

.PHONY: install
install:
	@which python
	@pip uninstall compose-stack -y
	@pip install -e .

.PHONY: install test
test:
	@pytest -v --cov=./cs/

.PHONY: docs
docs:
	@cd docs && make html

.PHONY: build
build:
	@python -m build --sdist
	@python -m build --wheel

.PHONY: test_upload
test_upload:
	@echo test
	@twine upload --repository compose-stack dist/*

.PHONY: upload-info
upload-info:
	@echo latest version:
	@curl -sL https://pypi.python.org/pypi/compose-stack/json | python -m json.tool | grep version | grep -v python | awk '{print "  "$$2}'
	@echo available uploads:
	@ls dist/ | sed 's/^/  /'

.PHONY: upload
upload: clean install docs test upload-info
	@echo info:
	@echo ' . now run twine upload dist/<your egg>'

.PHONY: clean
clean:
	@find . -type f -iname '*.pyc' -delete
	@find . -type d -iname __pycache__ -delete
	@rm -rf .pytest_cache
	@rm -rf docs/_build docs/_autosummary
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -f cs/_version.py
	@rm -f .coverage
	@pip uninstall -y compose-stack

