# Local Workflow Automation - GitHub Actions Translation

This document explains how GitHub Actions workflows translate to local installation equivalents, ensuring users can run the same automation regardless of deployment method (Docker, local service, or manual execution).

## Architecture Overview

```
GitHub Actions (Cloud)          Local Installation (Your Machine)
━━━━━━━━━━━━━━━━━━━━          ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                
Scheduled Workflows    ──→      run.sh Menu Options + Cron Jobs
API Keys from Secrets  ──→      .env File + Environment Variables
Python Scripts         ──→      Same scripts/workflow_generator.py
Auto-commits           ──→      Manual or scheduled git commits
Issue Creation         ──→      Local reports + optional webhooks
```

## Complete Workflow Translation Guide

### 1. Weekly KB Update (update-kb.yml)

**GitHub Actions:**
```yaml
# Runs: Every Sunday 00:00 UTC
# Uses: OLLAMA_API_KEY, OPENROUTER_API_KEY, GITHUB_TOKEN
schedule:
  - cron: '0 0 * * 0'
```

**Local Equivalent:**

**Option A: Menu-driven (Interactive)**
```bash
./run.sh
# Select option 2: "Update Knowledge Base (research pipeline)"
```

**Option B: Direct command**
```bash
# Set API keys in environment
export OLLAMA_API_KEY="your-key-here"
export OPENROUTER_API_KEY="your-key-here"

# Run the same script GitHub Actions uses
python scripts/research_pipeline.py
python scripts/enhance_sources.py --update
python scripts/generate_library.py
python scripts/validate_kb.py
```

**Option C: Automated with cron (Linux/macOS)**
```bash
# Add to crontab: crontab -e
0 0 * * 0 cd /path/to/BrowserOS_Guides && ./scripts/local_kb_update.sh
```

Create `scripts/local_kb_update.sh`:
```bash
#!/bin/bash
source .env  # Load API keys
cd "$(dirname "$0")/.."
python scripts/research_pipeline.py
python scripts/enhance_sources.py --update
python scripts/generate_library.py
python scripts/validate_kb.py
git add -A
git commit -m "🤖 Auto-update: KB refresh $(date +%Y-%m-%d)" || true
```

**Option D: Automated with Task Scheduler (Windows)**
```powershell
# Run update_kb.ps1 weekly
# Task Scheduler → Create Basic Task → Weekly Sunday 00:00
# Action: Start a program
# Program: powershell.exe
# Arguments: -File "C:\path\to\BrowserOS_Guides\update_kb.ps1"
```

---

### 2. AI Workflow Generation (update-kb.yml lines 100-112)

**GitHub Actions:**
```yaml
# Runs: Weekly with KB update
# Generates: New workflow ideas using Kimi-K2.5:cloud
python scripts/workflow_generator.py full \
  --use-case "emerging automation needs" \
  --complexity "medium" \
  --output-dir "BrowserOS/Workflows/Community-Contributed/generated-$(date +%Y-%m-%d)"
```

**Local Equivalents:**

**Option A: Web Interface (New! - This PR)**
```bash
# Start MCP server
./run.sh
# Select option 1: "Start MCP Server (Port 3100)"

# Open browser
# Navigate to: file:///path/to/BrowserOS_Guides/docs/index.html#tools
# OR: http://localhost:8080/#tools (if serving docs)
# Fill form, click "Generate My Workflow"
```

**Option B: CLI Menu (Interactive)**
```bash
./run.sh
# Select option 8: "Generate Workflow"
# Enter your workflow description when prompted
```

**Option C: Direct command**
```bash
export OLLAMA_API_KEY="your-key-here"

# Full generation (idea → implementation → validation)
python scripts/workflow_generator.py full \
  --use-case "automated invoice processing from Gmail" \
  --industry "finance" \
  --complexity "medium" \
  --output-dir "BrowserOS/Workflows/Custom"

# Or individual stages
python scripts/workflow_generator.py idea --use-case "your use case"
python scripts/workflow_generator.py implement --use-case "your use case"
python scripts/workflow_generator.py validate --workflow-file "path/to/workflow.json"
```

**Option D: Programmatic API**
```bash
# Start MCP server (once)
npm run mcp-server

# Call from any language
curl -X POST http://localhost:3100/api/generate-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "use_case": "monitor competitor prices and alert on changes",
    "industry": "e-commerce",
    "complexity": "medium"
  }'
```

