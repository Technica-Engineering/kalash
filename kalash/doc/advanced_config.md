# Advanced Configuration and Usage

## Base directory resolution in config files

[Interpolate WorkDir ThisFile]: #base-directory-resolution-in-config-files

By default an expression like `path: './test_something.py'` defaults to working directory: it will **look for paths relative to where `kalash` command is run**. For convenience we expose the following directory resolution options:

* `$(WorkDir)` - same behavior as `.`, relative to working directory.
* `$(ThisFile)` - relative to the location of the configuration file itself.

## Setup and teardown

[Setup Teardown]: #setup-and-teardown

On top of the standard `setUp` and `tearDown` methods we offer `setup` and `teardown` script mappings. For example:

```yaml
tests:
  - path: '$(WorkDir)/tests/test_scripts'
    setup: '$(ThisFile)/../tests/test_scripts/setup_teardown/setup_files/setup.py'
    teardown: '$(WorkDir)/tests/test_scripts/setup_teardown/setup_files/teardown.py'
config:
  report: './kalash_reports'
  setup: '$(ThisFile)/../tests/test_scripts/setup_teardown/setup_files/setup.py'
  teardown: '$(WorkDir)/tests/test_scripts/setup_teardown/setup_files/teardown.py'
```

The two flavors can be explained as follows:

* If the `setup`/`teardown` step is under a `Test` element (under `tests` in the YAML config) it runs once before/after the complete collection of tests from a `Test` element.
* If the `setup`/`teardown` step is under a `Config` element (under `config` in the YAML config) it runs once before/after the complete collection of tests from the entire run.

## Accessing configuration from within test cases

[Dynamic parametrization]: #accessing-configuration-from-within-test-cases

To allow dynamic parametrization we expose the following pattern:

```python
"""
META_START
---
id: 999999002_99-Blah_9-Whatever
META_END
"""

from kalash.run import MetaLoader, TestCase, main, parameterized

import os


class TestAdvancedFiltering1(TestCase):

    @parameterized.expand(['lincombo', 'cancombo'])
    def test_1(self, name):
        self.allow_when('run_only_with', name)
        print(f"Running for {name}")


if __name__ == '__main__':
    main(testLoader=MetaLoader())

```

`@parameterized.expand` is essentially unchanged, coming from the original `parameterized` Python library. `self.allow_when` queries the `config` section of the used configuration file with `run_only_with` and checks whether `name` is within the list of the `run_only_with` tags. Any configuration options can be filtered in this way, even `report`.

`self.allow_when` will only allow a parameterized test case to be triggered when the condition is met. If the file is run locally (triggered as a Python script, not via Kalash), the call will simply be ignored (since there is no config being provided in such a situation).

### Accessing configuration directly

The `TestCase` class exposes `trigger` property which lets you directly refer to the test case configuration elements:

```python
"""
META_START
---
id: 999999002_99-Blah_9-Whatever
META_END
"""

from kalash.run import MetaLoader, TestCase, main, parameterized


class TestSomething(TestCase):

    def test_1(self, name):
        if self.trigger:
            if self.trigger.config:
                # prints the `config` section
                print(self.trigger.config)


if __name__ == '__main__':
    main(testLoader=MetaLoader())

```

The name `trigger` comes from the name of the class used in [Python configuration files](kalash/doc/python_spec.md).

## Hypothetical runs

[What If]: #hypothetical-runs

If you wish to see what tests Kalash would run if it were to be triggered use the `--what-if` flag.

* `kalash -f some.yaml --what-if paths` - list all collected test paths
* `kalash -f some.yaml --what-if ids` - list all collected test ids
