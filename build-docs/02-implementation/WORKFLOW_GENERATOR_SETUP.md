# Workflow Generator Setup Guide

## Quick Start: Using the Web Interface

The workflow generator web interface requires the **OLLAMA_API_KEY** to function. Here's how to set it up:

### Option 1: Local Development (Recommended)

1. **Get your Ollama API Key:**
   - Sign up at https://ollama.ai
   - Navigate to https://ollama.ai/keys
   - Generate a new API key
   - Copy it (you'll only see it once!)

2. **Set the environment variable:**

   **On Linux/macOS:**
   ```bash
   export OLLAMA_API_KEY="your-api-key-here"
   ```

   **On Windows (PowerShell):**
   ```powershell
   $env:OLLAMA_API_KEY="your-api-key-here"
   ```

   **On Windows (CMD):**
   ```cmd
   set OLLAMA_API_KEY=your-api-key-here
   ```

3. **Start the MCP server:**
   ```bash
   npm run mcp-server
   ```

4. **Open the web interface:**
   ```bash
   # In another terminal
   cd docs
   python3 -m http.server 8080
   # Visit http://localhost:8080/#tools
   ```

5. **Generate your workflow!**
   - Fill out the form
   - Click "Generate My Workflow"
   - Wait 10-15 seconds
   - Download or copy the result

### Option 2: Using .env File (Persistent)

1. **Copy the template:**
   ```bash
   cp .env.template .env
   ```

2. **Edit .env file:**
   ```bash
   # Open in your favorite editor
   nano .env
   # or
   code .env
   ```

3. **Update the OLLAMA_API_KEY line:**
   ```
   OLLAMA_API_KEY=your-actual-api-key-here
   ```

4. **Load environment variables:**
   ```bash
   # Linux/macOS
   set -a && source .env && set +a
   
   # Or use direnv (recommended)
   echo 'dotenv' > .envrc
   direnv allow
   ```

5. **Start the server:**
   ```bash
   npm run mcp-server
   ```

### Option 3: Docker (Easiest)

1. **Create .env file with your key:**
   ```bash
   echo "OLLAMA_API_KEY=your-key-here" > .env
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose --profile full up
   ```

3. **Access the interface:**
   - MCP Server: http://localhost:3100
   - Web Interface: http://localhost:8080 (if using docs service)

---

## Available API Keys (Organization Secrets)

Your organization has these secrets configured:

| Secret Name | Purpose | Required For |
|------------|---------|--------------|
| `OLLAMA_API_KEY` | Kimi AI via Ollama Cloud | ✅ **Workflow Generator** |
| `OLLAMA_PROXY_API_KEY` | Ollama proxy service | Optional |
| `OLLAMA_TURBO_CLOUD_API_KEY` | Turbo cloud models | Optional |
| `GH_PAT` | GitHub API access | Research workflows |
| `NOSTR_PRIVATE_KEY` | Nostr integration | Future features |
| `SUPABASE_KEY` | Supabase backend | Optional |

**Note:** Organization secrets are automatically available in GitHub Actions but must be set manually for local development.

---

## Troubleshooting

### "Check if OLLAMA_API_KEY is set" Error

**Problem:** The workflow generator can't find your API key.

**Solutions:**
1. Verify the environment variable is set:
   ```bash
   echo $OLLAMA_API_KEY  # Linux/macOS
   echo %OLLAMA_API_KEY%  # Windows CMD
   $env:OLLAMA_API_KEY    # Windows PowerShell
   ```

2. If empty, export it again:
   ```bash
   export OLLAMA_API_KEY="your-key-here"
   ```

3. Restart the MCP server after setting the variable

### "Connection refused" or "ERR_CONNECTION_REFUSED"

**Problem:** MCP server isn't running.

**Solution:**
```bash
# Make sure the server is running
npm run mcp-server

# Check if it's listening
curl http://localhost:3100/mcp/health
```

### "Generation failed" or Timeout

**Possible causes:**
1. **Invalid API key** - Check your key at https://ollama.ai/keys
2. **Rate limiting** - Wait a few minutes and try again
3. **API outage** - Check https://status.ollama.ai

### Safety Filter Rejection

**Problem:** "This use case was rejected by safety filters"

**Explanation:** The public generator includes safety filters for NSFW and illegal content.

**Solutions:**
1. Rephrase your use case with more context (e.g., "payment processing for my checkout")
2. For legitimate use cases that trigger filters, run a private instance
3. See `docs/SAFETY_POLICY.md` for details

---

## Testing the Setup

### 1. Test the API Key
```bash
# Set the key
export OLLAMA_API_KEY="your-key-here"

# Test with Python directly
python3 -c "
import os
print('API Key set:', 'OLLAMA_API_KEY' in os.environ)
print('First 10 chars:', os.getenv('OLLAMA_API_KEY', '')[:10])
"
```

### 2. Test the MCP Server
```bash
# Start server
npm run mcp-server &

# Test health
curl http://localhost:3100/mcp/health

# Test workflow generation (replace with your key)
curl -X POST http://localhost:3100/api/generate-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "use_case": "monitor competitor prices",
    "industry": "e-commerce",
    "complexity": "medium"
  }'
```

### 3. Test the CLI Directly
```bash
# Test with a simple use case
python3 scripts/workflow_generator.py idea \
  --use-case "send daily summary emails" \
  --industry "productivity"
```

---

## For GitHub Actions (Already Configured!)

The organization secrets are automatically available in workflows. Nothing to do! ✅

The `update-kb.yml` workflow already uses `OLLAMA_API_KEY`:
```yaml
- name: Generate new workflow ideas (Weekly with Kimi)
  env:
    OLLAMA_API_KEY: ${{ secrets.OLLAMA_API_KEY }}
  run: |
    python scripts/workflow_generator.py full --use-case "..."
```

---

## Security Best Practices

### ✅ DO:
- Store API keys in environment variables or .env
- Add `.env` to `.gitignore` (already done)
- Use different keys for dev/staging/production
- Rotate keys periodically
- Use organization secrets for GitHub Actions

### ❌ DON'T:
- Commit API keys to Git
- Share keys in chat/email
- Use production keys in development
- Hardcode keys in source code
- Leave keys in shell history

---

## Getting More API Keys

### Ollama Cloud (Required)
- Free tier: Limited requests/month
- Paid plans: Higher limits + priority
- Sign up: https://ollama.ai/signup

### Alternative: Self-Hosted Ollama
If you don't want to use Ollama Cloud:
1. Install Ollama locally: https://ollama.ai/download
2. Pull the Kimi model: `ollama pull kimi-k2.5`
3. Update `scripts/workflow_generator.py` to use local endpoint
4. No API key needed!

---

## Need Help?

- 📖 Full docs: `README.md`
- 🛡️ Safety policy: `docs/SAFETY_POLICY.md`
- 🐛 Issues: https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/issues
- 💬 Discussions: https://github.com/Grumpified-OGGVCT/BrowserOS_Guides/discussions

---

**Ready to generate workflows!** 🚀
