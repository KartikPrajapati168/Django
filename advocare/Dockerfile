FROM python:3.11-slim

# ============================================================
# SYSTEM DEPENDENCIES
# ============================================================

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-guj \
    poppler-utils \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*


# ============================================================
# PYTHON ENVIRONMENT
# ============================================================

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive


# ============================================================
# WORKING DIRECTORY
# ============================================================

WORKDIR /app


# ============================================================
# INSTALL PYTHON PACKAGES
# ============================================================

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm


# ============================================================
# COPY PROJECT
# ============================================================

COPY . .


# ============================================================
# PORT
# ============================================================

EXPOSE 8000


# ============================================================
# START SERVER
# ============================================================

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn advocare.wsgi:application --bind 0.0.0.0:$PORT"]