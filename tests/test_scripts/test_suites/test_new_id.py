"""
META_START
---
id: PRODTEST_1234_twoja_stara                 # ID of the test
relatedUseCases:                              # JIRA codes of the related use cases
  - FearFactory                               # Example JIRA code
workbenches:                                  # Workbench where the test is meant to be runned
  - Gojira                                    # Example workbench
META_END
"""

from kalash.run import MetaLoader, TestCase, main


class TestLogger1(TestCase):

    def test_1(self):
        pass

    def test_2(self):
        pass


if __name__ == '__main__':
    main(testLoader=MetaLoader(yaml_path='./.kalash.yaml'))
