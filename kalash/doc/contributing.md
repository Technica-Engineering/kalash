# Contributing

## Prerequisites

All you need to develop for this project is to `pip install nox`.

`nox` is a build and test automation driver for Python development that will automatically prepare your environment for testing.

## Contributing - process

Before submitting a pull request you must make sure that the CI pipeline passes all tests. The simplest way to contribute is thus:

1. Fork this repo.
2. Implement tests for your change (Test-Driven Development).
3. Implement your change.
4. Run tests locally using `nox -e test`.
5. Check whether your tests have satisfactory coverage under `htmlcov/index.html`. Our minimum target coverage is 80%.
6. Document the change.
7. Update the `CHANGELOG`. Use the [correct](https://keepachangelog.com/en/1.0.0/) style guidelines for the changelog.
8. Push code to your fork.
9. Run the CI pipeline (will run tests, code quality checks).
10. Create a pull request to the **`develop` branch**.

**Note: requests to merge directly to `master` will be automatically rejected**.

New releases are prepared periodically by merging a stable `develop` branch into `master`. When the merge happens documentation is built and a new package will be created and published in PyPI. **Individuals merging to `master` should heed to change the version tag in `meta.yaml`**.
