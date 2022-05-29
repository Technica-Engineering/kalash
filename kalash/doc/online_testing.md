# Online Testing

## What is online testing used for

[What is online testing used for]: #what-is-online-testing-used-for

Online Testing is when you wait for a hardware (or software) system to do something instead of performing instant operations that Python scripts normally do sequentially.

In many cases hardware testing will require you to wait for a particular condition to be met or for a value to be returned from some system. You might not want to block your main runner thread or you want to wait for a value for a specified amount of time before you deem the test to be failed.

The easiest way to make any Python script wait a specified amount of time is to do:

```python
import time

timeout = 5
time.sleep(timeout)
```

> ❗ However the above results in a terrible problem: if you wait for 5 seconds how do you make sure that e.g. a message sent by a device isn't lost during that time when the interpreter just sits idle and does nothing? Wouldn't it be great to make the interpreter wait but also _simultaneously_ listen to any incoming messages?

For that you should use **asynchronous logic**. With _async_ (alias for _asynchronous_) logic, you can easily express situations in which:

- Your device does not return the message you want instantly
- You want to fail the test if the device did not respond with the proper message for a while

## Online Testing with Kalash

[Online Testing with Kalash]: #online-testing-with-kalash

### `asyncio` basics

[asyncio basics]: #asyncio-basics

Kalash makes ample use of the `asyncio` module which is a part of Python's standard library, i.e. is built-in.

> 👉 Although this may seem daunting, `asyncio` is fairly simple to understand if you give it a bit of practice. Read the rest of this section to learn about the basics.

If you want any operation to run concurrently you mark it as `async` and in the function's body you mark which value you want to `await`. `await` basically tells the Python interpreter to _wait until this value is available_:

```python
import asyncio


async def make_a_taco():
    seconds_to_make_a_taco = 10
    # simulate someone physically making the taco with `sleep`:
    await asyncio.sleep(seconds_to_make_a_taco)
    return "🌮"

async def get_a_taco():
    taco = await make_a_taco()
    return taco
```

The above will make whoever calls `get_a_taco()` wait until a taco is made... with a caveat: you will only get a taco if you patiently wait for it, i.e. you have to `await get_a_taco()`:

```python
async def get_a_taco():
    return await taco


async def main():
    taco = await get_a_taco()
    print(taco)
```

> 👀 At this point you might be asking yourself, how is this even useful? Well, you might want to do something else while waiting for a taco, right?

```python
async def browse_phone():
    while True:
        await asyncio.sleep(1)
        print("Browsing Phone")
```

Now, you're waiting for a taco and just passing time playing with your phone. With `asyncio` it's easy to wrap your phone-playing in a cancellable `Task`. So instead of `browse_phone()` called directly, we use `asyncio.create_task`:

```python
async def get_a_taco():
    phone = asyncio.create_task(browse_phone())
    taco = await make_a_taco()
    phone.cancel()
    return taco
```

The code above will start the `browse_phone` function and then instead of just keeping on printing `Browsing Phone` over and over again, it will continue to the next line. In the next line it will simply wait until we get the taco and once we get the taco, we can `phone.cancel()`.

### Async logic in Kalash test cases

[Async logic in Kalash test cases]: #async-logic-in-kalash-test-cases

To make asserting some values a bit easier than juggling a bunch of `async` code, we're giving you an `expect` method on the `TestCase` class which can be conveniently used with the `with` statement:

```python
from kalash.test_case import TestCase, async_test

class MyTestCase(TestCase):

    @async_test
    async def test_something(self: TestCase):
        async with self.expect(some_function, timeout=3, some_argument=5) as future:
            some_value_that_you_wait_for = await future
            self.assertEqual(
                some_value_that_you_wait_for,
                42
            )
```

The above code assumes that `some_function` and `some_argument` exist in the current scope and will run `some_function` with `some_argument` set to `5`. This is equivalent to `some_function(some_argument=5)`. The value returned by a function is named here `future` and when the value is available, it will be written to `some_value_that_you_wait_for`.

> 👀 `self.expect` accepts any awaitable objects and functions that return awaitable objects.
