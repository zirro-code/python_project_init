import asyncio
import os

from loguru import logger
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import (
    DeclarativeBase,
)

from src.app.config import Configuration


class BaseModel(AsyncAttrs, DeclarativeBase):
    pass


class Connector:
    db: async_sessionmaker[AsyncSession]
    engine: AsyncEngine

    def __init__(self, database_name: str):
        database_url = f"{os.environ['POSTGRES_URI']}{database_name}"

        self.engine = create_async_engine(
            database_url,
            echo=Configuration.get_debug_mode(),
            pool_pre_ping=True,
        )
        self.db = async_sessionmaker(self.engine, expire_on_commit=False)

        try:
            tables = inspect(self.db().get_bind().engine).get_table_names()
            logger.info(f"Connected to Postgres. Database has {len(tables)} tables.")
        except Exception:
            logger.critical("Could not connect to Postgres")
            raise

    async def ainit(self) -> "Connector":
        # create tables (for demo; use Alembic in real apps)
        async with self.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

        return self


if __name__ == "__main__":

    async def main():
        os.environ["POSTGRES_DATABASE_NAME"] = "test"
        os.environ["POSTGRES_URI"] = (
            "postgresql+asyncpg://pguser:pgpass@localhost:5432/"
        )

        db = (
            await (
                Connector(database_name=os.environ["POSTGRES_DATABASE_NAME"])
            ).ainit()
        ).db
        async with db() as session:
            stmt = select().where()
            result = (await session.execute(stmt)).scalars().all()
            logger.info(f"Result: {result}")

    asyncio.run(main())
