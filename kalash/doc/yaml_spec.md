# YAML Config File Specification

[YAML Spec]: #yaml-config-file-specification
[Kalash Spec From Code]: #kalash.config.Spec

## Example YAML (simple)

A conventional metadata tag in a test template looks like this:

```python
"""
META_START
---
id: 000000003_12_0_1234-SomethingElse 
use_cases:
  - Some Jira ticket
workbenches:
  - BloodhoundGang
META_END

Below the META_END tag you can write any additional comments you need
for your test case.
"""
```

It's always placed at the top of the test case file.

Imagine it's saved under `test_something.py`. The simplest way to run the test case using Kalash would be:

1. Create a `something.yaml` file with the following contents:

    ```yaml
    tests:
      - path: './test_something.py'
    ```

2. Run `kalash run -f ./something.yaml`.

## Config section

The configuration file is split into two components: `tests` and `config`.

* `tests` - this section defines **solely the test collection process**.
* `config` - this section **modifies runtime behavior of the test cases**.

`config` section is optional.

## Advanced features

Read [advanced configuration options](advanced_config.md#base-directory-resolution-in-config-files) to learn more about the more advanced configuration options using the YAML file.

## Example YAML (complex)

```yaml
tests:
  - path: '$(WorkDir)/tests/test_scripts'
    id:
      - '000000003_12_0_1234-SomethingElse'
    setup: '$(ThisFile)/../tests/test_scripts/setup_teardown/setup_files/setup.py'
    teardown: '$(WorkDir)/tests/test_scripts/setup_teardown/setup_files/teardown.py'
config:
  report: './kalash_reports'
```

## Full API specification

The allowed up-to date values for the YAML specification are outlined in the documentation of the [`Spec` class][kalash.config.Spec].
