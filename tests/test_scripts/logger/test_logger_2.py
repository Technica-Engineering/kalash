"""
META_START
---
id: 999999002_99-Blah_9-Whatever              # ID of the test
use_cases:                              # JIRA codes of the related use cases
  - FearFactory                               # Example JIRA code
workbenches:                                  # Workbench where the test is meant to be runned
  - Gojira                                    # Example workbench
META_END
"""

from kalash.run import MetaLoader, TestCase, main
from kalash.testutils import testing_callback


class TestLogger2(TestCase):

    def test_1(self):
        self.logger.info("hellowchen")
        testing_callback(__file__, "test_1")

    def test_2(self):
        self.logger.info("hellowiener")
        testing_callback(__file__, "test_2")


if __name__ == '__main__':
    main(testLoader=MetaLoader(yaml_path='./.kalash.yaml'))
