# 🚀 Universal Deployment Guide

## Overview

This system supports **multiple deployment modes** and **agent connection types** to fit any environment:

- **🌐 Cloud APIs** (HTTP/REST)
- **📦 SDK Libraries** (Python, Node.js)
- **🔌 MCP** (Model Context Protocol)
- **💻 Local** (Self-hosted binaries)
- **🐳 Docker** (Containerized)
- **🔀 Hybrid** (Automatic fallback)

## Quick Start by Mode

### 1. Cloud HTTP Mode (Simplest)

**Best for**: Getting started quickly, GitHub Actions

```bash
# 1. Set API keys
export OLLAMA_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"
export GITHUB_TOKEN="your-token"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python scripts/research_pipeline.py
```

**Configuration**: Uses HTTP APIs, no local setup needed.

---

### 2. Docker Mode (Recommended for Production)

**Best for**: Production, consistent environments, local LLMs

```bash
# 1. Copy environment template
cp .env.template .env

# 2. Edit .env with your keys
nano .env

# 3. Start services
docker-compose up -d

# 4. View logs
docker-compose logs -f research

# 5. Run manual update
docker-compose exec research python scripts/research_pipeline.py
```

**Includes**:
- Research application
- Local Ollama service
- Optional MCP server

---

### 3. SDK Mode (For Developers)

**Best for**: Custom integrations, programmatic access

```bash
# 1. Install SDKs
pip install ollama openai PyGithub

# 2. Configure mode
export AGENT_MODE=sdk
export OLLAMA_MODE=sdk
export OPENROUTER_MODE=sdk

# 3. Configure SDK settings in config.yml

# 4. Run
python scripts/research_pipeline.py
```

**Advantages**:
- Native Python objects
- Better error handling
- Type hints and IDE support

---

### 4. MCP Mode (Model Context Protocol)

**Best for**: MCP-compatible tools, standardized interfaces

```bash
# 1. Start MCP server
docker-compose --profile mcp up -d

# 2. Configure MCP in config.yml
AGENT_MODE=mcp

# 3. Run with MCP connection
python scripts/research_pipeline.py
```

**Features**:
- Standardized protocol
- Tool discovery
- Resource management
- Multiple transports (stdio, HTTP, WebSocket)

---

### 5. Local Binary Mode

**Best for**: Self-hosted, air-gapped environments

```bash
# 1. Install Ollama locally
curl https://ollama.ai/install.sh | sh

# 2. Start Ollama service
ollama serve &

# 3. Pull models
ollama pull llama2
ollama pull codellama

# 4. Configure local mode
export AGENT_MODE=local
export OLLAMA_MODE=local

# 5. Run
python scripts/research_pipeline.py
```

**Benefits**:
- No external dependencies
- Complete privacy
- No API costs

---

### 6. Hybrid Mode (Automatic - Recommended)

**Best for**: Maximum flexibility, automatic fallback

```bash
# 1. Set all available options
export AGENT_MODE=hybrid
export OLLAMA_API_KEY="your-key"  # Optional
export OPENROUTER_API_KEY="your-key"  # Optional

# 2. System auto-selects best available method
python scripts/research_pipeline.py
```

**How it works**:
1. Tries HTTP API (if keys provided)
2. Falls back to SDK (if installed)
3. Falls back to MCP (if server running)
4. Falls back to Docker (if containers running)
5. Falls back to local (if binary available)

---

## Configuration Files

### config.yml (Main Configuration)

Comprehensive configuration file with all options:

```yaml
AGENT_MODE: "hybrid"

OLLAMA:
  enabled: true
  mode: "http"  # http, sdk, mcp, docker, local
  http:
    base_url: "https://api.ollama.ai/v1"
    api_key_env: "OLLAMA_API_KEY"
  # ... more options

OPENROUTER:
  enabled: true
  mode: "http"
  # ... more options
```

**Edit this file** to customize:
- Connection methods
- Model selection
- Timeouts and retries
- Performance tuning
- Feature flags

### .env (Environment Variables)

Secret keys and environment-specific settings:

```bash
# Copy template
cp .env.template .env

# Edit with your values
nano .env
```

**Never commit** `.env` to version control!

---

## Deployment Scenarios

### Scenario 1: GitHub Actions (Cloud APIs)

**Setup**:
1. Add secrets to GitHub repository
2. Workflow uses HTTP mode automatically
3. No local setup needed

**Secrets required**:
- `OLLAMA_API_KEY`
- `OPENROUTER_API_KEY`

**Cost**: ~$2-7/month

---

### Scenario 2: Local Development (SDK)

**Setup**:
```bash
pip install -r requirements.txt
pip install ollama openai
export AGENT_MODE=sdk
python scripts/research_pipeline.py
```

**Cost**: Free (if using local Ollama)

---

### Scenario 3: Production Server (Docker)

