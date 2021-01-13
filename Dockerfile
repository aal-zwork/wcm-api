FROM python:3.8-alpine
RUN apk add tini openssl-dev libffi-dev build-base
RUN pip install pipenv
COPY [ "Pipfile", "Pipfile.lock", "/api/" ]
WORKDIR /api
RUN pipenv sync
COPY src /api
COPY docker/sh/* /
VOLUME [ "/api-etc" ]
ENTRYPOINT [ "tini", "-v", "--" ]
CMD /entrypoint.sh