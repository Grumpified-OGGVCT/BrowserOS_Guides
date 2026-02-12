# 🚀 Workflow Trigger Guide

Complete guide to triggering and monitoring BrowserOS_Guides automated workflows.

## Overview

The BrowserOS_Guides repository includes several automated GitHub Actions workflows that:
- **Generate workflows** from external sources
- **Update knowledge base** from official BrowserOS repository
- **Run self-tests** to verify integrity
- **Scan for security** vulnerabilities
- **Deploy pages** to GitHub Pages

This guide explains how to trigger these workflows and verify they're working correctly.

---

## 📋 Available Workflows

### 1. Update Knowledge Base (`update-kb.yml`)
**Purpose**: Syncs with official BrowserOS repo, generates new workflows, updates search index

**Triggers**:
- 🕐 **Scheduled**: Weekly on Sundays at 00:00 UTC
- ⚡ **Manual**: Via workflow_dispatch (see below)

**What it does**:
1. Clones/updates the official BrowserOS repository
2. Runs AI-powered research pipeline
3. Validates knowledge base completeness
4. Generates new workflows using Kimi-K2.5:cloud AI (weekly only)
5. Regenerates repository structure JSON
6. Regenerates search index
7. Commits and pushes all changes

### 2. Self-Test & Quality Assurance (`self-test.yml`)
**Purpose**: Automated testing and quality checks

**Triggers**:
- 🕐 **Scheduled**: Weekly on Sundays at 02:00 UTC
- 🔗 **After**: Update Knowledge Base workflow completes
- ⚡ **Manual**: Via workflow_dispatch

**What it does**:
1. Runs comprehensive security scan
2. Executes 42 self-tests covering:
   - KB completeness
   - Search index validity
   - Website asset integrity
   - Workflow validation
   - Documentation link checking
   - Python script syntax
3. Auto-fixes 85%+ of issues found
4. Creates GitHub issues for manual review if needed

### 3. Deploy Pages (`deploy-pages.yml`)
**Purpose**: Deploys website to GitHub Pages

**Triggers**:
- 🔀 **Push**: When changes pushed to main branch
- ⚡ **Manual**: Via workflow_dispatch

---

## ⚡ How to Manually Trigger Workflows

### Method 1: GitHub Web Interface

1. **Go to Actions tab**: https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/actions

2. **Select workflow** from left sidebar:
   - "Update BrowserOS Knowledge Base"
   - "Self-Test & Quality Assurance"
   - "Deploy Pages"

3. **Click "Run workflow"** dropdown (right side)

4. **Select branch**: Usually `main`

5. **Set options** (if available):
   - For `update-kb.yml`: Option to force full KB regeneration
   - For `self-test.yml`: Option to enable/disable auto-fix

6. **Click "Run workflow"** button

### Method 2: GitHub CLI (gh)

```bash
# Install GitHub CLI if needed
# https://cli.github.com/

# Trigger Update KB workflow
gh workflow run update-kb.yml \
  --ref main \
  -f force_update=false

# Trigger Self-Test workflow
gh workflow run self-test.yml \
  --ref main \
  -f force_fix=true

# Trigger Deploy Pages workflow
gh workflow run deploy-pages.yml --ref main
```

### Method 3: GitHub API

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_token_here"

# Trigger Update KB workflow
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/Grumpified-OGGVCT/BrowserOS_Guides/actions/workflows/update-kb.yml/dispatches \
  -d '{"ref":"main","inputs":{"force_update":"false"}}'

# Trigger Self-Test workflow
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/Grumpified-OGGVCT/BrowserOS_Guides/actions/workflows/self-test.yml/dispatches \
  -d '{"ref":"main","inputs":{"force_fix":"true"}}'
```

---

## 👀 Monitoring Workflow Runs

### View Workflow Runs

1. Go to: https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/actions

2. Click on a specific workflow run to see:
   - **Status**: Queued, In Progress, Completed, Failed
   - **Duration**: How long it took
   - **Jobs**: Individual steps and their status
   - **Logs**: Detailed output from each step

### Check Logs

1. Click on a workflow run
2. Click on a job name (e.g., "update-knowledge-base")
3. Expand steps to see detailed logs
4. Look for:
   - ✅ Success indicators
   - ⚠️ Warnings
   - ❌ Errors
   - 📊 Statistics (files processed, tests passed, etc.)

### Download Artifacts

Some workflows produce artifacts (e.g., test results, security reports):

1. Go to workflow run page
2. Scroll to "Artifacts" section
3. Download available artifacts:
   - `self-test-results` (from self-test.yml)
   - Test result JSONs
   - Security scan reports

---

## 🔍 Verifying Workflow Success

### After Update KB Workflow

**Check for these changes**:

```bash
# 1. Check for new commits
git log --oneline -5 | grep "Automated KB update"

# 2. Verify file updates
ls -lh docs/repo-structure.json
ls -lh docs/search-index.json

# 3. Check workflow count
find BrowserOS/Workflows -type f -name "*.json" | wc -l
# Should show 917+ workflows

