import asyncio
import os
import sys
from typing import Self

from loguru import logger

from src.core.file_manager import FileManager


class Configuration:
    _debug_mode: bool | None = None

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
            level="DEBUG" if self.debug_mode else "INFO",
        )

    def _validate_env(self) -> None:
        file_manager = FileManager()
        example_env_variables: list[str] = list(
            file_manager.get_env_variable_names(".env.example")
        )
        env_variables: list[str] = list(file_manager.get_env_variable_names(".env"))
        for variable in example_env_variables:
            if variable not in env_variables:
                raise ValueError(
                    ".env file has variables that don't exist in .env.example file"
                )
        for variable in env_variables:
            if variable not in example_env_variables:
                raise ValueError(
                    ".env.example file has variables that don't exist in .env file"
                )

    async def asetup(self) -> Self:
        return self

    @property
    def debug_mode(self) -> bool:
        if self._debug_mode is not None:
            return self._debug_mode

        env_var: str | None = os.getenv("DEBUG_MODE")
        result: bool

        if env_var is None:
            result = False
        elif env_var.lower() == "true":
            result = True
        else:
            result = False

        self._debug_mode = result

        return self._debug_mode

    def setup(self) -> Self:
        FileManager.set_up_directory("./backup/mongo")
        self._set_up_logger()
        self._validate_env()

        return self

    @property
    def app_version(self) -> str:
        return os.getenv("APP_VERSION", "Failed to get application version")


if __name__ == "__main__":

    async def main() -> None:
        await Configuration().setup().asetup()

    asyncio.run(main())
