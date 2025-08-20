FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything (manage.py + taskverse package)
COPY . /app/

# Prevent Python buffering
ENV PYTHONUNBUFFERED=1

# Use entrypoint to wait for deps and run migrations; command overridden by compose
ENTRYPOINT ["/bin/bash", "/app/taskverse/settings/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
