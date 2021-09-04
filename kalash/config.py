from __future__ import annotations

__doc__ = """"""

from collections import defaultdict
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union
from dataclasses import dataclass, field
from toolz import pipe

import unittest
import logging
import os
import yaml
import inspect

from .smuggle import smuggle
from .spec import Spec

T = TypeVar('T')
TestPath = str
AuxiliaryPath = str
UseCase = str
LastResult = str
TestId = str
Workbench = str
Device = str
Suite = str
FunctionalityItem = str
Toggle = bool
KalashYamlObj = Dict[str, Any]
ArbitraryYamlObj = Dict[str, Any]
ConstructorArgsTuple = Tuple[Any, ...]
TestModule = ModuleType
TemplateVersion = str
OneOrList = Union[List[T], T]

# Please document type aliases below:

__doc__ += """
Module containing the entire configuration data model for Kalash

Type Aliases:

* `TestPath` = `str`
* `AuxiliaryPath` = `str`
* `UseCase` = `str`
* `LastResult` = `str`
* `TestId` = `str`
* `Workbench` = `str`
* `Device` = `str`
* `Suite` = `str`
* `FunctionalityItem` = `str`
* `Toggle` = `bool`
* `KalashYamlObj` = `Dict[str, Any]`
* `ArbitraryYamlObj` = `Dict[str, Any]`
* `ConstructorArgsTuple` = `Tuple[Any, ...]`
* `TestModule` = `ModuleType`
* `TemplateVersion` = `str`
* `OneOrList` = `Union[List[T], T]`
"""


@dataclass
class CliConfig:
    """A class collecting all CLI options fed into
    the application. The instance is created by the
    main function and used downstream in the call stack.

    Args:
        file (Optional[str]): config filename (YAML or Python file)
        log_dir (str): base directory for log files
        group_by (Optional[str]): group logs by a particular property
            from the metadata tag
        no_recurse (bool): don't recurse into subfolders when scanning
            for tests to run
        debug (bool): run in debug mode
        no_log (bool): suppress logging
        no_log_echo (bool): suppress log echoing to STDOUT
        spec_path (str): custom YAML/Meta specification path, the file
            should be in YAML format
        log_level (int): `logging` module log level
        log_format (str): formatter string for `logging` module logger
        what_if (Optional[str]): either 'ids' or 'paths', prints hypothetical
            list of IDs or paths of collected tests instead of running the
            actual tests, useful for debugging and designing test suites
        fail_fast (bool): if `True` the test suite won't be continued if
            at least one of the tests that have been collected and triggered
            has failed
    """
    file:        Optional[str] = None
    # if not running in CLI context we initialize reasonable defaults:
    log_dir:     str           = '.'
    group_by:    Optional[str] = None
    no_recurse:  bool          = False
    debug:       bool          = False
    no_log:      bool          = False
    no_log_echo: bool          = False
    spec_path:   str           = 'spec.yaml'
    log_level:   int           = logging.INFO
    log_format:  str           = '%(message)s'
    what_if:     Optional[str] = None
    fail_fast:   bool          = False

    def __post_init__(self):
        spec_abspath = os.path.join(os.path.dirname(__file__), self.spec_path)
        self.spec = Spec.load_spec(spec_abspath)
        self.log_format = self.spec.cli_config.log_formatter


class classproperty(object):
    """https://stackoverflow.com/a/13624858
    Only Python 3.9 allows stacking `@classmethod`
    and `@property` decorators to obtain static
    properties. We use this decorator as a workaround
    since we wish to support 3.7+ for quite a while.
    """
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


@dataclass
class SharedMetaElements:
    """Collects Metadata-modifying methods with `CliConfig` instance
    providing a parameter closure. Most methods here are related
    to built-in interpolation of patterns like `$(WorkDir)`.
    """

    cli_config: CliConfig

    def _interpolate_workdir(self, ipt: str) -> str:
        """Interpolates CWD variable. This variable is used to
        resolve paths within Kalash YAML relative to the current
        working directory. Equivalent to using the dotted file path.

        Args:
            ipt (str): input string to interpolate
            yaml_abspath (str): path to the Kalash YAML file.

        Returns: interpolated string
        """
        return os.path.normpath(
            ipt.replace(
                self.cli_config.spec.test.interp_cwd, os.getcwd()
            )
        )

    def _interpolate_this_file(self, ipt: str, yaml_abspath: str) -> str:
        """Interpolates THIS_FILE variable. THIS_FILE is used to resolve
        paths within Kalash YAML relative to the YAML file itself.

        Args:
            ipt (str): input string to interpolate
            yaml_abspath (str): path to the Kalash YAML file
                or the `.py` configuration file

        Returns: interpolated string
        """
        return os.path.normpath(
            ipt.replace(
                self.cli_config.spec.test.interp_this_file,
                os.path.dirname(yaml_abspath)
            )
        )

    def _interpolate_all(self, ipt: Union[str, None], yaml_abspath: str) -> Union[str, None]:
        """Interpolates all variable values using a toolz.pipe

        Args:
            ipt (str): input string to interpolate
            yaml_abspath (str): path to the Kalash YAML file
                or the `.py` configuration file

        Returns: interpolated string
        """
        if ipt:
            return pipe(
                self._interpolate_this_file(ipt, yaml_abspath),
                self._interpolate_workdir
            )
        return ipt

    def resolve_interpolables(self, o: object, yaml_abspath: str):
        for k, v in o.__dict__.items():
            if type(v) is str:
                setattr(o, k, self._interpolate_all(v, yaml_abspath))


