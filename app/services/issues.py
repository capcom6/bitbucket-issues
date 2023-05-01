import asyncio
import threading
import typing
from enum import Enum

from app.core import logger
from app.storage.repositories import IssuesRepository

from .bitbucket import BitBucketService


class Priority(Enum):
    TRIVIAL = "trivial"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"
    BLOCKER = "blocker"


class IssuesService:
    def __init__(
        self,
        bitbucket: BitBucketService,
        issues: IssuesRepository,
        *,
        repos_filter: typing.Union[str, None] = None,
        issues_filter: typing.Union[str, None] = None,
    ) -> None:
        self._client = bitbucket
        self._repo = issues

        self._repos_filter = repos_filter or ""
        self._issues_filter = (
            issues_filter
            or '(state = "new" OR state = "open" OR state = "on hold") AND (priority = "major" OR priority = "critical" OR priority = "blocker")'
        )

        self._sync_lock = asyncio.Lock()
        self._issues = []

    async def select(
        self,
        *,
        priority: typing.Union[Priority, None] = None,
        assignee: typing.Union[str, None] = None,
    ) -> typing.List[dict]:
        issues = await self._repo.select(
            priority=priority.value if priority else None, assignee=assignee
        )

        return sorted(issues, key=lambda i: i["created_on"])

    async def sync(self, *args, **kwargs):
        if await self._repo.exists():
            return

        return await self._sync()

    async def _sync(self):
        if self._sync_lock.locked():
            return

        logger.info(f"Sync on {threading.current_thread().name} started")
        async with self._sync_lock, self._client:

            async def gen_to_list(
                gen: typing.AsyncGenerator[typing.Dict[str, typing.Any], None]
            ) -> typing.List[typing.Dict[str, typing.Any]]:
                data = []
                async for item in gen:
                    data.append(item)
                return data

            repos = await self._client.select_repositories(
                params={
                    "q": "has_issues = True"
                    if len(self._repos_filter) == 0
                    else f"(has_issues = True) AND {self._repos_filter}"
                }
            )

            repo_tasks = [
                asyncio.create_task(
                    gen_to_list(
                        await self._client.select_issues(
                            repo["uuid"],
                            params={"q": self._issues_filter},
                        )
                    )
                )
                async for repo in repos
            ]

            results = await asyncio.gather(*repo_tasks)
            issues = [issue for group in results for issue in group]

            await self._repo.replace(issues)
            self._issues = issues

        logger.info(f"Sync on {threading.current_thread().name} finished")
