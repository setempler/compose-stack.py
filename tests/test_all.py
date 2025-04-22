# tests.test_all


import os
import pytest


import cs
from cs.config import Config
from cs.service import Service, Stack


def test_version_is_string():
    assert isinstance(cs.version, str)


def test_create_Config_obj():
    cfg = Config()
    assert isinstance(cfg, Config)


def test_Config_raises_ValueError():
    os.environ.pop("COMPOSE_STACK_CONFIG", None)
    with pytest.raises(ValueError, match="Cannot find configuration file"):
        Config()
    #os.environ["COMPOSE_STACK_CONFIG"] = ""


def test_create_Service_obj():
    srv = Service()
    assert isinstance(srv, Service)


def test_create_Stack_obj():
    stk = Stack()
    assert isinstance(stk, Stack)