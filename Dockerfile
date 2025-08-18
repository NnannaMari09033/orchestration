# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything (manage.py + taskverse package)
COPY . /app/

# Prevent Python buffering
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
