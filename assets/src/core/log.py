import asyncio
import time
from collections.abc import Awaitable, Callable, Coroutine, Generator
from contextlib import contextmanager
from typing import (
    Any,
    Literal,
    ParamSpec,
    TypeVar,
    cast,
    overload,
)
from uuid import uuid4

from loguru import logger

T = TypeVar("T")
P = ParamSpec("P")


@contextmanager
def log_context(
    *,
    func: Callable[P, Awaitable[T]] | Callable[P, T],
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG",
    name: str | None = None,
) -> Generator[Callable[P, Awaitable[T]] | Callable[P, T], Any, None]:
    job_uuid = str(uuid4())
    function_name = name if name is not None else func.__name__

    logger.log(level, f"Started {function_name} {job_uuid}")
    start_time = time.perf_counter_ns()
    yield func
    time_taken_ms = (time.perf_counter_ns() - start_time) // 1_000_000
    logger.log(
        level,
        f"Finished {function_name} {job_uuid}. Taken {time_taken_ms} ms.",
    )


def log(
    *,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG",
    name: str | None = None,
) -> Callable[..., Any]:
    @overload
    def decorator(
        func: Callable[P, Awaitable[T]],
    ) -> Callable[P, Coroutine[Any, Any, T]]: ...
    @overload
    def decorator(func: Callable[P, T]) -> Callable[P, T]: ...
    def decorator(
        func: Callable[P, Any],
    ) -> Callable[P, Coroutine[Any, Any, Awaitable[T]]] | Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with log_context(func=func, level=level, name=name):
                result = cast(Callable[P, T], func)(*args, **kwargs)
                return result

        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Awaitable[T]:
            with log_context(func=func, level=level, name=name):
                result = await cast(Callable[P, Awaitable[Awaitable[T]]], func)(
                    *args, **kwargs
                )
                return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


if __name__ == "__main__":

    @log(level="INFO")
    def test_sync(test: int) -> str:
        return f"str {test}"

    @log(level="INFO")
    async def test_async(test: int) -> str:
        return f"str {test}"

    test_sync(1)
    asyncio.run(test_async(1))
