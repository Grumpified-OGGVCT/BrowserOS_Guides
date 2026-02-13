# Phase 10: Integration Testing Guide

**Status:** Ready for Execution  
**Last Updated:** 2026-02-13  
**Purpose:** Comprehensive testing guide for BrowserOS automation infrastructure

---

## Overview

This document provides step-by-step integration testing procedures to validate the entire BrowserOS automation stack after hardening.

---

## Pre-Test Checklist

- [ ] Fresh clone of repository
- [ ] Clean environment (no existing .env or .installation_state)
- [ ] Python 3.11+ installed
- [ ] Node.js 14+ installed (for MCP server tests)
- [ ] Internet connectivity
- [ ] At least 1GB free disk space

---

## Test Suite 1: Installation Flow (Windows)

### Test 1.1: Fresh Installation
```cmd
cd BrowserOS_Guides
install.bat
```

**Expected Results:**
- ✅ Python version check passes
- ✅ Node.js check warns if missing but continues
- ✅ Dependencies installed successfully
- ✅ Setup wizard launches automatically
- ✅ .env file created
- ✅ No errors in console

**Validation:**
- Check `.installation_state` exists
- Check `.env` has configuration
- Check `requirements.txt` unchanged

### Test 1.2: Installation Interruption & Resume
```cmd
# Interrupt during step 4 (Ctrl+C)
install.bat
```

**Expected Results:**
- ✅ Resumes from last checkpoint
- ✅ Skips completed steps
- ✅ Completes remaining steps
- ✅ Cleanup of state file on success

### Test 1.3: Installation Failure & Rollback
```cmd
# Simulate failure (rename requirements.txt temporarily)
ren requirements.txt requirements.txt.backup
install.bat
# Restore
ren requirements.txt.backup requirements.txt
```

**Expected Results:**
- ✅ Error detected and reported
- ✅ Rollback mechanism activated
- ✅ Backup restored if created
- ✅ Clear "Next Steps" message displayed
- ✅ Exit code 1 returned

---

## Test Suite 2: Installation Flow (Unix)

### Test 2.1: Fresh Installation (Linux/macOS)
```bash
cd BrowserOS_Guides
bash install.sh
```

**Expected Results:**
- ✅ OS detection works correctly
- ✅ Python version check passes
- ✅ Dependencies installed
- ✅ Setup wizard launches
- ✅ Platform-specific guidance shown

### Test 2.2: Distribution-Specific Testing

**Ubuntu/Debian:**
```bash
# Check apt-based guidance
grep -A5 "Ubuntu\|Debian" install.sh
```

**CentOS/Fedora:**
```bash
# Check yum/dnf-based guidance
grep -A5 "CentOS\|Fedora" install.sh
```

**Arch Linux:**
```bash
# Check pacman-based guidance
grep -A5 "Arch" install.sh
```

---

## Test Suite 3: Runtime Menu System

### Test 3.1: Configuration Option (Option 1)
```cmd
run.bat
# Select: 1
# Complete wizard
# Exit
```

**Expected Results:**
- ✅ Setup wizard launches
- ✅ All 8 configuration steps available
- ✅ Configuration saved to .env
- ✅ Returns to menu cleanly

### Test 3.2: MCP Server (Option 3)
```cmd
run.bat
# Select: 3
# Wait 5 seconds
# Ctrl+C to stop
```

**Expected Results:**
- ✅ Server starts on port 3100
- ✅ Node.js process runs
- ✅ Graceful shutdown on Ctrl+C
- ✅ Returns to menu

### Test 3.3: Update Knowledge Base (Option 5)
```cmd
run.bat
# Select: 5
```

**Expected Results:**
- ✅ Script executes without errors
- ✅ Retry logic engages on network failures
- ✅ Structured logging visible
- ✅ KB file updated
- ✅ Returns to menu

### Test 3.4: Self-Test (Option 6)
```cmd
run.bat
# Select: 6
```

**Expected Results:**
- ✅ 13/13 or 10+/13 tests pass
- ✅ Test results JSON created
- ✅ Clear pass/fail summary
- ✅ Returns to menu

### Test 3.5: All Menu Options (1-9, A-F, 0)

**Test Matrix:**
| Option | Expected Behavior | Status |
|--------|-------------------|--------|
| 1 | Launch wizard | ⬜ |
| 2 | Check updates | ⬜ |
| 3 | Start MCP | ⬜ |
| 4 | Watchtower | ⬜ |
| 5 | Update KB | ⬜ |
| 6 | Self-test | ⬜ |
| 7 | Validate KB | ⬜ |
| 8 | Generate lib | ⬜ |
| 9 | Workflow gen | ⬜ |
| A | Monitor WA | ⬜ |
| B | Provenance | ⬜ |
| C | Security scan | ⬜ |
| D | Gen structure | ⬜ |
| E | Extract skills | ⬜ |
| F | View docs | ⬜ |
| 0 | Exit | ⬜ |

---

## Test Suite 4: Resilience Validation

### Test 4.1: Network Failure Handling
```cmd
# Disable network temporarily
# Run: python scripts/research_pipeline.py
# Re-enable network
```

**Expected Results:**
- ✅ Retry logic activates (1s, 2s, 4s delays)
- ✅ Structured error messages logged
- ✅ Eventually succeeds or fails gracefully
- ✅ No silent failures

