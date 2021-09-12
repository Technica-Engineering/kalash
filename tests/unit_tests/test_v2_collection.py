import unittest

from kalash.config import CliConfig, Trigger
from kalash.run import _collect_test_case_v2_0
import os
from pathlib import Path


class TestV2Collection(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_path = str(
            Path(
                os.path.dirname(__file__)
            ) / '..' / 'test_scripts' / 'test_template_v2' / 'test_template_v2.py'
        )
        cls.yaml_path = str(
            Path(
                os.path.dirname(__file__)
            ) / '..' / 'test_yamls' / 'test_v2.yaml'
        )

    def test_v2_template_collection(self):
        self.assertRaises(Exception, lambda: _collect_test_case_v2_0(
            self.test_path,
            Trigger.from_file(
                self.yaml_path,
                CliConfig(
                    self.yaml_path,
                    no_log=True,
                    no_log_echo=True
                )
            )
        ))


if __name__ == "__main__":
    unittest.main()
