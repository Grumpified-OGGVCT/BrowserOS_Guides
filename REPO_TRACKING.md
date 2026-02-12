# 🔄 GitHub Repository Tracking & Database Maintenance

## Overview

The BrowserOS KB now maintains an **intelligent database** that tracks the official repository state through direct GitHub access. This enables:

✅ **Incremental Updates** - Only process new commits/releases since last run  
✅ **Change Detection** - Automatically identify new features, bug fixes, breaking changes  
✅ **Smart Initialization** - Bootstrap from existing releases and commit history  
✅ **Version Tracking** - Maintain complete release and change history  
✅ **Zero Duplication** - Never re-process the same commits

## How It Works

### 1. Database Initialization (First Run)

On first run, the system:
1. Connects to https://github.com/browseros-ai/BrowserOS via GitHub API
2. Fetches all releases (tags, notes, assets)
3. Loads recent commit history (last 100 commits)
4. Saves initial state to `BrowserOS/Research/repo_state.json`

```bash
# First run creates the database
python scripts/research_pipeline.py
```

**Output**:
```
📚 First run detected - initializing repository database...
✓ Loaded 15 releases
✓ Loaded 100 recent commits
✓ Repository database initialized
```

### 2. Incremental Updates (Subsequent Runs)

On subsequent runs, the system:
1. Loads previous state from `repo_state.json`
2. Fetches only NEW commits since `last_commit_sha`
3. Fetches only NEW releases since `last_release_tag`
4. Analyzes changes and categorizes them
5. Updates KB with only relevant new information
6. Saves updated state

```bash
# Subsequent runs are incremental
python scripts/research_pipeline.py
```

**Output**:
```
🔄 Getting incremental updates since last run...
✓ Found 5 new commits
✓ Found 1 new releases

Commit analysis:
  - features: 2 commits
  - bug_fixes: 2 commits
  - documentation: 1 commits
```

## Repository State Database

### File: `BrowserOS/Research/repo_state.json`

```json
{
  "repo_name": "browseros-ai/BrowserOS",
  "last_commit_sha": "abc123...",
  "last_commit_date": "2026-02-10T15:30:00Z",
  "last_release_tag": "v2.5.0",
  "last_release_date": "2026-02-01T00:00:00Z",
  "last_updated": "2026-02-11T22:00:00Z",
  "total_commits_processed": 247,
  "total_releases_processed": 15
}
```

### Fields

| Field | Description |
|-------|-------------|
| `repo_name` | Repository being tracked |
| `last_commit_sha` | SHA of last processed commit |
| `last_commit_date` | Timestamp of last commit |
| `last_release_tag` | Tag name of last release (e.g., v2.5.0) |
| `last_release_date` | Publication date of last release |
| `last_updated` | When state was last updated |
| `total_commits_processed` | Cumulative commit count |
| `total_releases_processed` | Cumulative release count |

## Features

### 1. Commit Analysis

Automatically categorizes commits by keywords:

- **Features**: `feat`, `feature`, `add`, `implement`, `new`
- **Bug Fixes**: `fix`, `bug`, `issue`, `resolve`, `patch`
- **Breaking Changes**: `breaking`, `break`, `major`, `remove`
- **Documentation**: `docs`, `doc`, `documentation`, `readme`
- **Deprecations**: `deprecate`, `deprecated`, `obsolete`

Example analysis:
```python
{
  'features': [
    {'message': 'feat: Add parallel workflow execution', 'sha': 'abc1234'}
  ],
  'bug_fixes': [
    {'message': 'fix: Resolve timeout in step execution', 'sha': 'def5678'}
  ],
  'breaking_changes': [
    {'message': 'breaking: Remove deprecated API methods', 'sha': 'ghi9012'}
  ]
}
```

### 2. Release Tracking

Extracts complete release information:

```python
{
  'tag': 'v2.5.0',
  'name': 'BrowserOS Workflows v2.5.0',
  'published_at': '2026-02-01T00:00:00Z',
  'author': 'browseros-team',
  'body': 'Release notes markdown...',
  'url': 'https://github.com/browseros-ai/BrowserOS/releases/tag/v2.5.0',
  'is_prerelease': False,
  'assets': [
    {'name': 'browseros-v2.5.0.tar.gz', 'download_url': '...', 'size': 1048576}
  ]
}
```

### 3. Changelog Parsing

Automatically parses `CHANGELOG.md` into structured data:

```python
{
  '[2.5.0] - 2026-02-01': '### Added\n- New feature X\n### Fixed\n- Bug Y',
  '[2.4.0] - 2026-01-15': '### Changed\n- Updated API\n...'
}
```

## Direct API Access Benefits

### Why Direct GitHub Access?

✅ **More Accurate** - Get exact commit data, not scraped HTML  
✅ **Structured Data** - JSON responses, not parsed HTML  
✅ **Complete History** - Access full git history programmatically  
✅ **Real-time** - Get updates as they happen  
✅ **Efficient** - Only fetch what changed (incremental)  
✅ **Reliable** - Official API, not brittle web scraping

### Comparison

