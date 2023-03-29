from redis.asyncio import Redis


def connect(dsn: str) -> Redis:
    return Redis.from_url(dsn)
