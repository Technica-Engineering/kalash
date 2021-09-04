import unittest
import shutil
import os
import glob
import time

from kalash.config import CliConfig
from kalash.log import (_make_tree, _make_log_tree_from_id,
                        register_logger, _LOGGERS, get, close, close_all)


class TestLogging(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.testid = "000000001_Blah"
        cls.log_path_pattern = \
            r'000000001_Blah_TestLog[\\\/]\d+_000000001_Blah_TestLog'
        cls.expected_log_path = 'logs/000000001_Blah_TestLog'

    def test_grouping_path(self):
        """Tests directory tree restructure based
        on device category.
        """
        path = _make_log_tree_from_id(
            self.testid,
            "TestLog"
        )
        self.assertRegex(path, self.log_path_pattern)

    def test_directory_tree(self):
        """Req:
        LogDir
        |-> TestSuite X
            |-> CM-100-High
            |   |-> test_script_1_param_set_1
            |   |-> test_script_1_param_set_2
            |-> CM-Eth
                |-> test_some_other_script_1_param_set_1
                |-> test_some_other_script_1_param_set_2
        """
        _make_tree(self.testid, "TestLog", "logs")
        if not os.path.exists(self.expected_log_path):
            self.fail('Target path for logs not created properly!')

    def test_register_logger(self):
        register_logger(__name__, 'log.log', CliConfig(None))
        self.assertEqual(len(_LOGGERS), 1)
        close_all()

    def test_logger_user_facing_functions(self):
        logger = get(
            self.testid,
            "TestLog",
            CliConfig(
                None,
                log_dir='logs2',
                no_log_echo=True
            )
        )
        logger.info('hello')
        close(logger)
        time.sleep(0.5)
        self.assertGreater(len(glob.glob('logs2/**/*.log')), 0)

    @unittest.skip("Awaiting reimplementation of grouping")
    def test_logfile_grouping(self):
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        # need to sleep a while because it seems Windows doens't
        # want to release the file handle quickly enough
        time.sleep(0.5)
        shutil.rmtree('logs', ignore_errors=True)
        os.unlink('log.log')
        shutil.rmtree('logs2', ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
