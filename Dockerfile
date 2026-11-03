FROM node:26-bookworm-slim AS ui
WORKDIR /ui
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm AS dependencies
WORKDIR /app
RUN pip install --no-cache-dir uv==0.11.32
COPY pyproject.toml uv.lock README.md ./
COPY backend/ backend/
RUN uv sync --frozen --no-dev --extra inference --extra parsing --no-editable

FROM python:3.12-slim-bookworm AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 agentbucket \
    && useradd --uid 10001 --gid agentbucket --create-home agentbucket
WORKDIR /app
COPY --from=dependencies /app/.venv /app/.venv
COPY --from=ui /ui/dist /app/ui
COPY examples/demo-data /app/demo-data
RUN mkdir -p /data && chown -R 10001:10001 /data /app
ENV PATH="/app/.venv/bin:$PATH" AB_DATA_DIR=/data AB_UI_DIR=/app/ui \
    AB_DEMO_DIR=/app/demo-data PYTHONUNBUFFERED=1 HOME=/home/agentbucket
USER 10001:10001
VOLUME ["/data"]
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"
CMD ["uvicorn", "agent_bucket.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
