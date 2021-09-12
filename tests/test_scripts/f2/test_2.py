"""
META_START
---
id: 000000011_19-CM1000_45-LOOL_SomethingElse  # ID of the test
use_cases:                               # JIRA codes of the related use cases
  - PRODTEST-2787                              # Example JIRA code
workbenches:                                   # Workbench where the test is meant to be runned
  - BloodhoundGang                             # Example workbench
META_END
"""

from kalash.run import MetaLoader, TestCase, main
from kalash.testutils import testing_callback


class TestEd(TestCase):

    def test_1(self):
        testing_callback(__file__, "test_1")

    def test_2(self):
        testing_callback(__file__, "test_2")


if __name__ == '__main__':
    main(testLoader=MetaLoader(yaml_path='./.kalash.yaml'))
