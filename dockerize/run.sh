#!/bin/sh

# Debug output
set -x

# Exit on error
set -e

if [ "$1" = 'django-apps' ]; then
	shift;
	manage.py migrate
	exec gunicorn "$@"
fi

exec "$@"
