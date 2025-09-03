import abc
import asyncio
import traceback
from typing import Any, Literal
from urllib.parse import urlencode

import aiohttp
from loguru import logger

from src.core.misc import async_atomic

HTTP_METHODS = Literal[
    "GET",
    "POST",
    "PUT",
    "HEAD",
    "DELETE",
    "PATCH",
    "OPTIONS",
    "CONNECT",
    "TRACE",
]
ASYNC_LOCK = asyncio.Lock()


class HttpClientError(Exception):
    pass


class HttpClient:
    def __init__(
        self,
        total_timeout: float = 60.0,
        connect_timeout: float = 5.0,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._session: aiohttp.ClientSession | None = None
        self._running: bool = False
        self._total_timeout: float = total_timeout
        self._connect_timeout: float = connect_timeout
        self._headers: dict[str, str] = headers or {}

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise Exception("Session is not initialized")

        return self._session

    @async_atomic(ASYNC_LOCK)
    async def run(self) -> None:
        if self._running:
            logger.warning("HttpClient is already running.")
            return

        connector = aiohttp.TCPConnector(limit=200)
        self._session = aiohttp.ClientSession(
            raise_for_status=True,
            connector=connector,
            timeout=aiohttp.ClientTimeout(self._total_timeout, self._connect_timeout),
            headers=self._headers,
        )
        self._running = True

    @async_atomic(ASYNC_LOCK)
    async def stop(self) -> None:
        if self._session is not None:
            await self._session.close()
        self._running = False

    async def __aenter__(self) -> None:
        await self.run()

    async def __aexit__(self, *_exc: Any) -> None:
        await self.stop()


class AbstractHttpClient(abc.ABC):
    _http_client: HttpClient | None = None

    base_url: str

    @property
    def http_client(self) -> HttpClient:
        if self._http_client is None:
            self._http_client = HttpClient()
        assert self._http_client is not None
        return self._http_client

    @http_client.setter
    def http_client(self, client: HttpClient) -> None:
        self._http_client = client

    @abc.abstractmethod
    def __init__(self, *args: Any, base_url: str, **kwargs: Any) -> None:
        self.base_url = base_url

    @abc.abstractmethod
    async def _handle_response_code(self, request: aiohttp.ClientResponse) -> bool:
        code: int = request.status
        result: bool = False
        if code in [200, 201]:
            result = True
        elif code in [400, 401, 404, 500, 501]:
            result = False
        return result

    async def _json_to_dict(
        self, request: aiohttp.ClientResponse
    ) -> Any | HttpClientError:
        try:
            return await request.json()
        except Exception:
            logger.error(
                f"Failed to parse {request.url} response. {traceback.format_exc()}"
            )
            return HttpClientError("Failed to parse response to json.")

    def _build_url(self, route: str, query: dict[str, Any] | None) -> str:
        result = f"{self.base_url}/{route}"
        if query is not None:
            result += f"?{urlencode(query)}"
        return result

    @abc.abstractmethod
    async def request(
        self,
        *args: Any,
        method: HTTP_METHODS,
        route: str,
        query: dict[str, Any] | None,
        data: Any | None,
        headers: dict[str, str],
        retries: int = 0,
        **kwargs: Any,
    ) -> Any | HttpClientError:
        url: str = self._build_url(route=route, query=query)

        for request_iteration in range(1, retries + 1):
            async with self.http_client.session.request(
                method=method,
                url=url,
                headers=headers,
            ) as request:
                if not await self._handle_response_code(request):
                    logger.debug(
                        f"Request {request.url} unsuccessful "
                        f"in {request_iteration} attempt."
                    )
                    continue
                result: Any | HttpClientError = await self._json_to_dict(request)

                return result

        return HttpClientError("Ran out of retries")


if __name__ == "__main__":

    async def main() -> None:
        class ClientUser1(AbstractHttpClient):
            def __init__(self) -> None:
                pass

            async def _handle_response_code(
                self, request: aiohttp.ClientResponse
            ) -> bool:
                if request.status == 200:
                    return True
                else:
                    return False

            async def request(self, retries: int = 1) -> Any:  # type: ignore [override]
                for request_iteration in range(1, retries + 1):
                    async with self.http_client.session.request(
                        "GET",
                        "https://ipinfo.io",
                        headers={"Accept": "application/json"},
                    ) as request:
                        if not await self._handle_response_code(request):
                            logger.debug(
                                f"Request {request.url} unsuccessful "
                                f"in {request_iteration} attempt."
                            )
                            continue
                        result: Any | HttpClientError = await self._json_to_dict(
                            request
                        )

                        return result

                return HttpClientError("Ran out of retries")

        class ClientUser2:
            def __init__(self) -> None:
                self.http_client = HttpClient()

            async def request(self) -> Any:
                async with self.http_client.session.request(
                    "GET", "https://ipinfo.io", headers={"Accept": "application/json"}
                ) as request:
                    return await request.json()

        clients: list[ClientUser1 | ClientUser2] = [ClientUser1(), ClientUser2()]
        for user_client in clients:
            async with user_client.http_client:
                logger.info(await user_client.request())

            await user_client.http_client.run()
            logger.info(await user_client.request())
            await user_client.http_client.stop()

    asyncio.run(main())
