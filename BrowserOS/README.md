# BrowserOS Workflows Knowledge Base

This directory contains the comprehensive BrowserOS Workflows knowledge base, designed to be the definitive technical reference for workflow creation, automation, and integration.

## Directory Structure

```
BrowserOS/
├── structure.md                              # Research brief and KB index
├── Research/
│   ├── .gitkeep                             # Ensures directory is tracked
│   ├── BrowserOS_Workflows_KnowledgeBase.md # Complete technical KB (12 sections)
│   ├── sources.json                         # Source manifest with metadata
│   ├── verify_kb_completeness.ps1           # Self-verifying validation script
│   └── raw/                                 # Archived sources and cloned repos
│       ├── *.html                           # Archived web pages (gitignored)
│       └── browseros-ai-BrowserOS/          # Cloned official repo (gitignored)
```

## Key Files

### structure.md
The primary index file containing:
- **Research Brief**: Complete research objectives and target information
- **Deliverable**: Summary of knowledge base purpose
- **Knowledge Base Link**: Direct link to the comprehensive KB

### BrowserOS_Workflows_KnowledgeBase.md
Comprehensive technical reference with 12 H2 sections:
1. Overview & Scope
2. Architecture Diagram
3. Step Types Catalog (14+ step types)
4. Execution Flow Control Primer
5. Trigger & Integration Matrix
6. Configuration Schema Reference (Full JSON Schema)
7. Advanced / Enterprise Features
8. Limitations & Constraints
9. Security Best Practices
10. Community Patterns & Case Studies
11. Migration & Version History
12. Appendices (Glossary, Acronyms, FAQ, License)

### sources.json
Manifest of all research sources with:
- URL
- Access timestamp (ISO-8601)
- Author/handle
- Type (official_docs, github_repo, community_discussion, etc.)
- Abstract

### verify_kb_completeness.ps1
Self-verifying script that validates:
- **C01**: All required sections present
- **C02**: No placeholder markers (TODO, TBD, etc.)
- **C03**: All sources reachable and archived
- **C04**: YAML/JSON schema validation
- **C05**: Checksum stability
- **C06**: Git repository cleanliness and tagging

## Automation Scripts

Located in the repository root:

### update_kb.ps1
Weekly automation script that:
1. Pulls latest changes from this repository
2. Clones/updates official BrowserOS repository (https://github.com/browseros-ai/BrowserOS)
3. Runs research pipeline
4. Commits changes
5. Creates version tag (kb-YYYY.MM.DD)
6. Pushes to remote

**Schedule**: Configure in Windows Task Scheduler for weekly execution

**Usage**:
```powershell
# Normal run
.\update_kb.ps1

# Dry run (no commits/pushes)
.\update_kb.ps1 -DryRun
```

## Verification Workflow

The knowledge base includes a self-verifying loop that:
1. Runs all verification checks (C01-C06)
2. Logs failures with detailed information
3. Optionally auto-fixes issues by re-running research pipeline
4. Iterates until all checks pass (max 3 iterations)

**Usage**:
```powershell
# Run verification only
pwsh BrowserOS/Research/verify_kb_completeness.ps1

# Run with auto-fix
pwsh BrowserOS/Research/verify_kb_completeness.ps1 -AutoFix

# Custom max iterations
pwsh BrowserOS/Research/verify_kb_completeness.ps1 -MaxIterations 5
```

## Development Workflow

### Initial Setup
1. Repository already initialized with all required files
2. `.gitignore` configured (TextMate template + custom rules)
3. MIT LICENSE in place
4. Research directory structure created

### Weekly Updates
1. Task Scheduler runs `update_kb.ps1` weekly
2. Script auto-pulls from official BrowserOS GitHub
3. Research pipeline updates knowledge base
4. Changes committed and tagged automatically
5. Verification runs to ensure completeness

### Manual Updates
```powershell
# Pull latest from official BrowserOS repo
cd BrowserOS/Research/raw/browseros-ai-BrowserOS
git pull origin main

# Update knowledge base (manual editing)
# Edit: BrowserOS/Research/BrowserOS_Workflows_KnowledgeBase.md

# Verify changes
pwsh BrowserOS/Research/verify_kb_completeness.ps1

# Update checksum
Get-FileHash -Algorithm SHA256 BrowserOS/Research/BrowserOS_Workflows_KnowledgeBase.md | 
  Select-Object -ExpandProperty Hash | 
  Set-Content BrowserOS/Research/BrowserOS_Workflows_KnowledgeBase.md.checksum

# Commit
git add .
git commit -m "Manual KB update - [description]"
git tag "kb-$(Get-Date -Format 'yyyy.MM.dd')"
git push origin main --tags
```

## Knowledge Base Content

The KB covers:
- **Core Architecture**: How workflows are structured and executed
- **Step Types**: 14+ step types (navigate, click, input, extract, conditional, loop, parallel, code execution, file operations, API calls)
- **Programmatic Integration**: Python CodeAgent, lifecycle hooks, custom tools, MCP integration
- **Local Workspace**: Cowork integration, file system access, shell commands
- **Flow Control**: Branching, loops, parallel execution, error handling
- **Triggers**: Manual, scheduled, event-driven, API, file watch, webhook
- **Data Handling**: Variable interpolation, state management, extraction
- **Security**: Secrets management, input validation, XSS prevention, workspace isolation
- **Enterprise Features**: Workflow composition, deterministic execution, monitoring

## Contributing

### Adding New Sources
1. Update `Research/sources.json` with new source entry
2. Run verification script to archive the source
3. Update knowledge base with extracted information
4. Cite sources using footnotes in the KB

### Updating Knowledge Base
1. Make changes to `BrowserOS_Workflows_KnowledgeBase.md`
2. Ensure all 12 H2 sections remain present
3. Cite all facts with source references
4. Run verification script before committing
5. Update checksum file

### Testing
```powershell
# Validate JSON
Get-Content BrowserOS/Research/sources.json | ConvertFrom-Json

# Check PowerShell syntax
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
  'BrowserOS/Research/verify_kb_completeness.ps1', 
  [ref]$null, [ref]$null
)

# Run full verification
pwsh BrowserOS/Research/verify_kb_completeness.ps1
```

## License

This knowledge base is provided under the MIT License. See the repository LICENSE file for details.

## Support

For questions or issues:
- Open an issue in the GitHub repository
- Refer to the comprehensive KB in `Research/BrowserOS_Workflows_KnowledgeBase.md`
- Check the Appendices section for FAQ and troubleshooting

---

**Last Updated**: 2026-02-11  
**Version**: 1.0.0  
**Status**: ✅ All verification checks passing
