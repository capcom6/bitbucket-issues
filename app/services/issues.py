import datetime
import threading
import typing
from enum import Enum

from app.core import logger
from app.core.decorators import run_in_background
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

        self._sync_lock = threading.Lock()
        self._issues = []
        self._issues_time = 0

    async def select(
        self,
        *,
        priority: typing.Union[Priority, None] = None,
        assignee: typing.Union[str, None] = None,
    ) -> typing.List[dict]:
        if not self._repo.exists():
            self._sync()

        issues = self._repo.select(
            priority=priority.value if priority else None, assignee=assignee
        )

        return sorted(issues, key=lambda i: i["created_on"])

    @run_in_background
    def _sync(self):
        if self._sync_lock.locked():
            return

        logger.info(f"Sync on {threading.current_thread().name} started")
        with self._sync_lock:
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
            # так делать нельзя, потому что соединени с Redis уже привязано к основному циклу событий
            self._repo.replace(issues)
            self._issues = issues
            self._issues_time = datetime.datetime.now().timestamp()

        logger.info(f"Sync on {threading.current_thread().name} finished")
