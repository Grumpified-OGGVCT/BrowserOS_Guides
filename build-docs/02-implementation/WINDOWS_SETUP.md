# 🪟 BrowserOS Knowledge Base - Windows Setup Guide

Complete guide for installing, configuring, and running BrowserOS Knowledge Base on Windows.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [First-Run Configuration](#first-run-configuration)
- [Running the System](#running-the-system)
- [Auto-Update System](#auto-update-system)
- [Configuration Management](#configuration-management)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## 🚀 Quick Start

**3-Step Setup:**

```batch
1. install.bat          ← Install dependencies
2. [Setup Wizard]       ← Configure your installation (runs automatically)
3. run.bat              ← Start using the system
```

That's it! The system will auto-update each time you run it.

---

## 💻 System Requirements

### Required:
- **Windows 10/11** (or Windows Server 2016+)
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
  - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
- **Git** ([Download](https://git-scm.com/download/win)) - Optional but recommended
- **Internet Connection** - For downloading dependencies and updates

### Recommended:
- **4GB RAM** minimum (8GB+ recommended)
- **1GB free disk space**
- **Command Prompt** or **PowerShell** with execution permissions

---

## 📥 Installation

### Step 1: Clone or Download Repository

**Option A: Using Git (Recommended)**
```batch
git clone https://github.com/Grumpified-OGGVCT/BrowserOS_Guides.git
cd BrowserOS_Guides
```

**Option B: Download ZIP**
1. Download ZIP from GitHub
2. Extract to a permanent location (e.g., `C:\BrowserOS_Guides`)
3. Open Command Prompt in that folder

### Step 2: Run Installation Script

```batch
install.bat
```

**What this does:**
- ✓ Checks Python 3.11+ is installed
- ✓ Checks Git is installed (optional)
- ✓ Upgrades pip, setuptools, wheel
- ✓ Installs all Python dependencies from `requirements.txt`
- ✓ Creates directory structure (logs, BrowserOS folders)
- ✓ Creates `.env` configuration file from template
- ✓ Launches the setup wizard automatically

**Expected Output:**
```
================================================================================
   BrowserOS Knowledge Base - Installation Script
================================================================================

[1/6] Checking Python installation...
Found: Python 3.11.5
OK: Python version is compatible

[2/6] Checking Git installation...
Found: Git 2.42.0

[3/6] Checking pip installation...
OK: pip is available

[4/6] Installing Python dependencies...
Successfully installed requests-2.31.0 beautifulsoup4-4.12.0 ...
OK: All dependencies installed successfully

[5/6] Creating directory structure...
OK: Directories created

[6/6] Checking configuration...
Created .env from template

================================================================================
   Installation Complete!
================================================================================

Press any key to launch the setup wizard...
```

---

## ⚙️ First-Run Configuration

The **Setup Wizard** runs automatically after installation. It guides you through all configuration options.

### Configuration Steps

#### **1. Agent Connection Mode**

Choose how the system connects to AI services:

- **HYBRID** (Recommended) - Automatically tries multiple connection methods
- **SDK** - Use official Python SDK libraries
- **HTTP** - Direct REST API calls (most compatible)
- **MCP** - Model Context Protocol (advanced)
- **LOCAL** - Local execution only
- **DOCKER** - Containerized execution

#### **2. API Keys**

Configure API keys for cloud services:

**Ollama Cloud API Key**
- Get from: https://ollama.ai/keys
- Required for: Kimi K2.5 and other Ollama Cloud models
- Can skip for local-only mode

**OpenRouter API Key**
- Get from: https://openrouter.ai/keys
- Required for: Claude, GPT-4, and other premium models
- Can skip if using only Ollama

**GitHub Token**
- Get from: https://github.com/settings/tokens
- Required for: Private repos, higher API limits
- Can skip for public repos only

#### **3. Connection Modes**

Configure how each service connects:
- Ollama: HTTP, SDK, MCP, Docker, or Local
- OpenRouter: HTTP, SDK, or MCP

#### **4. Model Selection**

Choose AI models:
- **Ollama**: `kimi-k2.5:cloud` (default), `llama2`, `codellama`
- **OpenRouter**: `anthropic/claude-3-sonnet` (default), `openai/gpt-4-turbo`

#### **5. Research Pipeline**

Configure automated research:
- Force full regeneration: Yes/No
- Fetch GitHub repos: Yes/No
- Fetch GitHub issues: Yes/No
- Fetch web sources: Yes/No

#### **6. Performance Settings**

Tune performance:
- **Max Workers**: 1-20 (default: 5)
- **Request Timeout**: 30-300 seconds (default: 60)
- **Cache Duration**: 1-30 days (default: 7)

#### **7. Logging**

Configure logging:
- **Log Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Metrics**: Enable Prometheus metrics (optional)

#### **8. Optional Features**

Additional configuration:
- **Auto-Update Mode**:
  - `auto` - Automatically install updates on startup (default)
  - `prompt` - Ask before installing updates
  - `disabled` - Skip update checks
- **Docker**: Enable Docker support
- **Encryption**: Enable secrets encryption (optional)

### Completing Setup

After configuration:
1. Settings are saved to `.env`
2. Configuration is validated
3. Summary is displayed
4. Option to launch `run.bat` immediately

**You can always reconfigure later using:**
```batch
python scripts\config_manager.py
```

---

## 🎯 Running the System

### Starting the System

```batch
run.bat
```

### On Startup

**Auto-Update Process:**
1. System checks for updates from GitHub
2. If updates are available:
   - **Auto mode**: Installs automatically
   - **Prompt mode**: Asks for confirmation
   - **Disabled mode**: Skips update
3. Creates backup before updating
4. Stashes any uncommitted changes
5. Pulls and installs updates
6. Restores uncommitted changes
7. Validates installation
8. Auto-updates Python dependencies if needed

### Main Menu

```
================================================================================
   BrowserOS Knowledge Base - Main Menu
================================================================================

Current Configuration:
  Agent Mode:        hybrid
  Log Level:         INFO
  Ollama API:        Configured
  OpenRouter API:    Configured

================================================================================

What would you like to do?

  1. Update Knowledge Base (research pipeline)
  2. Run Self-Test
  3. Generate Workflow
  4. Validate Knowledge Base
  5. Extract Claude Skills
  6. Generate Repository Structure
  7. Security Scan
  8. Check for and Install System Updates
  9. Configure Settings
  A. View Documentation
  0. Exit
```

### Menu Options Explained

**1. Update Knowledge Base**
- Runs the automated research pipeline
- Fetches latest BrowserOS documentation
- Uses AI to synthesize information
- Updates knowledge base with new findings
- **Duration**: 5-15 minutes

**2. Run Self-Test**
- Validates system integrity
- Checks all 42 automated tests
- Auto-fixes issues where possible
- Creates GitHub issues for manual review
- **Duration**: 2-5 minutes

**3. Generate Workflow**
- Creates new workflow JSON files using AI
- Prompts for workflow description
- Uses Kimi K2.5 for feasibility validation
- Saves to BrowserOS/Workflows directory
- **Duration**: 1-3 minutes

**4. Validate Knowledge Base**
- Checks KB completeness and accuracy
- Validates all 12 required sections
- Checks for placeholder markers
- Verifies source citations
- **Duration**: 30 seconds

**5. Extract Claude Skills**
- Extracts skills from awesome-claude-skills repo
- Applies security validation
- Adapts and transforms skills
- Stores in Community-Contributed folder
- **Duration**: 2-5 minutes

**6. Generate Repository Structure**
- Creates repo-structure.json
- Powers the repository browser
- Indexes all files and folders
- **Duration**: 10-30 seconds

**7. Security Scan**
- Scans for security vulnerabilities
- Detects malicious code patterns
- Checks for XSS, injection risks
- Generates security report
- **Duration**: 1-2 minutes

**8. Check for and Install System Updates**
- Manually trigger update check
- Installs any available updates
- Same process as startup auto-update
- **Duration**: 30 seconds - 2 minutes

**9. Configure Settings**
- Opens interactive configuration manager
- Modify any settings post-setup
- Backs up config before changes
- **Duration**: As needed

**A. View Documentation**
- Opens README.md in default editor
- Access to all documentation files

---

## 🔄 Auto-Update System

The auto-update system is **bulletproof** and handles all edge cases safely.

### How It Works

1. **Checks for Updates**
   - Fetches from remote repository
   - Compares local vs remote commits
   - Shows what changed

2. **Creates Safety Backup**
   - Backs up `.env`, `config.yml`, `logs/`
   - Backs up knowledge base file
   - Keeps last 5 backups

3. **Handles Uncommitted Changes**
   - Detects any local modifications
   - Stashes changes automatically
   - Restores after update

4. **Installs Updates**
   - Pulls changes from GitHub
   - Detects merge conflicts
   - Validates repository integrity

5. **Post-Update**
   - Restores stashed changes
   - Updates Python dependencies automatically
   - Validates installation

6. **Rollback on Failure**
   - Restores from backup if update fails
   - Keeps system in working state
   - Logs all actions

### Update Modes

**Auto Mode (Default)**
```
AUTO_UPDATE_MODE=auto
```
- Checks and installs updates automatically
- No user prompt required
- Best for unattended operation

**Prompt Mode**
```
AUTO_UPDATE_MODE=prompt
```
- Checks for updates
- Asks before installing
- Best for manual control

**Disabled Mode**
```
AUTO_UPDATE_MODE=disabled
```
- Skips all update checks
- For offline or development use

### Manual Update Check

At any time, you can manually check for and install updates:

```batch
# From main menu
run.bat → Option 8

# Or directly
python scripts\auto_update.py
```

### Update Logs

All update actions are logged to:
```
logs/update.log
```

View recent updates:
```batch
type logs\update.log
```

### Backups

Backups are stored in:
```
.update_backups\YYYYMMDD_HHMMSS\
```

To manually restore from backup:
1. Go to `.update_backups` folder
2. Find the backup you want (by timestamp)
3. Copy files back to repository root

---

## 🔧 Configuration Management

### Post-Setup Configuration

Modify settings anytime:

```batch
python scripts\config_manager.py
```

### Configuration Manager Menu

```
================================================================================
   BrowserOS Knowledge Base - Configuration Manager
================================================================================

Current Configuration Status:
  Agent Mode:        hybrid
  Ollama API Key:    ✓ Configured
  OpenRouter Key:    ✓ Configured
  GitHub Token:      ✓ Configured
  Log Level:         INFO

What would you like to configure?

  1. Agent Connection Settings
  2. API Keys & Tokens
  3. Model Selection
  4. Research Pipeline
  5. Performance & Concurrency
  6. Logging & Monitoring
  7. Optional Features
  8. View Current Configuration
  9. Reset to Defaults
  10. Save and Exit
```

### Configuration File

All settings are stored in:
```
.env
```

**Important:**
- Never commit `.env` to version control
- It's in `.gitignore` by default
- Contains sensitive API keys
- Backups are created automatically

### Viewing Configuration

**View in Configuration Manager:**
```batch
python scripts\config_manager.py → Option 8
```

**View file directly:**
```batch
type .env
```

**View non-sensitive settings:**
```batch
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'Mode: {os.getenv(\"AGENT_MODE\")}')"
```

---

## 🔍 Troubleshooting

### Installation Issues

**Problem: "Python is not installed or not in PATH"**

**Solution:**
1. Install Python 3.11+ from https://www.python.org/downloads/
2. During installation, CHECK "Add Python to PATH"
3. Restart Command Prompt
4. Verify: `python --version`

---

**Problem: "ERROR: Failed to install dependencies"**

**Solution:**
1. Check internet connection
2. Update pip: `python -m pip install --upgrade pip`
3. Try manual install: `python -m pip install -r requirements.txt`
4. If behind proxy, set: `set HTTP_PROXY=http://proxy:port`

---

**Problem: "Git is not installed"**

**Solution:**
- Git is optional but recommended
- Download from: https://git-scm.com/download/win
- Or continue without Git (auto-update will be disabled)

---

### Configuration Issues

**Problem: "Configuration not found" when running run.bat**

**Solution:**
1. Run setup wizard: `python scripts\setup_wizard.py`
2. Or copy template: `copy .env.template .env`
3. Edit `.env` with your settings

---

**Problem: API keys not working**

**Solution:**
1. Verify keys are valid (not expired)
2. Check for extra spaces in `.env` file
3. Regenerate keys from provider websites
4. Update with: `python scripts\config_manager.py → Option 2`

---

### Update Issues

**Problem: "Failed to fetch updates"**

**Solution:**
1. Check internet connection
2. Verify Git is installed: `git --version`
3. Check remote: `git remote get-url origin`
4. Try manual fetch: `git fetch origin`

---

**Problem: "Merge conflicts detected"**

**Solution:**
1. Auto-update will abort safely
2. Backup is automatically created
3. Manually resolve: `git status` then `git merge --abort`
4. Or reset: `git reset --hard origin/main`
5. Run update again

---

**Problem: "Update failed" but system still works**

**Solution:**
- System is designed to be bulletproof
- Backup is preserved in `.update_backups`
- Check logs: `type logs\update.log`
- Restore if needed: Copy from `.update_backups\<timestamp>\`

---

### Runtime Issues

**Problem: "ERROR: Research pipeline failed"**

**Solution:**
1. Check API keys are configured
2. Verify internet connection
3. Check logs: `type logs\research_pipeline.log`
4. Try with lower concurrency: Reduce MAX_WORKERS in `.env`

---

**Problem: Scripts fail with "ModuleNotFoundError"**

**Solution:**
1. Reinstall dependencies: `python -m pip install -r requirements.txt`
2. Check Python version: `python --version` (must be 3.11+)
3. Activate virtual environment if using one

---

**Problem: High memory usage**

**Solution:**
1. Reduce MAX_WORKERS in configuration
2. Lower CACHE_DURATION
3. Close other applications
4. Increase system RAM if possible

---

## 🚀 Advanced Usage

### Running in Silent Mode

Skip all prompts for automation:

```batch
python scripts\auto_update.py --silent
python scripts\setup_wizard.py --silent
```

### Using Virtual Environment

Isolate Python dependencies:

```batch
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run normally
run.bat

# Deactivate when done
deactivate
```

### Scheduled Tasks

Run knowledge base updates automatically:

1. Open **Task Scheduler**
2. Create Basic Task
3. **Trigger**: Daily at 2 AM
4. **Action**: Start a program
   - Program: `C:\BrowserOS_Guides\run.bat`
   - Arguments: (leave blank, it will auto-update)
   - Start in: `C:\BrowserOS_Guides`

### Docker Deployment

Run in Docker container:

```batch
# Build image
docker build -t browseros-kb .

# Run container
docker run -d --name browseros-kb \
  -e OLLAMA_API_KEY=your-key \
  -e OPENROUTER_API_KEY=your-key \
  -v "%CD%\BrowserOS:/app/BrowserOS" \
  browseros-kb

# Or use docker-compose
docker-compose up -d
```

### Environment Variables

Override config via environment variables:

```batch
# Set before running
set AGENT_MODE=sdk
set LOG_LEVEL=DEBUG
set MAX_WORKERS=10

# Run
run.bat
```

### API Key Rotation

Rotate API keys safely:

```batch
# Method 1: Configuration Manager
python scripts\config_manager.py
# → Option 2: API Keys & Tokens
# → Update each key

# Method 2: Edit .env directly
notepad .env
# Change values, save

# Method 3: Environment variables (temporary)
set OLLAMA_API_KEY=new-key
run.bat
```

### Custom Scripts

Add custom scripts to the menu:

1. Create script in `scripts\` folder
2. Edit `run.bat`
3. Add menu option:
```batch
echo   B. My Custom Script
...
if /i "%CHOICE%"=="B" goto CUSTOM_SCRIPT
...
:CUSTOM_SCRIPT
python scripts\my_custom_script.py
goto MAIN_MENU
```

### Logging Configuration

Customize logging:

**Change log level:**
```
LOG_LEVEL=DEBUG  # Most verbose
LOG_LEVEL=INFO   # Normal (default)
LOG_LEVEL=WARNING # Only warnings and errors
LOG_LEVEL=ERROR  # Only errors
```

**Enable metrics:**
```
ENABLE_METRICS=true
METRICS_PORT=9090
```

Access metrics:
```
http://localhost:9090/metrics
```

---

## 📚 Additional Resources

### Documentation Files

- `README.md` - Repository overview
- `AUTOMATION_QUICKSTART.md` - Automation guide
- `DEPLOYMENT.md` - Deployment options
- `WORKFLOW_TESTING_COMPLETE.md` - Workflow testing
- `SECURITY-POLICY.md` - Security policy

### Support

- **Issues**: https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/issues
- **Discussions**: https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/discussions

### BrowserOS Resources

- **GitHub**: https://github.com/browseros-ai/BrowserOS
- **Documentation**: https://docs.browseros.com

---

## ✅ Setup Checklist

Use this checklist to ensure complete setup:

- [ ] Python 3.11+ installed
- [ ] Git installed (optional)
- [ ] Ran `install.bat` successfully
- [ ] Completed setup wizard
- [ ] Configured API keys (or chose local mode)
- [ ] Selected agent and connection modes
- [ ] Configured auto-update mode
- [ ] Ran `run.bat` successfully
- [ ] Tested auto-update (or manual update check)
- [ ] Ran at least one operation (e.g., self-test)
- [ ] Verified logs directory created
- [ ] Backed up `.env` file to safe location
- [ ] Bookmarked this guide for reference

**Congratulations! Your BrowserOS Knowledge Base is ready to use! 🎉**

---

*Last Updated: 2026-02-12*
