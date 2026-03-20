# pynq-hal-generator

Generates a PYNQ HAL Python class and a Jupyter notebook test scaffold from an `axi_config.json` file.

## Install

```bash
pip install git+https://github.com/ascialdo/pynq-hal-generator
```

## Usage

```bash
pynq-hal-gen axi_config.json \
  --output-dir pynq_driver \
  --ip-name logic_gate_tester \
  --vlnv xilinx.com:module_ref:logic_gate_tester:1.0 \
  --submodule-path ./logic-gates-tester
```

### Arguments

| Argument | Default | Description |
|---|---|---|
| `config` | (required) | Path to `axi_config.json` |
| `--output-dir` | `pynq_driver/` | Output directory |
| `--ip-name` | parent dir name | Used for class naming (`logic_gate_tester` → `LogicGateTester`) |
| `--vlnv` | `xilinx.com:module_ref:<ip_name>:1.0` | IP VLNV string for `bindto` |
| `--submodule-path` | `.` | Relative path from board repo notebook to HDL submodule root (used in `sys.path.insert`) |

## Outputs

All files are written to `--output-dir`:

- **`hal.py`** — `<PascalCase(ip_name)>` class inheriting `pynq.DefaultIP` with register properties, field-level helpers, `reset()`, `__repr__`, and `run_all_tests()`
- **`test_template.ipynb`** — 6-cell Jupyter notebook scaffold
- **`__init__.py`** — makes the output dir a Python package

### Using the HAL in a board repo notebook

If the HDL repo is a submodule at `./logic-gates-tester/`:

```python
import sys
sys.path.insert(0, './logic-gates-tester/pynq_driver')
from hal import LogicGateTester
```

## CI Integration

In your HDL repo's `.gitlab-ci.yml`:

```yaml
generate_hal:
  stage: hal
  before_script:
    - pip install git+https://github.com/ascialdo/pynq-hal-generator
  script:
    - pynq-hal-gen axi_config.json --output-dir pynq_driver --ip-name $CI_PROJECT_NAME
  artifacts:
    paths:
      - pynq_driver/
```

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```
