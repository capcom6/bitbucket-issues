import abc
import datetime
import hashlib
import json
import typing
from redis.asyncio import Redis


class IssuesRepository(abc.ABC):
    def __init__(
        self, *, ttl: datetime.timedelta = datetime.timedelta(hours=6)
    ) -> None:
        super().__init__()
        self.ttl = ttl

    async def exists(self) -> bool:
        raise NotImplemented

    async def select(
        self,
        *,
        priority: typing.Union[str, None] = None,
        assignee: typing.Union[str, None] = None,
    ) -> typing.List[dict]:
        raise NotImplemented

    async def replace(self, issues: typing.List[dict]):
        raise NotImplemented


class MemoryIssuesRepository(IssuesRepository):
    def __init__(self, *, ttl: datetime.timedelta) -> None:
        super().__init__(ttl=ttl)
        self._issues = []
        self._issues_time = 0

    async def exists(self) -> bool:
        return (
            self._issues_time + self.ttl.seconds > datetime.datetime.now().timestamp()
        )

    async def select(
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

    async def replace(self, issues: typing.List[dict]):
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

    async def exists(self) -> bool:
        return await self._con.get(self.KEY_ISSUES_ACTUAL) is not None

    async def select(
        self,
        *,
        priority: typing.Union[str, None] = None,
        assignee: typing.Union[str, None] = None,
    ) -> typing.List[dict]:
        issues: typing.List[str] = []

        async with self._con.pipeline():
            if priority is None and assignee is None:
                issues = await self._con.hvals(self.KEY_ISSUES)
            elif priority is not None and assignee is not None:
                keys = await self._con.sinter(
                    f"{self.KEY_PRIORITY}{priority}", f"{self.KEY_ASSIGNEE}{assignee}"
                )
                issues = await self._con.hmget(self.KEY_ISSUES, keys)  # type: ignore
            elif priority is not None:
                keys = await self._con.smembers(f"{self.KEY_PRIORITY}{priority}")
                issues = await self._con.hmget(self.KEY_ISSUES, keys)  # type: ignore
            elif assignee is not None:
                keys = await self._con.smembers(f"{self.KEY_ASSIGNEE}{assignee}")
                issues = await self._con.hmget(self.KEY_ISSUES, keys)  # type: ignore

        return [json.loads(v) for v in issues]

    async def replace(self, issues: typing.List[dict]):
        async with self._con.pipeline():
            keys = await self._con.keys(f"{self.KEY_ISSUES}*")
            if keys:
                await self._con.delete(*keys)

            for i in issues:
                key = self._md5(i["links"]["self"]["href"])
                await self._con.hset(self.KEY_ISSUES, key, json.dumps(i))
                await self._con.sadd(f"{self.KEY_PRIORITY}{i['priority']}", key)
                if i.get("assignee") is not None:
                    await self._con.sadd(
                        f"{self.KEY_ASSIGNEE}{i['assignee']['uuid']}", key
                    )
            await self._con.set(
                self.KEY_ISSUES_ACTUAL, datetime.datetime.now().timestamp(), ex=self.ttl
            )

    def _md5(self, val: str) -> str:
        return hashlib.md5(val.encode()).hexdigest()
