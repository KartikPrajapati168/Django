#!/bin/bash

# Install Node.js (for React build)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# System dependencies (OCR)
apt-get update && apt-get install -y tesseract-ocr poppler-utils libpq-dev

# Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# *** Run database migrations ***
python manage.py migrate --noinput

# *** Create superuser (if not exists) ***
python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")
EOF