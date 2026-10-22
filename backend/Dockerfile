FROM python:3.12.10-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.lock.txt .
RUN pip install --no-cache-dir -r requirements.lock.txt && useradd --create-home app
COPY . .
RUN mkdir -p uploads && chown -R app:app /app
USER app
EXPOSE 8000
CMD ["sh","-c","python manage.py migrate --noinput && python manage.py seed_demo && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile -"]
