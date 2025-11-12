# ----------> Stage 1: Builder <----------
    FROM python:3.11-slim AS builder

    WORKDIR /app
    
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    # Install system dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc curl && \
        rm -rf /var/lib/apt/lists/*
    
    # Copy and install dependencies
    COPY requirements.txt .
    RUN pip install --upgrade pip && \
        pip install --prefix=/install -r requirements.txt --no-cache-dir
    
    # ----------> Stage 2: Runtime <----------
    FROM python:3.11-slim
    
    WORKDIR /app
    RUN apt-get update && apt-get install -y --no-install-recommends curl && \
        rm -rf /var/lib/apt/lists/*
    
    # Copy dependencies
    COPY --from=builder /install /usr/local
    
    # Copy app code only
    COPY app/ ./app/
    COPY config/ ./config/
    
    # Setup logs and non-root user
    RUN useradd -m appuser && mkdir -p /app/logs && \
        chown -R appuser /app && chmod -R 755 /app
    USER appuser
    
    # Healthcheck (optional but good for ECS)
    HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
    
    EXPOSE 8000
    CMD ["uvicorn", "app.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
    