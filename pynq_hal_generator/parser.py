"""Parse axi_config.json into HalConfig."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Union

from .models import Field, HalConfig, Register


def _parse_bits(bits: Any) -> tuple[int, int]:
    """Normalise bits to (bit_high, bit_low)."""
    if isinstance(bits, list):
        return max(bits), min(bits)
    if isinstance(bits, str):
        if ":" in bits:
            parts = bits.split(":")
            return int(parts[0]), int(parts[1])
        return int(bits), int(bits)
    if isinstance(bits, int):
        return bits, bits
    raise ValueError(f"Unsupported bits format: {bits!r}")


def _parse_field(raw: Dict[str, Any]) -> Field:
    port = raw.get("port") or raw.get("name")
    if port is None:
        raise ValueError(f"Field has neither 'port' nor 'name': {raw}")
    bit_high, bit_low = _parse_bits(raw["bits"])
    return Field(
        port=port,
        bit_high=bit_high,
        bit_low=bit_low,
        access=raw.get("access", "RW"),
        description=raw.get("description", ""),
    )


def _parse_register(name: str, raw: Dict[str, Any]) -> Register:
    offset_str = raw["offset"]
    offset = int(offset_str, 16) if isinstance(offset_str, str) else int(offset_str)
    fields = [_parse_field(f) for f in raw.get("fields", [])]
    return Register(
        name=name,
        offset=offset,
        offset_hex=hex(offset),
        description=raw.get("description", ""),
        fields=fields,
    )


def parse(config_path: Union[str, Path], ip_name: str, vlnv: str) -> HalConfig:
    config_path = Path(config_path)
    with config_path.open() as fh:
        raw = json.load(fh)

    register_width = raw.get("register_width", 32)
    registers_raw = raw["registers"]

    if isinstance(registers_raw, dict):
        items = registers_raw.items()
    elif isinstance(registers_raw, list):
        items = ((r["name"], r) for r in registers_raw)
    else:
        raise ValueError("'registers' must be a dict or list")

    registers = [_parse_register(name, data) for name, data in items]
    for reg in registers:
        reg.register_width = register_width

    return HalConfig(
        ip_name=ip_name,
        vlnv=vlnv,
        registers=registers,
        register_width=register_width,
    )
