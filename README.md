# BrowserOS_Guides

A self-maintaining, AI-powered knowledge base for BrowserOS Workflows. The repository automatically compiles and updates comprehensive guides from online sources using Ollama and OpenRouter APIs.

## 🤖 Automated KB Compilation

This repository features **GitHub Actions automation** that:
- 📚 Pulls latest information from official BrowserOS sources
- 🧠 Uses **Ollama** and **OpenRouter** AI APIs for intelligent analysis
- 📝 Compiles comprehensive technical documentation
- ✅ Self-validates and maintains completeness
- 🔄 Updates weekly (every Sunday) automatically

### Quick Setup

1. **Add API Keys** to repository secrets:
   - `OLLAMA_API_KEY` - Your Ollama Cloud Service key
   - `OPENROUTER_API_KEY` - Your OpenRouter API key

2. **Enable GitHub Actions** with write permissions

3. **Manual trigger** or wait for weekly schedule

📖 **Full Setup Guide**: [AUTOMATION_QUICKSTART.md](AUTOMATION_QUICKSTART.md)

## 📁 Repository Structure

```
BrowserOS/
├── structure.md              # Primary index with research brief
├── README.md                 # Complete usage guide
└── Research/
    ├── BrowserOS_Workflows_KnowledgeBase.md  # Comprehensive KB (641 lines)
    ├── sources.json          # 12 research sources manifest
    ├── verify_kb_completeness.ps1  # Validation script
    └── raw/                  # Archived sources & cloned repos

.github/
├── workflows/
│   └── update-kb.yml         # GitHub Actions automation
└── ACTIONS_SETUP.md          # Detailed automation docs

scripts/
├── research_pipeline.py      # AI-powered research engine
└── validate_kb.py            # KB validation (C01-C05)

requirements.txt              # Python dependencies
update_kb.ps1                 # PowerShell automation script
```

## 🎯 Knowledge Base Features

The KB covers BrowserOS Workflows comprehensively:

- **Core Architecture** - How workflows are structured and executed
- **14+ Step Types** - Navigate, click, input, extract, conditional, loops, parallel, code execution
- **Programmatic Integration** - Python CodeAgent, lifecycle hooks, custom tools
- **Local Workspace** - Cowork integration for file system access
- **Flow Control** - Branching, loops, parallel execution, error handling
- **Security** - Secrets management, input validation, XSS prevention
- **Enterprise Features** - Workflow composition, deterministic execution, monitoring

## 🔄 Automation Workflow

```
GitHub Actions (Weekly)
    │
    ├─→ Clone BrowserOS repo
    ├─→ Fetch web sources
    ├─→ AI Analysis (Ollama + OpenRouter)
    ├─→ Synthesize findings
    ├─→ Update KB
    ├─→ Validate completeness
    └─→ Commit & Tag (kb-YYYY.MM.DD)
```

## 🚀 Getting Started

### View the Knowledge Base

Navigate to: [BrowserOS/Research/BrowserOS_Workflows_KnowledgeBase.md](BrowserOS/Research/BrowserOS_Workflows_KnowledgeBase.md)

### Enable Automation

See: [AUTOMATION_QUICKSTART.md](AUTOMATION_QUICKSTART.md)

### Validate Locally

```bash
pip install -r requirements.txt
python scripts/validate_kb.py
```

## 📊 Validation Checks

All KB updates must pass:
- ✅ **C01**: All 12 required sections present
- ✅ **C02**: No placeholder markers (TODO, TBD, etc.)
- ✅ **C03**: Valid sources.json with metadata
- ✅ **C04**: Schema validation for code snippets
- ✅ **C05**: Checksum stability tracking
- ✅ **C06**: Git cleanliness and tagging

## 🔗 Official Sources

Primary research sources:
- [BrowserOS Official Docs](https://docs.browseros.com)
- [BrowserOS GitHub](https://github.com/browseros-ai/BrowserOS) ⭐
- [workflow-use Repository](https://github.com/browser-use/workflow-use)
- [Browser Use Docs](https://docs.browser-use.com)

## 📅 Update Schedule

- **Automatic**: Every Sunday at 00:00 UTC
- **Manual**: Via GitHub Actions workflow_dispatch
- **Version Tags**: kb-YYYY.MM.DD format

## 🛠️ Local Development

### Test Research Pipeline

```bash
export OLLAMA_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"
python scripts/research_pipeline.py
```

### Validate KB

```bash
python scripts/validate_kb.py
```

### Manual Update (PowerShell)

```powershell
.\update_kb.ps1 -DryRun  # Test without committing
.\update_kb.ps1           # Full update
```

## 🤝 Contributing

Improvements welcome:
1. Fork repository
2. Create feature branch
3. Test automation locally
4. Submit PR with description

## 📜 License

MIT License - See [LICENSE](LICENSE)

## 💡 Learn More

- **Automation Setup**: [AUTOMATION_QUICKSTART.md](AUTOMATION_QUICKSTART.md)
- **Detailed Docs**: [.github/ACTIONS_SETUP.md](.github/ACTIONS_SETUP.md)
- **KB Structure**: [BrowserOS/README.md](BrowserOS/README.md)
- **Primary Index**: [BrowserOS/structure.md](BrowserOS/structure.md)
