import asyncio
import time
from typing import Callable
import unittest
from kalash.model import CliConfig, Meta, Trigger
from kalash.test_case import TestCase, async_test


def make_test_case(callback_to_run_in_await: Callable) -> TestCase:
    class FakeTestCase(TestCase):

        # @async_test  # used in user API, but needs to be turned off
                       # for testing since you cannot run two event loops
                       # (notice that `async_test` is used below in
                       # `TestOnlineTesting` class)
        async def test_something(self: TestCase):
            async with self.expect(callback_to_run_in_await) as f:
                return f

    test_case = FakeTestCase(
        "test_something",
        "1234_ID",
        Meta("1234_ID"),
        Trigger(cli_config=CliConfig(no_log=True))
    )

    return test_case


class TestOnlineTesting(unittest.TestCase):

    @async_test
    async def test_online_testing(self):
        sleep_time = 0.25

        async def wait():
            start = time.time()
            await asyncio.sleep(sleep_time)
            end = time.time()
            return end

        test_case = make_test_case(wait)

        time_elapsed = await test_case.test_something()  # type: ignore
        if time_elapsed < sleep_time:
            self.fail(
                "The async operation seems to have lasted less than "
                "the configured sleep time. Make sure your async logic "
                "for online testing is on point."
            )


if __name__ == "__main__":
    unittest.main()
