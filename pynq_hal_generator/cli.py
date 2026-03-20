"""CLI entry point for pynq-hal-gen."""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .parser import parse
from .generator import generate


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="pynq-hal-gen",
        description="Generate a PYNQ HAL class and Jupyter notebook from axi_config.json",
    )
    parser.add_argument("config", help="Path to axi_config.json")
    parser.add_argument(
        "--output-dir",
        default="pynq_driver",
        help="Directory for generated files (default: pynq_driver/)",
    )
    parser.add_argument(
        "--ip-name",
        default=None,
        help="IP name used for class naming; defaults to parent directory name",
    )
    parser.add_argument(
        "--vlnv",
        default=None,
        help="IP VLNV string; defaults to xilinx.com:module_ref:<ip_name>:1.0",
    )
    parser.add_argument(
        "--submodule-path",
        default=".",
        help=(
            "Relative path from the board repo notebook to the HDL submodule root "
            "(used for sys.path.insert in the generated notebook). Default: '.'"
        ),
    )

    args = parser.parse_args(argv)

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    ip_name = args.ip_name or config_path.parent.name
    vlnv = args.vlnv or f"xilinx.com:module_ref:{ip_name}:1.0"

    hal_config = parse(config_path, ip_name=ip_name, vlnv=vlnv)
    written = generate(hal_config, output_dir=Path(args.output_dir), submodule_path=args.submodule_path)

    for name, path in written.items():
        print(f"  wrote {path}")


if __name__ == "__main__":
    main()
