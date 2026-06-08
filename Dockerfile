FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the engine and API source
COPY src/ src/
COPY apps/__init__.py apps/__init__.py
COPY apps/api/ apps/api/

# Default port (Railway injects $PORT automatically)
ENV PORT=8000
EXPOSE 8000

CMD uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT}
