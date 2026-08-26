# ==============================================================================
# PersuAId MCP Server — Production Dockerfile for Coolify Deployment
# Multi-stage build with non-root security context and health check
# ==============================================================================

# Stage 1: Build & Dependency Resolution
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-server.txt .
RUN pip install --no-cache-dir --user -r requirements-server.txt

# ------------------------------------------------------------------------------
# Stage 2: Final Minimal Runtime Image
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS runner

WORKDIR /app

# Install curl for container health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local

# Ensure local user binaries are on PATH
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0

# Create non-root system user and app group
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser && \
    mkdir -p /app/data /home/appuser/.persuaid && \
    chown -R appuser:appgroup /app /home/appuser/.persuaid && \
    cp -r /root/.local /home/appuser/.local && \
    chown -R appuser:appgroup /home/appuser/.local

# Copy application source code
COPY --chown=appuser:appgroup engine/ /app/engine/
COPY --chown=appuser:appgroup scripts/ /app/scripts/
COPY --chown=appuser:appgroup references/ /app/references/
COPY --chown=appuser:appgroup SKILL.md /app/SKILL.md

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH \
    HOME=/home/appuser

# Expose internal listening port for Coolify / Traefik
EXPOSE 8000

# Docker healthcheck
HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the MCP HTTP & SSE server in foreground
CMD ["python3", "-m", "engine.mcp_http_server"]
