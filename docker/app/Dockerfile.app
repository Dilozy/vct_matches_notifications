FROM python:3.11.14-alpine3.22

ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

RUN python -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry

ENV PATH="${PATH}:${POETRY_VENV}/bin"

RUN apk update && apk add --no-cache bash

WORKDIR /app
ENV PYTHONPATH=/app

COPY pyproject.toml poetry.lock ./
COPY docker/app docker/
COPY docker/wait-for-it.sh docker/
COPY docker/entrypoint_app.sh docker/

RUN poetry install --no-root --no-interaction --no-ansi
RUN chmod +x docker/entrypoint_app.sh
RUN sed -i 's/\r$//' docker/entrypoint_app.sh docker/wait-for-it.sh

WORKDIR /app/src

COPY src/common .
COPY src/services .
COPY src/__init__.py .
COPY src/init_data.py .
COPY src/main.py .

WORKDIR /

ENTRYPOINT [ "/bin/sh", "docker/entrypoint_app.sh" ]