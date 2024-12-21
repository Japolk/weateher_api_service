FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./src /app/src
COPY ./pyproject.toml ./uv.lock /app/

WORKDIR /app
RUN uv sync --frozen --no-cache

CMD ["sh", "-c", "uv run uvicorn src.main:app --host 0.0.0.0 --port 80 --workers 8"]