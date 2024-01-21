FROM python:3.9-alpine3.13
LABEL MAINTAINER="Manimaran Panneerselvam"

# Recommended to prevent buffering of console output
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app

EXPOSE 8000

# Modifies build process for development and deployment
ARG DEV=false

RUN python -m venv /py && \
        /py/bin/pip install -U pip && \
        /py/bin/pip install -r /tmp/requirements.txt && \
        if [ $DEV = "true" ]; \
            then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
        fi && \
        rm -rf /tmp && \
        adduser \
                --disabled-password \
                --no-create-home \
                django-user

ENV PATH="/py/bin:$PATH"

USER django-user