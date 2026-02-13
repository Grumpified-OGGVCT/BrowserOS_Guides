# Windows Setup Guide

## Prerequisites

1. **Python 3.11+** — Download from [python.org](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation
2. **Node.js 14+** — Download from [nodejs.org](https://nodejs.org/)
3. **Git** — Download from [git-scm.com](https://git-scm.com/)

## Installation

```batch
git clone https://github.com/Grumpified-OGGVCT/BrowserOS_Guides.git
cd BrowserOS_Guides
install.bat
```

## Configuration

1. Copy `.env.template` to `.env`
2. Edit `.env` and add your API keys:
   - `OLLAMA_API_KEY` — For workflow generation
   - `OPENROUTER_API_KEY` — For enhanced AI research
   - `GITHUB_TOKEN` — For repository tracking

## Running

```batch
run.bat
```

This opens an interactive menu with options to:
- Start the MCP Server
- Run the research pipeline
- Validate the knowledge base
- Run self-tests

## MCP Server

```batch
npm start
```

The server starts at `http://localhost:3100/mcp`.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `python` not found | Reinstall Python with "Add to PATH" checked |
| `node` not found | Restart your terminal after installing Node.js |
| Port 3100 in use | Set `MCP_SERVER_PORT=3101` in `.env` |

See [CROSS_PLATFORM_SETUP.md](./CROSS_PLATFORM_SETUP.md) for more details.
