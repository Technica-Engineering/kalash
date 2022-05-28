__docformat__ = "google"

import unittest
import argparse
import xmlrunner
import os.path
import platform
import inspect
import webbrowser

from unittest import TextTestRunner, TestLoader
from unittest import TestResult
from unittest.result import failfast
from unittest.main import TestProgram

from types import ModuleType
from parameterized import parameterized
from typing import Callable, Dict, Iterator, Optional, Tuple

from .utils import get_ts
from .filter import apply_filters
from .smuggle import smuggle
from .model import (Collector, CollectorArtifact, Config,
                    PathOrIdForWhatIf, CliConfig, Trigger)
from .test_case import TestCase
from .log import close_all
from .collectors import (_collect_test_case_v1_x, _collect_test_case_v2_0,
                         _collect_test_case_from_module)

kalash = ModuleType('kalash')


__all__ = (
    'unittest', 'TextTestRunner', 'TestResult',
    'TestProgram', 'failfast', 'MetaLoader', 'main', 'TestCase',
    'get_ts', 'parameterized'
)

# ====================
# Public Utilities
# ====================


def find_my_yaml(filevar: str, path: str) -> str:
    """
    Figures out the path to the YAML file relative to a given
    test script, should be used like:

    ```python
    YAML = find_my_yaml(__file__, "../yamls/yaml.yaml")
    ```

    Args:
        filevar (str): should always be set to `__file__`, it's not
            hardcoded for improved readability (indicates you're
            looking for a YAML relative to the current test script)
        path (str): relative path component that points to the YAML

    Returns:
        Normalized absolute path to the correct YAML file
    """
    return os.path.normpath(
        os.path.abspath(
            os.path.join(os.path.dirname(filevar), path)
        )
    )


# =============================================================================
# ====================
# COLLECTOR LOOKUP
# ====================
# all 1.x versions will map to v1_x function
COLLECTOR_FUNC_LOOKUP: Dict[str, Collector] = \
    {f'1.{k}': _collect_test_case_v1_x for k in range(0, 10)}
# all further declarations will be mapped manually
COLLECTOR_FUNC_LOOKUP['2.0'] = _collect_test_case_v2_0

# =============================================================================


def prepare_suite(
    kalash_trigger: Trigger
) -> Iterator[CollectorArtifact]:
    """
    Higher-order suite definition function.
    As opposed to `Collector`, this function iterates over the
    YAML config and calls `Collector` on a per-test basis.

    This function calls `apply_filters`. If no filters are
    provided the `kalash_test_loader` will be called directly,
    otherwise the collected tests will be skimmed to match the
    provided filters.

    Args:
        kalash_trigger (Trigger): `Trigger` object collecting
            all configuration elements.

    Yields:
        One or more `CollectArtifact` elements.
    """

    for test_idx, test_conf in enumerate(kalash_trigger.tests):

        # set up path (if exists) and non-filter keys
        path = test_conf.path

        if not path:
            path = '.'  # default to CWD

        # recursive directory search can be set in a config or as a global flag when calling
        no_recurse_from_file: Optional[bool] = test_conf.no_recurse
        cli_config = kalash_trigger.cli_config
        if no_recurse_from_file is not None:
            cli_config.no_recurse = cli_config.no_recurse or no_recurse_from_file

        yield apply_filters(
            test_conf,
            path,
            COLLECTOR_FUNC_LOOKUP,
            kalash_trigger
        )


