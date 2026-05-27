FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev deps in production)
RUN uv sync --frozen --no-dev

# Copy source code
COPY actions/ ./actions/

# Create logs directory
RUN mkdir -p logs

EXPOSE 5055

# Run action server
CMD ["uv", "run", "uvicorn", "actions.server:app", "--host", "0.0.0.0", "--port", "5055"]
