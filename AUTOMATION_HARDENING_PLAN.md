# BrowserOS Automation Hardening Plan

## Executive Summary
Making all automations **immaculate, robust, and bulletproof** through systematic application of resilience patterns.

---

## ✅ Foundation Complete

### Resilience Module Created (`scripts/utils/resilience.py`)
- ✅ Exponential backoff retry decorator
- ✅ API key validation with placeholder detection  
- ✅ Structured logging (ResilientLogger)
- ✅ Safe file I/O operations
- ✅ Resilient HTTP requests with timeouts
- ✅ URL validation
- ✅ Dependency checker

---

## 🔧 Priority 1: Critical Script Hardening

### 1. `research_pipeline.py` - CRITICAL
**Issues:**
- ❌ Line 43-45: Silent config loader failure
- ❌ Line 56-58: No API key placeholder validation
- ❌ Line 72-98, 107-146: No retry logic on requests
- ❌ Line 104-105, 139-146: Returns empty string on failure (silent)
- ❌ Line 156-192: No URL validation

**Fixes:**
- ✅ Import resilience module
- ✅ Replace print statements with ResilientLogger
- ✅ Add @retry_with_backoff to all network calls
- ✅ Validate API keys with validate_api_key()
- ✅ Add timeout=30 to all requests
- ✅ Raise exceptions instead of returning empty strings
- ✅ Use validate_url() before fetching

###2. `workflow_generator.py` - CRITICAL
**Issues:**
- ❌ Line 64-65, 72-73, 89-90, 98-99: Bare `except: pass`
- ❌ Line 59: Print instead of logging
- ❌ Line 205-207: No fallback for missing API key
- ❌ ~Line 210: No timeout on requests
- ❌ Line 37-101: Silent JSON extraction failures

**Fixes:**
- ✅ Import resilience module
- ✅ Replace all `except: pass` with specific exception + logging
- ✅ Use ResilientLogger instead of print
- ✅ Add timeout to all requests
- ✅ Use safe_json_load() for JSON parsing
- ✅ Log each failed extraction strategy

### 3. `semantic_bridge.py` - CRITICAL
**Issues:**
- ❌ Line 107-164: No retry between model attempts
- ❌ Line 113-115: Incomplete API key validation
- ❌ Line 155: No try-catch on json.loads()
- ❌ Line 170-173: File I/O can hang
- ❌ Line 175-183: Telemetry errors swallowed

**Fixes:**
- ✅ Import resilience module
- ✅ Add exponential backoff between model retries
- ✅ Use validate_api_key() for proper validation
- ✅ Wrap JSON parsing in safe_json_load()
- ✅ Use safe_file_write() for status files
- ✅ Log failed telemetry to stderr

---

## 🔧 Priority 2: Supporting Scripts

### 4. `setup_wizard.py` - HIGH
**Issues:**
- ❌ Line 204-213: Silent .env parsing failures
- ❌ Line 470-480: No input bounds before parsing
- ❌ Line 110-115: Weak API key validation
- ❌ Line 644-649: Continues on missing critical deps

**Fixes:**
- Use safe_file_read() for .env parsing
- Validate ranges before int conversion
- Use validate_api_key() 
- Exit on missing critical dependencies

### 5. `self_test.py` - HIGH
**Issues:**
- ❌ Line 218-221, 238-241: Doesn't log stderr on subprocess failure
- ❌ Line 506-508: No check if dir creation succeeded
- ❌ Line 191: File read errors not logged

**Fixes:**
- Capture and log stderr/stdout on subprocess errors
- Use safe_file_write() for test results
- Log file validation failures

### 6. `validate_kb.py` - MEDIUM
**Issues:**
- ❌ Line 171: Bare exception message, no traceback
- ❌ Line 191-192: `errors='ignore'` masks problems
- ❌ Line 46, 66: Inconsistent path checking

**Fixes:**
- Log full tracebacks
- Remove `errors='ignore'`, log encoding issues
- Consistent use of Path.exists()

### 7. `generate_library.py` - MEDIUM
**Issues:**
- ❌ Line 159: No field validation before .get()
- ❌ Line 174-175: Catches all, continues silently
- ❌ Line 31-36: No schema validation

**Fixes:**
- Validate required fields exist
- Log full tracebacks
- Validate schema completeness

---

## 🔧 Priority 3: Installation & Runtime

### 8. `install.bat` / `install.sh`
**Issues:**
- ⚠️ Line 261: Fixed closing parenthesis
- ❌ Dependency checks don't validate versions
- ❌ No rollback on partial failure

**Improvements:**
- Add version checking for Python/Node
- Implement rollback mechanism
- Better error messages with next steps

### 9. `run.bat` / `run.sh`  
**Audit Needed:**
- Verify all menu options (1-9, A-E, 0) work
- Test each option end-to-end
- Ensure all scripts are called correctly
- Add error handling for script failures

---

## 📋 Implementation Strategy

### Phase 1: Foundation (✅ COMPLETE)
- [x] Create resilience.py module
- [x] Test resilience utilities
- [x] Document patterns

### Phase 2: Critical Script Hardening - Part 1 (🟡 IN PROGRESS)
- [ ] Harden research_pipeline.py (HIGH - network heavy)
- [ ] Test research_pipeline.py with retry scenarios
- [ ] Commit and verify

### Phase 3: Critical Script Hardening - Part 2
- [ ] Harden workflow_generator.py (HIGH - JSON extraction critical)
- [ ] Test workflow_generator.py with malformed responses
- [ ] Commit and verify

### Phase 4: Critical Script Hardening - Part 3
- [ ] Harden semantic_bridge.py (HIGH - model pool fallback)
- [ ] Test semantic_bridge.py with API failures
- [ ] Commit and verify

