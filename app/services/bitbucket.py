import functools
import typing

from bitbucket.client import Client


class BitBucketService:
    def __init__(
        self, login: str, password: str, owner: typing.Union[str, None]
    ) -> None:
        self._client = Client(login, password, owner)

    def select_repositories(
        self, *, params: typing.Union[dict, None] = None
    ) -> typing.Generator[dict, None, None]:
        return self._get_pages(self._client.get_repositories, params)

    def select_issues(
        self, repository_slug: str, *, params: typing.Union[dict, None] = None
    ) -> typing.Generator[dict, None, None]:
        return self._get_pages(
            functools.partial(self._client.get_issues, repository_slug), params
        )

    def _get_pages(
        self,
        func: typing.Callable[[dict], typing.Union[dict, None]],
        params: typing.Union[dict, None] = None,
    ) -> typing.Generator[dict, None, None]:
        params = params or {}
        page = 1

        while True:
            params["page"] = page
            resp = func(params)
            if resp is None:
                break

            yield from resp["values"]

            if not "next" in resp:
                break

            page += 1
