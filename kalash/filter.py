from typing import Dict, Union
from unittest import TestSuite
from functools import reduce

import warnings

from .metaparser import iterable_or_scalar, parse_metadata_section, match_id
from .last_result_filter import is_test_fail_or_error,\
    is_test_pass, filter_for_result
from .config import (
    ArbitraryYamlObj, Collector, CollectorArtifact,
    Meta, OneOrList, TemplateVersion, Test, TestPath, Trigger)
from .kalash_test_loader import make_test_loader


def dict_intersection(selected: ArbitraryYamlObj, parsed: ArbitraryYamlObj):
    """
    Checks whether a dict of values filtered against in YAML (selected)
    intersects with the parsed values:

    Args:
        selected (dict): dictionary of selected values
        parsed (dict): dictionary of parsed values

    Returns:
        `True` if any of the selected values coincides to be
        within the parsed values as well. `False` otherwise.
    """
    if selected and parsed:  # both shall be not-None
        for k, v in selected.items():
            if k in parsed.keys():
                for f1, f2 in zip(parsed[k], v):
                    if f1 == f2:
                        return True
        return False
    else:
        # by default we do not ignore those that don't specify
        # the selected and parsed lists
        return True


def apply_filters(
    test_collection_config: Test,
    tests_directory: OneOrList[TestPath],
    collector_functions: Dict[TemplateVersion, Collector],
    trigger: Trigger
) -> CollectorArtifact:
    """
    Main filtering function allowing testers to dynamically
    change the behavior of the test loader by modifying
    the contents of the YAML file.

    Args:
        test_collection_config (Test): a single `Test` collection
            config block
        tests_directory (OneOrList[TestPath]): path to a base
            directory to scour for tests
        collector_functions (Dict[TemplateVersion, Collector]):
            a map of `Collector` functions that are tied
            to particular versions of the test template
        trigger (Trigger): `Trigger` master instance

    Returns:
        A `CollectorArtifact`.
    """

    # TODO: generic way of filtering without the need to specify separate filter tags
    def _get_filterables(data_class: Union[Meta, Test]):
        selected = {}
        for k, v in data_class.__dict__.items():
            x1, x2 = getattr(OneOrList[str], '__args__')
            if (type(v) is x1 or type(v) is x2) \
                    and k not in Test._non_filters:
                selected[k] = (iterable_or_scalar(v))
        return selected

    def loader_callback(
        single_test_path: str,
        trigger: Trigger
    ) -> CollectorArtifact:
        """
        Test loader callback function for filtering.

        Args:
            single_test_path (str): path to a test under analysis
            trigger (Trigger): `Trigger` instance

        Returns:
            None
        """
        cli_config = trigger.cli_config
        try:
            parsed_meta = Meta.from_yaml(
                parse_metadata_section(single_test_path, cli_config),
                cli_config
            )
        except TypeError:
            if cli_config.debug:
                warnings.warn(
                    f"\nFile: {single_test_path}\n"
                    "does not contain any metadata tag, so "
                    "we ignore it!"
                )
            return TestSuite(), []  # silently skip files that do not declare a metadata section
            # we assume any file that doesn't have meta is NOT a test file

        # -----------------------------
        # Last result filter:
        # -----------------------------

        # last result is expected to be OK or NOK
        selected_last_result = test_collection_config.last_result
        if selected_last_result:
            if selected_last_result.lower() == cli_config.spec.test.ok.lower():
                parsed_last_result = filter_for_result(is_test_pass)(
                    single_test_path, trigger.config.report
                )  # the filtering function must be aware of the location of reports
            elif selected_last_result.lower() == cli_config.spec.test.nok.lower():
                parsed_last_result = filter_for_result(is_test_fail_or_error)(
                    single_test_path, trigger.config.report
                )
            else:
                raise ValueError(f"Last result should be {cli_config.spec.test.ok} or "
                                 f"{cli_config.spec.test.ok} or None!")
        else:
            parsed_last_result = []

        # -----------------------------
        # CALLBACK SWITCH:
        # -----------------------------
        version = parsed_meta.version
        if version:
            callback: Collector = collector_functions[version]
        else:
            callback: Collector = collector_functions["1.0"]
        if not callback:
            raise Exception(
                "Collector for version {version} of the template"
                "has not been found."
            )

        # -----------------------------
        # MAIN FILTER BOOLEAN REDUCER:
        # -----------------------------
        try:
            # create an array of booleans to reduce over, each represent a 'voice'
            # of a filter saying whether the test should run:
            run_this_test = [
                # TODO: generic way of filtering without the need to specify separate filter tags
                dict_intersection(
                    _get_filterables(parsed_meta),
                    _get_filterables(test_collection_config)
                ),
                match_id(parsed_meta.id, iterable_or_scalar(test_collection_config.id))
            ] + parsed_last_result

            # if all filters applied evaluate to true for a given test, run callback:
            if reduce(lambda x, y: x and y, run_this_test):
                return callback(single_test_path, trigger)
            else:
                return TestSuite(), []
        except KeyError:
            print(f"{single_test_path} failed. Make sure the metadata section is valid")
        return TestSuite(), []

    test_loader = make_test_loader(trigger)

    return test_loader(
        tests_directory,
        loader_callback
    )
