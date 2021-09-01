"""
META_START
---
id: 999999001_99-Blah_9-Whatever              # ID of the test
relatedUseCases:                              # JIRA codes of the related use cases
  - FearFactory                               # Example JIRA code
workbenches:                                  # Workbench where the test is meant to be runned
  - Gojira                                    # Example workbench
META_END
"""

from kalash.run import MetaLoader, TestCase, main
from kalash.testutils import testing_callback


class TestLogger1(TestCase):

    def test_1(self):
        self.logger.info("hello1")
        testing_callback(__file__, "test_1")

    def test_2(self):
        self.logger.info("hello2")
        testing_callback(__file__, "test_2")


if __name__ == '__main__':
    main(testLoader=MetaLoader(yaml_path='./.kalash.yaml'))