@dataclass
class Base:
    """Base config class. `Meta`, `Config` and `Test`
    inherit from this minimal pseudo-abstract base class.
    """
    @classmethod
    def from_yaml(cls, yaml_obj: ArbitraryYamlObj, cli_config: CliConfig) -> Base:
        raise NotImplementedError("Base class methods should be overridden")

    def get(self, argname: str):
        """`getattr` alias for those who wish to use this
        from within the `TestCase` class.
        """
        return getattr(self, argname, None)


@dataclass
class Meta(Base):
    """Provides a specification outline for the Metadata tag
    in test templates.

    Args:
        id (Optional[TestId]): unique test ID
        version (Optional[TemplateVersion]): template version
        use_cases (Optional[OneOrList[UseCase]]): one or more
            use case IDs (preferably from a task tracking system
            like Jira) that a particular test refers to
        workbenches (Optional[OneOrList[Workbench]]): one or more
            physical workbenches where the test should be triggered
        devices (Optional[OneOrList[Device]]): one or more device
            categories for which this test has been implemented
        suites (Optional[OneOrList[Suite]]): one or more arbitrary
            suite tags (should be used only if remaining tags don't
            provide enough possibilities to describe the context of
            the test script)
        functionality (Optional[OneOrList[FunctionalityItem]]): one
            or more functionality descriptors for the test script
    """
    id:            Optional[TestId] = None
    version:       Optional[TemplateVersion] = None
    use_cases:     Optional[OneOrList[UseCase]] = None
    workbenches:   Optional[OneOrList[Workbench]] = None
    devices:       Optional[OneOrList[Device]] = None
    suites:        Optional[OneOrList[Suite]] = None
    functionality: Optional[OneOrList[FunctionalityItem]] = None
    cli_config:    CliConfig = CliConfig()

    def __post_init__(self):
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        if module:
            module_path = os.path.abspath(module.__file__)
            SharedMetaElements(self.cli_config).resolve_interpolables(self, module_path)

    @classmethod
    def from_yaml(cls, yaml_obj: ArbitraryYamlObj, cli_config: CliConfig) -> Meta:
        block_spec = cli_config.spec.test
        meta_spec = cli_config.spec.meta
        params = dict(
            id=yaml_obj.get(block_spec.id, None),
            version=yaml_obj.get(meta_spec.template_version, None),
            use_cases=yaml_obj.get(meta_spec.related_usecase, None),
            workbenches=yaml_obj.get(meta_spec.workbench, None),
            devices=yaml_obj.get(block_spec.devices, None),
            suites=yaml_obj.get(block_spec.suites, None),
            functionality=yaml_obj.get(block_spec.functionality, None)
        )
        return Meta(
            **params
        )


@dataclass
class Test(Meta):
    """Provides a specification outline for a single category
    of tests that should be collected, e.g. by path, ID or any
    other parameter inherited from `Meta`.

    Args:
        path (Optional[OneOrList[TestPath]]): path to a test
            directory or a single test path
        id (Optional[OneOrList[TestId]]): one or more IDs to
            filter for
        no_recurse (Optional[Toggle]): if `True`, subfolders
            will not be searched for tests, intended for use with
            the `path` parameter
        last_result (Optional[LastResult]): if `OK` then filters
            out only the tests that have passed in the last run,
            if `NOK` then it only filters out those tests that
            have failed in the last run
        setup (Optional[AuxiliaryPath]): path to a setup script;
            runs once at the start of the test category run
        teardown (Optional[AuxiliaryPath]): path to a teardown
            script; runs once at the end of the test category
            run
    """
    path:          Optional[OneOrList[TestPath]] = None
    id:            Optional[OneOrList[TestId]] = None
    no_recurse:    Optional[Toggle] = None
    last_result:   Optional[LastResult] = None
    setup:         Optional[AuxiliaryPath] = None
    teardown:      Optional[AuxiliaryPath] = None
    cli_config:    CliConfig = CliConfig()

    def __post_init__(self):
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        if module:
            module_path = os.path.abspath(module.__file__)
            SharedMetaElements(self.cli_config).resolve_interpolables(self, module_path)

    @classmethod
    def from_yaml(cls, yaml_obj: ArbitraryYamlObj, cli_config: CliConfig) -> Test:
        """Loads `Test` blocks from a YAML object."""

        block_spec = cli_config.spec.test
        base_class_instance = super().from_yaml(yaml_obj, cli_config)
        return Test(
            path=yaml_obj.get(block_spec.path, None),
            no_recurse=yaml_obj.get(block_spec.no_recurse, None),
            last_result=yaml_obj.get(block_spec.last_result, None),
            setup=yaml_obj.get(block_spec.setup_script, None),
            teardown=yaml_obj.get(block_spec.teardown_script, None),
            **base_class_instance.__dict__
        )

    @classproperty
    def _non_filters(cls):
        # ID is listed as non-filter beacuse it's handled
        # differently. A `Test` definition can filter for
        # multiple IDs. A `Meta` definition can only have
        # one ID (1 ID == 1 test case). Hence ID is handled
        # separately in the `apply_filters` function using
        # `match_id` helper
        return ['setup', 'teardown', 'path', 'id']


