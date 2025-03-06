# syntax = docker/dockerfile:1.2
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
WORKDIR /app

# Install dependencies
RUN uv sync --frozen

# Run the application
CMD ["uv", "run", "python", "main.py"]
