import abc
import datetime
import hashlib
import json
import typing
from redis import Redis


class IssuesRepository(abc.ABC):
    def __init__(
        self, *, ttl: datetime.timedelta = datetime.timedelta(hours=6)
    ) -> None:
        super().__init__()
        self.ttl = ttl

    def exists(self) -> bool:
        raise NotImplemented

    def select(
        self,
        *,
        priority: typing.Union[str, None] = None,
        assignee: typing.Union[str, None] = None,
    ) -> typing.List[dict]:
        raise NotImplemented

    def replace(self, issues: typing.List[dict]):
        raise NotImplemented


class MemoryIssuesRepository(IssuesRepository):
    def __init__(self, *, ttl: datetime.timedelta) -> None:
        super().__init__(ttl=ttl)
        self._issues = []
        self._issues_time = 0

    def exists(self) -> bool:
        return (
            self._issues_time + self.ttl.seconds > datetime.datetime.now().timestamp()
        )

    def select(
        self,
        *,
        priority: typing.Union[str, None] = None,
        assignee: typing.Union[str, None] = None,
    ) -> typing.List[dict]:
        def filter_fn(i: dict) -> bool:
            return (priority is None or i["priority"] == priority) and (
                assignee is None
                or (not i["assignee"] is None and i["assignee"]["uuid"] == assignee)
            )

        return list(filter(filter_fn, self._issues))

    def replace(self, issues: typing.List[dict]):
        self._issues = issues
        self._issues_time = datetime.datetime.now().timestamp()


class RedisIssuesRepository(IssuesRepository):
    KEY_ISSUES = "issues"
    KEY_ISSUES_ACTUAL = "issues:actual"
    KEY_PRIORITY = "issues:priority:"
    KEY_ASSIGNEE = "issues:assignee:"

    def __init__(
        self,
        connection: Redis,
        *,
        ttl: datetime.timedelta = datetime.timedelta(hours=6),
    ) -> None:
        super().__init__(ttl=ttl)
        self._con = connection

    def exists(self) -> bool:
        return self._con.get(self.KEY_ISSUES_ACTUAL) is not None

    def select(
        self,
        *,
        priority: typing.Union[str, None] = None,
        assignee: typing.Union[str, None] = None,
    ) -> typing.List[dict]:
        issues = []
        if priority is None and assignee is None:
            issues = self._con.hvals(self.KEY_ISSUES)
        elif priority is not None and assignee is not None:
            keys = self._con.sinter(
                f"{self.KEY_PRIORITY}{priority}", f"{self.KEY_ASSIGNEE}{assignee}"
            )
            issues = self._con.hmget(self.KEY_ISSUES, keys)
        elif priority is not None:
            keys = self._con.smembers(f"{self.KEY_PRIORITY}{priority}")
            issues = self._con.hmget(self.KEY_ISSUES, keys)
        elif assignee is not None:
            keys = self._con.smembers(f"{self.KEY_ASSIGNEE}{assignee}")
            issues = self._con.hmget(self.KEY_ISSUES, keys)

        return [json.loads(v) for v in issues]

    def replace(self, issues: typing.List[dict]):
        self._con.delete(*self._con.keys(f"{self.KEY_ISSUES}*"))

        for i in issues:
            key = self._md5(i["links"]["self"]["href"])
            self._con.hset(self.KEY_ISSUES, key, json.dumps(i))
            self._con.sadd(f"{self.KEY_PRIORITY}{i['priority']}", key)
            if i.get("assignee") is not None:
                self._con.sadd(f"{self.KEY_ASSIGNEE}{i['assignee']['uuid']}", key)
        self._con.set(
            self.KEY_ISSUES_ACTUAL, datetime.datetime.now().timestamp(), ex=self.ttl
        )

    def _md5(self, val: str) -> str:
        return hashlib.md5(val.encode()).hexdigest()
