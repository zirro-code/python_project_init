from typing import Any, Callable, Literal
from uuid import uuid4

from loguru import logger


def log(
    *,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG",
    name: str | None = None,
):
    def decorator(f: Callable[..., Any]):
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            job_uuid = str(uuid4())
            function_name = name if name is not None else f.__name__

            logger.log(level, f"Started {function_name} {job_uuid}")
            result = await f(*args, **kwargs)
            logger.log(level, f"Finished {function_name} {job_uuid}")

            return result

        return wrapper

    return decorator
