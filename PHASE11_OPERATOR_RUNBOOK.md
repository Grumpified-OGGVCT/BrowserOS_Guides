# Phase 11: Operator Runbooks & Documentation

**Status:** Complete  
**Last Updated:** 2026-02-13  
**Purpose:** Production operations guide for BrowserOS automation infrastructure

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Daily Operations](#daily-operations)
3. [Troubleshooting](#troubleshooting)
4. [Maintenance](#maintenance)
5. [Disaster Recovery](#disaster-recovery)
6. [Monitoring](#monitoring)
7. [Security Operations](#security-operations)

---

## Quick Start

### For New Operators

**First Time Setup (15 minutes):**
```bash
# 1. Clone repository
git clone https://github.com/Grumpified-OGGVCT/BrowserOS_Guides.git
cd BrowserOS_Guides

# 2. Run installation (Windows)
install.bat

# 2. Run installation (Unix)
bash install.sh

# 3. Configure system
run.bat  # Or: bash run.sh
# Select Option 1: Configure Settings

# 4. Run self-test
# Select Option 6: Self-Test
```

**Verification (2 minutes):**
```bash
# Check configuration
cat .env | grep -E "AGENT_MODE|LOG_LEVEL"

# Check installation state
cat .installation_state

# Run basic health check
python scripts/self_test.py
```

---

## Daily Operations

### Morning Checks (5 minutes)

**1. System Status**
```bash
# Run menu
bash run.sh

# Check configuration summary at menu
# Verify API keys configured
```

**2. Knowledge Base Freshness**
```bash
# Option 5: Update Knowledge Base
# Should complete in 2-5 minutes
# Check timestamp in BrowserOS/Research/
```

**3. Run Self-Test**
```bash
# Option 6: Self-Test
# Expected: 10-13 tests passing
# If <10, investigate failures
```

### Routine Tasks

**Update System (Weekly):**
```bash
# Option 2: Check for and Install System Updates
# Reviews: install.bat, install.sh, requirements.txt
# Auto-updates if AUTO_UPDATE_MODE=auto
```

**Generate Library Artifacts (As Needed):**
```bash
# Option 8: Generate Library Artifacts
# Duration: 30-60 seconds
# Generates: library/templates/pattern_index.json
```

**Security Scan (Weekly):**
```bash
# Option C: Security Scan
# Duration: 2-3 minutes
# Reviews all Python scripts for vulnerabilities
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "Configuration not found" Error

**Symptoms:**
```
ERROR: Configuration not found!
Please run the installation and setup first
```

**Solution:**
```bash
# 1. Check if .env exists
ls -la .env

# 2. If missing, reconfigure
# Option 1: Configure Settings

# 3. If exists but corrupted, backup and regenerate
cp .env .env.backup
# Option 1: Configure Settings
```

---

#### Issue: Installation Fails Midway

**Symptoms:**
```
ERROR: Failed to install dependencies
Rollback initiated...
```

**Solution:**
```bash
# 1. Check installation state
cat .installation_state
# Shows: last_checkpoint=X

# 2. Review error in console output
# Look for specific package failures

# 3. Fix underlying issue, then resume
bash install.sh
# Will automatically resume from checkpoint X+1

# 4. If rollback needed
rm .installation_state
rm -rf .install_backups/
bash install.sh
```

---

#### Issue: "API Key Not Set or Is Placeholder"

**Symptoms:**
```
[Warn] Skipping model: OpenRouter API key not set or is placeholder
```

**Solution:**
```bash
# 1. Check current key
grep OPENROUTER_API_KEY .env

# 2. If placeholder, update
# Option 1: Configure Settings
# Navigate to Step 2: API Keys
# Enter real key (20+ characters, alphanumeric)

# 3. Validate
python -c "from utils.resilience import validate_api_key; validate_api_key('YOUR_KEY', 'TEST')"
```

---

#### Issue: Network Timeouts During KB Update

**Symptoms:**
```
[research_pipeline] [ERROR] Ollama API error: Timeout
Retrying in 2.0s... (attempt 2/3)
```

**Solution:**
```bash
# This is EXPECTED BEHAVIOR - retry logic at work!

# 1. Wait for retries to complete
# System will retry 3 times with exponential backoff

# 2. If all retries fail, check network
ping 8.8.8.8

# 3. If network OK, check service
curl http://localhost:11434/api/tags  # For Ollama

# 4. Adjust timeout if needed
# Edit .env:
REQUEST_TIMEOUT=120  # Increase from 60

# 5. Retry operation
# Option 5: Update Knowledge Base
```

---

#### Issue: Self-Test Failures

**Symptoms:**
```
Self-Test Results: 8/13 tests passed
FAILED: openrouter_key
FAILED: kb_completeness
```

**Solution Matrix:**

| Failed Test | Cause | Solution |
|-------------|-------|----------|
| `config_file` | .env missing | Run Option 1 |
| `ollama_key` | Key not set | Set OLLAMA_API_KEY in .env |
| `openrouter_key` | Key not set | Set OPENROUTER_API_KEY in .env |
| `kb_exists` | KB file missing | Run Option 5 (Update KB) |
| `kb_valid` | KB corrupted | Re-run Option 5 with FORCE_UPDATE=true |
| `search_index` | Index missing | Run Option D (Generate Structure) |
| `workflows_count` | <900 workflows | Expected if fresh install |
| `source_files` | sources.json missing | Run Option 5 |
| `schema_valid` | Schema issue | Run Option 7 (Validate KB) |
| `scripts_syntax` | Python error | Check scripts/*.py for syntax |

---

#### Issue: Menu Option Doesn't Return

**Symptoms:**
```
# Selected Option 3 (MCP Server)
# Server started but never returned to menu
```

**Solution:**
```bash
# For background services (MCP Server, Watchtower):
# 1. These run in foreground by default
# 2. Use Ctrl+C to stop
# 3. Menu will re-appear

# To run in background (Unix):
nohup node server/mcp-server.js &
# Menu continues immediately

# To run in background (Windows):
start /B node server\mcp-server.js
# Menu continues immediately
```

---

#### Issue: Permission Denied Errors

**Symptoms:**
```
[ERROR] Failed to write to logs/telemetry.json: Permission denied
```

**Solution:**
```bash
# Unix:
sudo chown -R $USER:$USER logs/
chmod -R 755 logs/

# Windows (run as Administrator):
icacls logs /grant %USERNAME%:F /T

# Then retry operation
```

---

## Maintenance

### Weekly Maintenance (15 minutes)

**1. Update System**
```bash
# Option 2: Check for and Install System Updates
```

**2. Security Scan**
```bash
# Option C: Security Scan
# Review output for vulnerabilities
```

**3. Validate KB**
```bash
# Option 7: Validate Knowledge Base
# Ensure all checks pass (C01-C06)
```

**4. Clean Up Logs**
```bash
# Remove old telemetry (>30 days)
find logs/ -name "*.log" -mtime +30 -delete

# Remove old backups (>7 days)
find .install_backups/ -type f -mtime +7 -delete
```

### Monthly Maintenance (30 minutes)

**1. Full System Test**
```bash
# Option 6: Self-Test
# Expect 13/13 passing

# If failures, investigate and resolve
```

**2. Review Configuration**
```bash
# Check for outdated settings
cat .env

# Reconfigure if needed
# Option 1: Configure Settings
```

**3. Update Dependencies**
```bash
# Check for outdated Python packages
pip list --outdated

# Update if needed
pip install --upgrade -r requirements.txt
```

**4. Generate Fresh Artifacts**
```bash
# Option 8: Generate Library Artifacts
# Option D: Generate Repository Structure
```

### Quarterly Maintenance (1 hour)

**1. Full Reinstall Test**
```bash
# Backup configuration
cp .env .env.quarterly_backup

# Clean install
rm -rf venv/ .installation_state
bash install.sh

# Restore configuration
cp .env.quarterly_backup .env

# Verify
bash run.sh
# Option 6: Self-Test
```

**2. Documentation Review**
```bash
# Review and update:
- AUTOMATION_HARDENING_PLAN.md
- SETUP_WIZARD_MAP.md
- This runbook
```

---

## Disaster Recovery

### Scenario 1: Complete System Failure

**Recovery Steps:**
```bash
# 1. Backup current state
tar -czf backup_$(date +%Y%m%d).tar.gz .env logs/ BrowserOS/Research/

# 2. Fresh clone
cd ..
git clone https://github.com/Grumpified-OGGVCT/BrowserOS_Guides.git BrowserOS_Guides_recovery
cd BrowserOS_Guides_recovery

# 3. Restore configuration
cp ../BrowserOS_Guides/.env .

# 4. Restore critical data
cp -r ../BrowserOS_Guides/logs/ .
cp -r ../BrowserOS_Guides/BrowserOS/Research/ BrowserOS/

# 5. Reinstall
bash install.sh

# 6. Verify
bash run.sh
# Option 6: Self-Test
```

**RTO:** 15 minutes  
**RPO:** Last backup (recommend daily backups)

### Scenario 2: Configuration Corruption

**Recovery Steps:**
```bash
# 1. Check for backup
ls -la .env.env.backup.*

# 2. Restore from backup
cp .env.env.backup.YYYYMMDD_HHMMSS .env

# 3. If no backup, reconfigure
# Option 1: Configure Settings

# 4. Verify
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('OK' if os.getenv('AGENT_MODE') else 'FAIL')"
```

**RTO:** 5 minutes  
**RPO:** Last auto-backup (created before each config change)

### Scenario 3: Knowledge Base Corruption

**Recovery Steps:**
```bash
# 1. Backup corrupted version
cp BrowserOS/Research/BrowserOS_Workflows_KnowledgeBase.md BrowserOS_Workflows_KnowledgeBase.md.corrupted

# 2. Force regeneration
export FORCE_UPDATE=true  # Unix
set FORCE_UPDATE=true     # Windows

# Option 5: Update Knowledge Base

# 3. Verify
# Option 7: Validate Knowledge Base

# 4. If still corrupted, restore from git
git checkout HEAD -- BrowserOS/Research/BrowserOS_Workflows_KnowledgeBase.md
```

**RTO:** 10 minutes  
**RPO:** Last git commit or last KB update

---

## Monitoring

### Key Metrics to Track

**1. Self-Test Success Rate**
```bash
# Target: >90% (10+/13 tests passing)
# Frequency: Daily
# Alert: <8/13 tests passing
```

**2. KB Update Duration**
```bash
# Target: <5 minutes
# Frequency: Weekly
# Alert: >10 minutes
```

**3. Installation Success Rate**
```bash
# Target: 100% on clean environments
# Frequency: Per installation
# Alert: Any failures
```

**4. API Availability**
```bash
# Monitor:
# - Ollama: http://localhost:11434/api/tags
# - OpenRouter: Rate limit status
# Frequency: Hourly (if running 24/7)
# Alert: 3 consecutive failures
```

### Log Locations

```bash
# Installation logs
.installation_state              # Current installation progress
.install_backups/               # Rollback backups

# Runtime logs  
logs/telemetry.json             # Operation telemetry (if generated)
logs/semantic_bridge_status.json # Bridge status (if generated)

# Test results
BrowserOS/Research/test_results.json  # Self-test results

# Application logs
# (Logged to console by default via ResilientLogger)
```

---

## Security Operations

### Access Control

**File Permissions:**
```bash
# Recommended permissions:
.env                    → 600 (owner read/write only)
scripts/*.py            → 755 (owner rwx, group/other rx)
install.sh/run.sh       → 755
logs/                   → 755 (directory)
```

**API Key Rotation:**
```bash
# 1. Generate new keys at providers:
# - Ollama: (if using cloud)
# - OpenRouter: https://openrouter.ai/keys

# 2. Update configuration
# Option 1: Configure Settings
# Step 2: API Keys

# 3. Test new keys
# Option 6: Self-Test
# Verify openrouter_key and ollama_key tests pass

# 4. Revoke old keys at providers
```

**Frequency:** Every 90 days

### Security Scan Results

**Interpreting Output:**
```bash
# Option C: Security Scan

# Expected output:
# - 0 critical vulnerabilities
# - 0 high vulnerabilities
# - <5 medium vulnerabilities (false positives acceptable)

# Action on findings:
# CRITICAL: Immediate patching required
# HIGH: Patch within 24 hours
# MEDIUM: Patch within 7 days
# LOW: Patch during next maintenance window
```

### Incident Response

**Security Incident Process:**

1. **Detect:** Security scan finds vulnerability
2. **Assess:** Determine severity and exploitability
3. **Contain:** If exploitable, disable affected component
4. **Remediate:** Apply patch or workaround
5. **Verify:** Re-run security scan
6. **Document:** Update security log

---

## Appendix: Command Quick Reference

### Installation
```bash
# Windows
install.bat

# Unix
bash install.sh

# Resume from checkpoint
# (Automatic - just rerun install script)
```

### Runtime Operations
```bash
# Windows
run.bat

# Unix
bash run.sh

# Direct script execution
python scripts/self_test.py
python scripts/research_pipeline.py
node server/mcp-server.js
```

### Diagnostics
```bash
# Check configuration
cat .env | grep -v "^#" | grep -v "^$"

# Check installation state
cat .installation_state

# Check Python syntax
find scripts -name "*.py" -exec python -m py_compile {} \;

# Check dependencies
pip list | grep -E "requests|beautifulsoup4|ollama|openai"

# Test resilience module
python -c "from utils.resilience import ResilientLogger; ResilientLogger(__name__).info('Test')"
```

### Backup & Restore
```bash
# Backup
tar -czf browseros_backup_$(date +%Y%m%d).tar.gz .env logs/ BrowserOS/Research/

# Restore
tar -xzf browseros_backup_YYYYMMDD.tar.gz

# Restore specific file
git checkout HEAD -- path/to/file
```

---

## Support

### Documentation Index

- **Installation:** `AUTOMATION_HARDENING_PLAN.md` Phase 8
- **Menu Options:** `PHASE9_MENU_VALIDATION_REPORT.md`
- **Setup Wizard:** `SETUP_WIZARD_MAP.md`
- **Testing:** `PHASE10_INTEGRATION_TESTING.md`
- **Operations:** This document (`PHASE11_OPERATOR_RUNBOOK.md`)

### Getting Help

1. **Check self-test:** `Option 6: Self-Test`
2. **Review logs:** Check console output
3. **Consult docs:** Review relevant phase documentation
4. **File issue:** GitHub Issues with test results

### Contact

- Repository: https://github.com/Grumpified-OGGVCT/BrowserOS_Guides
- Issues: https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/issues

---

**Document Version:** 1.0  
**Last Review:** 2026-02-13  
**Next Review:** 2026-05-13 (Quarterly)  
**Status:** Production Ready ✅
