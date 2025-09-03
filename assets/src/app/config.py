import asyncio
import sys
from pathlib import Path

from loguru import logger


class Configuration:
    def _set_up_logger(self) -> None:
        self._set_up_directories(["./logs"])

        logger.remove()
        logger.add(
            "./logs/application.log",
            level="DEBUG",
            rotation="20 MB",
            retention="30 days",
            compression="zip",
        )
        logger.add(
            sys.stderr,
            level="INFO",
        )

    def _set_up_directories(self, paths: list[str]) -> None:
        for path in paths:
            if not Path(path).exists():
                Path(path).mkdir(parents=True)

    def setup(self) -> "Configuration":
        self._set_up_directories(["./", "./backup/mongo"])
        self._set_up_logger()

        return self

    async def asetup(self) -> "Configuration":
        return self


if __name__ == "__main__":

    async def main() -> None:
        await Configuration().setup().asetup()

    asyncio.run(main())