---

### 3. Self-Test Validation (self-test.yml)

**GitHub Actions:**
```yaml
# Runs: Every Sunday 02:00 UTC (after KB update)
# Uses: OLLAMA_API_KEY, OPENROUTER_API_KEY
schedule:
  - cron: '0 2 * * 0'
```

**Local Equivalents:**

**Option A: Menu-driven**
```bash
./run.sh
# Select option 3: "Run Self-Test"
```

**Option B: Direct command**
```bash
export OLLAMA_API_KEY="your-key-here"
export OPENROUTER_API_KEY="your-key-here"
python scripts/self_test.py
```

**Option C: Automated with cron**
```bash
# Add to crontab: crontab -e
0 2 * * 0 cd /path/to/BrowserOS_Guides && source .env && python scripts/self_test.py
```

---

### 4. WhatsApp Integration Monitor (whatsapp-monitor.yml)

**GitHub Actions:**
```yaml
# Runs: Daily 00:00 UTC
# Monitors: 3 BrowserOS repos for WhatsApp integration keywords
schedule:
  - cron: '0 0 * * *'
```

**Local Equivalents:**

**Option A: Menu-driven**
```bash
./run.sh
# Select option 5: "Monitor WhatsApp Integration"
```

**Option B: Direct command**
```bash
export GITHUB_TOKEN="your-pat-here"
python scripts/monitor_whatsapp.py
# Output: WHATSAPP_WATCH_REPORT.md
```

**Option C: Automated with cron (daily)**
```bash
# Add to crontab: crontab -e
0 0 * * * cd /path/to/BrowserOS_Guides && source .env && python scripts/monitor_whatsapp.py
```

---

### 5. MCP Server (Local Only - No GitHub Equivalent)

**Local Usage:**

**Option A: Menu-driven**
```bash
./run.sh
# Select option 1: "Start MCP Server (Port 3100)"
```

**Option B: Direct command**
```bash
# Node.js version
npm run mcp-server

# Or with custom port
MCP_SERVER_PORT=3100 node server/mcp-server.js
```

**Option C: Docker**
```bash
docker-compose up browseros-guides-mcp
# Server runs on http://localhost:3100/mcp
```

**Option D: As system service (Linux)**
```bash
# Create /etc/systemd/system/browseros-mcp.service
[Unit]
Description=BrowserOS Guides MCP Server
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/BrowserOS_Guides
Environment="MCP_SERVER_PORT=3100"
Environment="OLLAMA_API_KEY=your-key"
ExecStart=/usr/bin/node /path/to/BrowserOS_Guides/server/mcp-server.js
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable browseros-mcp
sudo systemctl start browseros-mcp
```

---

## Configuration Matrix

### API Keys Setup

| Method | GitHub Actions | Local Installation |
|--------|----------------|-------------------|
| **Source** | Organization/Repository Secrets | `.env` file or environment variables |
| **Access** | `${{ secrets.OLLAMA_API_KEY }}` | `export OLLAMA_API_KEY="..."` or loaded from `.env` |
| **Scope** | All workflows in repo | Current shell session or system-wide |

**Local Setup Steps:**
```bash
# 1. Copy template
cp .env.template .env

# 2. Edit with your keys
nano .env
# OR use setup wizard
./run.sh → Option D: "Configure Settings"

# 3. Load in shell
source .env

# 4. Verify
echo $OLLAMA_API_KEY
```

### Cross-Platform Support

| Platform | Menu Script | Automation | Service |
|----------|-------------|------------|---------|
| **Linux** | `./run.sh` | cron | systemd |
| **macOS** | `./run.sh` | cron | launchd |
| **Windows** | `run.bat` | Task Scheduler | NSSM/sc.exe |
| **Docker** | N/A | compose + cron in container | container auto-restart |

---

## Complete Local Automation Setup

### Full Automation (Replicates ALL GitHub Actions Locally)