class MetaLoader(TestLoader):

    def __init__(
        self,
        yaml_path: Optional[str] = None,
        trigger: Optional[Trigger] = None,
        local=True
    ):
        """
        Custom `TestLoader` for Kalash. This provides consistency
        between running local and remote tests.

        Args:
            yaml_path (str): for backwards compatibility with Kalash YAML files,
                set instantly to the `config_file_path` value
            trigger (Optional[Trigger]): `Trigger` instance providing the
                entire configuration model or `None` if the test is run
                in a local context
            local (bool): if True, run only this test even when `Trigger`
                or `yaml_path` is provided when in local context
        """
        if yaml_path and not trigger:
            self._kalash_trigger = Trigger()
            self._kalash_trigger.cli_config.file = yaml_path
        elif yaml_path and trigger:
            self._kalash_trigger.cli_config.file = yaml_path
        elif not yaml_path and trigger:
            self._kalash_trigger = trigger
        else:
            self._kalash_trigger = Trigger()
        self._local = local
        self.suite = unittest.TestSuite()

    @property
    def trigger(self) -> Trigger:
        """Typesafe handler of `KalashYamlObj`.
        Throws an Exception if the YAML object
        hasn't been parsed correctly.
        """
        if not self._kalash_trigger:
            raise Exception(
                "No `Trigger` on this `MetaLoader` instance"
            )
        else:
            return self._kalash_trigger

    def loadTestsFromKalashYaml(self) -> CollectorArtifact:  # noqa: E501,N802 keeping in line with `unittest` camelCase naming
        """Loads tests from associated YAML or `Trigger`"""
        whatif_names: PathOrIdForWhatIf = []
        for a in prepare_suite(
            self.trigger
        ):
            one_suite, one_whatif_names = a
            self.suite.addTests(one_suite)
            whatif_names.extend(one_whatif_names)
        return self.suite, list(set(whatif_names))

    def loadTestsFromModule(self, module, *args, pattern=None, **kws):  # noqa: E501,N802 keeping in line with `unittest` camelCase naming

        def tests_generator(suite: unittest.TestSuite):
            """
            Recursive test generator for unittest.TestSuite
            (because a suite can contain other suites recursively).

            Args:
                suite (unittest.TestSuite): tests suite to pull tests from

            Yields:
                unittest test functions
            """
            for test in suite:
                if not type(test) is unittest.TestSuite:
                    yield test
                else:
                    for t in tests_generator(test):
                        yield t

        if self.trigger.cli_config.file:
            # parse YAML if provided
            self._kalash_trigger = Trigger.infer_trigger(
                self.trigger.cli_config
            )

        if self._local and self.trigger.cli_config.file:
            # if YAML exists and isolated mode is on, make sure values from YAML can be injected
            for test_idx, test_conf in enumerate(self.trigger.tests):
                # find whether any block declares path that pertains to this module config
                # or if the module is placed in any directory that should inherit config
                from pathlib import Path
                if test_conf.path:
                    if type(test_conf.path) is str:
                        path = Path(test_conf.path)
                    elif type(test_conf.path) is list:
                        path = Path(test_conf.path[0])
                    else:
                        path = Path(str(test_conf.path))
                else:
                    path = Path('.')
                files = [os.path.abspath(str(f)) for f in path.glob("**/*")]
                for file in files:
                    if os.path.normcase(os.path.abspath(module.__file__)) == os.path.normcase(file):
                        self.suite.addTests([
                            suite for suite, _ in prepare_suite(
                                self.trigger
                            )
                        ])
        elif self.trigger.cli_config.file and not self._local:
            # if not running in isolated mode and the YAML is provided, run all tests
            # that are declared in the YAML
            self.loadTestsFromKalashYaml()
        else:
            tests, _ = _collect_test_case_from_module(module, None)
            # if no YAML provided just add tests from the current module to the suite
            for test in tests_generator(tests):
                # suite is defined globally
                self.suite.addTest(test)
        return self.suite

    def _smuggle_fixture_module(self, is_setup: bool):
        cfg_section: Config = self.trigger.config
        if cfg_section:
            relpath_to_script = cfg_section.setup if is_setup else cfg_section.teardown
            if relpath_to_script:
                p = os.path.abspath(relpath_to_script)
                smuggle(p)

    def one_time_setup(self):
        """Runs One-time-setup script"""
        self._smuggle_fixture_module(True)

    def one_time_teardown(self):
        """Runs One-time-teardown script"""
        self._smuggle_fixture_module(False)


