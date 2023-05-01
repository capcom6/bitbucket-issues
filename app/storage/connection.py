import datetime
from urllib.parse import urlparse
from redis.asyncio import Redis

from .repositories import (
    IssuesRepository,
    MemoryIssuesRepository,
    RedisIssuesRepository,
)


def create_issues_repository(
    dsn: str, *, ttl: datetime.timedelta = datetime.timedelta(hours=6)
) -> IssuesRepository:
    parsed = urlparse(dsn)
    if parsed.scheme == "memory":
        return MemoryIssuesRepository(ttl=ttl)
    if parsed.scheme == "redis":
        redis = Redis.from_url(dsn)
        return RedisIssuesRepository(redis, ttl=ttl)
    raise ValueError("Provided DSN is not supported")
