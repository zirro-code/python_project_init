import asyncio

import app.application
import app.config


async def main() -> None:
    await app.config.Configuration().setup().asetup()
    await (await app.application.Application().ainit()).run()


if __name__ == "__main__":
    asyncio.run(main())

# TODO: ci (tox)
# TODO: cd
# TODO: terraform
# TODO: fastapi
# TODO: write tests for current functionality
