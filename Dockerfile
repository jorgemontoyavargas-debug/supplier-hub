FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN addgroup --system supplierhub && adduser --system --ingroup supplierhub supplierhub

COPY requirements.txt requirements-production.txt ./
RUN pip install --no-cache-dir -r requirements-production.txt

COPY . .
RUN mkdir -p /app/media /app/staticfiles && \
    chmod +x /app/scripts/docker-entrypoint.sh && \
    chown -R supplierhub:supplierhub /app

USER supplierhub

EXPOSE 8000
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "120"]
