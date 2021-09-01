"""
META_START
---
id: 000000001_30-CMEth_9-FLASH_SomethingElse  # ID of the test
relatedUseCases:                              # JIRA codes of the related use cases
  - PRODTEST-9998                             # Example JIRA code
workbenches:                                  # Workbench where the test is meant to be runned
  - Rammstein                                 # Example workbench
META_END
"""

from kalash.run import MetaLoader, TestCase, main
from kalash.testutils import testing_callback


class TestSomethingElse(TestCase):

    def test_1(self):
        pass

    def test_2(self):
        self.fail("Xfail")
    
    def test_3(self):
        pass


if __name__ == '__main__':
    main(testLoader=MetaLoader(yaml_path='./.kalash.yaml'))
