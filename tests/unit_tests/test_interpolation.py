import unittest
from kalash.interpolation import AmbigouosInterpolationException, _disambiguate_interpolation_map


class TestInterpolation(unittest.TestCase):

    def setUp(self) -> None:
        self.interpolation_map = {
            "$(ThisThing)": "Lol",
            "$(ThatThing)": "Rotfl",
        }
        self.interpolation_map_ambiguous = {
            "$(ThisThing)": lambda _1, _2, _3: "Lol",
            "$(thisthing)": lambda _1, _2, _3: "Rotfl",
        }

    def test_ambiguous_map(self):
        with self.assertRaises(AmbigouosInterpolationException):
            _disambiguate_interpolation_map(self.interpolation_map_ambiguous)

    def test_interpolation_with_fake_map(self):
        pass


if __name__ == "__main__":
    unittest.main()