# 4. Verify generated tag
git tag | grep "kb-20"
```

**Expected files updated**:
- `BrowserOS/Research/*` (KB content)
- `docs/repo-structure.json` (repository structure)
- `docs/search-index.json` (search index)
- `BrowserOS/structure.md` (structure documentation)

### After Self-Test Workflow

**Check for**:

```bash
# 1. Look for auto-fix commits
git log --oneline -5 | grep "Auto-fix"

# 2. Check for created issues
# Visit: https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/issues?q=label%3Aself-test

# 3. Review test artifacts (download from Actions tab)
```

### After Deploy Pages Workflow

**Verify deployment**:

1. Visit: https://grumpified-oggvct.github.io/BrowserOS_Guides/
2. Check that changes are live
3. Test updated features:
   - Search functionality
   - Repository browser
   - Updated workflow counts (917+)

---

## 🛠️ Running Scripts Locally

You can also run the underlying scripts locally for testing:

### Extract Claude Skills

```bash
cd /path/to/BrowserOS_Guides

# Extract workflows from awesome-claude-skills
python scripts/extract_claude_skills.py --verbose

# Should extract 917+ workflows to:
# BrowserOS/Workflows/Community-Contributed/claude-skills-adapted/
```

### Generate Repository Structure

```bash
# Regenerate repo-structure.json
python scripts/generate_repo_structure.py

# Output: docs/repo-structure.json
# Contains: File tree, stats, metadata
```

### Generate Search Index

```bash
# Regenerate search-index.json
python scripts/generate_search_index.py

# Output: docs/search-index.json
# Indexes: All markdown documentation
```

### Run Self-Tests

```bash
# Run all tests with auto-fix
python scripts/self_test.py --auto-fix --verbose

# Run tests without auto-fix (report only)
python scripts/self_test.py --verbose

# Generate report only
python scripts/self_test.py --report-only
```

### Security Scan

```bash
# Scan all files for security issues
python scripts/security_scanner.py --verbose

# Fail on critical vulnerabilities
python scripts/security_scanner.py --fail-on-critical
```

### Generate New Workflows (Requires API Key)

```bash
# Set Ollama API key
export OLLAMA_API_KEY="your_key_here"

# Generate single workflow idea
python scripts/workflow_generator.py idea \
  --use-case "automate invoice processing" \
  --complexity medium

# Generate full workflow with validation
python scripts/workflow_generator.py full \
  --use-case "monitor competitor prices" \
  --industry "e-commerce" \
  --validate \
  --output-dir "./generated"
```

---

## 📊 Expected Results

### Successful Update KB Run

```
✅ Cloned/updated BrowserOS repository
✅ Research pipeline completed
✅ KB validation passed
✅ Generated repository structure (995 files, 20 folders)
✅ Regenerated search index (29 documents)
✅ Generated new workflow ideas (if weekly run)
✅ Committed changes
✅ Tagged release: kb-2026.02.12
```

### Successful Self-Test Run

```
✅ Security scan: 0 critical issues
✅ KB completeness: 100%
✅ Search index: Valid
✅ Website assets: All present
✅ Workflows: 917+ validated
✅ Links: All working
✅ Python scripts: Syntax valid
✅ Tests passed: 42/42
✅ Auto-fixes applied: [list]
```

---

## ❌ Troubleshooting

### Workflow Not Triggering

**Problem**: Manual trigger doesn't start workflow

**Solutions**:
1. Check you have write access to repository
2. Verify workflow file exists in `.github/workflows/`
3. Check workflow file syntax (YAML)
4. Look for GitHub Actions outages

### Workflow Fails

**Problem**: Workflow runs but fails

**Common issues**:

1. **Missing API Keys**
   - Solution: Add secrets in repository settings
   - Required: `OLLAMA_API_KEY`, `OPENROUTER_API_KEY`

2. **Python Dependency Issues**
   - Check: `requirements.txt` is up to date
   - Fix: Update dependencies in workflow file

3. **Permission Errors**
   - Check: Workflow has correct permissions
   - Fix: Add required permissions in workflow YAML

4. **Rate Limiting**
   - GitHub API rate limits reached
   - Wait and retry later

### No Changes Committed

**Problem**: Workflow runs successfully but no changes

**Possible reasons**:
1. No new content available (expected for KB updates)
2. Generated content identical to existing
3. Auto-fix had nothing to fix (self-test)

**This is normal** if:
- Official BrowserOS repo hasn't changed
- All tests passing
- No new workflows generated

---

## 🔐 Required Secrets

Some workflows require GitHub Secrets to be configured:

### Setting Secrets

1. Go to: Repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add required secrets:

| Secret Name | Required For | Purpose |
|------------|--------------|---------|
| `OLLAMA_API_KEY` | update-kb.yml | AI workflow generation via Kimi |
| `OPENROUTER_API_KEY` | update-kb.yml | Alternative AI provider |
| `GITHUB_TOKEN` | All workflows | Automatic (provided by GitHub) |

---

## 📈 Workflow Metrics

Track workflow effectiveness:

### Update KB Workflow
- **Frequency**: Weekly
- **Duration**: ~5-10 minutes
- **Changes per run**: Variable (0-100+ files)
- **Generated workflows**: 0-20 per run (when scheduled)

### Self-Test Workflow
- **Frequency**: Weekly + after updates
- **Duration**: ~2-5 minutes
- **Tests run**: 42
- **Auto-fix rate**: 85%+

---

## 🎯 Best Practices

1. **Schedule Regular Runs**: Let automated schedule work (weekly is good)
2. **Manual Trigger for Testing**: Use manual triggers when testing changes
3. **Monitor First Runs**: Watch first few runs closely
4. **Check Artifacts**: Download and review test results
5. **Review Issues**: Check auto-created issues weekly
6. **Update Secrets**: Rotate API keys periodically
7. **Tag Releases**: Workflows create tags automatically

---

## 📚 Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Files](.github/workflows/)
- [Automation Quickstart](AUTOMATION_QUICKSTART.md)
- [Repository Tracking](REPO_TRACKING.md)
- [Security Policy](SECURITY-POLICY.md)

---

## 🤝 Support

If workflows aren't working:

1. Check this guide
2. Review workflow logs
3. Check GitHub Actions status: https://www.githubstatus.com/
4. Open an issue with:
   - Workflow name
   - Run ID
   - Error messages
   - Screenshots

---

**Last Updated**: 2026-02-12  
**Version**: 1.0.0
