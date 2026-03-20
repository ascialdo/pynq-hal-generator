"""Orchestrate Jinja2 rendering and write output files."""

from __future__ import annotations
import re
from pathlib import Path

from jinja2 import PackageLoader, Environment, StrictUndefined

from .models import HalConfig


def _pascal_case(name: str) -> str:
    return "".join(word.capitalize() for word in re.split(r"[_\-\s]+", name))


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

    # Derive output package name from the output dir basename
    output_package = output_dir.name

    context = {
        "config": config,
        "submodule_path": submodule_path,
        "output_package": output_package,
    }

    written = {}

    # hal.py
    hal_path = output_dir / "hal.py"
    hal_path.write_text(env.get_template("hal.py.j2").render(**context))
    written["hal.py"] = hal_path

    # test_template.ipynb
    nb_path = output_dir / "test_template.ipynb"
    nb_path.write_text(env.get_template("test_template.ipynb.j2").render(**context))
    written["test_template.ipynb"] = nb_path

    # __init__.py — makes output_dir a Python package
    init_path = output_dir / "__init__.py"
    init_path.write_text("")
    written["__init__.py"] = init_path

    return written
