#!/usr/bin/env sh

export PYTHONPATH=/api:$PYTHONPATH
pipenv run python bin/wcm-server.py --config /api-etc/wcm.yaml