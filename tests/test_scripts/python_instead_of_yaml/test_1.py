"""
META_START
---
id: 999999002_99-Blah_9-Whatever              # ID of the test
relatedUseCases:                              # JIRA codes of the related use cases
  - FearFactory                               # Example JIRA code
workbenches:                                  # Workbench where the test is meant to be runned
  - Gojira                                    # Example workbench
devices:
  - cancombo
  - lincombo
META_END
"""

from typing import List, Optional
from kalash.run import MetaLoader, TestCase, main, parameterized
from kalash.run import smuggle

import os


class TestAdvancedFiltering1(TestCase):

    @parameterized.expand(['lincombo', 'cancombo'])
    def test_1(self, name):
        self.allow_when('run_only_with', name)
        print(f"Running for {name}")


if __name__ == '__main__':
    main(testLoader=MetaLoader())
