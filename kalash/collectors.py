"""
This module contains lowest-level test collection strategies
for a particular version of a test template.

Test collectors accept a `TestModule` instance, runtime and
static configuration objects (`CliConfig` and `Trigger`,
thus it follows a function signature defined in the `Collector`
type). A `TestModule` will be scanned for objects that will
be relevant to a test definition. For example V1 template
collection looks for `TestCase` instances.
"""
__docformat__ = "google"

from typing import Optional
import unittest
import os
import inspect

from .model import (CollectorArtifact, Meta,
                    PathOrIdForWhatIf, TestModule, Trigger)
from .smuggle import smuggle
from .metaparser import parse_metadata_section
from .test_case import TestCase


def _collect_test_case_from_module(
    test: TestModule,
    trigger: Optional[Trigger]
):
    identifiers: PathOrIdForWhatIf = []
    suite = unittest.TestSuite()
    _trigger: Trigger = trigger if trigger else Trigger()
    meta = Meta.from_yaml_obj(
        parse_metadata_section(test, _trigger.cli_config),
        _trigger.cli_config
    )
    for name, obj in test.__dict__.items():
        # sadly need to check against class first because Python...
        if inspect.isclass(obj):

            if issubclass(obj, TestCase):
                _id = meta.id if meta else None
                # add test functions to the suite
                for funcname, func in obj.__dict__.items():

                    if inspect.isfunction(func) \
                        and funcname.startswith('test') \
                            and _id is not None:

                        suite.addTest(obj(
                            funcname, _id, meta, trigger
                        ))
                        if _trigger.cli_config:
                            if _trigger.cli_config.what_if == \
                                    _trigger.cli_config.spec.cli_config.whatif_ids:
                                identifiers.append(_id)
                            elif _trigger.cli_config.what_if == \
                                    _trigger.cli_config.spec.cli_config.whatif_paths:
                                identifiers.append(os.path.abspath(test.__file__))  # type: ignore
                                # `__file__` always exists in this context
                            else:
                                identifiers.append(os.path.abspath(test.__file__))  # type: ignore
                                # `__file__` always exists in this context

                        if _trigger.cli_config and _trigger.cli_config.debug:
                            print(f"ADDED: {funcname} from {test.__file__}")
    # delete reference to clean up
    del test
    return suite, identifiers


# ====================
# V1 TEMPLATE HANDLING
# ====================
def _collect_test_case_v1_x(
    file: str,
    trigger: Trigger
) -> CollectorArtifact:
    # import the test from absolute or relative path
    # path should be relative to current working directory when calling kalash

    test = smuggle(os.path.abspath(file))
    # meta = defaultdict(lambda: None, parse_metadata_section(file))['values']
    # meta = defaultdict(lambda: None, meta) if meta else defaultdict(lambda: None)

    return _collect_test_case_from_module(test, trigger)

# =============================================================================


# ====================
# V2 TEMPLATE HANDLING
# ====================
def _collect_test_case_v2_0(
    file: str,
    trigger: Trigger
) -> CollectorArtifact:
    raise NotImplementedError("Test case V2 has not been implemented yet")

# =============================================================================
