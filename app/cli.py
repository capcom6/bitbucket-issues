import asyncio
import functools

import click

from app.core.logger import setup_logging


def make_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    setup_logging()
    pass


@cli.command()
@click.option(
    "--host", default="127.0.0.1", show_default=True, help="Hostname to listen on"
)
@click.option("--port", default=8000, show_default=True, help="Port to listen on")
def api(host: str, port: int):
    """Start the API server"""
    import uvicorn

    uvicorn.run("app.api:server", host=host, port=port, reload=True)
