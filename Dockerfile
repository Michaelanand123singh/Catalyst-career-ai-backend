# Use Python 3.11 slim image for smaller size and better performance
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/career_documents /app/data/vector_db && \
    chown -R app:app /app

# Copy application code
COPY . .

# Set ownership of all files to app user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Create data directories if they don't exist (in case COPY didn't include them)
RUN mkdir -p data/career_documents data/vector_db

# Runtime configuration
ENV PORT=8000
ENV HOST=0.0.0.0
ENV ENVIRONMENT=production

# Expose port (Cloud Run will override this)
EXPOSE 8000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/ping', timeout=10)" || exit 1

# Start the application using run.py
CMD ["python", "run.py"]