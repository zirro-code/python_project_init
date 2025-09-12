import asyncio
import time
from typing import Any

import pytest

import src.core.misc


@pytest.mark.asyncio
async def test_async_atomic() -> None:
    start_time = time.perf_counter()

    @src.core.misc.async_atomic()
    async def test_async(test: int) -> str:
        await asyncio.sleep(0.01)
        return f"str {test}"

    await asyncio.gather(*(test_async(1) for _ in range(10)))

    lock1 = asyncio.Lock()

    @src.core.misc.async_atomic(lock1)
    async def test_async1(test: int) -> str:
        await asyncio.sleep(0.01)
        return f"str {test}"

    await asyncio.gather(*(test_async1(1) for _ in range(10)))
    end_time = time.perf_counter()

    assert (end_time - start_time) > 0.2


@pytest.mark.parametrize(
    ("_input", "expected"),
    (
        (
            ({"a": 1}),
            ({"a": 1}),
        ),
        # This function is... Meh, shit.
        (
            ([{"a": 1}]),
            ({".0.a": 1}),
        ),
        (
            ({"a": 1, "b": {"c": 1, "d": 2}}),
            ({"a": 1, "b.c": 1, "b.d": 2}),
        ),
        (
            ({"a": 1, "b": [{"c": 1, "d": 2}, {"c": 1, "d": 2}]}),
            ({"a": 1, "b.0.c": 1, "b.0.d": 2, "b.1.c": 1, "b.1.d": 2}),
        ),
    ),
)
def test_flatten_json(
    _input: dict[str, Any] | list[Any], expected: dict[str, Any]
) -> None:
    assert src.core.misc.flatten_json(_input) == expected
