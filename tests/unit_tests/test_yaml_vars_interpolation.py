import os
import unittest
from pathlib import Path

from kalash.run import prepare_suite
from kalash.config import CliConfig, Test, Trigger, SharedMetaElements, Spec


class TestYamlVarsInterpolation(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        cls.yaml_path = str(Path(os.path.dirname(__file__)) / '..' / 'test_yamls' / 'test_interpolation.yaml')
        cls.trigger = lambda cls: Trigger.from_yaml(cls.yaml_path, CliConfig(
            cls.yaml_path,
            no_log=True,
            no_log_echo=True
        ))
        cls.cwd = cls.trigger(cls).cli_config.spec.test.interp_cwd
        cls.this_file = cls.trigger(cls).cli_config.spec.test.interp_this_file

    def test_interpolate_workdir(self):
        """
        Changes dir to tests and then
        tries interpolating CWD variable. Will fail
        if the expected fake path doesn't match the actual.
        **Tests correctness**
        """
        ipt = os.path.normpath(f"{self.cwd}/blah/blah.py")
        old_cwd = os.getcwd()
        os.chdir("tests")  # change workdir, otherwise we're same as root
        expected = str(Path(os.getcwd()) / 'blah' / 'blah.py')
        actual = SharedMetaElements(
            self.trigger().cli_config
        )._interpolate_workdir(ipt)
        os.chdir(old_cwd)
        self.assertEqual(expected, actual)

    def test_interpolate_this_file(self):
        """
        Changes dir to tests/test_yamls and then
        tries interpolating THIS_FILE variable. Will fail
        if the expected fake path doesn't match the actual.
        **Tests correctness**
        """
        ipt = os.path.normpath(f"{self.this_file}/blah/blah.py")
        old_cwd = os.getcwd()
        os.chdir("tests/test_yamls")  # change workdir, otherwise we're same as root
        expected = os.path.normcase(Path(os.getcwd()) / 'blah' / 'blah.py')
        actual = os.path.normcase(SharedMetaElements(
            self.trigger().cli_config
        )._interpolate_this_file(ipt, self.yaml_path))
        os.chdir(old_cwd)
        self.assertEqual(expected, actual)

    def test_yaml_vars_interpolation(self):
        """
        Checks if all expected variables have been successfully
        interpolated.
        **Tests completeness**
        """
        not_contains_cwd = lambda s: not (self.cwd in s)
        not_contains_this_file = lambda s: not (self.this_file in s)
        not_contains = lambda s: not_contains_cwd(s) and not_contains_this_file(s)
        trigger = self.trigger()

        trigger._resolve_interpolables(self.yaml_path)
        lines_to_verify = [
            trigger.tests[0].path,
            trigger.tests[1].path,
            trigger.tests[1].setup,
            trigger.tests[1].teardown,
            trigger.config.setup,
            trigger.config.teardown
        ]
        self.assertTrue(all(map(not_contains, lines_to_verify)))

    def test_collection_after_interpolation(self):
        """
        1. Checks if the plain path with a '.' gets resolved
        the same way as a standard relative path, i.e. the
        same way as CWD interpolated variant.
        2. Checks if each of the blocks collects an expected
        number of 2 different test functions.
        """
        is_of_len_2 = lambda l: len(l._tests) == 2
        trigger = self.trigger()
        trigger._resolve_interpolables(self.yaml_path)
        refs = [s for s, n in prepare_suite(trigger)]
        self.assertTrue(all(map(is_of_len_2, refs)))


if __name__ == "__main__":
    unittest.main()
