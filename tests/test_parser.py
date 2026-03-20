"""Tests for parser.py."""

import pytest
from pathlib import Path

from pynq_hal_generator.parser import parse, _parse_bits

FIXTURE = Path(__file__).parent / "fixtures" / "axi_config.json"


def test_parse_bits_list():
    assert _parse_bits([0, 0]) == (0, 0)
    assert _parse_bits([9, 6]) == (9, 6)
    assert _parse_bits([31, 0]) == (31, 0)


def test_parse_bits_string():
    assert _parse_bits("5:2") == (5, 2)
    assert _parse_bits("0") == (0, 0)


def test_parse_bits_int():
    assert _parse_bits(3) == (3, 3)


def test_parse_fixture():
    cfg = parse(FIXTURE, ip_name="logic_gate_tester", vlnv="xilinx.com:module_ref:logic_gate_tester:1.0")
    assert cfg.ip_name == "logic_gate_tester"
    assert cfg.register_width == 32
    assert len(cfg.registers) == 4


def test_register_names():
    cfg = parse(FIXTURE, ip_name="x", vlnv="v")
    names = [r.name for r in cfg.registers]
    assert "REG_CTRL" in names
    assert "REG_ERRORS" in names
    assert "ERROR_SELECT" in names
    assert "READ_LATENCY" in names


def test_reg_errors_is_read_only():
    cfg = parse(FIXTURE, ip_name="x", vlnv="v")
    reg = next(r for r in cfg.registers if r.name == "REG_ERRORS")
    assert reg.is_read_only is True


def test_reg_ctrl_is_not_read_only():
    cfg = parse(FIXTURE, ip_name="x", vlnv="v")
    reg = next(r for r in cfg.registers if r.name == "REG_CTRL")
    assert reg.is_read_only is False


def test_reg_ctrl_offsets():
    cfg = parse(FIXTURE, ip_name="x", vlnv="v")
    reg = next(r for r in cfg.registers if r.name == "REG_CTRL")
    assert reg.offset == 0x00
    reg_errors = next(r for r in cfg.registers if r.name == "REG_ERRORS")
    assert reg_errors.offset == 0x08


def test_field_mask():
    cfg = parse(FIXTURE, ip_name="x", vlnv="v")
    reg = next(r for r in cfg.registers if r.name == "REG_CTRL")
    input_a = next(f for f in reg.fields if f.port == "input_a")
    # bits [5,2] → mask = 0b111100 = 0x3C
    assert input_a.mask == 0x3C
    assert input_a.mask_hex == "0x3c"
