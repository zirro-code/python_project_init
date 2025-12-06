import asyncio
import os
from typing import Any, TypedDict

from bson import ObjectId
from loguru import logger
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from src.core.mongo.base import AbstractCollection, Connector, MongoCollectionSingleton


class User(TypedDict):
    _id: ObjectId


class UsersCollection(MongoCollectionSingleton, AbstractCollection):
    def _init_singleton(self) -> None:
        self.db: AsyncDatabase[Any] = Connector(
            database_name=os.environ["MONGO_DATABASE_NAME"]
        ).db

        self.collection_name = "users"
        self.collection: AsyncCollection[User] = self.db[self.collection_name]


if __name__ == "__main__":

    async def main() -> None:
        os.environ["MONGO_DATABASE_NAME"] = "_test"
        os.environ["MONGO_URI"] = "mongodb://localhost:27017/"

        mongo_collection1 = UsersCollection()
        mongo_collection2 = UsersCollection()
        assert mongo_collection1 is mongo_collection2

        logger.info(f"Result: {await mongo_collection1.collection.find_one({})}")
        await mongo_collection1.backup()

    asyncio.run(main())
