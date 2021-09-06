# Python Config File Specification

[Python Spec]: #python-config-file-specification

Python configuration files follow the same pattern as the YAML configuration files, albeit in Python code. It's best to explain it with an example:

```python
from kalash.config import CliConfig, Config, Trigger, Test
from kalash.run import run

t = Trigger(
    tests=[
        Test(
            path='./tests/some_directory'
        )
    ],
    config=Config(report='report-dir')
)

if __name__ == "__main__":
    run(t)

```

The entrypoint `run` accepts a `Trigger` instance which is a direct equivalent of a YAML configuration file. A `Trigger` object consists of:

- `tests` - a list of `Test` objects responsible for test collection configuration
- `config` - a `Config` object that modifies runtime parameters

## Extending specification

You can inherit from the original `Test` and `Config` classes to extend the configuration:

```python
from typing import Any, Dict, List
from kalash.config import CliConfig, Config, Trigger, Test, dataclass, field
from kalash.run import run


@dataclass
class CustomConfig(Config):
    run_only_with: List[str] = field(default_factory=list)


t = Trigger(
    tests=[
        Test(
            path='./tests/test_scripts/python_instead_of_yaml'
        )
    ],
    config=CustomConfig(run_only_with=['cancombo'])
)

if __name__ == "__main__":
    run(t)

```

One caveat here is that **you must provide default values** for each new attribute on a customized class. That's because the default classes already have sensible defaults baked in and you cannot place attributes without default values after attributes with default values.

## Running tests with a Python config

Because this is a Python file you can either run it directly or still use Kalash CLI to trigger your tests.

### Running with Kalash CLI

Simply put: `kalash -f ./path/to/config.py`.

### Runing directly with Python

If the `__main__` clause is present in the file you may just trigger the script with Python, e.g. `python ./path/to/config.py`.

The difference is that when you run this as a Python script you will not be able to provide additional CLI flags on the command line. But you may choose to feed them in directly within the configuration file:

```python
from kalash.config import CliConfig, Config, Trigger, Test
from kalash.run import run

t = Trigger(
    tests=[
        Test(
            path='./tests/some_directory'
        )
    ],
    config=Config(report='report-dir')
)

if __name__ == "__main__":
    run(t, CliConfig(log_dir='logs'))

```

Note:

- The **python config is a better choice when you want to preserve CLI configuration** for all future runs.
- The **`CliConfig` specified in the file will be overridden if you run this with `kalash` CLI command**.
