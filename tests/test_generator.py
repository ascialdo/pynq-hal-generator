"""Tests for generator.py."""

import ast
import json
import tempfile
from pathlib import Path

import pytest

from pynq_hal_generator.parser import parse
from pynq_hal_generator.generator import generate

FIXTURE = Path(__file__).parent / "fixtures" / "axi_config.json"


def _get_cfg():
    return parse(FIXTURE, ip_name="logic_gate_tester", vlnv="xilinx.com:module_ref:logic_gate_tester:1.0")


def test_generate_creates_files():
    cfg = _get_cfg()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pynq_driver"
        written = generate(cfg, out)
        assert (out / "hal.py").exists()
        assert (out / "test_template.ipynb").exists()
        assert (out / "__init__.py").exists()


def test_hal_py_valid_syntax():
    cfg = _get_cfg()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pynq_driver"
        generate(cfg, out)
        source = (out / "hal.py").read_text()
        ast.parse(source)


def test_hal_has_bindto():
    cfg = _get_cfg()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pynq_driver"
        generate(cfg, out)
        source = (out / "hal.py").read_text()
        assert "bindto" in source
        assert "xilinx.com:module_ref:logic_gate_tester:1.0" in source


def test_hal_no_setter_for_ro_register():
    cfg = _get_cfg()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pynq_driver"
        generate(cfg, out)
        source = (out / "hal.py").read_text()
        for line in source.splitlines():
            if "@reg_errors.setter" in line:
                pytest.fail("Found setter for read-only register REG_ERRORS")


def test_hal_no_utility_methods():
    cfg = _get_cfg()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pynq_driver"
        generate(cfg, out)
        source = (out / "hal.py").read_text()
        assert "def reset(" not in source
        assert "def run_all_tests(" not in source
        assert "def test_register_rw(" not in source


def test_notebook_valid_json():
    cfg = _get_cfg()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pynq_driver"
        generate(cfg, out)
        nb_text = (out / "test_template.ipynb").read_text()
        nb = json.loads(nb_text)
        assert nb["nbformat"] == 4


def test_notebook_five_cells():
    cfg = _get_cfg()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pynq_driver"
        generate(cfg, out)
        nb = json.loads((out / "test_template.ipynb").read_text())
        assert len(nb["cells"]) == 5


def test_notebook_cell4_reads_registers():
    cfg = _get_cfg()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pynq_driver"
        generate(cfg, out)
        nb = json.loads((out / "test_template.ipynb").read_text())
        cell4_src = "".join(nb["cells"][3]["source"])
        assert "reg_ctrl" in cell4_src
        assert "hex(dut." in cell4_src


def test_notebook_sys_path_insert():
    cfg = _get_cfg()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pynq_driver"
        generate(cfg, out, submodule_path="./logic-gates-tester")
        nb = json.loads((out / "test_template.ipynb").read_text())
        cell1_src = "".join(nb["cells"][0]["source"])
        assert "sys.path.insert" in cell1_src
        assert "./logic-gates-tester" in cell1_src
