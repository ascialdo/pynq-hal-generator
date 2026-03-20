"""Orchestrate Jinja2 rendering and write output files."""

from __future__ import annotations
import json
import re
from pathlib import Path

from jinja2 import PackageLoader, Environment, StrictUndefined

from .models import HalConfig


def _pascal_case(name: str) -> str:
    return "".join(word.capitalize() for word in re.split(r"[_\-\s]+", name))


def _build_notebook(config: HalConfig, submodule_path: str, output_package: str) -> dict:
    """Build the test notebook as a Python dict (serialised separately as JSON)."""
    pascal_name = _pascal_case(config.ip_name)

    def code_cell(source: list) -> dict:
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source,
        }

    cell1 = [
        "# Cell 1: imports\n",
        "import sys\n",
        f"sys.path.insert(0, '{submodule_path}')\n",
        "\n",
        "import pynq\n",
        "import numpy as np\n",
        f"from {output_package}.hal import {pascal_name}",
    ]

    cell2 = [
        "# Cell 2: load overlay\n",
        "ol = pynq.Overlay('design_1.bit')",
    ]

    cell3 = [
        "# Cell 3: instantiate HAL\n",
        f"dut = ol.{config.ip_name}_0\n",
        "print(type(dut))",
    ]

    reg_lines = ["# Cell 4: read all registers\n"]
    for reg in config.registers:
        reg_lines.append(f"print('{reg.name}:', hex(dut.{reg.name.lower()}))\n")
    if reg_lines[-1].endswith("\n"):
        reg_lines[-1] = reg_lines[-1][:-1]

    cell5 = [
        "# Cell 5: Custom Tests\n",
        "# Add your test cases here\n",
    ]

    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.8.0"},
        },
        "cells": [
            code_cell(cell1),
            code_cell(cell2),
            code_cell(cell3),
            code_cell(reg_lines),
            code_cell(cell5),
        ],
    }


def generate(
    config: HalConfig,
    output_dir: Path,
    submodule_path: str = ".",
) -> dict[str, Path]:
    """Render templates and write outputs. Returns {name: path} for written files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=PackageLoader("pynq_hal_generator", "templates"),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    env.filters["pascal_case"] = _pascal_case

    output_package = output_dir.name

    written = {}

    # hal.py
    hal_path = output_dir / "hal.py"
    hal_path.write_text(env.get_template("hal.py.j2").render(config=config))
    written["hal.py"] = hal_path

    # test_template.ipynb — built programmatically to avoid JSON escaping issues
    nb_path = output_dir / "test_template.ipynb"
    nb = _build_notebook(config, submodule_path, output_package)
    nb_path.write_text(json.dumps(nb, indent=1))
    written["test_template.ipynb"] = nb_path

    # __init__.py
    init_path = output_dir / "__init__.py"
    init_path.write_text("")
    written["__init__.py"] = init_path

    return written
