import asyncio
import os
from typing import Optional

from assets.src.core.postgres.base import async_sessionmaker
from loguru import logger
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.core.postgres.base import Connector
from src.core.postgres.models import User


class UsersTable:
    _instance: Optional["UsersTable"] = None
    __initialized: bool

    def __new__(cls) -> "UsersTable":
        if cls._instance is None:
            cls._instance = super(UsersTable, cls).__new__(cls)
            cls.__initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self.__initialized:
            return
        self.__initialized = True

        self.db: async_sessionmaker[AsyncSession] = Connector(
            database_name=os.environ["POSTGRES_DATABASE_NAME"]
        ).db

    async def create_user(self) -> None:
        async with self.db() as session:
            async with session.begin():
                u = User(
                    name="alice",
                )
                session.add(u)


if __name__ == "__main__":

    async def main() -> None:
        os.environ["POSTGRES_DATABASE_NAME"] = "test"
        os.environ["POSTGRES_URI"] = (
            "postgresql+asyncpg://pguser:pgpass@localhost:5432/"
        )

        postgres_users = UsersTable()
        logger.info(f"Result: {await postgres_users.create_user()}")

    asyncio.run(main())
