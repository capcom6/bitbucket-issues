from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from .router import router

server = FastAPI()

server.add_middleware(GZipMiddleware)

server.include_router(router)

__all__ = ["server"]
