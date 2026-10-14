# ---- Stage 1: install Python dependencies into an isolated virtualenv ----
FROM python:3.13-slim AS deps
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
# pip is only needed to build the venv. Its vendored libraries (urllib3, msgpack,
# setuptools metadata) were reported HIGH by Trivy, so pip is removed afterwards.
RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && pip uninstall -y pip

# ---- Stage 2: runtime image (no build tooling, non-root user) ----
FROM python:3.13-slim AS runtime
ARG APP_VERSION=dev
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_VERSION=${APP_VERSION}
LABEL org.opencontainers.image.title="shelflife-backend" \
      org.opencontainers.image.description="ShelfLife pantry tracker - FastAPI backend" \
      org.opencontainers.image.revision="${APP_VERSION}"

# The base image's own pip is not needed at runtime either; removing it shrinks the
# attack surface and keeps the Trivy HIGH/CRITICAL gate meaningful.
RUN python -m pip uninstall -y pip \
 && rm -rf /usr/local/lib/python3.13/ensurepip \
 && groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --home-dir /app --shell /usr/sbin/nologin app
WORKDIR /app
COPY --from=deps /opt/venv /opt/venv
COPY --chown=10001:10001 alembic.ini docker-entrypoint.sh ./
COPY --chown=10001:10001 alembic ./alembic
COPY --chown=10001:10001 app ./app
# Strip CRLF in case the script was checked out on Windows without .gitattributes.
RUN sed -i "s/\r$//" docker-entrypoint.sh && chmod 0555 docker-entrypoint.sh

# Numeric UID so Kubernetes can verify runAsNonRoot.
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=90s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"]
ENTRYPOINT ["./docker-entrypoint.sh"]
