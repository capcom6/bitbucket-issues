#!/bin/sh

PORT=${PORT:-8000}

gunicorn --bind=0.0.0.0:${PORT} --access-logfile=- --proxy-allow-from='*' -k uvicorn.workers.UvicornWorker app.api:server $@
