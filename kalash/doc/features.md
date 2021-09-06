# Features

## What **you** can do with Kalash

- Run Software or Hardware tests in an automated context as well as locally:
    - As singular Python Scripts
    - As test suites defined in a simple declarative [YAML](yaml_spec.md#yaml-config-file-specification) file or more flexible [Python configuration files](python_spec.md#python-config-file-specification)
    - In [isolation](basic_usage.md#why-use-kalash) from lower-level automation server job configuration (e.g. you don't need to manage Jenkins to change the definition of a test suite to be triggered by a job)
- [Filter](yaml_spec.md#yaml-config-file-specification) test cases by way more than just a name, defining rich, complex test suites
- Document metadata for your test cases in a manner that is [both human-readable and machine-readable](basic_usage.md#creating-test-cases)
- Generate [standard XML XUnit reports](basic_usage.md#reports)
- Log whatever happens within the test cases on a [per-test-case level of granularity](basic_usage.md#logging)
- [Parameterize](advanced_config.md#accessing-configuration-from-within-test-cases) test cases easily
- Perform [hypothetical runs](advanced_config.md#hypothetical-runs)

Read [Why Use Kalash](basic_usage.md#why-use-kalash) to get a more comprehenisve overview of the system.

## Notable Features Available

- [Filtering](yaml_spec.md#yaml-config-file-specification) by metadata tags
- [Python](python_spec.md#python-config-file-specification) or [YAML](yaml_spec.md#yaml-config-file-specification) declarative-style configuration files for test suites
- [Setup and Teardown](advanced_config.md#setup-and-teardown) scripts are supported
- `--no-recurse` option
- `--fail-fast` option
- Each test case has its own [logger](basic_usage.md#logging)
- `--what-if` option
- [Logger configuration](basic_usage.md#logging) via CLI
- [Dynamic parametrization](advanced_config.md#accessing-configuration-from-within-test-cases) of the test cases

## Notable Features Planned

- Log files grouping based on arbitrary metadata tags
- Stable last-result filtering
- JIRA integration - loading metadata automatically from JIRA tickets
