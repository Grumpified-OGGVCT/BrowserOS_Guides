# 🤖 Automated KB Update - Quick Setup Guide

## Prerequisites

Organization has API keys for:
- ✅ **Ollama Cloud Service** - For local LLM processing
- ✅ **OpenRouter** - For enhanced AI research (Claude, GPT-4, etc.)

## Setup Steps (5 minutes)

### 1. Add API Keys to GitHub Secrets

Navigate to: **Repository Settings → Secrets and variables → Actions → New repository secret**

Add these two secrets:

| Secret Name | Value | Get it from |
|-------------|-------|-------------|
| `OLLAMA_API_KEY` | Your Ollama API key | https://ollama.ai/keys |
| `OPENROUTER_API_KEY` | Your OpenRouter key | https://openrouter.ai/keys |

### 2. Enable GitHub Actions

1. Go to **Settings → Actions → General**
2. Under "Workflow permissions":
   - ✅ Select "Read and write permissions"
   - ✅ Check "Allow GitHub Actions to create and approve pull requests"
3. Click **Save**

### 3. Test the Workflow

#### Manual Run (Recommended First Time):

1. Go to **Actions** tab
2. Select **"Update BrowserOS Knowledge Base"**
3. Click **"Run workflow"** dropdown
4. Select branch: `main` (or current branch)
5. Optional: Check **"Force full KB regeneration"**
6. Click green **"Run workflow"** button

#### Monitor Progress:

- Watch workflow run in real-time
- Check each step's output
- View summary at bottom of run
- Look for ✅ green checkmarks

### 4. Verify Results

After successful run, check:

- [ ] New commit with "🤖 Automated KB update"
- [ ] New tag: `kb-YYYY.MM.DD`
- [ ] KB file updated: `BrowserOS/Research/BrowserOS_Workflows_KnowledgeBase.md`
- [ ] "Latest Updates" section added at bottom

## Automatic Schedule

Once enabled, workflow runs:
- 📅 **Every Sunday at midnight UTC**
- 🔄 **Automatically** (no manual intervention)
- 🤖 **Self-maintaining** KB compilation

## What It Does

```
┌─────────────────────────────────────────────┐
│  1. Clone BrowserOS Official Repo           │
│     https://github.com/browseros-ai/BrowserOS
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  2. Fetch & Archive Web Sources             │
│     • Documentation sites                    │
│     • GitHub issues/PRs                      │
│     • Community discussions                  │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  3. AI-Powered Analysis                      │
│     • Ollama: Local LLM processing          │
│     • OpenRouter: Claude/GPT research       │
│     • Extract key insights & changes        │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  4. Synthesize & Update KB                   │
│     • Generate findings summary              │
│     • Append to knowledge base              │
│     • Validate completeness                 │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  5. Commit & Tag                             │
│     • Auto-commit changes                    │
│     • Create version tag                     │
│     • Push to repository                     │
└──────────────────────────────────────────────┘
```

## Troubleshooting

### ❌ Workflow Not Showing Up
**Problem**: Can't see workflow in Actions tab  
**Solution**: 
1. Ensure files are on `main` branch
2. Merge PR if on feature branch
3. Check `.github/workflows/update-kb.yml` exists

### ❌ API Key Errors
**Problem**: "API key not configured" warnings  
**Solution**:
1. Double-check secret names (case-sensitive)
2. Verify keys are valid and not expired
3. Test keys with API provider's test endpoint

### ❌ No Changes Committed
**Problem**: Workflow runs but no commit  
**Reason**: KB is already up-to-date (normal behavior)  
**Action**: Check workflow logs for "No updates needed"

### ❌ Validation Fails
**Problem**: KB validation step fails  
**Solution**:
1. Check KB structure hasn't been manually corrupted
2. Verify all 12 required sections present
3. Look for placeholder markers (TODO, TBD)
4. Run locally: `python scripts/validate_kb.py`

## Cost Considerations

### Ollama API
- Charges per token/request
- KB updates use ~2000-4000 tokens per run
- Weekly runs: ~16K tokens/month
- **Estimate**: $1-5/month depending on model

### OpenRouter API
- Pay-per-use pricing
- Claude Sonnet: ~$3 per million tokens
- KB updates use ~4000 tokens per run
- **Estimate**: $0.50-2/month

**Total**: ~$1.50-7/month for automated KB maintenance

## Advanced Configuration

### Change Schedule

Edit `.github/workflows/update-kb.yml`:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'    # Daily at midnight
    - cron: '0 */12 * * *' # Every 12 hours
    - cron: '0 0 * * 1,4'  # Monday & Thursday only
```

### Customize AI Prompts

Edit `scripts/research_pipeline.py`:

```python
prompt = f"""Your custom instructions for AI research...

Focus on:
1. New feature announcements
2. Breaking changes
3. Security updates
...
"""
```

### Add More Sources

Edit `BrowserOS/Research/sources.json`:

```json
{
  "url": "https://your-new-source.com",
  "accessed": "2026-02-11T00:00:00Z",
  "author": "Author Name",
  "type": "documentation",
  "abstract": "What this source covers"
}
```

## Support

📖 **Full Documentation**: [.github/ACTIONS_SETUP.md](.github/ACTIONS_SETUP.md)

🔧 **Test Locally**: 
```bash
pip install -r requirements.txt
python scripts/research_pipeline.py
python scripts/validate_kb.py
```

❓ **Issues**: Open GitHub issue with:
- Workflow run URL
- Error messages from logs
- Steps already tried

## Success Checklist

- [ ] API keys added to GitHub Secrets
- [ ] GitHub Actions permissions configured
- [ ] Manual workflow run successful
- [ ] Commit and tag created
- [ ] KB updated with new section
- [ ] All validation checks passed
- [ ] Automatic schedule enabled

**Congratulations! Your KB is now self-maintaining! 🎉**

---

Next scheduled update: Check **Actions** tab for countdown
