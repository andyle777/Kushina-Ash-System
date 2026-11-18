FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Resolve and install dependencies at image build time.
COPY pyproject.toml ./
RUN uv sync

# Application code.
COPY worker.py ./
COPY app ./app

# The image must start the worker itself: no entrypoint setting exists.
CMD ["uv", "run", "--no-sync", "python", "worker.py"]
