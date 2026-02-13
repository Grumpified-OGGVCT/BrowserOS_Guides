# Cross-Platform Setup Guide

## Prerequisites

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Node.js 14+** — [Download](https://nodejs.org/)
- **Git** — [Download](https://git-scm.com/)

## Quick Start

### Windows

```batch
install.bat
run.bat
```

### macOS / Linux

```bash
chmod +x install.sh run.sh
./install.sh
./run.sh
```

## Python Command

| Platform | Command |
|----------|---------|
| Windows  | `python` |
| macOS/Linux | `python3` |

> **Note:** The `package.json` scripts use `python` for cross-platform compatibility.  
> On macOS/Linux, ensure `python` is aliased to `python3` or use the shell scripts instead.

## Environment Setup

1. Copy `.env.template` to `.env`
2. Add your API keys (see `.env.template` for details)
3. Run `install.bat` (Windows) or `./install.sh` (macOS/Linux)

## MCP Server

```bash
npm start        # Starts on http://localhost:3100
```

See [QUICKSTART_MCP.md](./QUICKSTART_MCP.md) for full MCP setup instructions.
