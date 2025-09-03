import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, ParamSpec, TypeVar

from loguru import logger

T = TypeVar("T")
P = ParamSpec("P")


def async_atomic(
    lock: asyncio.Lock | None = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Coroutine[Any, Any, T]]]:
    _lock = lock or asyncio.Lock()

    def decorator(
        func: Callable[P, Awaitable[T]],
    ) -> Callable[P, Coroutine[Any, Any, T]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            async with _lock:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":

    async def main() -> None:
        @async_atomic()
        async def test_async(test: int) -> str:
            await asyncio.sleep(0.1)
            logger.info("Got it")
            return f"str {test}"

        await asyncio.gather(*(test_async(1) for _ in range(10)))

        lock1 = asyncio.Lock()

        @async_atomic(lock1)
        async def test_async1(test: int) -> str:
            await asyncio.sleep(0.1)
            logger.info("Got it")
            return f"str {test}"

        await asyncio.gather(*(test_async1(1) for _ in range(10)))

    asyncio.run(main())
