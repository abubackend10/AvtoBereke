#!/usr/bin/env bash
set -euo pipefail

media_root="${MEDIA_ROOT:-/var/data}"
mkdir -p "$media_root"

if [ -d "back_media" ]; then
    cp -an back_media/. "$media_root/"
fi

exec gunicorn --config gunicorn.conf.py core.wsgi:application
