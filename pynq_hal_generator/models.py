"""Data models for the PYNQ HAL generator."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Field:
    port: str
    bit_high: int
    bit_low: int
    access: str
    description: str

    @property
    def mask(self) -> int:
        width = self.bit_high - self.bit_low + 1
        return ((1 << width) - 1) << self.bit_low

    @property
    def mask_hex(self) -> str:
        return hex(self.mask)

    @property
    def is_single_bit(self) -> bool:
        return self.bit_high == self.bit_low


@dataclass
class Register:
    name: str
    offset: int
    offset_hex: str
    description: str
    fields: List[Field] = field(default_factory=list)
    register_width: int = 32

    @property
    def is_read_only(self) -> bool:
        if not self.fields:
            return False
        return all(f.access == "RO" for f in self.fields)

    @property
    def has_fields(self) -> bool:
        return bool(self.fields)


@dataclass
class HalConfig:
    ip_name: str
    vlnv: str
    registers: List[Register]
    register_width: int = 32
