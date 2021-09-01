# Features

## What **you** can do with Kalash

- Run Software or Hardware tests in an automated context as well as locally:
    - As singular Python Scripts
    - As test suites defined in a simple declarative [YAML][YAML Spec] file or more flexible [Python configuration files][Python Spec]
    - In [isolation][Why] from lower-level automation server job configuration (e.g. you don't need to manage Jenkins to change the definition of a test suite to be triggered by a job)
- [Filter][YAML Spec] test cases by way more than just a name, defining rich, complex test suites
- Document metadata for your test cases in a manner that is [both human-readable and machine-readable][Test Case Main Example]
- Generate [standard XML XUnit reports][Reports]
- Log whatever happens within the test cases on a [per-test-case level of granularity][Logging]
- [Parameterize][Dynamic parametrization] test cases easily
- Perform [hypothetical runs][What If]

Read [Why Use Kalash][Why] to get a more comprehenisve overview of the system.

## Notable Features Available

- [Filtering][YAML Spec] by metadata tags
- [Python][Python Spec] or [YAML][YAML Spec] declarative-style configuration files for test suites
- [Setup and Teardown][Setup Teardown] scripts are supported
- `--no-recurse` option
- `--fail-fast` option
- Each test case has its own [logger][Logging]
- `--what-if` option
- [Logger configuration][Logging] via CLI
- [Dynamic parametrization][Dynamic parametrization] of the test cases

## Notable Features Planned

- Log files grouping based on arbitrary metadata tags
- Stable last-result filtering
- JIRA integration - loading metadata automatically from JIRA tickets
