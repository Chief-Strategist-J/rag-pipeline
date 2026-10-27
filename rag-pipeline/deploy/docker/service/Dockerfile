# syntax=docker/dockerfile:1.7

# ------------------------------------------------------------------------------
# Stage 1: Builder (Compilers and build dependencies live strictly here)
# ------------------------------------------------------------------------------
FROM python:3.11-slim@sha256:ae952e0a57138a4317b9b61caaa19a8217c2f356803f8d7e63aad08769950937 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=0

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml README.md ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install .

# ------------------------------------------------------------------------------
# Stage 2: Runtime (Hardened, minimal attack surface, non-root, tini supervisor)
# ------------------------------------------------------------------------------
FROM python:3.11-slim@sha256:ae952e0a57138a4317b9b61caaa19a8217c2f356803f8d7e63aad08769950937 AS runtime

LABEL org.opencontainers.image.title="rag-pipeline-service" \
      org.opencontainers.image.description="Stateless Query and Delivery Pod for RAG Pipeline" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.authors="Jaydeep Vagh <jaydeep.9664920749@gmail.com>" \
      org.opencontainers.image.vendor="Chief-Strategist-J"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    LANG=C.UTF-8 \
    TZ=UTC \
    HOME=/tmp

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    tzdata \
    tini \
    && rm -rf /var/lib/apt/lists/*

ARG APP_UID=10001
ARG APP_GID=10001

RUN groupadd --gid ${APP_GID} appgroup && \
    useradd  --uid ${APP_UID} --gid ${APP_GID} --no-create-home --shell /usr/sbin/nologin appuser && \
    mkdir -p /app && chown ${APP_UID}:${APP_GID} /app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=${APP_UID}:${APP_GID} config/ /app/config/
COPY --chown=${APP_UID}:${APP_GID} src/ /app/src/

USER ${APP_UID}:${APP_GID}

EXPOSE 8000

STOPSIGNAL SIGTERM

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-graceful-shutdown", "30"]