**Linux/macOS:**
```bash
# 1. Install repository
git clone https://github.com/Grumpified-OGGVCT/BrowserOS_Guides.git
cd BrowserOS_Guides
./install.sh

# 2. Configure API keys
cp .env.template .env
# Edit .env with your keys

# 3. Set up weekly KB update
crontab -e
# Add:
0 0 * * 0 cd /path/to/BrowserOS_Guides && source .env && ./scripts/local_kb_update.sh

# 4. Set up daily monitoring
# Add to same crontab:
0 0 * * * cd /path/to/BrowserOS_Guides && source .env && python scripts/monitor_whatsapp.py

# 5. Set up MCP server as service
sudo cp scripts/browseros-mcp.service /etc/systemd/system/
sudo systemctl enable browseros-mcp
sudo systemctl start browseros-mcp

# 6. Test everything
./run.sh → Option 3: "Run Self-Test"
```

**Windows:**
```powershell
# 1. Install repository
git clone https://github.com/Grumpified-OGGVCT/BrowserOS_Guides.git
cd BrowserOS_Guides
.\install.bat

# 2. Configure API keys
copy .env.template .env
# Edit .env with your keys

# 3. Set up weekly KB update
# Task Scheduler → Create Basic Task
# Name: BrowserOS KB Update
# Trigger: Weekly, Sunday 00:00
# Action: Start a program
#   Program: powershell.exe
#   Arguments: -File "C:\path\to\BrowserOS_Guides\update_kb.ps1"

# 4. Set up daily monitoring (similar task)

# 5. Set up MCP server as Windows Service
# Using NSSM (Non-Sucking Service Manager)
nssm install BrowserOSMCP "C:\Program Files\nodejs\node.exe"
nssm set BrowserOSMCP AppDirectory "C:\path\to\BrowserOS_Guides"
nssm set BrowserOSMCP AppParameters "server\mcp-server.js"
nssm set BrowserOSMCP AppEnvironmentExtra "MCP_SERVER_PORT=3100" "OLLAMA_API_KEY=your-key"
nssm start BrowserOSMCP
```

**Docker (All Platforms):**
```bash
# 1. Clone repository
git clone https://github.com/Grumpified-OGGVCT/BrowserOS_Guides.git
cd BrowserOS_Guides

# 2. Configure environment
cp .env.template .env
# Edit .env with your keys

# 3. Start all services
docker-compose --profile full up -d

# 4. Services running:
# - MCP Server: http://localhost:3100
# - Docs: http://localhost:8080
# - Cron jobs inside container handle automation

# 5. View logs
docker-compose logs -f browseros-guides-mcp

# 6. Manual workflow generation
docker-compose exec browseros-guides-mcp python scripts/workflow_generator.py full --use-case "test"
```

---

## Workflow Generator - All Access Methods

### 1. Web Interface (NEW - This PR)

**Start server:**
```bash
npm run mcp-server
# OR
./run.sh → Option 1: "Start MCP Server"
```

**Access:**
- Direct: `file:///path/to/BrowserOS_Guides/docs/index.html#tools`
- Local server: `http://localhost:8080/#tools`
- Production: `https://yoursite.com/#tools`

**Features:**
- ✅ Form-based input (no CLI needed)
- ✅ Real-time generation with progress
- ✅ Copy/download workflow JSON
- ✅ Safety filtering built-in
- ✅ Rate limiting (2 concurrent, 10/hour)

### 2. CLI Menu (Interactive)

```bash
./run.sh
# Select 8: "Generate Workflow"
# Enter description when prompted
```

### 3. Direct Python Script

```bash
export OLLAMA_API_KEY="your-key"

# Quick generate
python scripts/workflow_generator.py full \
  --use-case "send daily sales report via email" \
  --industry "sales" \
  --complexity "beginner"

# With validation
python scripts/workflow_generator.py full \
  --use-case "scrape competitor prices from 5 websites" \
  --industry "e-commerce" \
  --complexity "medium" \
  --validate

# Custom output location
python scripts/workflow_generator.py full \
  --use-case "backup files to Google Drive" \
  --output-dir "MyWorkflows" \
  --validate
```

### 4. API Calls (Programmatic)

```bash
# Ensure MCP server is running
npm run mcp-server &

# Call from curl
curl -X POST http://localhost:3100/api/generate-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "use_case": "automated invoice processing",
    "industry": "finance",
    "complexity": "medium"
  }'

# Call from Python
import requests
response = requests.post('http://localhost:3100/api/generate-workflow', json={
    'use_case': 'monitor social media mentions',
    'industry': 'marketing',
    'complexity': 'medium'
})
print(response.json())

# Call from JavaScript
fetch('http://localhost:3100/api/generate-workflow', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    use_case: 'backup database daily',
    industry: 'tech',
    complexity: 'medium'
  })
}).then(r => r.json()).then(console.log);
```