### Phase 5: Supporting Scripts - Part 1
- [ ] Harden setup_wizard.py (user-facing, critical for first run)
- [ ] Test setup wizard with invalid inputs
- [ ] Commit and verify

### Phase 6: Supporting Scripts - Part 2
- [ ] Harden self_test.py (validation critical)
- [ ] Harden validate_kb.py (validation critical)
- [ ] Test both validation scripts
- [ ] Commit and verify

### Phase 7: Supporting Scripts - Part 3
- [ ] Harden generate_library.py
- [ ] Harden any other scripts in scripts/ directory
- [ ] Test library generation
- [ ] Commit and verify

### Phase 8: Installation Scripts
- [ ] Add version checking to install.bat/install.sh
- [ ] Implement rollback mechanism
- [ ] Better error messages with next steps
- [ ] Test installation flow end-to-end

### Phase 9: Runtime Scripts & Menu Options
- [ ] Audit all run.bat/run.sh menu options (1-9, A-E, 0)
- [ ] Test each option individually
- [ ] Fix any broken options
- [ ] Add error handling for script failures

### Phase 10: Integration Testing
- [ ] Full install.bat test (Windows)
- [ ] Full install.sh test (Unix)
- [ ] All run.bat menu options test
- [ ] All run.sh menu options test
- [ ] Error scenario testing (missing deps, bad keys, network failures)
- [ ] Performance testing (retry delays acceptable)

### Phase 11: Documentation & Runbooks
- [ ] Update README with robustness features
- [ ] Document retry patterns for developers
- [ ] Add troubleshooting guide for users
- [ ] Create operator runbook for deployments
- [ ] Document sandbox utility pattern

---

## 💡 Sandbox Utility Pattern

### Making the Sandbox USEFUL & ACTIONABLE

The sandbox is a **safe, isolated environment** where agents can create immediate-need utility functions that are:
- ✅ **REAL CODE** - Fully functional, tested, production-quality
- ✅ **ACTIONABLE** - Can be used immediately for specific tasks
- ✅ **SAFE** - Isolated from production, no direct commit access
- ✅ **REUSABLE** - Can be packaged into `scripts/utils/` for permanent use

### Use Cases for Sandbox Utilities

**1. Data Processing Scripts**
```python
# Example: Create a one-off data migration script
/tmp/migrate_workflow_metadata.py
- Test in sandbox
- Run once to migrate data
- Archive or promote to scripts/utils/ if reusable
```

**2. Diagnostic Tools**
```python
# Example: Quick diagnostic for API connectivity
/tmp/test_all_apis.py
- Check Ollama, OpenRouter, GitHub APIs
- Report status and latency
- Keep in /tmp/ for ad-hoc use
```

**3. Rapid Prototypes**
```python
# Example: Prototype a new feature
/tmp/swarm_coordinator_prototype.py
- Test concept in sandbox
- Iterate quickly without polluting repo
- Promote to scripts/ when mature
```

**4. Quick Fixes**
```python
# Example: One-time data cleanup
/tmp/fix_malformed_workflows.py
- Fix batch of corrupted JSON files
- Run once, verify, delete
```

### Promotion Path: Sandbox → Production

```
1. Create in /tmp/               (Sandbox experimentation)
   ↓
2. Test & iterate               (Safe iteration)
   ↓
3. If useful → scripts/utils/   (Permanent utility)
   OR
3. If one-time → Archive        (Keep for reference)
```

### Safety Guarantees

- ❌ **Can't accidentally commit** - /tmp/ is in .gitignore
- ❌ **Can't break production** - Isolated environment
- ✅ **Can experiment freely** - No risk of polluting main repo
- ✅ **Can test immediately** - Real Python/Node environment
- ✅ **Can promote vetted code** - Explicit move to scripts/

### Example: Creating a Sandbox Utility

```bash
# Agent creates immediate-need utility in sandbox
cat > /tmp/check_workflow_health.py << 'EOF'
"""Quick health check for all workflows"""
import json
from pathlib import Path

def check_workflow(path):
    try:
        data = json.loads(Path(path).read_text())
        return "name" in data and "steps" in data
    except:
        return False

# Scan all workflows
workflows = Path("BrowserOS/Workflows").rglob("*.json")
broken = [w for w in workflows if not check_workflow(w)]
print(f"Broken workflows: {len(broken)}")
for w in broken:
    print(f"  - {w}")
EOF

# Run immediately
python /tmp/check_workflow_health.py

# If useful, promote
cp /tmp/check_workflow_health.py scripts/utils/workflow_health_checker.py
```

This pattern enables **rapid utility creation without compromising safety**.

---

## 🎯 Success Criteria

✅ **Zero Silent Failures** - All errors logged with context  
✅ **Automatic Recovery** - Transient failures handled via retry  
✅ **Graceful Degradation** - Clear error messages when unrecoverable  
✅ **Dependency Validation** - All deps checked before execution  
✅ **Input Validation** - All user inputs sanitized and validated  
✅ **Timeout Protection** - No infinite hangs on network/I/O  
✅ **Structured Logging** - Consistent, parseable log format  
✅ **API Key Safety** - Placeholder detection, format validation  

---

## 📊 Progress Tracking

**Scripts Hardened:** 0 / 7 critical scripts  
**Patterns Applied:** Resilience module created  
**Tests Passing:** Self-test passed  
**Installation Flow:** Not tested yet  

**ETA:** Phase 2 completion within 2-3 commits
**Blockers:** None currently

---

*Last Updated: 2026-02-13*
*Status: Phase 2 In Progress*
