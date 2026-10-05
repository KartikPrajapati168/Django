FROM python:3.11-slim

# ============================================================
# Linux dependencies
# ============================================================

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-guj \
    poppler-utils \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*


# ============================================================
# Python environment
# ============================================================

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Start with English OCR.
# Change to eng+guj later if required.
ENV OCR_LANG=eng


# ============================================================
# Application
# ============================================================

WORKDIR /app


COPY requirements.txt .


RUN pip install --upgrade \
    pip \
    setuptools \
    wheel


RUN pip install \
    --no-cache-dir \
    -r requirements.txt


# ============================================================
# Copy project
# ============================================================

COPY . .


# ============================================================
# Port
# ============================================================

EXPOSE 8000


# ============================================================
# Start Django
# ============================================================

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn advocare.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120"]