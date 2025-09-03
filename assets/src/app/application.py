import asyncio


class Application:
    def __init__(self) -> None:
        pass

    async def ainit(self) -> "Application":
        return self

    async def run(self) -> None:
        pass


if __name__ == "__main__":

    async def main() -> None:
        await (await Application().ainit()).run()

    asyncio.run(main())
