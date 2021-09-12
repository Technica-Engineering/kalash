
"""
META_START
---
version: 2.0                                  # Version of the test template
id: 001111111_12_0_1234-NextGenTestCase       # ID of the test
use_cases:                              # JIRA codes of the related use cases
  - PRODTEST-2787                             # Example JIRA code
workbenches:                                  # Workbench where the test is meant to be run
  - BloodhoundGang                            # Example workbench
META_END
"""

from kalash.run import run_test_case, find_my_yaml

# TEST_CASE replaces test class name:
TEST_CASE = "NextGenTestCase"

# PARAMS replaces parameterized.expand:
PARAMS = [
    ('canCombo', 'CAN_COMBO_ADAPTER'),
    ('linCombo', 'LIN_COMBO_ADAPTER'),
]

# YAML replaces MetaLoader(yaml="some.yaml"),
# `find_my_yaml` resolves path to the YAML file relative to the
# test file
YAML = find_my_yaml(__file__, '../../test_yamls/test_v2.yaml')


# CIVAR functions are now top-level
def configuration(*params):
    f"CONF {params[0]}, {params[1]}"


def interaction(*params):
    f"INTER {params[0]}, {params[1]}"


def validation(*params):
    f"VALID {params[0]}, {params[1]}"


def restoration(*params):
    f"RESTORE {params[0]}, {params[1]}"


# Simplified main clause, YAML looked up automatically
if __name__ == "__main__":
    run_test_case(__file__)
