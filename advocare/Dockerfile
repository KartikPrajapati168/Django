# Use a Python image that includes build tools
FROM python:3.11-slim

# Install system dependencies (Tesseract, poppler, postgres client)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (React build must exist locally)
RUN python manage.py collectstatic --noinput

# Run migrations and create superuser
RUN python manage.py migrate --noinput || true
RUN python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" || true

# Expose port
EXPOSE 8000

# Start command
CMD ["gunicorn", "advocare.wsgi:application", "--bind", "0.0.0.0:8000"]