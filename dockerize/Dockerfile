FROM hypriot/rpi-alpine:3.6

MAINTAINER Oleg Kovalenko <monstrenyatko@gmail.com>

RUN apk update && \
    apk add --no-cache python3 py3-openssl openssl && \
    python3 -m ensurepip && \
    rm -rf /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    rm -rf /root/.cache && mkdir -p /root/.cache && \
    rm -rf /tmp/* /var/tmp/* && \
    rm -rf /var/cache/apk/*

RUN buildDeps='build-base mariadb-dev python3-dev'; \
    apk update && \
    apk add --no-cache $buildDeps mariadb-client-libs bash su-exec shadow && \
    \
# mimic gosu
    ln -s /sbin/su-exec /usr/bin/gosu && \
    \
    pip3 install \
    django \
    djangorestframework \
    gunicorn==19.6.0 \
    mysqlclient \
    && \
    apk del $buildDeps && \
    rm -rf /root/.cache && mkdir -p /root/.cache && \
    rm -rf /tmp/* /var/tmp/* /var/cache/apk/*

ENV APP_USERNAME="butler"
RUN addgroup -S $APP_USERNAME && \
    adduser -S -h /butler-api -g $APP_USERNAME -G $APP_USERNAME $APP_USERNAME

COPY dockerize/run.sh /
RUN chmod +x /run.sh

COPY dockerize/app-entrypoint.sh /
RUN chmod +x /app-entrypoint.sh

RUN ln -s /butler-api/src/manage.py /usr/local/bin/manage.py

COPY manage.py /butler-api/src/
COPY butler_api /butler-api/src/butler_api/
COPY auth_manager /butler-api/src/auth_manager/
COPY cert_manager /butler-api/src/cert_manager/
COPY fw_manager /butler-api/src/fw_manager/

VOLUME ["/butler-api/cert", "/butler-api/fw"]

EXPOSE 8000

WORKDIR /butler-api/src/
ENTRYPOINT ["/run.sh"]
CMD ["django-apps", "-b", ":8000", "butler_api.wsgi"]
