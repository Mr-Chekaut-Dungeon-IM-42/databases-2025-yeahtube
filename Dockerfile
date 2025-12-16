FROM ghcr.io/astral-sh/uv:0.7.12-python3.11-alpine AS base

WORKDIR /app

ENV UV_LINK_MODE=copy
ENV PYTHON_UNBUFFERED=1

RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev --locked

COPY . .

CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0"]
