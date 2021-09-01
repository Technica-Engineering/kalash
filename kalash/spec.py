from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

import yaml

SpecPath = str
SpecKey = str


@dataclass
class BaseSpec:

    @classmethod
    def from_kwargs(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class CliConfigSpec(BaseSpec):
    whatif_paths: SpecKey
    whatif_ids: SpecKey
    group_device: SpecKey
    group_group: SpecKey
    log_formatter: SpecKey


@dataclass
class MetaSpec(BaseSpec):
    """
    Metadata section Spec.

    tts - test template start of metadata section
    tte - test template end of metadata section
    asc - not used now (will be needed for GUI app)
    dsc - not used now (will be needed for GUI app)
    related_usecase - related use case
    workbench - workbench list
    template_version - template version
    devices - device list
    suites - suite list
    functionality - functionality list
    """
    tts: SpecKey
    tte: SpecKey
    asc: SpecKey
    dsc: SpecKey
    related_usecase: SpecKey
    workbench: SpecKey
    template_version: SpecKey
    devices: SpecKey
    suites: SpecKey
    functionality: SpecKey


@dataclass
class TestSpec(BaseSpec):
    """
    A block is a single element in the YAML array
    that declares at least the `path` or `filter`
    fields.

    tests - tests top-level section key
    path - path to a folder of tests or a single test
    usecase - use cases to filter against
    no_recurse - disable recursive iteration over test directories
    last_result - filtering by last result
    devices - devices section (experimental device injection)
    parameters - parameters (experimental parameters injection)
    workbench - workbench that the filtered test is supposed to run on
    id - test ID key
    interp_cwd - point to the current working directory
    interp_this_file - points to the current YAML file path
    ok - value used for a test that passed last time
    nok - value used for a test that failed or errored out last time
    non_filters - list of properties that cannot be used like standard filters
    """
    tests: SpecKey
    path: SpecKey
    usecase: SpecKey
    no_recurse: SpecKey
    last_result: SpecKey
    devices: SpecKey
    workbench: SpecKey
    id: SpecKey
    setup_script: SpecKey
    teardown_script: SpecKey
    suites: SpecKey
    functionality: SpecKey
    interp_cwd: SpecKey
    interp_this_file: SpecKey
    ok: SpecKey
    nok: SpecKey

    def __post_init__(self):
        self.non_filters: List[SpecKey] = [
            self.path,
            self.no_recurse,
            self.setup_script,
            self.teardown_script,
            self.interp_cwd,
            self.interp_this_file
        ]


@dataclass
class ConfigSpec(BaseSpec):
    """
    Config section is free to have any other elements.
    **All elements here will not be attached as part 
    of the general configuration section to the TestCase class**.

    cfg - config section key
    report - location of the report folder
    one_time_setup_script - setup script key
    one_time_teardown_script - teardown script key
    """
    cfg: SpecKey
    report: SpecKey
    one_time_setup_script: SpecKey
    one_time_teardown_script: SpecKey
    run_only_with: SpecKey

    def __post_init__(self):
        self.non_attachable: List[SpecKey] = [
            self.report,
            self.one_time_setup_script,
            self.one_time_teardown_script
        ]


@dataclass
class Spec(BaseSpec):
    """
    This class defines naming patterns for
    the kalash YAML and metadata YAML
    specification.

    IMPORTANT NOTICE: all values in the Spec
    should be key:string pairs and converted
    to other types inplace when necessary.
    Please maintain type consistency accross
    this file.
    """

    cli_config: CliConfigSpec
    test: TestSpec
    config: ConfigSpec
    meta: MetaSpec

    @classmethod
    def load_spec(cls, spec_path: SpecPath) -> Spec:
        with open(spec_path, 'r') as f:
            yaml_obj = yaml.full_load(f)
        yaml_obj: Dict[str, Dict[str, SpecKey]] = yaml_obj
        return cls(
            CliConfigSpec.from_kwargs(
                **yaml_obj['cli_config']
            ),
            TestSpec.from_kwargs(
                **yaml_obj['test']
            ),
            ConfigSpec.from_kwargs(
                **yaml_obj['config']
            ),
            MetaSpec(
                **yaml_obj['meta']
            )
        )