# -----------------------------------------------------------------

main = TestProgram

# Exporting `unittest` components required in tests from `kalash`
# results in testers not needing to touch unittest itself.
# -----------------------------------------------------------------


def run_test_suite(
    loader: MetaLoader,
    kalash_trigger: Trigger,
    whatif_callback: Callable[[str], None] = print
) -> Tuple[Optional[xmlrunner.runner._XMLTestResult], int]:
    """Accepts a loader and a `Trigger` object
    and triggers the test run.

    Args:
        loader (MetaLoader): `MetaLoader` instance extending
            `unittest.TestLoader` with extra goodies
        kalash_trigger (Trigger): `Trigger` instance which
            directly translates to a YAML configuration file
            or an equivalent Python file
        whatif_callback (Callable[[str], None]): the function
            to call when running in a what-if mode

    Returns:
        A tuple of (unittest Result object, return code) or
            a tuple of (`None`, return code) when running
            in the what-if mode
    """
    suite, whatif_names = loader.loadTestsFromKalashYaml()

    return_code = 0

    if not kalash_trigger.cli_config.what_if:
        loader.one_time_setup()
        report = "."
        if kalash_trigger.config:
            report = kalash_trigger.config.report
            if report is None:
                raise ValueError(
                    "Missing report directory configuration. Check if the YAML config you used "
                    "declares an output directory path for the test reports"
                )
        result: xmlrunner.runner._XMLTestResult = xmlrunner.XMLTestRunner(
            output=report,
            failfast=kalash_trigger.cli_config.fail_fast
        ).run(suite)
        loader.one_time_teardown()

        # PRODTEST-4708 -> Jenkins needs a non-zero return code
        #                  on test failure
        # return a valid return code depending on the result:
        if len(result.failures) > 0:
            return_code = 1
        elif len(result.errors) > 0:
            return_code = 2

        return result, return_code

    else:
        for n in whatif_names:
            whatif_callback(n)
        return None, return_code


def run(
    kalash_trigger: Trigger,
    whatif_callback: Callable[[str], None] = print
) -> int:
    """User-friendly alias of the `run_test_suite` command
    for importable use in Python-based files.

    Args:
        kalash_trigger (Trigger): `Trigger` instance which
            directly translates to a YAML configuration file
            or an equivalent Python file
        whatif_callback (Callable[[str], None]): the function
            to call when running in a what-if mode

    Returns:
        Return code, 0 if all collected tests are passing.
            A non-zero return code indicates failure.
    """
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    module_path = module.__file__ if module else None
    loader = MetaLoader(
        module_path,
        local=False,
        trigger=kalash_trigger
    )

    _, return_code = run_test_suite(loader, kalash_trigger, whatif_callback)

    close_all()

    return return_code


def make_loader_and_trigger_object(
    config: CliConfig
) -> Tuple[MetaLoader, Trigger]:
    """Prepares a ``MetaLoader`` based
    on the YAML file parameters.

    Args:
        cli_config (CliConfig): a `CliConfig` object representing
            command-line parameters used to trigger the test run
            modifying behavior of certain aspects of the application
            like logging or triggering speculative runs instead of
            real runs

    Returns:
        A tuple of (`MetaLoader` instance, `Trigger` instance)
    """
    kalash_trigger = Trigger.infer_trigger(config)

    loader = MetaLoader(
        local=False,
        trigger=kalash_trigger
    )

    return loader, kalash_trigger


def docs():
    """Open bundled documentation in the web browser."""
    base_dir = os.path.dirname(__file__)
    rel_docpath = ['built_docs', 'kalash.html']
    docpath = os.path.join(base_dir, *rel_docpath)
    _platform = platform.system()
    if _platform == "Darwin" or "Linux":
        url = f"file://{os.path.join(docpath)}"
    elif _platform == "Windows":
        url = f"file:\\\\\\{os.path.join(docpath)}"
    else:
        raise SystemError("Web browser handler for this platform is not supported")
    webbrowser.open(url, new=2)


