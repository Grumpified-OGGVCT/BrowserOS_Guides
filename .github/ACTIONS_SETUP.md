# GitHub Actions Automated KB Updates

This guide explains how to configure and use the automated Knowledge Base update system using GitHub Actions with Ollama and OpenRouter APIs.

## 🚀 Quick Start

The repository is now configured with automated weekly KB updates. To enable:

1. **Configure Secrets** (see below)
2. **Enable GitHub Actions** in repository settings
3. **Manual trigger** or wait for weekly schedule

## 🔐 Required Secrets

Add these secrets in **Settings → Secrets and variables → Actions**:

### OLLAMA_API_KEY
Your Ollama Cloud Service API key for LLM-powered research.

**How to get it:**
1. Visit https://ollama.ai (or your Ollama cloud provider)
2. Sign in to your account
3. Navigate to API Keys section
4. Copy your API key
5. Add as repository secret: `OLLAMA_API_KEY`

### OPENROUTER_API_KEY
Your OpenRouter API key for enhanced AI research capabilities.

**How to get it:**
1. Visit https://openrouter.ai
2. Sign in or create account
3. Go to Keys section
4. Create a new API key
5. Add as repository secret: `OPENROUTER_API_KEY`

### GITHUB_TOKEN (Automatic)
This is automatically provided by GitHub Actions. No configuration needed.

## 📅 Workflow Schedule

The workflow runs:
- **Automatically**: Every Sunday at 00:00 UTC
- **Manually**: Via GitHub Actions UI (workflow_dispatch)

## 🎯 What It Does

### 1. Repository Sync
- Clones/updates official BrowserOS repository
- Archives web sources for research

### 2. AI-Powered Research
- Uses **Ollama API** for local LLM processing
- Uses **OpenRouter API** for advanced Claude/GPT analysis
- Fetches latest documentation from multiple sources
- Analyzes code, issues, PRs, and discussions

### 3. Knowledge Base Update
- Synthesizes findings with AI
- Updates KB with new information
- Validates completeness (12 required sections)
- Checks for placeholders and quality

### 4. Automated Commit
- Commits changes to main branch
- Creates version tag (kb-YYYY.MM.DD)
- Generates summary in workflow output

## 🛠️ Manual Trigger

To manually trigger KB update:

1. Go to **Actions** tab
2. Select **Update BrowserOS Knowledge Base**
3. Click **Run workflow**
4. Optional: Check "Force full KB regeneration"
5. Click **Run workflow** button

## 📊 Monitoring

View workflow runs:
- **Actions** tab → **Update BrowserOS Knowledge Base**
- Check logs for each step
- View summary at bottom of each run

Success indicators:
- ✅ All steps green
- 📝 New commit with "🤖 Automated KB update"
- 🏷️ New tag: kb-YYYY.MM.DD

## 🔧 Configuration

### Workflow File
`.github/workflows/update-kb.yml`

Key settings:
```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight UTC
  workflow_dispatch:     # Manual trigger
```

### Research Pipeline
`scripts/research_pipeline.py`

Customizable:
- API endpoints
- Research sources
- AI prompts
- Update frequency

### Validation Script
`scripts/validate_kb.py`

Checks:
- C01: All 12 sections present
- C02: No placeholder markers
- C03: Valid sources.json
- C05: Checksum updates

## 🔍 Troubleshooting

### API Keys Not Working

**Symptoms**: Warnings about missing API keys
**Solution**: 
1. Verify secrets are set in repository settings
2. Check secret names match exactly: `OLLAMA_API_KEY`, `OPENROUTER_API_KEY`
3. Ensure API keys are valid and not expired

### No Changes Detected

**Symptoms**: Workflow completes but no commit
**Reason**: KB is already up-to-date
**Action**: Normal behavior - check logs for details

### Workflow Fails

**Common causes:**
1. **Rate limiting**: Wait and retry, or adjust API call frequency
2. **Invalid secrets**: Check API keys are correct
3. **Network issues**: Retry workflow
4. **Validation failure**: Check KB structure hasn't been corrupted

**Debug steps:**
1. View workflow logs in Actions tab
2. Check each step's output
3. Look for error messages
4. Manually run validation: `python scripts/validate_kb.py`

### Force Update

If KB needs full regeneration:
1. Manual trigger with "Force full KB regeneration" checked
2. Or set environment variable: `FORCE_UPDATE=true`

## 📁 File Structure

```
.github/workflows/
  └── update-kb.yml           # GitHub Actions workflow
scripts/
  ├── research_pipeline.py    # AI-powered research
  └── validate_kb.py          # KB validation
requirements.txt              # Python dependencies
BrowserOS/Research/
  ├── BrowserOS_Workflows_KnowledgeBase.md
  ├── sources.json
  └── raw/
      ├── *.html              # Archived web pages
      └── browseros-ai-BrowserOS/  # Cloned repo
```

## 🔄 Update Cycle

1. **Trigger**: Schedule (Sunday) or manual
2. **Clone**: Pull latest BrowserOS repository
3. **Research**: Fetch & analyze sources with AI
4. **Synthesize**: Generate insights with Ollama/OpenRouter
5. **Update**: Append findings to KB
6. **Validate**: Check completeness & quality
7. **Commit**: Push changes with version tag

## 🎓 Advanced Usage

### Custom Research Prompts

Edit `scripts/research_pipeline.py`:
```python
prompt = f"""Your custom research instructions here...
Research Summary:
{summary}
"""
```

### Add New Sources

Edit `BrowserOS/Research/sources.json`:
```json
{
  "url": "https://example.com/new-source",
  "accessed": "2026-02-11T00:00:00Z",
  "author": "Author Name",
  "type": "documentation",
  "abstract": "Brief description"
}
```

### Change Schedule

Edit `.github/workflows/update-kb.yml`:
```yaml
schedule:
  - cron: '0 0 * * *'  # Daily at midnight
  - cron: '0 */6 * * *'  # Every 6 hours
```

## 🤝 Contributing

To improve the automation:

1. **Test locally** first
2. **Document changes** in this file
3. **Update validation** if KB structure changes
4. **Monitor workflow** runs after changes

## 📞 Support

Issues with automation:
1. Check this documentation
2. View workflow logs
3. Test scripts locally: `python scripts/research_pipeline.py`
4. Open GitHub issue with logs

## 📜 License

Part of BrowserOS_Guides repository - MIT License
