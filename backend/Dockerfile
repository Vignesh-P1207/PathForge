FROM python:3.11-slim

# Install system deps in one layer, clean up immediately
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first — Docker cache layer: only rebuilds if requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app code last — cache busts only when code changes
COPY app/ ./app/

# No --reload in production: saves CPU, removes filesystem watcher overhead
# Multiple workers: handles concurrent requests without queuing
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--loop", "uvloop", \
     "--http", "httptools", \
     "--no-access-log"]
