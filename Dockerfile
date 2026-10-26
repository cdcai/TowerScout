# syntax=docker/dockerfile:1

FROM node:22-bookworm-slim@sha256:de170b39439eb0e5a3444ad7d60b015614a381e10fecae2e30ec9e735122f38d AS frontend

WORKDIR /src
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates=20250419~deb12u2 \
    && rm -rf /var/lib/apt/lists/*
COPY package.json package-lock.json ./
RUN NODE_OPTIONS=--use-openssl-ca npm ci --ignore-scripts
COPY webapp/build.js webapp/build.js
COPY webapp/js webapp/js
RUN npm run build


FROM python:3.11-slim-bookworm@sha256:f06d01d4ba3f8ad5af45a3ec87df19c1d317d8e8961edc0fabda61811af6f7cf AS runtime

ARG PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cpu
ARG TOWERSCOUT_PYTORCH_FLAVOR=cpu
ARG TOWERSCOUT_TORCH_VERSION=2.10.0
ARG TOWERSCOUT_TORCHVISION_VERSION=0.25.0
ARG TOWERSCOUT_RELEASE_VERSION=container-local
ARG TOWERSCOUT_SOURCE_REF=unknown

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    TOWERSCOUT_LAZY_MODEL_INIT=1 \
    TOWERSCOUT_STARTUP_PRELOAD=0 \
    TOWERSCOUT_PYTORCH_FLAVOR=${TOWERSCOUT_PYTORCH_FLAVOR} \
    YOLO_CONFIG_DIR=/app/webapp/cache/ultralytics \
    TOWERSCOUT_VERSION=${TOWERSCOUT_RELEASE_VERSION}

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates=20250419~deb12u2 \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY webapp/requirements.txt webapp/requirements.txt
COPY scripts/bootstrap-pip.py scripts/bootstrap-pip.py
RUN --mount=type=secret,id=towerscout_build_ca,required=false \
    if [ -f /run/secrets/towerscout_build_ca ]; then \
        export PIP_CERT=/run/secrets/towerscout_build_ca; \
    fi \
    && python scripts/bootstrap-pip.py \
    && python -m pip install --no-cache-dir \
        "torch==${TOWERSCOUT_TORCH_VERSION}" \
        "torchvision==${TOWERSCOUT_TORCHVISION_VERSION}" \
        --index-url "${PYTORCH_INDEX_URL}" \
    && grep -Ev '^(torch|torchvision)==' webapp/requirements.txt > /tmp/requirements-runtime.txt \
    && python -m pip install --no-cache-dir -r /tmp/requirements-runtime.txt \
    && rm /tmp/requirements-runtime.txt

COPY webapp webapp
COPY docs docs
COPY --from=frontend /src/webapp/js/towerscout.js webapp/js/towerscout.js
COPY LICENSE NOTICE THIRD_PARTY_NOTICES.md MODEL_LICENSES.md DATA_LICENSES.md PROVIDER_TERMS.md SOURCE.txt SBOM.txt release-manifest.v1.json ./
COPY licenses licenses
COPY scripts/write-source-notice.py scripts/write-source-notice.py
RUN python scripts/write-source-notice.py --source-ref "${TOWERSCOUT_SOURCE_REF}" --output SOURCE.txt

LABEL org.opencontainers.image.title="TowerScout" \
    org.opencontainers.image.source="https://github.com/cdcai/TowerScout" \
    org.opencontainers.image.description="TowerScout agpl-yolo runtime image; release-specific metadata is authoritative in the release control ZIP." \
    org.opencontainers.image.version="${TOWERSCOUT_RELEASE_VERSION}" \
    org.opencontainers.image.revision="${TOWERSCOUT_SOURCE_REF}" \
    org.opencontainers.image.licenses="LicenseRef-TowerScout-agpl-yolo" \
    org.towerscout.pytorch.flavor="${TOWERSCOUT_PYTORCH_FLAVOR}"

WORKDIR /app/webapp

EXPOSE 5000

VOLUME ["/app/webapp/config", "/app/webapp/model_params", "/app/webapp/data", "/app/webapp/logs", "/app/webapp/flask_session", "/app/webapp/temp/session", "/app/webapp/uploads", "/app/webapp/cache"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import json, urllib.request; data=json.load(urllib.request.urlopen('http://127.0.0.1:5000/api/health', timeout=3)); raise SystemExit(0 if data.get('status') == 'ok' else 1)"

CMD ["python", "towerscout.py"]
