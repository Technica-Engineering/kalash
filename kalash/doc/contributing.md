# Contributing

## Prerequisites

All you need to develop for this project is to `pip install -e .[dev]` which will install all development dependencies for Kalash and Kalash itself in your virtual environment of choice. If you're unfamiliar what `pip install -e .` does, _now_ would be the time to read the documentation of the `pip` package manager.

Most build and test automation relies on `nox`. `nox` is a build and test automation driver for Python development that will automatically prepare your environment for testing.

## Contributing - process 🖋

Before submitting a pull request you must make sure that the CI pipeline passes all tests. The simplest way to contribute is thus:

1. Read the [Processes and conventions section](#processes-and-conventions).
2. Fork this repo.
3. Install Kalash in develop mode: `pip install -e '.[dev]'`.
4. Implement tests for your change (Test-Driven Development).
5. Implement your change.
6. If you have modified the user-facing data model (e.g. `Trigger`, `Test` or `Meta` classes), make sure to regenerate the JSON schema (`nox -e json_schema`).
7. Run tests locally using `nox -e test`.
8. Check whether your tests have satisfactory coverage: Run `coverage html` after triggering the tests and check `htmlcov/index.html`. Our minimum target coverage is 85%.
9. Run `flake8` at the root of this repository and correct any code-style deviations.
10. Document the change.
11. Update the `CHANGELOG`. Use the [correct](https://keepachangelog.com/en/1.0.0/) style guidelines for the changelog.
12. Push code to your fork.
13. Run the CI pipeline (will run tests, code quality checks).
14. Create a pull request to the **`master` branch**.

New releases are prepared periodically by checking out a stable `master` branch. When the release is published documentation is built and a new package will be created and published in PyPI. **Maintainers creating releases should heed to change the version tag in `setup.cfg`**.

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
3. There is one protected branch: `master`.
4. When creating a pull request you should **create a pull request for `master` branch**. Nobody is permitted to merge broken and untested code to `master`.

## Code quality 💯

Few things to heed:

* **If `flake8` tells you your code is crap, fix it before creating a pull request**. We want this project to have high code quality standards. The pipeline will check it for you, so if it doesn't pass you will have to correct yourself before proceeding. 😄
* **Use type hints**. Seriosusly. Code that takes little care of the types will be rejected right away. We know Python is dynamically typed but we don't like it. It seems like a pain in the neck in the beginning but spend a month with type hints and you'll never go back. It's much easier to catch nasty bugs when you use them.
* **Create tests**. Generally, small fixes *might* be accepted without tests, usually when we're dealing with something that's blatantly obvious. But you should always prefer to create tests for your changes and test locally before creating a pull request.
* **Use a good editor or an IDE**. You should aim for no red squiggly lines, be it in VSCode or PyCharm, doesn't matter. But be sure that if one of the maintainers pulls your change and sees red squiggly lines, you will need to correct your changes accordingly before anything can be merged. **We strongly recommend VSCode with Pylance Python Server**, always the latest stable version.
* If you're using **type aliases** consider adding them in `"config.py"` and documenting them in the `__doc__` attribute. `"config.py"` contains the base data model for Kalash, we want to keep it that way so that it's easy to reason about type dependencies. **Type aliases are recommended** because if whenever you decide you need a different type, you only need to change one line (unless the type is incompatible). 😀

## How the release is built 🔨

1. The changes in the `Unreleased` section of `CHANGELOG.md` are moved under a new version tag.
2. The CI pipeline for the latest `master` commit is proven to be green through-and-through.
3. The maintainer tags the release using unannotated `git tag` with the `v` prefix, e.g. `git tag v4.0.0`.
4. The tag is pushed to remote using `git push --tags`.
5. The maintainer creates a Release in the [Release view](https://github.com/Technica-Engineering/kalash/releases) on GitHub.
6. When the new release is posted the pipeline runs automatically with steps as defined in `.github/workflows/deploy-workflow.yaml`.
7. Final result: the Python Package Wheel is pushed to PyPI and is now installable with the `pip` package manager.
