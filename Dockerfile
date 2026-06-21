FROM python:3.12-slim

# Bring in the uv binary (pinned image tag for reproducibility)
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

WORKDIR /app

# Install ONLY the locked dependencies (not the project itself).
# --frozen: use uv.lock as-is, never re-resolve.
# --no-dev: skip the dev/test/docs/security groups.
# --no-install-project: don't build/install qforge — it has no .git in the image
#   (setuptools_scm would fail), and the app runs from the copied source below.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy the engine and API source (imported from the /app working directory)
COPY src/ src/
COPY apps/__init__.py apps/__init__.py
COPY apps/api/ apps/api/

# Put the venv on PATH so `uvicorn` resolves without `uv run`
ENV PATH="/app/.venv/bin:$PATH"

# Default port (Railway injects $PORT automatically)
ENV PORT=8000
EXPOSE 8000

# Shell form is intentional so ${PORT} is expanded at runtime
CMD uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT}
