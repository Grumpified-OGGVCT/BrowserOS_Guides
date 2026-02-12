# Quick Start: Using BrowserOS_Guides MCP Server

## What is This?

This repository now includes an HTTP-based MCP (Model Context Protocol) server that provides BrowserOS agents with self-aware intelligence - workflow knowledge, validation tools, and 917+ executable workflow templates.

## For BrowserOS Users

### Step 1: Start the MCP Server

```bash
# Clone the repository
git clone https://github.com/Grumpified-OGGVCT/BrowserOS_Guides.git
cd BrowserOS_Guides

# Start the server
npm run mcp-server
```

The server will start on `http://localhost:3100/mcp`

### Step 2: Add to BrowserOS

1. Open BrowserOS
2. Go to **Settings** → **Connected Apps**
3. Click **"Add Custom App"**
4. Fill in:
   - **Name**: `BrowserOS Workflows KB`
   - **URL**: `http://localhost:3100/mcp`
   - **Description**: `BrowserOS Workflows Knowledge Base - Provides workflow documentation, validation, and 917+ workflow templates`
5. Click **"Add Server"**

### Step 3: Use It!

Now you can ask your BrowserOS agent questions like:

- "Show me workflows for price tracking"
- "Validate this workflow against best practices"
- "What are the limitations of the navigate step?"
- "Find workflows that handle pagination"
- "Generate a workflow stub for scraping product reviews"

The agent will automatically use the MCP server to answer.

---

## For Developers

### Available Tools

The MCP server exposes 10 tools:

1. `query_knowledge` - Query the knowledge base
2. `validate_workflow` - Validate workflow definitions
3. `search_workflows` - Search 917+ workflows
4. `get_workflow_template` - Get complete workflow code
5. `check_constraints` - Check anti-patterns
6. `get_step_documentation` - Get step docs
7. `list_categories` - List all categories
8. `get_anti_patterns` - Get constraints catalog
9. `check_source_freshness` - Check KB currency
10. `generate_workflow_stub` - Generate workflow stubs

### Example: Query the Knowledge Base

```bash
curl -X POST http://localhost:3100/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "query_knowledge",
    "parameters": {
      "query": "how to handle pagination",
      "format": "markdown"
    }
  }'
```

### Example: Search Workflows

```bash
curl -X POST http://localhost:3100/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "search_workflows",
    "parameters": {
      "query": "amazon",
      "category": "e-commerce",
      "limit": 5
    }
  }'
```

### Example: Validate a Workflow

```bash
curl -X POST http://localhost:3100/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "validate_workflow",
    "parameters": {
      "workflow": {
        "name": "My Workflow",
        "version": "1.0.0",
        "steps": [
          {
            "type": "navigate",
            "name": "Go to page",
            "url": "https://example.com"
          }
        ]
      }
    }
  }'
```

---

## For Other MCP Tools (Claude Desktop, Cursor, etc.)

This server works with any MCP-capable tool that supports HTTP transport.

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "browseros-guides": {
      "transport": "http",
      "url": "http://localhost:3100/mcp"
    }
  }
}
```

---

## Health Check

Test if the server is running:

```bash
curl http://localhost:3100/mcp/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "workflows_count": 917,
  "last_updated": "2026-02-12T..."
}
```

---

## Troubleshooting

**Server won't start?**
- Check if port 3100 is available: `lsof -i :3100`
- Try a different port: `BROWSEROS_GUIDES_PORT=3101 npm run mcp-server`

**BrowserOS can't connect?**
- Verify server is running: `curl http://localhost:3100/mcp/health`
- Check firewall settings
- Ensure URL in BrowserOS matches exactly

**No search results?**
- Run: `npm run generate-library` to rebuild indexes
- Check server logs for errors

---

## Next Steps

- Read [MCP_SERVER_INTEGRATION.md](./MCP_SERVER_INTEGRATION.md) for full API documentation
- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for system design details
- Browse [library/templates/](./library/templates/) for workflow templates
- Check [BrowserOS/ANTI_PATTERNS_AND_CONSTRAINTS.md](./BrowserOS/ANTI_PATTERNS_AND_CONSTRAINTS.md) for limitations

---

## What Makes This Special?

✅ **Self-Aware Intelligence**: Knows its own capabilities and limitations
✅ **Ground Truth Validated**: All knowledge validated against BrowserOS source code
✅ **917+ Workflows**: Searchable, executable, documented
✅ **Anti-Pattern Detection**: Warns about common mistakes before execution
✅ **Content Integrity**: SHA-256 hashing ensures knowledge accuracy
✅ **Real-Time Updates**: Event-driven synchronization with BrowserOS repo
✅ **Universal**: Works with BrowserOS, Claude Desktop, Cursor, and more

---

**Status**: ✅ Production Ready - v2.0  
**Last Updated**: 2026-02-12
