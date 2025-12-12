FROM ghcr.io/astral-sh/uv:0.7.12-python3.11-alpine AS base

ADD . /app
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHON_UNBUFFERED=1

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
 
RUN uv sync --locked

CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0"]
