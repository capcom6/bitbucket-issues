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
    TIMEOUT = 6 * 3600

    def __init__(self, bitbucket: BitBucketService) -> None:
        self._client = bitbucket
        self._issues = []
        self._issues_time = 0

    async def select(
        self,
        *,
        priority: typing.Union[Priority, None] = None,
        assignee: typing.Union[str, None] = None
    ) -> typing.List[dict]:
        def filter_fn(i: dict) -> bool:
            return (priority is None or i["priority"] == priority.value) and (
                assignee is None
                or (not i["assignee"] is None and i["assignee"]["uuid"] == assignee)
            )

        issues = filter(filter_fn, self._load())

        return sorted(issues, key=lambda i: i["created_on"])

    def _load(self) -> typing.List[dict]:
        if datetime.datetime.now().timestamp() < self._issues_time + self.TIMEOUT:
            return self._issues

        issues = [
            issue
            for repo in self._client.select_repositories(
                params={"q": "has_issues = True"}
            )
            for issue in self._client.select_issues(
                repo["uuid"],
                params={
                    "q": '(state = "new" OR state = "open" OR state = "on hold") AND (priority = "major" OR priority = "critical" OR priority = "blocker")'
                },
            )
        ]
        self._issues = issues
        self._issues_time = datetime.datetime.now().timestamp()

        return issues
