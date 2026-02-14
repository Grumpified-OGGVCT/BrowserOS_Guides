# 🌍 BrowserOS Knowledge Base - Cross-Platform Setup Guide

Complete guide for installing, configuring, and running BrowserOS Knowledge Base on **Windows, macOS, and Linux**.

## 📋 Table of Contents

- [Quick Start by Platform](#quick-start-by-platform)
- [System Requirements](#system-requirements)
- [Platform-Specific Installation](#platform-specific-installation)
- [Universal Configuration](#universal-configuration)
- [Running the System](#running-the-system)
- [Auto-Update System](#auto-update-system)
- [Platform Differences](#platform-differences)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start by Platform

### 🪟 Windows

```batch
# Install
install.bat

# Run
run.bat
```

📖 **Detailed Guide**: [WINDOWS_SETUP.md](WINDOWS_SETUP.md)

---

### 🍎 macOS

```bash
# Install
chmod +x install.sh
./install.sh

# Run
chmod +x run.sh
./run.sh
```

---

### 🐧 Linux

```bash
# Install
chmod +x install.sh
./install.sh

# Run
chmod +x run.sh
./run.sh
```

---

## 💻 System Requirements

### All Platforms

**Required:**
- **Python 3.11+**
- **Internet Connection**

**Recommended:**
- **Git** (for auto-updates and version control)
- **4GB RAM** minimum (8GB+ recommended)
- **1GB free disk space**

---

### Platform-Specific Prerequisites

#### 🪟 Windows 10/11

**Python Installation:**
1. Download from https://www.python.org/downloads/
2. ⚠️ **IMPORTANT**: Check "Add Python to PATH"
3. Verify: `python --version`

**Git Installation:**
1. Download from https://git-scm.com/download/win
2. Use default settings during installation
3. Verify: `git --version`

---

#### 🍎 macOS

**Python Installation:**

```bash
# Option 1: Homebrew (recommended)
brew install python@3.11

# Option 2: Official installer
# Download from https://www.python.org/downloads/mac-osx/

# Verify
python3 --version
```

**Git Installation:**

```bash
# Option 1: Xcode Command Line Tools
xcode-select --install

# Option 2: Homebrew
brew install git

# Verify
git --version
```

---

#### 🐧 Linux

**Ubuntu/Debian:**

```bash
# Update package list
sudo apt update

# Install Python 3.11+
sudo apt install python3.11 python3-pip

# Install Git
sudo apt install git

# Verify
python3 --version
git --version
```

**CentOS/RHEL:**

```bash
# Install Python
sudo yum install python3.11

# Install Git
sudo yum install git

# Verify
python3 --version
git --version
```

**Fedora:**

```bash
# Install Python
sudo dnf install python3.11

# Install Git
sudo dnf install git
```

**Arch Linux:**

```bash
# Install Python
sudo pacman -S python

# Install Git
sudo pacman -S git
```

---

## 📥 Platform-Specific Installation

### 🪟 Windows Installation

#### Step 1: Clone Repository

```batch
# Using Git
git clone https://github.com/Grumpified-OGGVCT/BrowserOS_Guides.git
cd BrowserOS_Guides

# Or download and extract ZIP
```

#### Step 2: Run Installer

```batch
install.bat
```

**What happens:**
- ✓ Checks Python 3.11+
- ✓ Checks Git (optional)
- ✓ Installs dependencies
- ✓ Creates directory structure
- ✓ Launches setup wizard

#### Step 3: Complete Setup Wizard

Follow the interactive prompts to configure:
- Agent mode
- API keys
- Connection settings
- Performance options
- Auto-update mode

#### Step 4: Start Using

```batch
run.bat
```

---

### 🍎 macOS Installation

#### Step 1: Clone Repository

```bash
# Using Git
git clone https://github.com/Grumpified-OGGVCT/BrowserOS_Guides.git
cd BrowserOS_Guides

# Or download and extract
```

#### Step 2: Make Scripts Executable

```bash
chmod +x install.sh run.sh
```

#### Step 3: Run Installer

```bash
./install.sh
```

**What happens:**
- ✓ Detects macOS
- ✓ Checks Python 3.11+
- ✓ Checks Git (optional)
- ✓ Installs dependencies
- ✓ Creates directory structure
- ✓ Launches setup wizard

#### Step 4: Complete Setup Wizard

Same interactive configuration as Windows

#### Step 5: Start Using

```bash
./run.sh
```

---

### 🐧 Linux Installation

#### Step 1: Clone Repository

```bash
# Using Git
git clone https://github.com/Grumpified-OGGVCT/BrowserOS_Guides.git
cd BrowserOS_Guides
```

#### Step 2: Make Scripts Executable

```bash
chmod +x install.sh run.sh
```

#### Step 3: Run Installer

```bash
./install.sh
```

**What happens:**
- ✓ Detects Linux distribution
- ✓ Checks Python 3.11+
- ✓ Checks Git (optional)
- ✓ Installs dependencies
- ✓ Creates directory structure
- ✓ Launches setup wizard

#### Step 4: Complete Setup Wizard

Same interactive configuration as other platforms

#### Step 5: Start Using

```bash
./run.sh
```

---

## ⚙️ Universal Configuration

The **Setup Wizard** is identical across all platforms and guides you through:

### 1. Agent Connection Mode

Choose how to connect to AI services:
- **HYBRID** (Recommended) - Tries multiple methods
- **SDK** - Python client libraries
- **HTTP** - REST API calls
- **MCP** - Model Context Protocol
- **LOCAL** - Local execution only
- **DOCKER** - Containerized

### 2. API Keys

Configure credentials:
- **Ollama Cloud API**: https://ollama.ai/keys
- **OpenRouter API**: https://openrouter.ai/keys
- **GitHub Token**: https://github.com/settings/tokens

### 3. Connection Modes

Per-service connection method:
- Ollama: HTTP, SDK, MCP, Docker, Local
- OpenRouter: HTTP, SDK, MCP

### 4. Model Selection

Choose AI models:
- **Ollama**: `kimi-k2.5:cloud`, `llama2`, `codellama`
- **OpenRouter**: `anthropic/claude-3-sonnet`, `openai/gpt-4-turbo`

### 5. Research Pipeline

Configure automation:
- Force full regeneration
- Fetch GitHub repos
- Fetch GitHub issues
- Fetch web sources

### 6. Performance Settings

Tune performance:
- **Max Workers**: 1-20 (default: 5)
- **Request Timeout**: 30-300s (default: 60)
- **Cache Duration**: 1-30 days (default: 7)

### 7. Logging

Configure logging:
- **Log Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Metrics**: Enable Prometheus metrics

### 8. Optional Features

Additional configuration:
- **Auto-Update Mode**: auto, prompt, disabled
- **Docker**: Enable Docker support
- **Encryption**: Secrets encryption

---

## 🎯 Running the System

### Startup Sequence (All Platforms)

1. **Auto-Update Check**
   - Checks for repository updates
   - Installs if available (based on mode)
   - Creates backup before updating

2. **Main Menu Appears**
   - Shows current configuration
   - 11 operation options
   - Clean, color-coded interface

### Main Menu Options

Same on all platforms:

1. **Update Knowledge Base** - Run research pipeline
2. **Run Self-Test** - Verify system integrity
3. **Generate Workflow** - Create workflow with AI
4. **Validate Knowledge Base** - Check KB completeness
5. **Extract Claude Skills** - Import community skills
6. **Generate Repository Structure** - Update repo browser
7. **Security Scan** - Check for vulnerabilities
8. **Check for Updates** - Manual update check
9. **Configure Settings** - Modify configuration
10. **View Documentation** - Open docs
0. **Exit** - Quit application

---

## 🔄 Auto-Update System

### Universal Features

The auto-update system works identically on all platforms:

**Safety Features:**
- ✓ Checks Git availability
- ✓ Fetches from remote repository
- ✓ Creates timestamped backups
- ✓ Stashes uncommitted changes
- ✓ Detects merge conflicts
- ✓ Validates after update
- ✓ Automatic rollback on failure
- ✓ Auto-updates dependencies

**Update Modes:**

```bash
# In .env file:
AUTO_UPDATE_MODE=auto      # Install automatically (default)
AUTO_UPDATE_MODE=prompt    # Ask before installing
AUTO_UPDATE_MODE=disabled  # Skip update checks
```

### Manual Update Check

**Windows:**
```batch
python scripts\auto_update.py
```

**macOS/Linux:**
```bash
python3 scripts/auto_update.py
```

---

## 🔍 Platform Differences

### File Paths

**Windows:**
- Path separator: `\`
- Example: `scripts\setup_wizard.py`

**macOS/Linux:**
- Path separator: `/`
- Example: `scripts/setup_wizard.py`

**Solution:** Python scripts handle this automatically using `pathlib`

---

### Line Endings

**Windows:**
- Line ending: CRLF (`\r\n`)
- Files: `.bat`, Windows text files

**macOS/Linux:**
- Line ending: LF (`\n`)
- Files: `.sh`, Unix text files

**Solution:** Git automatically handles line ending conversion

---

### Script Execution

**Windows:**
```batch
install.bat
run.bat
python scripts\setup_wizard.py
```

**macOS/Linux:**
```bash
./install.sh          # Or: bash install.sh
./run.sh              # Or: bash run.sh
python3 scripts/setup_wizard.py
```

**Python Command:**
- Windows: Usually `python`
- macOS/Linux: Usually `python3`
- Scripts detect automatically

---

### Permissions

**Windows:**
- No execute permissions needed
- Scripts run directly

**macOS/Linux:**
- Execute permission required:
  ```bash
  chmod +x install.sh run.sh
  ```

---

### Environment Variables

**Windows:**
```batch
set VARIABLE=value
echo %VARIABLE%
```

**macOS/Linux:**
```bash
export VARIABLE=value
echo $VARIABLE
```

**Configuration:**
- Both use `.env` file (same format)
- Python's `dotenv` handles both platforms

---

## 🔧 Configuration Management

### Post-Setup Changes

**All Platforms:**
```bash
# Windows
python scripts\config_manager.py

# macOS/Linux
python3 scripts/config_manager.py

# Or via menu
run.bat → Option 9  (Windows)
./run.sh → Option 9 (macOS/Linux)
```

### Configuration File

**Location (all platforms):**
```
.env
```

**Format (universal):**
```bash
AGENT_MODE=hybrid
OLLAMA_API_KEY=your-key
OPENROUTER_API_KEY=your-key
AUTO_UPDATE_MODE=auto
```

---

## 🔍 Troubleshooting

### Common Issues (All Platforms)

#### Problem: "Python not found"

**Solution:**

Windows:
```batch
# Reinstall Python from python.org
# Ensure "Add to PATH" is checked
```

macOS:
```bash
brew install python@3.11
# Or download from python.org
```

Linux:
```bash
# Ubuntu/Debian
sudo apt install python3.11

# CentOS/RHEL
sudo yum install python3.11
```

---

#### Problem: "Permission denied" (macOS/Linux)

**Solution:**
```bash
chmod +x install.sh run.sh
./install.sh
```

---

#### Problem: "pip not found"

**Solution:**

Windows:
```batch
python -m ensurepip --default-pip
```

macOS/Linux:
```bash
python3 -m ensurepip --default-pip
# Or: sudo apt install python3-pip (Ubuntu)
```

---

#### Problem: Dependency installation fails

**Solution:**

Windows:
```batch
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

macOS/Linux:
```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

---

### Platform-Specific Issues

#### macOS: "command not found: python"

**Solution:**
```bash
# Use python3 instead
python3 --version

# Or create alias
alias python=python3
```

---

#### Linux: "apt-get command not found"

**Solution:**
```bash
# You're not on Debian/Ubuntu
# Use your distro's package manager:

# Fedora
sudo dnf install python3

# CentOS
sudo yum install python3

# Arch
sudo pacman -S python
```

---

#### Windows: Scripts won't run in PowerShell

**Solution:**
```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use Command Prompt instead
cmd
install.bat
```

---

## 🚀 Advanced Cross-Platform Usage

### Virtual Environments

**All Platforms:**

```bash
# Create virtual environment
python -m venv venv  # or python3 on macOS/Linux

# Activate
# Windows
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run normally
run.bat  # Windows
./run.sh # macOS/Linux

# Deactivate
deactivate
```

---

### Docker (Universal)

**All Platforms:**

```bash
# Build image
docker build -t browseros-kb .

# Run container
docker run -d --name browseros-kb \
  -e OLLAMA_API_KEY=your-key \
  -e OPENROUTER_API_KEY=your-key \
  -v "$(pwd)/BrowserOS:/app/BrowserOS" \
  browseros-kb

# Or use docker-compose
docker-compose up -d
```

---

### Running in Background

**Windows:**
```batch
# Run as Windows service (advanced)
# Or use Task Scheduler

# Schedule daily at 2 AM:
# Task Scheduler → Create Task
# Trigger: Daily at 2:00 AM
# Action: Start program → run.bat
```

**macOS:**
```bash
# Use launchd
# Create plist file in ~/Library/LaunchAgents/

# Or use cron
crontab -e
# Add: 0 2 * * * /path/to/run.sh
```

**Linux:**
```bash
# Use systemd or cron
crontab -e
# Add: 0 2 * * * /path/to/run.sh

# Or create systemd service
sudo systemctl enable browseros-kb.service
```

---

## ✅ Cross-Platform Checklist

Use this checklist for any platform:

- [ ] Python 3.11+ installed
- [ ] Git installed (recommended)
- [ ] Repository cloned or downloaded
- [ ] Scripts made executable (Unix only)
- [ ] Ran installation script
- [ ] Completed setup wizard
- [ ] Configured API keys (or local mode)
- [ ] Selected agent and connection modes
- [ ] Configured auto-update mode
- [ ] Ran main script successfully
- [ ] Tested auto-update
- [ ] Ran at least one operation
- [ ] Verified logs created
- [ ] Backed up .env file

---

## 📚 Platform-Specific Documentation

- **Windows**: [WINDOWS_SETUP.md](../../WINDOWS_SETUP.md)
- **All Platforms**: This guide
- **General**: [README.md](../../README.md)
- **Automation**: [AUTOMATION_QUICKSTART.md](../../AUTOMATION_QUICKSTART.md)

---

## 🆘 Getting Help

**Check logs:**
```bash
# All platforms (adjust path separator)
cat logs/update.log
cat logs/research_pipeline.log
```

**GitHub Issues:**
https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/issues

**BrowserOS Resources:**
- GitHub: https://github.com/browseros-ai/BrowserOS
- Docs: https://docs.browseros.com

---

## 🎉 Success!

You now have a **universal, cross-platform** installation of BrowserOS Knowledge Base that:

✅ Works on Windows, macOS, and Linux
✅ Automatically updates itself
✅ Maintains configuration across platforms
✅ Provides identical functionality everywhere

**Start using:**

```bash
# Windows
run.bat

# macOS/Linux
./run.sh
```

---

*Last Updated: 2026-02-12*
*Supports: Windows 10/11, macOS 10.15+, Linux (all major distros)*
