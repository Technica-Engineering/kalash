"""
META_START
---
id: 999999002_99-Blah_9-Whatever              # ID of the test
use_cases:                              # JIRA ticket names
  - FearFactory                               # Example JIRA ticket name
workbenches:                                  # Workbench where the test is meant to be run
  - Gojira                                    # Example workbench
devices:                                      # Dedicated devices list
  - cancombo                                  # Example device name
  - lincombo
META_END
"""

from kalash.run import MetaLoader, TestCase, main, parameterized


class TestSomething(TestCase):

    @parameterized.expand(['lincombo', 'cancombo'])
    def test_something(self, name):
        self.assertEqual(name, name)


if __name__ == '__main__':
    main(testLoader=MetaLoader())
