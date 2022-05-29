from typing import Callable
import unittest
from kalash.model import Meta
from kalash.test_case import TestCase


def make_test_method(callback_to_run_in_await: Callable) -> Callable:
    def test_something(self: TestCase):
        with self.awaitTrue(callback):
            # TODO: `asyncio`
            # TODO: `Condition`
            callback()
    return test_something


def make_test_case(test_method: Callable[[Callable], Callable]) -> TestCase:
    test_case = TestCase(
        "test_something",
        "1234_ID",
        Meta("1234_ID"),
        None
    )
    setattr(test_case, "test_something", test_method)
    return test_case





class TestOnlineTesting(unittest.TestCase):

    def test_online_testing(self):
        test_case = make_test_case(make_test_method())
        

if __name__ == "__main__":
    unittest.main()
