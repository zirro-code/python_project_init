import sys
from pathlib import Path

from loguru import logger


class Configuration:
    def _set_up_logger(self) -> None:
        logger.remove()
        logger.add(
            sys.stderr,
            level="INFO",
        )

    def _set_up_directories(self) -> None:
        paths: list[str] = ["./"]
        for path in paths:
            if not Path(path).exists():
                Path(path).mkdir(parents=True)

    def setup(self) -> "Configuration":
        self._set_up_logger()
        self._set_up_directories()

        return self

    async def asetup(self) -> "Configuration":
        return self
