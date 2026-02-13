# GitHub Actions Workflows

This directory contains all automated workflows for the BrowserOS_Guides repository.

## 📋 Available Workflows

### Core Workflows

#### 1. Update BrowserOS Knowledge Base (`update-kb.yml`)
**Purpose**: Keeps repository synchronized with official BrowserOS sources

**Triggers**:
- 🕐 **Scheduled**: Weekly on Sundays at 00:00 UTC
- ⚡ **Manual**: Via workflow_dispatch

**What it does**:
- Clones/updates official BrowserOS repository
- Runs AI-powered research pipeline
- Validates knowledge base completeness
- Generates new workflows using Kimi-K2.5:cloud (on schedule)
- Updates repository structure JSON
- Regenerates search index
- Commits changes and creates version tag

**Duration**: ~5-10 minutes

---

#### 2. Self-Test & Quality Assurance (`self-test.yml`)
**Purpose**: Automated testing and quality validation

**Triggers**:
- 🕐 **Scheduled**: Weekly on Sundays at 02:00 UTC
- 🔗 **After**: Update KB workflow completes
- ⚡ **Manual**: Via workflow_dispatch

**What it does**:
- Runs comprehensive security scan
- Executes 42 self-tests covering:
  - KB completeness
  - Search index validity
  - Website assets
  - Workflow validation
  - Documentation links
  - Python script syntax
- Auto-fixes 85%+ of issues
- Creates GitHub issues for manual review

**Duration**: ~2-5 minutes

---

#### 3. Deploy to GitHub Pages (`deploy-pages.yml`)
**Purpose**: Deploys documentation website

**Triggers**:
- 🔀 **Push**: When changes pushed to main branch (docs/, BrowserOS/, scripts/ paths)
- ⚡ **Manual**: Via workflow_dispatch

**What it does**:
- Generates repository structure JSON
- Generates search index
- Builds GitHub Pages site
- Deploys to https://grumpified-oggvct.github.io/BrowserOS_Guides/

**Duration**: ~2-3 minutes

---

### Utility Workflows

#### 4. Trigger All Workflows (`trigger-all-workflows.yml`)
**Purpose**: Convenience workflow to trigger other workflows

**Triggers**:
- ⚡ **Manual only**: Via workflow_dispatch

**What it does**:
- Triggers Update KB workflow (optional)
- Triggers Self-Test workflow (optional)
- Triggers Deploy Pages workflow (optional)
- Provides summary of triggered workflows

**Duration**: <1 minute

---

### GitHub Managed Workflows

#### 5. Automatic Dependency Submission
**Purpose**: Submits dependency graph to GitHub
**Status**: Auto-managed by GitHub

#### 6. Copilot Code Review
**Purpose**: Automated code review on pull requests
**Status**: Auto-managed by GitHub Copilot

#### 7. Copilot Coding Agent
**Purpose**: Automated coding assistance
**Status**: Auto-managed by GitHub Copilot

#### 8. Pages Build and Deployment
**Purpose**: GitHub Pages deployment
**Status**: Auto-managed by GitHub Pages

---

## 🚀 How to Trigger Workflows

### Method 1: GitHub Web Interface (Recommended)

1. Go to [Actions tab](https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/actions)
2. Select workflow from left sidebar
3. Click "Run workflow" dropdown (right side)
4. Select branch (usually `main`)
5. Configure inputs if available
6. Click green "Run workflow" button

### Method 2: Use Trigger All Workflows

**Easiest way to test all workflows at once:**

1. Go to [Actions tab](https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/actions)
2. Click "Trigger All Workflows" in left sidebar
3. Click "Run workflow"
4. Select which workflows to trigger:
   - ✅ Trigger Update KB workflow (default: on)
   - ✅ Trigger Self-Test workflow (default: on)
   - ⬜ Trigger Deploy Pages workflow (default: off)
5. Click "Run workflow"

### Method 3: GitHub CLI

