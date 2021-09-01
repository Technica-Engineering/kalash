from __future__ import annotations

from collections import defaultdict
from types import ModuleType
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union
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


@dataclass
class CliConfig:
    file:        Optional[str] = None
    # if not running in CLI context we initialize reasonable defaults:
    log_dir:     str           = '.'
    group_by:    Optional[str] = None
    no_recurse:  bool          = False
    debug:       bool          = False
    no_log:      bool          = False
    no_log_echo: bool          = False
    spec_path:   str           = os.path.join(os.path.dirname(__file__), 'spec.yaml')
    log_level:   int           = logging.INFO
    log_format:  str           = '%(message)s'
    what_if:     Optional[str] = None
    fail_fast:   bool          = False

    def __post_init__(self):
        self.spec = Spec.load_spec(self.spec_path)
        self.log_format = self.spec.cli_config.log_formatter



class classproperty(object):

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


@dataclass
class SharedMetaElements:

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
            ipt: (str): input string to interpolate
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
            ipt: (str): input string to interpolate
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
    report: str = './kalash_reports'
    setup: Optional[str] = None
    teardown: Optional[str] = None
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
