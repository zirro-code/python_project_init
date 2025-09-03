import asyncio

import src.app.application
import src.app.config
import src.core.log


@src.core.log.log(level="INFO", name=__name__)
async def main() -> None:
    await src.app.config.Configuration().setup().asetup()
    await (await src.app.application.Application().ainit()).run()


if __name__ == "__main__":
    asyncio.run(main())