def main_cli():
    """
    Main function. Expected to be run from CLI and used
    only in automated context.
    """
    config = CliConfig()

    parser = argparse.ArgumentParser(description='Test automation runner')
    subparsers = parser.add_subparsers()

    parser.add_argument(
        '-dd', '--docs',
        action='store_true', help='Display bundled documentation'
    )

    # `run` subcommand:
    parser_run = subparsers.add_parser('run', help='run an analysis')
    parser_run.add_argument(
        '-f', '--file',
        type=str, help='Path to .kalash.yaml')
    parser_run.add_argument(
        '-n', '--no-recurse',
        action='store_true', help='Do not walk directories')
    parser_run.add_argument(
        '-d', '--debug',
        action='store_true', help='Run in debug mode')
    parser_run.add_argument(
        '-ff', '--fail-fast',
        action='store_true', help='Fail suite if at least one test fails')
    parser_run.add_argument(
        '-nl', '--no-log',
        action='store_true', help='Disable logging')
    parser_run.add_argument(
        '-ne', '--no-log-echo',
        action='store_true', help='If set, log calls will not be echoed to STDOUT')
    parser_run.add_argument(
        '-ld', '--log-dir',
        type=str, help='Log base directory')
    parser_run.add_argument(
        '-ll', '--log-level',
        type=int, help='Python `logging` log level ('
                       'CRITICAL = 50, '
                       'ERROR = 40, '
                       'WARNING = 30, '
                       'INFO = 20, '
                       'DEBUG = 10, '
                       'NOTSET = 0, default level is INFO)')
    parser_run.add_argument(
        '-lf', '--log-format',
        type=str, help=f'Log format string, default is %{config.log_format}')
    parser_run.add_argument(
        '-g', '--group-by',
        type=str, help='Log directories grouping: '
                       f'<{config.spec.cli_config.group_device}|'
                       f'{config.spec.cli_config.group_group}>')
    # ---
    # This one doesn't belong in internal config:
    parser_run.add_argument(
        '-wi', '--what-if',
        type=str, help='Collects the tests but does not run them '
                       'and produces a list of paths or IDs that have been '
                       'collected for the run. Use '
                       f'<{config.spec.cli_config.whatif_paths}|'
                       f'{config.spec.cli_config.whatif_ids}> '
                       'to modify the output behavior of the what-if flag.'
    )

    # `configure` subcommand
    parser_configure = subparsers.add_parser(
        'configure', help='Perfoms stateful configuration of Kalash')
    parser_configure.add_argument(
        '-cfg', '--config-file',
        type=str, help='Path to the internal config file that you want to use instead of '
                       'the default `internal-config.yaml` from the package directory.'
    )
    parser_configure.add_argument(
        '-cfgd', '--config-file-display',
        action="store_true", help='Display the currently used internal configuration path. '
                                  'Tip: pipe into `cat` to display the contents of the file.'
    )

    args = parser.parse_args()

    if args.docs:
        docs()
        close_all()
        return 0

    if args.config_file:
        config.change_internal_config_path(args.config_file)
        close_all()
        return 0

    if args.config_file_display:
        print(config.resolved_internal_cfg_path)
        close_all()
        return 0

    if args.file:
        config.file = args.file

    # FIXME: `args.spec_config` is no more
    if args.spec_config:
        config.spec_path = args.spec_config
    config.__post_init__()

    if args.log_dir:
        config.log_dir = args.log_dir
    if args.group_by:
        config.group_by = args.group_by
    if args.log_level:
        config.log_level = args.log_level
    if args.log_format:
        config.log_format = args.log_format
    if args.what_if:
        config.what_if = args.what_if

    loader, kalash_trigger = make_loader_and_trigger_object(
        config
    )

    _, return_code = run_test_suite(loader, kalash_trigger)

    close_all()

    return return_code
