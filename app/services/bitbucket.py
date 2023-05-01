import typing

from bitbucket import AsyncClient


class BitBucketService:
    def __init__(
        self, login: str, password: str, owner: typing.Union[str, None]
    ) -> None:
        self._client = AsyncClient(login, password, owner)

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self._client.__aexit__(*args, **kwargs)

    async def select_repositories(
        self, *, params: typing.Union[dict, None] = None
    ) -> typing.AsyncGenerator[dict, None]:
        return self._client.all_pages(self._client.get_repositories, params)

    async def select_issues(
        self, repository_slug: str, *, params: typing.Union[dict, None] = None
    ) -> typing.AsyncGenerator[dict, None]:
        return self._client.all_pages(self._client.get_issues, repository_slug, params)