### Test 4.2: Invalid API Keys
```cmd
# Set placeholder keys in .env
OLLAMA_API_KEY=your-ollama-api-key
OPENROUTER_API_KEY=your-openrouter-api-key
# Run: python scripts/workflow_generator.py --help
```

**Expected Results:**
- ✅ Placeholder detection works
- ✅ Clear warning message displayed
- ✅ Script doesn't crash
- ✅ Actionable guidance provided

### Test 4.3: File System Errors
```cmd
# Make logs directory read-only
attrib +R logs
# Run: python scripts/semantic_bridge.py
# Restore
attrib -R logs
```

**Expected Results:**
- ✅ Safe file write detects permission error
- ✅ Error logged with context
- ✅ Script continues if possible
- ✅ Clear error message to user

---

## Test Suite 5: Cross-Platform Validation

### Test 5.1: Windows Batch Scripts
```cmd
# Test all .bat files execute without syntax errors
install.bat /?
run.bat (menu appears)
```

### Test 5.2: Unix Shell Scripts
```bash
# Test all .sh files have correct syntax
bash -n install.sh && echo "OK"
bash -n run.sh && echo "OK"
```

### Test 5.3: Python Scripts
```bash
# Test all Python scripts compile
find scripts -name "*.py" -exec python -m py_compile {} \;
```

---

## Test Suite 6: Error Scenarios

### Test 6.1: Missing Dependencies
```cmd
# Uninstall a dependency
pip uninstall requests -y
# Run: python scripts/research_pipeline.py
# Reinstall
pip install requests
```

**Expected Results:**
- ✅ ImportError caught
- ✅ Clear message about missing package
- ✅ Installation instructions provided
- ✅ Exit code 1

### Test 6.2: Corrupted Configuration
```cmd
# Add malformed line to .env
echo "BROKEN LINE WITHOUT EQUALS" >> .env
# Run: run.bat
# Fix
# Edit .env and remove broken line
```

**Expected Results:**
- ✅ Parsing error detected
- ✅ Line number reported
- ✅ Suggestion to run Option 1 (reconfigure)
- ✅ Script doesn't crash

### Test 6.3: Disk Space Exhaustion
```cmd
# Simulate low disk space (requires admin)
# Run: install.bat
```

**Expected Results:**
- ✅ Pre-check detects low space
- ✅ Warning message with space requirement
- ✅ Option to continue or cancel
- ✅ Rollback if installation fails

---

## Test Suite 7: Performance & Load

### Test 7.1: Concurrent Operations
```cmd
# Open 3 terminals
# Terminal 1: run.bat -> Option 5
# Terminal 2: run.bat -> Option 6  
# Terminal 3: run.bat -> Option 7
```

**Expected Results:**
- ✅ No file lock conflicts
- ✅ All processes complete
- ✅ Logs don't intermingle
- ✅ No corruption

### Test 7.2: Large KB Updates
```cmd
# Run with FORCE_UPDATE=true
set FORCE_UPDATE=true
run.bat
# Select: 5
```

**Expected Results:**
- ✅ Completes without timeout
- ✅ Progress visible
- ✅ Memory usage reasonable
- ✅ KB file updated correctly

---

## Pass/Fail Criteria

### Critical (Must Pass)
- [ ] Fresh installation completes on Windows
- [ ] Fresh installation completes on Linux
- [ ] Fresh installation completes on macOS
- [ ] All 16 menu options execute without crash
- [ ] Rollback mechanism works on failure
- [ ] Retry logic activates on network errors
- [ ] Self-test passes 10+/13 tests

### Important (Should Pass)
- [ ] Resume from checkpoint works
- [ ] Placeholder API key detection works
- [ ] All Python scripts compile without errors
- [ ] All shell scripts have valid syntax
- [ ] Concurrent operations don't conflict
- [ ] Error messages are actionable

### Nice-to-Have (May Pass)
- [ ] All 13/13 self-tests pass
- [ ] Distribution-specific guidance shown
- [ ] Performance under load acceptable
- [ ] Disk space pre-check works

---

## Reporting Template

```markdown
## Integration Test Report

**Date:** YYYY-MM-DD
**Tester:** [Name]
**Platform:** [Windows 11 / Ubuntu 22.04 / macOS Ventura / etc.]
**Python Version:** [X.Y.Z]
**Node.js Version:** [X.Y.Z]

### Results Summary
- Total Tests: XX
- Passed: XX
- Failed: XX
- Skipped: XX

### Critical Issues Found
1. [Issue description]
   - Impact: [High/Medium/Low]
   - Workaround: [If available]

### Test Details
[Paste test matrix with checkmarks]

### Notes
[Any additional observations]
```

---

## Automation

For CI/CD integration, use:

```bash
# Run all integration tests
./scripts/run_integration_tests.sh --all

# Run specific suite
./scripts/run_integration_tests.sh --suite installation

# Generate report
./scripts/run_integration_tests.sh --report
```

---

## Next Steps After Testing

1. **If all critical tests pass:** Proceed to Phase 11 (Documentation)
2. **If any critical test fails:** File issue with test report
3. **If important tests fail:** Investigate and fix before merge
4. **If nice-to-have fails:** Document known issues

---

## Contact

For questions or issues with integration testing:
- Check: `AUTOMATION_HARDENING_PLAN.md`
- Review: `SETUP_WIZARD_MAP.md`
- Contact: BrowserOS Team

---

**Status:** Ready for Execution ✅
