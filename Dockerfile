FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

COPY . .
RUN uv sync --locked --no-dev

EXPOSE 8080
CMD ["uv", "run", "--no-dev", "main.py"]
