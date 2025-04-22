# tests.test_io


import json
import logging


import yaml
import pytest


from cs.io import read_txt, read_json, read_yaml


def test_read_txt_basic(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("Hello, world!")    
    result = read_txt(str(file))
    assert result == "Hello, world!"


def test_read_txt_with_encoding(tmp_path):
    file = tmp_path / "utf_test.txt"
    file.write_text("Café", encoding="utf-8")
    result = read_txt(str(file), encoding="utf-8")
    assert result == "Café"


def test_read_txt_binary_mode(tmp_path):
    file = tmp_path / "binary_test.txt"
    file.write_bytes(b"\x00\x01\x02")
    result = read_txt(str(file), "rb")
    assert result == b"\x00\x01\x02"


def test_read_txt_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_txt("nonexistent.txt")


def test_read_json_valid(tmp_path):
    data = {"name": "Alice", "age": 30}
    file = tmp_path / "data.json"
    file.write_text(json.dumps(data))
    result = read_json(str(file))
    assert result == data


def test_read_json_invalid_json(tmp_path):
    file = tmp_path / "invalid.json"
    file.write_text("{bad json: }")  # malformed
    with pytest.raises(json.JSONDecodeError):
        read_json(str(file))


def test_read_json_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_json("nonexistent.json")


def test_read_yaml_basic(tmp_path):
    file = tmp_path / "config.yml"
    content = {"name": "Alice", "age": 30}
    file.write_text(yaml.dump(content))

    result = read_yaml(str(file))
    assert result == content


def test_read_yaml_with_include(tmp_path):
    # File to include
    included = tmp_path / "included.yml"
    included.write_text("job: engineer")
    # Main YAML using !include
    main = tmp_path / "main.yml"
    main.write_text("person: !include included.yml")
    result = read_yaml(str(main))
    assert result == {"person": {"job": "engineer"}}


def test_read_yaml_file_not_found(caplog):
    with caplog.at_level(logging.ERROR):
        result = read_yaml("nonexistent.yaml")
        assert result == {}
        assert "missing YAML file" in caplog.text


def test_read_yaml_invalid_yaml(tmp_path, caplog):
    bad_file = tmp_path / "bad.yml"
    bad_file.write_text("this: [unclosed")
    with caplog.at_level(logging.ERROR):
        result = read_yaml(str(bad_file))
        assert result == {}
        assert "failed importing" in caplog.text


def test_read_yaml_logging_info_debug(tmp_path, caplog):
    file = tmp_path / "logtest.yml"
    file.write_text("hello: world")
    with caplog.at_level(logging.DEBUG):
        result = read_yaml(str(file))
        assert result == {"hello": "world"}
        assert "parsing YAML" in caplog.text
        assert "parsed YAML content" in caplog.text