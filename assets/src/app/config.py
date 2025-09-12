import asyncio
import os
import sys

from loguru import logger

from src.core.file_manager import FileManager


class Configuration:
    def _set_up_logger(self) -> None:
        FileManager.set_up_directory("./logs")

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
            level="DEBUG" if self.get_debug_mode() else "INFO",
        )

    @staticmethod
    def get_debug_mode() -> bool:
        env_var: str | None = os.getenv("DEBUG_MODE")

        if env_var is None:
            return False
        if env_var.lower() == "true":
            return True
        else:
            return False

    def setup(self) -> "Configuration":
        FileManager.set_up_directory("./backup/mongo")
        self._set_up_logger()

        return self

    async def asetup(self) -> "Configuration":
        return self


if __name__ == "__main__":

    async def main() -> None:
        await Configuration().setup().asetup()

    asyncio.run(main())
