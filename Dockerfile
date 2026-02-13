# ============================================================================
# BrowserOS KB Research - Multi-stage Dockerfile
# ============================================================================
# Supports multiple deployment modes: local, docker, with various agent types
# ============================================================================

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# ============================================================================
# Dependencies stage
# ============================================================================
FROM base as dependencies

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional packages for SDK support
RUN pip install --no-cache-dir \
    ollama \
    openai \
    PyGithub \
    pyyaml \
    python-dotenv

# ============================================================================
# Development stage
# ============================================================================
FROM dependencies as development

# Copy application code
COPY . .

# Set up Git for development
RUN git config --global user.name "BrowserOS KB Bot" && \
    git config --global user.email "kb-bot@browseros-guides.local"

# Expose ports for debugging
EXPOSE 8000 5678

# Development entrypoint
CMD ["python", "scripts/research_pipeline.py"]

# ============================================================================
# Production stage
# ============================================================================
FROM base as production

# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY scripts/ /app/scripts/
COPY BrowserOS/ /app/BrowserOS/
COPY config.yml /app/
COPY requirements.txt /app/

# Create necessary directories
RUN mkdir -p /app/BrowserOS/Research/raw /app/logs

# Set up Git
RUN git config --global user.name "BrowserOS KB Bot" && \
    git config --global user.email "kb-bot@browseros-guides.local"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run as non-root user for security
RUN useradd -m -u 1000 kbuser && \
    chown -R kbuser:kbuser /app
USER kbuser

# Production entrypoint
CMD ["python", "scripts/research_pipeline.py"]

# ============================================================================
# MCP Server stage
# ============================================================================
FROM node:18-slim as mcp-server

WORKDIR /app

# Copy package.json and install dependencies (currently only built-in modules)
COPY package.json ./
COPY server/ ./server/

# Install any future npm dependencies
# RUN npm install --production

# Create necessary directories
RUN mkdir -p /app/BrowserOS /app/logs

EXPOSE 3100

# Run MCP server
CMD ["node", "server/mcp-server.js"]
