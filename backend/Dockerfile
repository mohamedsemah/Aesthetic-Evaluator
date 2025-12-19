FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p temp_sessions

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Health check (Railway uses healthcheckPath from railway.json)
# Using port 8000 as default, Railway will override PORT env var at runtime
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
# Note: Using single worker for Railway deployment (workers cause issues with lifespan events)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

