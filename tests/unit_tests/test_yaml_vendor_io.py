from io import StringIO
import unittest
from kalash.spec import MetaSpec, Spec, CliConfigSpec, TestSpec, ConfigSpec, yaml
# from unittest.mock import Mock
from pathlib import Path


class TestYamlVendorIo(unittest.TestCase):

    def test_yaml_vendor_serialization_spec_object(self):
        spec = Spec(
            CliConfigSpec("1", "2", "3", "4", "5"),
            TestSpec("1", "2", "3", "4", "1", "2", "3", "4", "1", "2",
                     "3", "4", "1", "2", "3", "4", "1", "2", "3", "4"),
            ConfigSpec("1", "2", "3", "4", "5"),
            MetaSpec("1", "2", "3", "4", "1", "2", "3", "4", "5", "6")
        )
        # spec = Mock(Spec)
        stream = StringIO()
        yaml.dump(spec, stream)
        yaml.load(stream.getvalue(), yaml.Loader)
        self.assertIsInstance(
            spec.load_spec(str(Path(__file__).parent / "../../kalash/spec.yaml")),
            Spec
        )


if __name__ == "__main__":
    unittest.main()
