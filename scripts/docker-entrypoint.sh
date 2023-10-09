#!/bin/sh

PORT=${PORT:-8000}

gunicorn --bind=0.0.0.0:${PORT} --access-logfile=- --proxy-allow-from='*' --timeout 120 -k gevent app.api:server $@
