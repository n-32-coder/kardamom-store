FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBUG=False

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY manage.py .
COPY config/ ./config/
COPY customers/ ./customers/
COPY products/ ./products/
COPY cart/ ./cart/
COPY orders/ ./orders/
COPY kardamom/ ./kardamom/

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Probes hit /healthz; gunicorn serves 3 workers for in-pod concurrency
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60"]
