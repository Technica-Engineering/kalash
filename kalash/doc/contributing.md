# Contributing

## Prerequisites

All you need to develop for this project is to `pip install nox`.

`nox` is a build and test automation driver for Python development that will automatically prepare your environment for testing.

## Contributing - process

Before submitting a pull request you must make sure that the CI pipeline passes all tests. The simplest way to contribute is thus:

1. Fork this repo.
2. Install Kalash in develop mode: `pip install -e '.[dev]'`.
3. Implement tests for your change (Test-Driven Development).
4. Implement your change.
5. Run tests locally using `nox -e test`.
6. Check whether your tests have satisfactory coverage under `htmlcov/index.html`. Our minimum target coverage is 80%.
7. Document the change.
8. Update the `CHANGELOG`. Use the [correct](https://keepachangelog.com/en/1.0.0/) style guidelines for the changelog.
9. Push code to your fork.
10. Run the CI pipeline (will run tests, code quality checks).
11. Create a pull request to the **`develop` branch**.

**Note: requests to merge directly to `master` will be automatically rejected**.

New releases are prepared periodically by merging a stable `develop` branch into `master`. When the merge happens documentation is built and a new package will be created and published in PyPI. **Individuals merging to `master` should heed to change the version tag in `meta.yaml`**.

## Code quality

Few things to heed:

* **If `flake8` tells you your code is crap, fix it before creating a pull request**. We want this project to have high code quality standards.
* If you're using type aliases consider adding them in `"config.py"` and documenting them in the `__doc__` attribute. `"config.py"` contains the base data model for Kalash, we want to keep it that way so that it's easy to reason about type dependencies. **Type aliases are recommended** because if whenever you decide you need a different type, you only need to change one line (unless the type is incompatible) 😀
* **Use type hints**. Seriosusly. Code that takes little care of the types will be rejected right away. We know Python is dynamically typed but we don't like it. It seems like a pain in the neck in the beginning but spend a month with type hints and you'll never go back. It's much easier to catch nasty bugs when you use them.
* **Create tests**. Generally, small fixes *might* be accepted without tests, usually when we're dealing with something that's blatantly obvious. But you should always prefer to create tests for your changes and test locally before creating a pull request.
