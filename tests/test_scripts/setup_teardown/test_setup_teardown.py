"""
META_START
---
id: 000000678_12_0_1234-SomethingElse         # ID of the test
relatedUseCases:                              # JIRA codes of the related use cases
  - PRODTEST-2787                             # Example JIRA code
workbenches:                                  # Workbench where the test is meant to be runned
  - BloodhoundGang                            # Example workbench

META_END

Below the META_END tag you can write any additional comments you need
for your test case.
"""

# import kalash
from kalash.run import MetaLoader, TestCase, main
from kalash.testutils import testing_callback
import os
from pathlib import Path

yaml_path = Path(
    os.path.dirname(__file__)
) / ".." / ".." / "test_yamls" / "test_setup_and_teardown.yaml"


class SomeSomeTest(TestCase):

    def test_1(self):
        testing_callback(__file__, "test_1")

    def test_2(self):
        testing_callback(__file__, "test_2")


if __name__ == '__main__':
    main(testLoader=MetaLoader(yaml_path=str(yaml_path)))
