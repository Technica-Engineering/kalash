import unittest

from kalash.model import CliConfig
from pathlib import Path


class TestStatePersistence(unittest.TestCase):

    def setUp(self) -> None:
        self.cfg = CliConfig()
        self.prev_path = self.cfg.spec.cli_config.internal_config_path
        self.new_path = str(Path(__file__).parent / "../test_yamls/internal-config.yaml")

    def test_internal_config_path_override(self):
        self.cfg.change_internal_config_path(self.new_path)
        self.assertTrue(self.prev_path != self.new_path)
        self.assertTrue(self.prev_path != self.cfg.resolved_internal_cfg_path)
        self.assertTrue("$(ThisFile)" not in (self.cfg.resolved_internal_cfg_path or ""))
        with open(self.cfg._spec_abspath, "r") as f:
            spec_contents = f.read()
        self.assertTrue(len(spec_contents) > 0)

    def tearDown(self) -> None:
        self.cfg.change_internal_config_path(self.prev_path)


if __name__ == "__main__":
    unittest.main()
