from typing import List
from kalash.testutils import clear_results
from kalash.run import run_test_suite, make_loader_and_trigger_object
from kalash.model import CliConfig

import os
import time
import shutil
import glob

from unittest import main, TestCase


class TestKalash(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._debug = False

    def tearDown(self):
        clear_results()
        return super().tearDown()

    def test_one_time_setup_and_teardown(self):
        """
        Tests if the one-time setup and teardown fire exactly once.
        """
        _, _ = run_test_suite(*make_loader_and_trigger_object(CliConfig(
            "./tests/test_yamls/test_one_time_setup_and_teardown.yaml",
            "logs", "device",
            False, self._debug, True, fail_fast=True)))

        setup = int(os.environ.get('SETUP_RAN', 0))
        teardown = int(os.environ.get('TEARDOWN_RAN', 0))

        self.assertEqual(setup, 1)
        self.assertEqual(teardown, 1)

    def test_fail_fast_and_return_codes(self):

        # This test is equivalent to:
        # sys.argv += [
        #     "-f",
        #     "./tests/test_yamls/test_failfast_and_return_codes.yaml",
        #     "--failfast"
        # ]

        result, return_code = run_test_suite(*make_loader_and_trigger_object(CliConfig(
            "./tests/test_yamls/test_failfast_and_return_codes.yaml",
            "logs", "device",
            False, self._debug, True, fail_fast=True)))
        # there are 3 tests but 2nd fails so only 2 should run
        # (1 success, 1 failure)
        self.assertEqual(len(result.successes if result else []), 1)
        self.assertEqual(len(result.failures if result else []), 1)
        # return code 1 denotes test failure
        self.assertEqual(return_code, 1)

    def test_logging(self):
        result, return_code = run_test_suite(*make_loader_and_trigger_object(CliConfig(
            "./tests/test_yamls/test_logging.yaml",
            "logs", "devices",
            False, self._debug, False, False, fail_fast=True)))
        self.assertEqual(len(glob.glob('logs/**/**/*.log')), 2)

    def _whatif_helper(self, subdirs: List[str] = []):
        test_scripts_dir = os.path.join(
            os.path.dirname(__file__),
            'test_scripts'
        )
        if len(subdirs) > 0:
            test_scripts_dir = os.path.join(
                test_scripts_dir,
                *subdirs
            )
        paths_expected = []
        for root, dirs, files in os.walk(test_scripts_dir):
            for file in files:
                if file.startswith('test_') and file.endswith(".py"):
                    paths_expected.append(
                        os.path.normcase(os.path.join(root, file))
                    )
        return paths_expected

    def test_what_if_all_test_scripts(self):
        """Confirms whether the list of all test scripts
        is the same as the result of os.walk.
        """
        paths_expected = self._whatif_helper()
        paths_actual = []
        result, return_code = run_test_suite(*make_loader_and_trigger_object(CliConfig(
            "./tests/test_yamls/test_all.yaml",
            "logs", "device",
            False, self._debug, True, fail_fast=True, what_if='paths')),
            whatif_callback=lambda n: paths_actual.append(os.path.normcase(n)))
        self.assertListEqual(sorted(paths_actual), sorted(paths_expected))

    def test_what_if_some_scripts(self):
        """Selects a subset of tests and checks whether
        this corresponds to an expected set of values.
        """
        paths_expected = self._whatif_helper(['f1'])
        paths_expected.extend(self._whatif_helper(['setup_teardown']))
        paths_actual = []
        result, return_code = run_test_suite(*make_loader_and_trigger_object(CliConfig(
            "./tests/test_yamls/test_one_time_setup_and_teardown.yaml",
            "logs", "device",
            False, self._debug, True, fail_fast=True, what_if='paths')),
            whatif_callback=lambda n: paths_actual.append(os.path.normcase(n)))
        self.assertListEqual(sorted(paths_actual), sorted(paths_expected))

    def test_advanced_runtime_filtering(self):
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        time.sleep(0.1)
        shutil.rmtree("logs")
        time.sleep(0.1)


if __name__ == '__main__':
    main()
