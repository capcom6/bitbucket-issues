import asyncio
from functools import wraps


def run_in_background(func):
    """Decorator that runs function in the background."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, func, *args, **kwargs)

    return wrapper
