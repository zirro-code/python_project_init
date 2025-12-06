import abc
import asyncio
import gzip
import os
from typing import Any, ClassVar, Self

import arrow
from bson import json_util
from loguru import logger
from pymongo import AsyncMongoClient, timeout
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import ConnectionFailure

import src.core.log


class Connector:
    db: AsyncDatabase[Any]

    def __init__(self, database_name: str):
        self.db = AsyncMongoClient(os.environ["MONGO_URI"])[database_name]

    async def ainit(self) -> Self:
        try:
            with timeout(1):
                collections = await self.db.list_collection_names()
                logger.info(
                    f"Connected to MongoDB. "
                    f"Database has {len(collections)} collections."
                )
        except ConnectionFailure:
            logger.critical("Could not connect to mongodb")
            raise

        return self


class MongoCollectionSingleton(abc.ABC):
    _instance: ClassVar[Self | None] = None
    _initialized: ClassVar[bool] = False

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        cls = type(self)
        if cls._initialized:
            return
        super().__init__()
        cls._initialized = True
        self._init_singleton()

    @abc.abstractmethod
    def _init_singleton(self) -> None:
        """
        Hook called exactly once per subclass.
        Override this in subclasses instead of __init__.
        """
        raise NotImplementedError(
            "Initiated singleton subclass does not implement _init_singleton"
        )


class AbstractCollection(MongoCollectionSingleton, abc.ABC):
    db: AsyncDatabase[Any]
    collection_name: str
    collection: AsyncCollection[Any]

    @src.core.log.log(level="INFO")
    async def backup(self) -> None:
        with gzip.open(
            f"backup/mongo/{self.collection_name}_{arrow.utcnow().isoformat()}.gz",
            "wt",
            encoding="utf-8",
        ) as gz:
            async for document in self.collection.find({}):
                dumped_info = json_util.dumps(document)
                gz.write(dumped_info + "\n")

    def _init_singleton(self) -> None:
        pass


if __name__ == "__main__":

    async def main() -> None:
        os.environ["MONGO_DATABASE_NAME"] = "test"
        os.environ["MONGO_URI"] = "mongodb://localhost:27017/"

        db = (
            await Connector(database_name=os.environ["MONGO_DATABASE_NAME"]).ainit()
        ).db
        result = await db["users"].find_one({})

        logger.info(f"Result: {result}")

    asyncio.run(main())
