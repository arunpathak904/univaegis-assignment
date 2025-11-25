# backend/Dockerfile

FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# System dependencies (for Postgres, Tesseract, Poppler, Pillow, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy project files
COPY univaegis-backend/ /app/

# Collect static files (we’ll run this in entrypoint or docker-compose if needed)
# But safe to keep here for basic builds (won't break if no static apps yet)
RUN python manage.py collectstatic --noinput || echo "collectstatic failed (maybe no static files yet)."

# Expose port 8080 inside container
EXPOSE 8080

# Start gunicorn on port 8080
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3"]