**Setup**:
```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# With GPU support
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

**Benefits**:
- Isolated environment
- Easy scaling
- Persistent storage
- Health checks

---

### Scenario 4: Air-Gapped Environment

**Setup**:
1. Install Ollama locally
2. Download models offline
3. Use local mode
4. No internet required

```bash
# Offline setup
AGENT_MODE=local
OLLAMA_MODE=local
OPENROUTER_MODE=disabled
python scripts/research_pipeline.py
```

---

## Connection Type Comparison

| Feature | HTTP | SDK | MCP | Docker | Local |
|---------|------|-----|-----|--------|-------|
| **Setup** | Easy | Medium | Complex | Easy | Medium |
| **Dependencies** | Minimal | Libraries | Server | Docker | Binary |
| **Performance** | Good | Better | Good | Good | Best |
| **Privacy** | Cloud | Cloud | Depends | Local | Local |
| **Cost** | API fees | API fees | Depends | Free | Free |
| **Flexibility** | Medium | High | High | High | Medium |
| **Best for** | Quick start | Development | Standards | Production | Self-hosted |

---

## Advanced Configuration

### Custom Model Selection

Edit `config.yml`:

```yaml
OPENROUTER:
  models:
    primary: "anthropic/claude-3-opus"      # Best quality
    fallback: "openai/gpt-4-turbo"          # If primary fails
    budget: "meta-llama/llama-3-8b-instruct"  # Cost-effective
```

### Multi-Model Ensemble

Enable experimental ensemble mode:

```yaml
EXPERIMENTAL:
  ensemble_analysis:
    enabled: true
    models:
      - "anthropic/claude-3-sonnet"
      - "openai/gpt-4-turbo"
      - "meta-llama/llama-3-70b"
    voting_strategy: "majority"
```

### Rate Limiting

Control request rates:

```yaml
HTTP:
  rate_limit:
    enabled: true
    requests_per_second: 10
    burst: 20
```

### Caching

Aggressive caching for cost savings:

```yaml
PERFORMANCE:
  cache:
    enabled: true
    backend: "redis"  # or "memory", "file"
    ttl: 3600
```

---

## Monitoring & Debugging

### View Logs

```bash
# Application logs
tail -f logs/research_pipeline.log

# Docker logs
docker-compose logs -f research

# Docker Ollama logs
docker-compose logs -f ollama
```

### Enable Debug Mode

```bash
export LOG_LEVEL=DEBUG
python scripts/research_pipeline.py
```

### Check Agent Availability

```python
from scripts.agent_connectors import create_agent_connector

ollama = create_agent_connector("ollama")
print(f"Ollama available: {ollama.is_available()}")

openrouter = create_agent_connector("openrouter")
print(f"OpenRouter available: {openrouter.is_available()}")
```

---

## Troubleshooting

### Issue: "No available connector"

**Cause**: No connection method working

**Solutions**:
1. Check API keys are set
2. Verify service is running (Docker/local)
3. Test network connectivity
4. Enable hybrid mode for automatic fallback

### Issue: "Import Error: ollama not found"

**Cause**: SDK not installed

**Solution**:
```bash
pip install ollama openai
```

### Issue: Docker container won't start

**Cause**: Port already in use

**Solution**:
```bash
# Check what's using port 11434
lsof -i :11434

# Change port in docker-compose.yml
ports:
  - "11435:11434"
```

### Issue: Rate limited

**Cause**: Too many API requests

**Solution**:
```yaml
# config.yml
HTTP:
  rate_limit:
    enabled: true
    requests_per_second: 5  # Reduce
```

---

## Security Best Practices

### 1. API Key Management

```bash
# Use environment variables
export OLLAMA_API_KEY="$(cat ~/.secrets/ollama_key)"

# Or use secret management
# - AWS Secrets Manager
# - Azure Key Vault
# - HashiCorp Vault
```

### 2. Docker Security

```yaml
# docker-compose.yml
services:
  research:
    user: "1000:1000"  # Non-root user
    read_only: true    # Read-only filesystem
    security_opt:
      - no-new-privileges:true
```

### 3. Network Isolation

```yaml
networks:
  browseros-network:
    internal: true  # No external access
```

---

## Performance Optimization

### 1. Parallel Processing

```yaml
PERFORMANCE:
  max_workers: 10
  batch:
    enabled: true
    size: 20
```

### 2. Model Selection Strategy

```yaml
COST:
  model_selection:
    strategy: "cost_aware"
    prefer_local: true  # Use local Ollama when possible
```

### 3. Aggressive Caching

```yaml
RESEARCH:
  sources:
    cache_duration_days: 14  # Longer cache
```

---

## Support

- **Documentation**: See individual mode guides
- **Issues**: [GitHub Issues](https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/issues)
- **Config Help**: Review `config.yml` comments
- **Docker Help**: See `docker-compose.yml` examples

---

## Summary

Choose your deployment mode based on needs:

- **Quick Start** → HTTP mode
- **Production** → Docker mode
- **Development** → SDK mode
- **Standards** → MCP mode
- **Privacy** → Local mode
- **Flexible** → Hybrid mode

All modes work with the same codebase - just change configuration!
