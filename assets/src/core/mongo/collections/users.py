import asyncio
import os
from typing import Any, Optional, TypedDict

from bson import ObjectId
from loguru import logger
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from src.core.mongo.base import AbstractCollection, Connector


class User(TypedDict):
    _id: ObjectId


class UsersCollection(AbstractCollection):
    _instance: Optional["UsersCollection"] = None
    __initialized: bool

    def __new__(cls) -> "UsersCollection":
        if cls._instance is None:
            cls._instance = super(UsersCollection, cls).__new__(cls)
            cls.__initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self.__initialized:
            return
        self.__initialized = True

        self.db: AsyncDatabase[Any] = Connector(
            database_name=os.environ["MONGO_DATABASE_NAME"]
        ).db
        self.collection_name = "users"

        self.collection: AsyncCollection[User] = self.db[self.collection_name]


if __name__ == "__main__":

    async def main() -> None:
        os.environ["MONGO_DATABASE_NAME"] = "tradelink_test"
        os.environ["MONGO_URI"] = "mongodb://localhost:27017/"

        mongo_users = UsersCollection()
        logger.info(f"Result: {await mongo_users.collection.find_one({})}")
        await mongo_users.backup()

    asyncio.run(main())
