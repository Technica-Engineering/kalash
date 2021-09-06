# Contributing

## Prerequisites

All you need to develop for this project is to `pip install nox`.

`nox` is a build and test automation driver for Python development that will automatically prepare your environment for testing.

## Contributing - process 🖋

Before submitting a pull request you must make sure that the CI pipeline passes all tests. The simplest way to contribute is thus:

1. Read the [Processes and conventions section](#processes-and-conventions).
2. Fork this repo.
3. Install Kalash in develop mode: `pip install -e '.[dev]'`.
4. Implement tests for your change (Test-Driven Development).
5. Implement your change.
6. Run tests locally using `nox -e test`.
7. Check whether your tests have satisfactory coverage under `htmlcov/index.html`. Our minimum target coverage is 80%.
8. Run `flake8` at the root of this repository and correct any code-style deviations.
9. Document the change.
10. Update the `CHANGELOG`. Use the [correct](https://keepachangelog.com/en/1.0.0/) style guidelines for the changelog.
11. Push code to your fork.
12. Run the CI pipeline (will run tests, code quality checks).
13. Create a pull request to the **`develop` branch**.

**Note: requests to merge directly to `master` will be automatically rejected**.

New releases are prepared periodically by merging a stable `develop` branch into `master`. When the merge happens documentation is built and a new package will be created and published in PyPI. **Maintainers merging to `master` should heed to change the version tag in `setup.cfg`**.

## Processes and Conventions 👮‍♀️

[Processes and Conventions]: #processes-and-conventions

We use a slightly modified GitFlow practice in our development:

1. Each change/issue should have its own branch named after the issue ID, for instance:
    * `chore/2-git-hooks-setup`
    * `fix/123-some-bug`
    * `feature/456-some-feature`
    The part we really care about is whatever you place before the slash and should contain one of the well known Git keywords:
        * `chore`
        * `fix`
        * `feature`
        * `doc`
        * `refactor`
        * etc.
2. Each commit should start with the aforementioned keywords, e.g. `chore: updating version tag`.
3. There are 2 protected branches: `develop` and `master`.
4. When creating a pull request you should **create a pull request for `develop` branch**. In our workflow `master` contains only stable code most of the times equivalent to the latest release.

## Code quality 💯

Few things to heed:

* **If `flake8` tells you your code is crap, fix it before creating a pull request**. We want this project to have high code quality standards. The pipeline will check it for you, so if it doesn't pass you will have to correct yourself before proceeding. 😄
* **Use type hints**. Seriosusly. Code that takes little care of the types will be rejected right away. We know Python is dynamically typed but we don't like it. It seems like a pain in the neck in the beginning but spend a month with type hints and you'll never go back. It's much easier to catch nasty bugs when you use them.
* **Create tests**. Generally, small fixes *might* be accepted without tests, usually when we're dealing with something that's blatantly obvious. But you should always prefer to create tests for your changes and test locally before creating a pull request.
* **Use a good editor or an IDE**. You should aim for no red squiggly lines, be it in VSCode or PyCharm, doesn't matter. But be sure that if one of the maintainers pulls your change and sees red squiggly lines, you will need to correct your changes accordingly before anything can be merged.
* If you're using **type aliases** consider adding them in `"config.py"` and documenting them in the `__doc__` attribute. `"config.py"` contains the base data model for Kalash, we want to keep it that way so that it's easy to reason about type dependencies. **Type aliases are recommended** because if whenever you decide you need a different type, you only need to change one line (unless the type is incompatible). 😀
