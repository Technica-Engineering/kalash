from logging import warn
import unittest
import argparse
import xmlrunner
import os.path
import inspect

from unittest import TextTestRunner, TestLoader
from unittest import TestResult
from unittest.result import failfast
from unittest.main import TestProgram

from collections import defaultdict
from types import ModuleType
from functools import wraps
from parameterized import parameterized
from typing import Any, Callable, Dict, Iterator, Optional, Tuple

from .utils import get_ts
from .filter import apply_filters
from .smuggle import smuggle
from .config import Collector, CollectorArtifact, Config, KalashYamlObj, PathOrIdForWhatIf, SharedMetaElements, Spec, CliConfig, Trigger
from .test_case import TestCase
from .log import close_all
from .collectors import _collect_test_case_v1_x, _collect_test_case_v2_0, _collect_test_case_from_module

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
    ``YAML = find_my_yaml(__file__, "../yamls/yaml.yaml")``

    Args:
        filevar (:obj:``str``): should always be set to ``__file__``
        path (:obj:``str``): relative path component that points to the YAML
    
    Returns: normalized absolute path to the correct YAML file
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
    Importable run function. Higher-order suite definition function.
    As opposed to `Collector`, this function iterates over the
    YAML config and calls `Collector` on a per-test basis,
    using a callback system that also performs optional injection
    of parameters and configuration.

    Although `Collector` populates the suite directly,
    we use callbacks to dispatch the YAML blocks either directly
    towards the loader or to `apply_filters` function based on
    the form of the YAML. That's necessary to provide enough
    flexibility: the tester might want to take the whole repository
    and filter all tests or set per-directory filters. The call stack
    can be summarized as follows: `prepare_suite` -> (
        `apply_filters` OR `test_loader`
    ) -> (
        `fill_all_injection_closures` AND `Collector`
    )
    **This call stack should not be changed to ensure flexibility
    of the system is maintained**. Changes to `apply_filters`
    or `fill_params_and_add_to_suite` are welcome as long
    as all function signatures stay intact.

    Args:
        kalash_trigger (dict): dict returned from YAML parser
        no_recurse (bool): flag that switches on non-recursive directory search
        debug (bool): if True, prints the name of the functions and
            file paths from which they were picked up
        log (bool): if True, logging is enabled
        log_echo (bool): if True, log calls are echoed to STDOUT/STDERR

    Yields:
        unittest.TestSuite, List[str] of identifiers
    """

    for test_idx, test_conf in enumerate(kalash_trigger.tests):
        
        # set up path (if exists) and non-filter keys
        path = test_conf.path

        if not path:
            path = '.'  # default to CWD
        
        # recursive directory search can be set in a config or as a global flag when calling
        no_recurse_from_yaml: Optional[bool] = test_conf.no_recurse
        cli_config = kalash_trigger.cli_config
        if not no_recurse_from_yaml is None:
            cli_config.no_recurse = cli_config.no_recurse or no_recurse_from_yaml

        yield apply_filters(
            test_conf,
            path,
            COLLECTOR_FUNC_LOOKUP,
            kalash_trigger
        )


class MetaLoader(TestLoader):

    def __init__(
        self,
        yaml_path: str=None,
        trigger: Optional[Trigger]=None,
        local=True
    ):
        """
        Custom `TestLoader` for `kalash`. This provides consistency
        between running local and remote tests.

        Args:
            yaml_path (str): for backwards compatibility with Kalash YAML files,
                set instantly to the `config_file_path` value
            local (bool): if True, run only this test even when YAML
                is provided when in local context
            config (`CliConfig`): configuration object
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
                f"No `Trigger` on this `MetaLoader` instance"
            )
        else:
            return self._kalash_trigger

    def loadTestsFromKalashYaml(self) -> CollectorArtifact:
        whatif_names: PathOrIdForWhatIf = []
        for a in prepare_suite(
            self.trigger
        ):
            one_suite, one_whatif_names = a
            self.suite.addTests(one_suite)
            whatif_names.extend(one_whatif_names)
        return self.suite, list(set(whatif_names))

    def loadTestsFromModule(self, module, *args, pattern=None, **kws):

        def tests_generator(suite: unittest.TestSuite):
            """ 
            Recursive test generator from unittest.TestSuite
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
        self._smuggle_fixture_module(True)

    def one_time_teardown(self):
        self._smuggle_fixture_module(False)


main = TestProgram
"""
Exporting `unittest` components required in tests from `kalash`
results in testers not needing to touch unittest itself.
"""


def run_test_suite(
    loader: MetaLoader,
    kalash_trigger: Trigger,
    whatif_callback: Callable[[str], None] = print
):
    """Accepts a loader and Kalash YAML Object
    and triggers the test run.
    Returns:
        (unittest Result object, return code)
    """
    suite, whatif_names = loader.loadTestsFromKalashYaml()

    return_code = 0
    
    if not kalash_trigger.cli_config.what_if:
        loader.one_time_setup()
        report = "."
        if kalash_trigger.config:
            report = kalash_trigger.config.report
        result = xmlrunner.XMLTestRunner(
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
    config: Optional[CliConfig] = None,
    whatif_callback: Callable[[str], None] = print
):
    """User-friendly alias of the `run_test_suite` command
    for importable use in Python-based files.
    """
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    module_name = module.__name__ if module else None
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
):
    """Prepares a ``MetaLoader`` based
    on the YAML file parameters.
    Returns:
        (MetaLoader instance, Kalash YAML Object)
    """
    kalash_trigger = Trigger.infer_trigger(config)
    if config.file:
        config_file_path_relay = config.file
    else:
        signature = inspect.signature(Trigger.infer_trigger)
        config_file_path_relay = signature.parameters['default_path'].default

    loader = MetaLoader(
        local=False,
        trigger=kalash_trigger
    )

    return loader, kalash_trigger


def main_cli():
    """
    Main function. Expected to be run from CLI and used
    only in automated context.
    """
    config = CliConfig()

    parser = argparse.ArgumentParser(description='Test automation wrapper')
    parser.add_argument(
        '-f', '--file',
        type=str, help='Path to .kalash.yaml')
    parser.add_argument(
        '-n', '--no-recurse',
        action='store_true', help='Do not walk directories')
    parser.add_argument(
        '-d', '--debug',
        action='store_true', help='Run in debug mode')
    parser.add_argument(
        '-ff',  '--fail-fast',
        action='store_true', help='Fail suite if at least one test fails')
    parser.add_argument(
        '-nl', '--no-log',
        action='store_true', help='Disable logging')
    parser.add_argument(
        '-ne',  '--no-log-echo',
        action='store_true', help='If set, log calls will not be echoed to STDOUT')
    parser.add_argument(
        '-ld',  '--log-dir',
        type=str, help='Log base directory')
    parser.add_argument(
        '-ll',  '--log-level',
        type=int, help='Python `logging` log level ('
                       'CRITICAL = 50, '
                       'ERROR = 40, '
                       'WARNING = 30, '
                       'INFO = 20, '
                       'DEBUG = 10, '
                       'NOTSET = 0, default level is INFO)')
    parser.add_argument(
        '-sc', '--spec-config',
        type=str, help='Path to YAML specification YAML, default is `spec.yaml` '
                       'from the package directory.'
    )
    parser.add_argument(
        '-lf',  '--log-format',
        type=str, help=f'Log format string, default is %{config.spec.cli_config.log_formatter}')
    parser.add_argument(
        '-g', '--group-by',
        type=str, help='Log directories grouping: '
                       f'<{config.spec.cli_config.group_device}|'
                       f'{config.spec.cli_config.group_group}>')
    parser.add_argument(
        '-wi', '--what-if',
        type=str, help='Collects the tests but does not run them '
                       'and produces a list of paths or IDs that have been '
                       'collected for the run. Use '
                       f'<{config.spec.cli_config.whatif_paths}|'
                       f'{config.spec.cli_config.whatif_ids}> '
                       'to modify the output behavior of the what-if flag.'
    )
    args = parser.parse_args()

    if args.file:
        config.file = args.file

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

    loader, kalash_trigger= make_loader_and_trigger_object(
        config
    )

    _, return_code = run_test_suite(loader, kalash_trigger)

    close_all()

    return return_code
