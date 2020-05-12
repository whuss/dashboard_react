#!/bin/sh
gunicorn  --error-logfile err.log --access-logfile access.log --log-level debug app:app --worker-class=gevent --workers=9 --worker-connections=1000 -b 0.0.0.0:8003