### 5. GitHub Actions (Automated)

Already configured in `.github/workflows/update-kb.yml` lines 100-112.
Runs weekly, no local action needed for cloud deployment.

---

## Environment Variables Mapping

| GitHub Secret | Local .env | run.sh Reads | Purpose |
|--------------|------------|--------------|---------|
| `OLLAMA_API_KEY` | `OLLAMA_API_KEY=...` | ✅ Yes | Kimi AI workflow generation |
| `OPENROUTER_API_KEY` | `OPENROUTER_API_KEY=...` | ✅ Yes | Alternative AI provider |
| `GITHUB_TOKEN` | `GITHUB_TOKEN=...` | ✅ Yes | WhatsApp monitoring, auto-commits |
| `MCP_SERVER_PORT` | `MCP_SERVER_PORT=3100` | ✅ Yes | MCP server port |
| `AGENT_MODE` | `AGENT_MODE=local` | ✅ Yes | local/ci/docker |
| `LOG_LEVEL` | `LOG_LEVEL=INFO` | ✅ Yes | DEBUG/INFO/WARNING/ERROR |

**Load order in run.sh:**
1. Checks for `.env` file existence (line 56)
2. Reads all variables (lines 72-99)
3. Displays configuration summary
4. Passes to Python scripts via environment inheritance

---

## Testing Local Setup

### Verify Everything Works

```bash
# 1. Check installation
./run.sh → Option C: "Check for and Install System Updates"

# 2. Verify API keys
./run.sh → Option D: "Configure Settings" → View Configuration

# 3. Test workflow generation
./run.sh → Option 8: "Generate Workflow"
# Enter: "test automation for login page"

# 4. Run self-test
./run.sh → Option 3: "Run Self-Test"
# Should show: OLLAMA_API_KEY: ✓ Configured

# 5. Test MCP server
./run.sh → Option 1: "Start MCP Server"
# In another terminal:
curl http://localhost:3100/health
# Should return: {"status":"ok","timestamp":"..."}

# 6. Test web interface
# Start server, open docs/index.html#tools in browser
# Fill form, submit, verify workflow generates
```

---

## Troubleshooting

### "Configuration not found" Error

**Symptom:** run.sh shows error about missing .env file

**Fix:**
```bash
cp .env.template .env
./run.sh → Option D: "Configure Settings"
```

### Workflow Generation Fails

**Symptom:** "OLLAMA_API_KEY not set" or connection error

**Fix:**
```bash
# Check key is set
echo $OLLAMA_API_KEY

# If empty, set it
export OLLAMA_API_KEY="your-key-here"

# Or add to .env
echo "OLLAMA_API_KEY=your-key-here" >> .env

# Reload
source .env
```

### MCP Server Won't Start

**Symptom:** "Error: listen EADDRINUSE"

**Fix:**
```bash
# Check what's using port 3100
lsof -i :3100  # Linux/macOS
netstat -ano | findstr :3100  # Windows

# Kill the process or use different port
MCP_SERVER_PORT=3200 npm run mcp-server
```

### Web Interface Not Working

**Symptom:** Form submits but no response

**Fix:**
```bash
# 1. Check MCP server is running
curl http://localhost:3100/health

# 2. Check browser console for errors (F12)

# 3. Verify API key is set on server side
# Server needs OLLAMA_API_KEY environment variable
export OLLAMA_API_KEY="your-key"
npm run mcp-server
```

---

## Summary

**Key Takeaways:**

1. **GitHub Actions workflows** have **direct local equivalents** via `run.sh` menu
2. **API keys** move from GitHub Secrets → `.env` file
3. **Scheduled workflows** can be replicated with cron/Task Scheduler
4. **MCP server** is local-only and provides web interface + API
5. **Workflow generator** accessible 5 ways: Web, CLI menu, direct Python, API, GitHub Actions
6. **Cross-platform**: Linux, macOS, Windows, Docker all supported
7. **Full automation** possible locally with proper cron/service setup

**Quick Start for Local Users:**
```bash
./install.sh              # One-time setup
cp .env.template .env     # Configure API keys
./run.sh                  # Interactive menu
# OR
npm run mcp-server        # Start web interface
```

All the power of GitHub Actions, running on your machine! 🚀
