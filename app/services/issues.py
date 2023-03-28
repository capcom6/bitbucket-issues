import datetime
import typing
from enum import Enum

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
        *,
        ttl: typing.Union[datetime.timedelta, None] = None,
        repos_filter: typing.Union[str, None] = None,
        issues_filter: typing.Union[str, None] = None,
    ) -> None:
        self._client = bitbucket
        self._ttl = ttl or datetime.timedelta(hours=6)
        self._repos_filter = repos_filter or ""
        self._issues_filter = (
            issues_filter
            or '(state = "new" OR state = "open" OR state = "on hold") AND (priority = "major" OR priority = "critical" OR priority = "blocker")'
        )

        self._issues = []
        self._issues_time = 0

    async def select(
        self,
        *,
        priority: typing.Union[Priority, None] = None,
        assignee: typing.Union[str, None] = None,
    ) -> typing.List[dict]:
        def filter_fn(i: dict) -> bool:
            return (priority is None or i["priority"] == priority.value) and (
                assignee is None
                or (not i["assignee"] is None and i["assignee"]["uuid"] == assignee)
            )

        issues = filter(filter_fn, self._load())

        return sorted(issues, key=lambda i: i["created_on"])

    def _load(self) -> typing.List[dict]:
        if datetime.datetime.now().timestamp() < self._issues_time + self._ttl.seconds:
            return self._issues

        issues = [
            issue
            for repo in self._client.select_repositories(
                params={
                    "q": "has_issues = True"
                    if len(self._repos_filter) == 0
                    else f"(has_issues = True) AND {self._repos_filter}"
                }
            )
            for issue in self._client.select_issues(
                repo["uuid"],
                params={"q": self._issues_filter},
            )
        ]
        self._issues = issues
        self._issues_time = datetime.datetime.now().timestamp()

        return issues
