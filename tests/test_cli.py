"""Tests for cli.py."""

import json
import tempfile
from pathlib import Path

import pytest

from pynq_hal_generator.cli import main

FIXTURE = str(Path(__file__).parent / "fixtures" / "axi_config.json")


def test_cli_smoke(tmp_path):
    out = tmp_path / "pynq_driver"
    main([FIXTURE, "--output-dir", str(out), "--ip-name", "logic_gate_tester"])
    assert (out / "hal.py").exists()
    assert (out / "test_template.ipynb").exists()
    assert (out / "__init__.py").exists()


def test_cli_default_ip_name(tmp_path):
    """ip-name defaults to parent dir of axi_config.json."""
    out = tmp_path / "pynq_driver"
    main([FIXTURE, "--output-dir", str(out)])
    assert (out / "hal.py").exists()


def test_cli_custom_vlnv(tmp_path):
    out = tmp_path / "pynq_driver"
    main([FIXTURE, "--output-dir", str(out), "--ip-name", "my_ip", "--vlnv", "acme.com:user:my_ip:2.0"])
    source = (out / "hal.py").read_text()
    assert "acme.com:user:my_ip:2.0" in source


def test_cli_submodule_path(tmp_path):
    out = tmp_path / "pynq_driver"
    main([FIXTURE, "--output-dir", str(out), "--ip-name", "x", "--submodule-path", "./my-hdl-repo"])
    nb = json.loads((out / "test_template.ipynb").read_text())
    cell1 = "".join(nb["cells"][0]["source"])
    assert "./my-hdl-repo" in cell1


def test_cli_missing_config(tmp_path, capsys):
    with pytest.raises(SystemExit):
        main(["nonexistent.json", "--output-dir", str(tmp_path)])
    captured = capsys.readouterr()
    assert "not found" in captured.err