@dataclass
class Config(Base):
    """Provides a specification outline for the runtime
    parameters. Where `Test` defines what tests to collect,
    this class defines global parameters determining how
    to run tests.

    Args:
        report (str): directory path where reports will
            be stored in XML format
        setup (Optional[AuxiliaryPath]): path to a setup script;
            runs once at the start of the complete run
        teardown (Optional[AuxiliaryPath]): path to a teardown
            script; runs once at the end of the complete run
    """
    report: str = './kalash_reports'
    setup: Optional[AuxiliaryPath] = None
    teardown: Optional[AuxiliaryPath] = None
    cli_config: CliConfig = CliConfig()

    def __post_init__(self):
        SharedMetaElements(self.cli_config).resolve_interpolables(self, __file__)

    @classmethod
    def from_yaml(cls, yaml_obj: Optional[ArbitraryYamlObj], cli_config: CliConfig) -> Config:
        """Loads `Test` blocks from a YAML object."""
        config_spec = cli_config.spec.config
        if yaml_obj:
            return Config(
                yaml_obj.get(config_spec.report, None),
                yaml_obj.get(config_spec.one_time_setup_script, None),
                yaml_obj.get(config_spec.one_time_teardown_script, None)
            )
        else:
            return Config()


@dataclass
class Trigger:
    """Main configuration class collecting all information for
    a test run, passed down throughout the whole call stack.

    Args:
        tests (List[Test]): list of `Test` categories, each
            describing a sliver of a test suite that shares certain
            test collection parameters
        config (Config): a `Config` object defining parameters
            telling Kalash *how* to run the tests
        cli_config (CliConfig): a `CliConfig` object representing
            command-line parameters used to trigger the test run
            modifying behavior of certain aspects of the application
            like logging or triggering speculative runs instead of
            real runs
    """
    tests:  List[Test] = field(default_factory=list)
    config: Config     = field(default_factory=lambda: Config())
    cli_config: CliConfig = field(default_factory=lambda: CliConfig())

    @classmethod
    def from_yaml(cls, yaml_path: str, cli_config: CliConfig):
        with open(yaml_path, 'r') as f:
            yaml_obj: ArbitraryYamlObj = defaultdict(lambda: None, yaml.safe_load(f))
        list_blocks: List[ArbitraryYamlObj] = \
            yaml_obj[cli_config.spec.test.tests]
        cfg_section: ArbitraryYamlObj = yaml_obj[cli_config.spec.config.cfg]
        tests = [Test.from_yaml(i, cli_config) for i in list_blocks]
        config = Config.from_yaml(cfg_section, cli_config)
        return Trigger(tests, config, cli_config)

    def _resolve_interpolables(self, path: str):
        sm = SharedMetaElements(self.cli_config)
        for test in self.tests:
            sm.resolve_interpolables(test, path)
        sm.resolve_interpolables(self.config, path)

    @classmethod
    def infer_trigger(cls, cli_config: CliConfig, default_path: str = '.kalash.yaml'):
        """Creates the Trigger instance from a YAML file or
        a Python file.

        Args:
            path (str): path to the configuration file.

        Returns: `Tests` object
        """
        path = cli_config.file if cli_config.file else default_path
        if path.endswith('.yaml'):
            t = cls()
            t = Trigger.from_yaml(os.path.abspath(path), cli_config)
            t._resolve_interpolables(path)
            return t
        else:
            module = smuggle(os.path.abspath(path))
            for _, v in module.__dict__.items():
                if type(v) is cls:
                    v._resolve_interpolables(path)
                    return v
            else:
                raise ValueError(
                    f"No {cls.__name__} instance found in file {path}"
                )


PathOrIdForWhatIf = List[str]
CollectorArtifact = Tuple[unittest.TestSuite, PathOrIdForWhatIf]  # can be a list of IDs or paths
                                                                  # or a full test suite
Collector = Callable[[TestPath, Trigger], CollectorArtifact]

__doc__ += """
* `PathOrIdForWhatIf` = `List[str]`
* `CollectorArtifact` = `Tuple[unittest.TestSuite, PathOrIdForWhatIf]`
* `Collector` = `Callable[[TestPath, Trigger], CollectorArtifact]`
"""
