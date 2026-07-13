# --- Base image ---
FROM python:3.13-slim

# Install uv (fast package manager you already use locally)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# System deps that some ML/LLM libs need at build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Install Python deps first (layer caching) ---
# Build context here is the backend/ folder itself, so these paths
# are relative to backend/, not the repo root.
COPY pyproject.toml uv.lock* /app/

RUN uv sync --frozen --no-dev --no-install-project

# --- Copy the rest of the backend source ---
COPY . /app/

# Install the project itself now that source is present
RUN uv sync --frozen --no-dev

# Fly.io / Railway both expect the app to listen on $PORT
ENV PORT=8000
EXPOSE 8000

# app.py holds the real FastAPI instance (main.py is a dummy/runner),
# so we target app:app here.
CMD ["sh", "-c", "uv run uvicorn app:app --host 0.0.0.0 --port ${PORT} --no-access-log"]