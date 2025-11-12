# ----------> Stage 1: Builder <----------
FROM python:3.11-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy pre-downloaded wheels and install
COPY wheels/ ./wheels/
COPY requirements.txt .

RUN pip install --no-index --find-links=./wheels -r requirements.txt

# ----------> Stage 2: Runtime <----------
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY app/ ./app/
COPY config/ ./config/

RUN useradd -m appuser && mkdir -p /app/logs && \
    chown -R appuser /app && chmod -R 755 /app
USER appuser

# Healthcheck 
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "app.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
