import unittest

from kalash.config import CliConfig, Trigger
from kalash.collectors import _collect_test_case_v1_x


class TestLocalCollection(unittest.TestCase):

    def test_local_collection(self):
        suite, ids = _collect_test_case_v1_x(
            'tests/test_scripts/python_instead_of_yaml/test_1.py',
            Trigger(cli_config=CliConfig(None, no_log=True))
        )
        actual = [t._testMethodName for t in suite._tests]
        expected = [
            'test_1_0_lincombo',
            'test_1_1_cancombo',
        ]
        self.assertListEqual(sorted(actual), sorted(expected))


if __name__ == "__main__":
    unittest.main()