```bash
# Trigger Update KB
gh workflow run update-kb.yml --repo Grumpified-OGGVCT/BrowserOS_Guides --ref main -f force_update=false

# Trigger Self-Test
gh workflow run self-test.yml --repo Grumpified-OGGVCT/BrowserOS_Guides --ref main -f force_fix=true

# Trigger Deploy Pages
gh workflow run deploy-pages.yml --repo Grumpified-OGGVCT/BrowserOS_Guides --ref main

# Trigger all at once (easier)
gh workflow run trigger-all-workflows.yml --repo Grumpified-OGGVCT/BrowserOS_Guides --ref main
```

### Method 4: Python Scripts

```bash
# Test workflow syntax and configuration
python scripts/test_all_workflows.py

# Attempt to trigger workflows (requires gh CLI with auth)
python scripts/trigger_workflows.py
```

---

## 📊 Workflow Status

Check the current status of all workflows:

```bash
# List all workflows
gh workflow list --repo Grumpified-OGGVCT/BrowserOS_Guides

# List recent runs
gh run list --repo Grumpified-OGGVCT/BrowserOS_Guides --limit 10

# Check specific workflow
gh run list --workflow=update-kb.yml --repo Grumpified-OGGVCT/BrowserOS_Guides
```

Or visit: https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/actions

---

## ⚙️ Required Secrets

Some workflows require repository secrets:

| Secret | Required For | Purpose |
|--------|--------------|---------|
| `OLLAMA_API_KEY` | update-kb.yml | AI workflow generation via Kimi |
| `OPENROUTER_API_KEY` | update-kb.yml | Alternative AI provider |
| `GITHUB_TOKEN` | All workflows | Automatic (provided by GitHub) |

**To add secrets:**
1. Go to Repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add name and value
4. Click "Add secret"

---

## 📈 Workflow Schedule

Automated runs occur on this schedule:

| Day | Time (UTC) | Workflow | Action |
|-----|-----------|----------|---------|
| Sunday | 00:00 | Update KB | Sync and update |
| Sunday | 02:00 | Self-Test | Validate and test |
| Any push | On-demand | Deploy Pages | Deploy website |

---

## 🔍 Monitoring

### View Workflow Logs

1. Go to [Actions tab](https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/actions)
2. Click on a workflow run
3. Click on a job name
4. Expand steps to see detailed output

### Download Artifacts

Some workflows produce artifacts:

- **Self-Test**: Test results JSON, security reports
- **Deploy Pages**: Site build artifacts

To download:
1. Go to workflow run page
2. Scroll to "Artifacts" section
3. Click artifact name to download

---

## 🛠️ Troubleshooting

### Workflow Not Starting
- Check permissions (Actions must be enabled)
- Verify workflow syntax (use `test_all_workflows.py`)
- Check GitHub Actions status: https://www.githubstatus.com/

### Workflow Failing
- Check logs for error messages
- Verify required secrets are configured
- Check if dependencies are up to date
- Review recent code changes

### No Changes Committed
- This is often normal (no changes needed)
- Check workflow logs to verify it ran
- Ensure source data has changed
- Verify permissions to commit

---

## 📚 Related Documentation

- [WORKFLOW_TRIGGER_GUIDE.md](../../WORKFLOW_TRIGGER_GUIDE.md) - Detailed trigger guide
- [WORKFLOW_VERIFICATION_REPORT.md](../../build-docs/05-final-verification/WORKFLOW_VERIFICATION_REPORT.md) - Testing report
- [AUTOMATION_QUICKSTART.md](../../AUTOMATION_QUICKSTART.md) - Automation overview
- [SECURITY-POLICY.md](../../SECURITY-POLICY.md) - Security guidelines

---

## 📝 Workflow Development

When adding new workflows:

1. Create `.yml` file in this directory
2. Follow existing naming conventions
3. Include proper triggers and permissions
4. Add documentation to this README
5. Test with `test_all_workflows.py`
6. Update related documentation

---

**Last Updated**: 2026-02-12  
**Total Workflows**: 8 (4 custom + 4 GitHub-managed)
