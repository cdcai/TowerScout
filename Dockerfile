# syntax=docker/dockerfile:1

FROM node:18-bookworm-slim AS frontend

WORKDIR /src
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY webapp/build.js webapp/build.js
COPY webapp/js webapp/js
RUN npm run build


FROM python:3.11-slim-bookworm AS runtime

ARG PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cpu

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    TOWERSCOUT_LAZY_MODEL_INIT=1 \
    TOWERSCOUT_STARTUP_PRELOAD=0 \
    YOLO_CONFIG_DIR=/app/webapp/cache/ultralytics \
    TOWERSCOUT_VERSION=container-local

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gdal-bin \
        libgdal-dev \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY webapp/requirements.txt webapp/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir \
        torch==2.2.1 \
        torchvision==0.17.1 \
        --index-url "${PYTORCH_INDEX_URL}" \
    && grep -Ev '^(torch|torchvision)==' webapp/requirements.txt > /tmp/requirements-runtime.txt \
    && python -m pip install --no-cache-dir -r /tmp/requirements-runtime.txt \
    && rm /tmp/requirements-runtime.txt

COPY webapp webapp
COPY --from=frontend /src/webapp/js/towerscout.js webapp/js/towerscout.js

WORKDIR /app/webapp

EXPOSE 5000

VOLUME ["/app/webapp/config", "/app/webapp/model_params", "/app/webapp/data", "/app/webapp/logs", "/app/webapp/flask_session", "/app/webapp/temp/session", "/app/webapp/uploads", "/app/webapp/cache"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import json, urllib.request; data=json.load(urllib.request.urlopen('http://127.0.0.1:5000/api/health', timeout=3)); raise SystemExit(0 if data.get('status') == 'ok' else 1)"

CMD ["python", "towerscout.py"]
