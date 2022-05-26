__docformat__ = "google"

from typing import Any, Dict, List, Optional, Union

import yaml
import ast
import re

from collections.abc import Iterable
from functools import reduce

from .model import CliConfig, OneOrList, TestModule, TestPath


def wrap_as_iterable(item: OneOrList[Any]):
    """
    Simple helper function that wraps scalars into
    a list.

    Args:
        item (OneOrList[Any]): an item that can be
            either a singular value (scalar) or an
            iterator

    Returns:
        `item` or `[item]` if item is a scalar
    """
    if item:  # make sure None is not included
        # selected values can be either scalars or arrays:
        if isinstance(item, Iterable) and not isinstance(item, str):
            return item
        else:
            # just wrap in a list if it's not iterable
            return [item]


def __trim_yaml(yaml_meta_section: str, cli_config: CliConfig):
    # since we allow additional comments in the original meta docstring
    # and users can write whatever they need in that section outside of the
    # meta block, we need to make sure we trim the YAML section properly
    tts = cli_config.spec.meta.tts
    tte = cli_config.spec.meta.tte
    idx_start = yaml_meta_section.find(tts) + len(tts)
    idx_end = yaml_meta_section.find(tte)
    trimmed_yaml = yaml_meta_section[idx_start: idx_end]
    return trimmed_yaml


def extract_meta_from_test_script_ast(
    test_script_path: str,
    cli_config: CliConfig
) -> str:
    """Extracts YAML metadata tag as string from
    a given test path.

    Args:
        test_script (str): script path
        cli_config (CliConfig): `CliConfig` instance

    Returns:
        Trimmed YAML section as string (parsable by `pyyaml`)
    """

    def _find_meta_in_ast(node: ast.stmt) -> Optional[str]:
        """Typesafe walk of the AST tree
        to make linters and lanugage servers
        happy.
        """
        if type(node) is ast.Expr:
            ast_const = node.value
            if type(ast_const) is ast.Constant \
                    or type(ast_const) is ast.Str:
                yaml_meta_section = ast_const.s
                return yaml_meta_section

    # parse the yaml data of the file
    with open(test_script_path) as f:
        read_file = f.read()
    parsed_file_ast = ast.parse(read_file)
    # the metadata is expected to be the first expression in the file
    yaml_meta_section = ''
    try:
        ast_0_element = parsed_file_ast.body[0]
        yaml_meta_section = _find_meta_in_ast(ast_0_element)
    except (AttributeError, IndexError):
        # "Falling back to searching the AST tree"
        for node in parsed_file_ast.body:
            yaml_meta_section = _find_meta_in_ast(node)
    if not yaml_meta_section:
        raise Exception(
            f"No YAML meta section in {test_script_path} "
            "has been found."
        )
    return __trim_yaml(yaml_meta_section, cli_config)


def extract_meta_from_test_module(test: TestModule, cli_config: CliConfig):
    """Extracts YAML metadata tag as string from
    a given `TestModule` instance.

    Args:
        test (TestModule): test module
        cli_config (CliConfig): `CliConfig` instance

    Returns:
        Trimmed YAML section as string (parsable by `pyyaml`)
    """
    if hasattr(test, '__doc__') and test.__doc__:
        yaml_meta_section = __trim_yaml(test.__doc__, cli_config)
        if yaml_meta_section:
            return yaml_meta_section
    return None


def parse_metadata_section(
    test_script: Union[TestPath, TestModule],
    cli_config: CliConfig
) -> Dict[str, Any]:
    """Extracts YAML metadata tag from
    a given test path or module and
    reworks it into a dictionary.

    Args:
        test_script (Union[TestPath, TestModule]): script path
            or test module
        cli_config (CliConfig): `CliConfig` instance

    Returns:
        A dictionary corresponding to the original YAML
            metadata tag.
    """
    if type(test_script) is TestPath:
        try:
            trimmed_yaml = extract_meta_from_test_script_ast(test_script, cli_config)
        except Exception:
            return dict()  # silently skip files that do not declare a metadata section
    elif type(test_script) is TestModule:
        trimmed_yaml = extract_meta_from_test_module(test_script, cli_config)
    else:
        raise TypeError(
            "Metadata should only be parsed from a test module (path or module object)"
        )
    # check if the file contains yaml data, if not, discard it
    if trimmed_yaml:
        try:
            yaml_data = yaml.full_load(trimmed_yaml)
            return yaml_data
        except Exception:
            return dict()
    return dict()


def match_id(test_id: Optional[str], patterns: Optional[Union[str, List[str]]]) -> bool:
    """
    Checks the explicit name IDs (or RegEx patterns) coming
    from the main YAML/Python configuration file
    against a given test ID.

    Args:
        test_id (str): a test ID
        patterns: single RegEx pattern or a list
            of patterns to match against

    Returns:
        `True` if any of the patterns matched the query ID
    """
    if not test_id:
        # if the ID is `None` ignore filtering
        # and return `True`
        return True
    source_of_truth = []
    patterns_iter = wrap_as_iterable(patterns)
    if not patterns_iter:
        # if there are no patterns, the filter should ignore
        # filtering by pattern and thus return True
        return True
    for pattern in patterns_iter:
        expected = pattern
        actual = test_id
        if re.match(expected, actual):
            source_of_truth.append(True)
        else:
            source_of_truth.append(False)
    # if any of the pattern matched the return value will be True
    return reduce(lambda x, y: x or y, source_of_truth)