| Method | Data Quality | Performance | Maintenance |
|--------|--------------|-------------|-------------|
| **Web Scraping** | Medium | Slow | High (breaks often) |
| **Repo Clone** | Good | Medium | Medium |
| **GitHub API** ⭐ | Excellent | Fast | Low |

## Usage

### Standalone Testing

```bash
# Test repo tracker
python scripts/repo_tracker.py

# Output:
# First run detected - initializing...
# ✓ Initialized with 15 releases, 100 commits
# 
# Repository State Summary
# ========================
# Repository: browseros-ai/BrowserOS
# Last Commit: abc1234... (2026-02-10T15:30:00Z)
# Last Release: v2.5.0 (2026-02-01T00:00:00Z)
# Total Commits Processed: 100
# Total Releases Processed: 15
```

### Integrated with Pipeline

```bash
# Full research pipeline (includes GitHub tracking)
python scripts/research_pipeline.py

# Output:
# 🚀 Starting AI-Powered KB Research Pipeline with GitHub Tracking
# 🔍 Checking GitHub repository for updates...
# ✅ GitHub updates detected:
#   - 5 new commits
#   - 1 new releases
# 📚 Analyzing BrowserOS repository...
# 🤖 Synthesizing knowledge base updates with AI...
# ✅ Knowledge base updated
```

### GitHub Actions Integration

The workflow automatically uses repo tracking:

```yaml
# .github/workflows/update-kb.yml
- name: Run AI-powered research pipeline
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # For API access
    OLLAMA_API_KEY: ${{ secrets.OLLAMA_API_KEY }}
    OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
  run: |
    python scripts/research_pipeline.py
```

## Configuration

### Environment Variables

```bash
# Required for GitHub API access
export GITHUB_TOKEN="your_github_token"

# For rate limiting (optional)
export GITHUB_API_MAX_RETRIES=3
export GITHUB_API_TIMEOUT=30
```

### Rate Limits

- **Without token**: 60 requests/hour
- **With token**: 5000 requests/hour

Recommendation: Always use a GitHub token in GitHub Actions.

## Advanced Features

### 1. Force Full Refresh

```bash
# Ignore cache, re-fetch everything
export FORCE_UPDATE=true
python scripts/research_pipeline.py
```

### 2. Custom State File

```python
from scripts.repo_tracker import GitHubRepoTracker

tracker = GitHubRepoTracker(
    repo_name="browseros-ai/BrowserOS",
    state_file=Path("custom/path/repo_state.json")
)
```

### 3. Track Multiple Repos

```python
# Track official repo
main_tracker = GitHubRepoTracker("browseros-ai/BrowserOS")

# Track workflow-use repo
workflow_tracker = GitHubRepoTracker(
    "browser-use/workflow-use",
    state_file=Path("workflow_repo_state.json")
)
```

## Maintenance

### Reset State

```bash
# Delete state file to start fresh
rm BrowserOS/Research/repo_state.json

# Next run will re-initialize
python scripts/research_pipeline.py
```

### View Current State

```bash
# Pretty-print current state
cat BrowserOS/Research/repo_state.json | python3 -m json.tool
```

### Backup State

```bash
# Backup before major changes
cp BrowserOS/Research/repo_state.json \
   BrowserOS/Research/repo_state.$(date +%Y%m%d).backup
```

## Troubleshooting

### Issue: "GitHub API not available"

**Cause**: PyGithub not installed  
**Solution**: `pip install PyGithub`

### Issue: "Rate limit exceeded"

**Cause**: Too many API requests without token  
**Solution**: Set `GITHUB_TOKEN` environment variable

### Issue: "No updates detected"

**Cause**: Repository hasn't changed since last run  
**Action**: This is normal behavior - no action needed

### Issue: "State file corrupted"

**Cause**: Invalid JSON in state file  
**Solution**: Delete file and re-initialize:
```bash
rm BrowserOS/Research/repo_state.json
python scripts/research_pipeline.py
```

## Benefits

### For Users

- ✅ Always up-to-date with latest BrowserOS changes
- ✅ Never miss new features or releases
- ✅ Automatic change categorization
- ✅ Incremental updates (fast)

### For Maintainers

- ✅ No manual tracking needed
- ✅ Reduces API calls (incremental)
- ✅ Easy to debug (structured state file)
- ✅ Extensible to other repos

### For the KB

- ✅ More accurate information
- ✅ Timely updates
- ✅ Better coverage of changes
- ✅ Automatic version tracking

## Future Enhancements

- 🔮 **Webhook Integration** - Real-time updates on push events
- 🔮 **Multi-repo Tracking** - Track related repositories simultaneously
- 🔮 **Advanced Analytics** - Contributor stats, code frequency
- 🔮 **Semantic Analysis** - AI-powered commit message understanding
- 🔮 **Automated Changelog** - Generate KB changelog from commits
- 🔮 **Version Comparison** - Diff between any two versions

## Summary

The repository tracking system transforms the KB from a periodic web scraper into an **intelligent, event-driven knowledge base** that maintains itself through direct repository access. It's a no-brainer! 🚀
