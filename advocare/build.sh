#!/bin/bash

# Install Node.js (needed for React build)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# System dependencies install karo (OCR ke liye)
apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libpq-dev

# Python dependencies install karo
pip install -r requirements.txt

# React frontend build karo
cd frontend
npm install
npm run build
cd ..

# Django static files collect karo
python manage.py collectstatic --noinput

# Database migrations (pehle run nahi karenge, baad mein manually karenge)
# python manage.py migrate