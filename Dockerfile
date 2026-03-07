FROM python:3.14.2-slim AS builder

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- final image ---
FROM python:3.14.2-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY main.py .
COPY .env.example .

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 4467

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:4467/metrics')"

CMD ["python", "main.py"]
