#!/bin/bash

# Usage: file_env_opt VAR [DEFAULT]
file_env_opt() {
	local var="$1"
	local fileVar="${var}_FILE"
	local def="${2:-}"
	if [ -z "${!var:-}" ] && [ -z "${!fileVar:-}" ] && [ -z "${def:-}" ]; then
		return 0
	fi
	if [ "${!var:-}" ] && [ "${!fileVar:-}" ]; then
		echo >&2 "error: both $var and $fileVar are set (but are exclusive)"
		exit 1
	fi
	local val="$def"
	if [ "${!var:-}" ]; then
		val="${!var}"
	elif [ "${!fileVar:-}" ]; then
		val="$(< "${!fileVar}")"
	fi
	export "$var"="$val"
	unset "$fileVar"
}

file_env_opt 'BUTLER_API_DJANGO_SECRET_KEY'
file_env_opt 'BUTLER_DB_PASSWORD'

set -x
set -e

if [ -n "$BUTLER_API_GID" -a -n "$APP_USERNAME" -a "$APP_USERNAME" != 'root' ]; then
	groupmod --gid $BUTLER_API_GID $APP_USERNAME
	usermod --gid $BUTLER_API_GID $APP_USERNAME
fi

if [ -n "$BUTLER_API_UID" -a -n "$APP_USERNAME" -a "$APP_USERNAME" != 'root' ]; then
	usermod --uid $BUTLER_API_UID $APP_USERNAME
fi

if [ "$1" = 'django-apps' ]; then
	shift;
	manage.py migrate
	chown -R $APP_USERNAME:$APP_USERNAME /butler-api $BUTLER_HOME $BUTLER_MEDIA
	exec /app-entrypoint.sh gunicorn "$@"
fi

exec "$@"
