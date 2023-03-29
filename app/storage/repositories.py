import datetime
import hashlib
import json
import typing
from redis.asyncio import Redis


class IssuesRepository:
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
        self._con = connection
        self._ttl = ttl

    async def exists(self) -> bool:
        return await self._con.get(self.KEY_ISSUES_ACTUAL) is not None

    async def select(
        self,
        *,
        priority: typing.Union[str, None] = None,
        assignee: typing.Union[str, None] = None,
    ) -> typing.List[dict]:
        issues = []
        if priority is None and assignee is None:
            issues = await self._con.hvals(self.KEY_ISSUES)
        if priority is not None and assignee is not None:
            keys = await self._con.sinter(
                f"{self.KEY_PRIORITY}{priority}", f"{self.KEY_ASSIGNEE}{assignee}"
            )
            issues = await self._con.hmget(self.KEY_ISSUES, keys)
        if priority is not None:
            keys = await self._con.smembers(f"{self.KEY_PRIORITY}{priority}")
            issues = await self._con.hmget(self.KEY_ISSUES, keys)
        if assignee is not None:
            keys = await self._con.smembers(f"{self.KEY_ASSIGNEE}{assignee}")
            issues = await self._con.hmget(self.KEY_ISSUES, keys)

        return [json.loads(v) for v in issues]

    async def replace(self, issues: typing.List[dict]):
        for i in issues:
            key = self._md5(i["links"]["self"]["href"])
            await self._con.hset(self.KEY_ISSUES, key, json.dumps(i))
            await self._con.sadd(f"{self.KEY_PRIORITY}{i['priority']}", key)
            if i.get("assignee") is not None:
                await self._con.sadd(f"{self.KEY_ASSIGNEE}{i['assignee']['uuid']}", key)
        await self._con.set(
            self.KEY_ISSUES_ACTUAL, datetime.datetime.now().timestamp(), ex=self._ttl
        )

    def _md5(self, val: str) -> str:
        # create an MD5 hash object
        hash_object = hashlib.md5()

        # update the hash object with the string
        hash_object.update(val.encode())

        # get the hexadecimal representation of the hash
        return hash_object.hexdigest()
