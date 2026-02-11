# BrowserOS Workflows Knowledge Base

## Overview & Scope

This knowledge base provides a comprehensive technical reference for BrowserOS Workflows, covering all aspects from basic architecture to advanced enterprise features. It is designed to enable the creation of sophisticated, production-ready workflows that integrate web automation with local workspace operations.

**Scope:**
- Core workflow architecture and execution model
- Complete catalog of step types and configurations
- Programmatic integration capabilities
- Local workspace and file system access
- Advanced flow control patterns
- Trigger mechanisms and data handling
- Security best practices and limitations

**Target Audience:**
- Workflow developers and automation engineers
- System integrators
- Technical architects designing BrowserOS solutions
- DevOps teams implementing CI/CD with BrowserOS

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    BrowserOS Workflows                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │   Trigger   │────▶│   Workflow   │────▶│   Browser    │ │
│  │   Engine    │     │   Executor   │     │   Context    │ │
│  └─────────────┘     └──────────────┘     └──────────────┘ │
│         │                    │                     │         │
│         │                    │                     │         │
│         ▼                    ▼                     ▼         │
│  ┌─────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │  Scheduler  │     │  Code Agent  │     │   Cowork     │ │
│  │  (Cron/API) │     │  (Python)    │     │  (Local FS)  │ │
│  └─────────────┘     └──────────────┘     └──────────────┘ │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Data Flow & State Management             │  │
│  │  Variables → Interpolation → Extraction → Storage    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**

1. **Trigger Engine**: Initiates workflows via manual, scheduled, event-driven, or API mechanisms
2. **Workflow Executor**: Orchestrates step execution with support for branching, loops, and parallel execution
3. **Browser Context**: Manages browser automation, page interactions, and web scraping
4. **Code Agent**: Executes Python code for data processing and custom logic
5. **Cowork Integration**: Provides sandboxed access to local file system
6. **State Management**: Handles variable scope, data passing between steps, and persistence

## Step Types Catalog

| Step Name | Description | Key Configuration | Example |
|-----------|-------------|-------------------|---------|
| **navigate** | Navigate to a URL | `url`, `wait_until` | Navigate to login page |
| **click** | Click on an element | `selector`, `button`, `modifiers` | Click submit button |
| **input** | Type text into a field | `selector`, `value`, `slowly`, `submit` | Fill username field |
| **extract** | Extract data from page | `selector`, `attribute`, `store` | Extract product prices |
| **wait** | Wait for condition | `selector`, `text`, `time` | Wait for loading spinner to disappear |
| **conditional** | Branch based on condition | `condition`, `if_steps`, `else_steps` | Check if user is logged in |
| **loop** | Iterate over items | `iterator`, `steps` | Process each search result |
| **parallel** | Execute steps concurrently | `steps`, `join` | Scrape multiple pages simultaneously |
| **screenshot** | Capture page image | `element`, `fullPage`, `path` | Take screenshot of dashboard |
| **execute_code** | Run Python code | `code`, `context` | Process extracted data with pandas |
| **read_file** | Read from local workspace | `path`, `encoding` | Load CSV data |
| **write_file** | Write to local workspace | `path`, `data`, `format` | Save results to Excel |
| **shell** | Execute shell command | `command`, `cwd` | Run notification script |
| **api_call** | Make HTTP request | `url`, `method`, `headers`, `body` | POST data to webhook |
| **sub_workflow** | Call another workflow | `workflow_id`, `inputs` | Reuse login workflow |

**Configuration Schema Examples:**

```yaml
# Navigation step
- name: Open product page
  type: navigate
  url: "https://example.com/products"
  wait_until: networkidle

# Extraction step with variable storage
- name: Get product info
  type: extract
  selector: ".product-details"
  extract:
    - name: "{{.product-name}}"
    - price: "{{.product-price}}"
  store: product_data

# Conditional branching
- name: Check login status
  type: conditional
  condition: "{{page.url}} contains '/dashboard'"
  if_steps:
    - name: Proceed with scraping
      type: extract
      selector: "#user-data"
  else_steps:
    - name: Navigate to login
      type: navigate
      url: "/login"

# Parallel execution
- name: Scrape multiple categories
  type: parallel
  steps:
    - name: Scrape electronics
      type: navigate
      url: "/electronics"
    - name: Scrape books
      type: navigate
      url: "/books"
  join: true  # Wait for all to complete
```

## Execution Flow Control Primer

BrowserOS Workflows support sophisticated flow control patterns:

### Sequential Execution
Default mode where steps execute one after another in order.

### Conditional Branching
Use `conditional` steps to create if-then-else logic based on:
- Page content (text presence, element visibility)
- Variable values
- Previous step results
- Custom Python expressions

### Loops and Iteration
Supported loop types:
- **foreach**: Iterate over arrays/lists
- **while**: Loop until condition is false
- **repeat**: Execute N times
- **repeat-until**: Loop until condition is true

**Example:**
```yaml
- name: Process all products
  type: foreach
  iterator: "$.products"
  steps:
    - name: Extract product details
      type: extract
      selector: "[data-product-id='{{item.id}}']"
```

### Parallel Execution
Execute multiple steps concurrently to improve performance:
- Independent page scraping
- Multiple API calls
- Parallel data processing

**Considerations:**
- Resource limits apply (max concurrent operations)
- Join points synchronize parallel branches
- Error handling affects all parallel branches

### Error Handling & Retry Logic
- **Automatic retries**: Configurable retry count and backoff strategy
- **Self-healing**: Falls back to AI-powered element detection on failure
- **Try-catch blocks**: Graceful error handling with fallback steps
- **Timeouts**: Per-step and global timeout configuration

**Example:**
```yaml
- name: Click submit with retry
  type: click
  selector: "#submit-btn"
  retry:
    max_attempts: 3
    backoff: exponential
    fallback: ai_detection
  timeout: 30000  # 30 seconds
```

## Trigger & Integration Matrix

| Trigger Type | Description | Configuration | Use Cases |
|--------------|-------------|---------------|-----------|
| **Manual** | User-initiated via UI | Button click, keyboard shortcut | Ad-hoc data extraction, testing |
| **Scheduled** | Cron-based execution | Schedule expression, timezone | Daily reports, periodic scraping |
| **Event-driven** | Triggered by system events | Event type, filter conditions | File upload completion, webhook receipt |
| **API** | Invoked via REST API | Authentication, parameters | Integration with external systems |
| **File Watch** | Triggered by file changes | Directory path, file pattern | Process new CSV files automatically |
| **Webhook** | HTTP POST endpoint | Secret validation, payload schema | GitHub PR events, payment notifications |

### Integration Capabilities

**External APIs:**
```yaml
- name: Send data to CRM
  type: api_call
  url: "https://api.crm.com/leads"
  method: POST
  headers:
    Authorization: "Bearer {{secrets.crm_token}}"
  body: "{{extracted_data}}"
```

**MCP (Model Context Protocol) Tools:**
- Access to custom tools and services
- Extensible agent capabilities
- Standardized tool interface

**Shell Command Integration:**
```yaml
- name: Run data analysis
  type: shell
  command: "python analyze.py {{data_file}}"
  cwd: "C:/workspace/scripts"
  capture_output: true
```

## Configuration Schema Reference

Complete JSON Schema for BrowserOS Workflows:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BrowserOS Workflow",
  "type": "object",
  "required": ["name", "version", "steps"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Workflow name"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version"
    },
    "description": {
      "type": "string",
      "description": "Workflow description"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "author": {"type": "string"},
        "created": {"type": "string", "format": "date-time"},
        "tags": {"type": "array", "items": {"type": "string"}}
      }
    },
    "variables": {
      "type": "object",
      "description": "Global workflow variables"
    },
    "secrets": {
      "type": "array",
      "description": "Required secret names",
      "items": {"type": "string"}
    },
    "steps": {
      "type": "array",
      "items": {"$ref": "#/definitions/step"},
      "minItems": 1
    }
  },
  "definitions": {
    "step": {
      "type": "object",
      "required": ["name", "type"],
      "properties": {
        "name": {"type": "string"},
        "type": {
          "enum": [
            "navigate", "click", "input", "extract", "wait",
            "conditional", "loop", "parallel", "screenshot",
            "execute_code", "read_file", "write_file", "shell",
            "api_call", "sub_workflow"
          ]
        },
        "selector": {"type": "string"},
        "value": {"type": "string"},
        "url": {"type": "string", "format": "uri"},
        "condition": {"type": "string"},
        "steps": {
          "type": "array",
          "items": {"$ref": "#/definitions/step"}
        },
        "retry": {
          "type": "object",
          "properties": {
            "max_attempts": {"type": "integer", "minimum": 1},
            "backoff": {"enum": ["linear", "exponential"]},
            "fallback": {"enum": ["ai_detection", "skip", "fail"]}
          }
        },
        "timeout": {"type": "integer", "description": "Timeout in milliseconds"}
      }
    }
  }
}
```

**Variable Interpolation:**
- Syntax: `{{variable_name}}`
- Supported contexts: `{{item}}`, `{{page.url}}`, `{{extracted.field}}`, `{{secrets.key}}`
- Nested access: `{{data.users[0].name}}`
- Filters: `{{text | uppercase}}`, `{{price | currency}}`

## Advanced / Enterprise Features

### Secrets Management
- Secure storage of API keys, passwords, tokens
- Encrypted at rest and in transit
- Scoped per workspace
- Rotation and expiration policies

### Workflow Composition
- Sub-workflow calls for modularity
- Input/output parameter passing
- Shared workflow library
- Version control and rollback

### Deterministic Execution (workflow-use)
- Record-once, replay-forever pattern
- No AI inference for production stability
- Semantic element mapping with fallback selectors
- Self-healing with configurable retry strategies

### CodeAgent Capabilities
- Python 3.x execution environment
- Pre-installed libraries: pandas, numpy, requests, BeautifulSoup4, lxml
- Access to workflow context and variables
- Return values flow back to workflow state

**Example:**
```yaml
- name: Process and analyze data
  type: execute_code
  code: |
    import pandas as pd
    df = pd.DataFrame(extracted_data)
    summary = df.groupby('category')['price'].mean()
    return summary.to_dict()
  store: price_summary
```

### Lifecycle Hooks
Custom logic at workflow boundaries:
- `on_workflow_start`: Setup and initialization
- `on_workflow_end`: Cleanup and finalization
- `on_step_start`: Pre-step validation
- `on_step_end`: Post-step processing
- `on_error`: Error handling and logging

### Monitoring & Observability
- Step-level execution metrics
- Variable inspection at runtime
- Screenshot capture on failure
- Structured logging with correlation IDs
- Integration with monitoring platforms

## Limitations & Constraints

### Resource Limits
- **Maximum workflow duration**: 60 minutes (configurable)
- **Maximum concurrent workflows**: 10 per workspace
- **Maximum parallel steps**: 5 per workflow
- **Memory limit per workflow**: 2GB
- **File upload size limit**: 100MB
- **API call timeout**: 30 seconds default

### Browser Context Restrictions
- **Sandboxed execution**: Cannot access system resources outside designated workspace
- **Same-origin policy**: Standard browser security applies
- **Popup handling**: Limited support for browser-initiated popups
- **Certificate validation**: Strict HTTPS enforcement (configurable)

### Cowork File System Access
- **Designated folder only**: Cannot access arbitrary file system locations
- **Read/write permissions**: Explicit user consent required
- **File type restrictions**: Configurable whitelist/blacklist
- **Storage quota**: Subject to browser storage limits

### Performance Considerations
- **Page load timeouts**: Default 30s, configurable up to 120s
- **Element selection**: CSS selectors faster than XPath
- **Data extraction**: Large datasets may require pagination
- **Parallel execution**: Diminishing returns beyond 5 concurrent operations

### Version Compatibility
- **BrowserOS version**: >= 0.37.0 for workflow-use
- **Browser requirements**: Chromium-based browsers
- **Python version**: 3.8+ for CodeAgent
- **Node.js**: Not required (workflow-use uses native APIs)

## Security Best Practices

### Input Validation
```yaml
- name: Validate user input
  type: execute_code
  code: |
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_input):
      raise ValueError("Invalid input format")
    return user_input
```

### Secrets Handling
- **Never hardcode secrets** in workflow definitions
- Use `{{secrets.key_name}}` interpolation
- Rotate secrets regularly
- Limit secret scope to required workflows only

### XSS Prevention
- Use `html_escape` for user-provided content
- Validate and sanitize extracted data before storage
- Content Security Policy (CSP) enforcement in browser context

### Injection Attack Prevention
- Parameterized queries for database operations
- Command injection protection in shell steps
- SQL injection prevention in data processing

### Workspace Isolation
- Each workflow runs in isolated VM
- No cross-workflow data access without explicit sharing
- File system access limited to designated folders
- Network access controllable via firewall rules

### Audit & Compliance
- Workflow execution logs retained for 90 days
- Step-level audit trail with timestamps
- Secret access logging
- GDPR-compliant data handling

## Community Patterns & Case Studies

### Pattern 1: E-commerce Price Monitoring
**Use Case**: Track competitor prices daily and alert on changes

```yaml
name: Price Monitor
version: 1.0.0
steps:
  - name: Read product list
    type: read_file
    path: "products.csv"
    store: products
  
  - name: Scrape prices
    type: foreach
    iterator: "{{products}}"
    steps:
      - name: Navigate to product
        type: navigate
        url: "{{item.url}}"
      - name: Extract price
        type: extract
        selector: ".price"
        store: "prices[{{item.id}}]"
  
  - name: Compare with previous
    type: execute_code
    code: |
      import pandas as pd
      current = pd.DataFrame(prices)
      previous = pd.read_csv('previous_prices.csv')
      changes = current.merge(previous, on='id')
      alerts = changes[changes.price_x != changes.price_y]
      return alerts.to_dict('records')
    store: price_changes
  
  - name: Send alerts
    type: api_call
    url: "{{secrets.slack_webhook_url}}"
    method: POST
    body: "{{price_changes}}"
```

### Pattern 2: Lead Generation with CRM Integration
**Use Case**: Extract leads from directory, enrich data, push to CRM

**Key Features**:
- Parallel page scraping for performance
- Data enrichment via external APIs
- Bulk CRM upload with error handling

### Pattern 3: Document Processing Pipeline
**Use Case**: Download invoices, extract data, update accounting system

**Components**:
- File system monitoring trigger
- OCR-based data extraction
- Database update with transaction management

### Pattern 4: Social Media Content Aggregation
**Use Case**: Collect posts from multiple platforms, analyze sentiment

**Highlights**:
- Multi-platform authentication handling
- Rate limiting and pagination
- Sentiment analysis with Python NLP libraries

### Case Study: Customer Success Team Automation
**Organization**: SaaS company with 500+ customers

**Challenge**: Manual onboarding tasks taking 2 hours per customer

**Solution**:
- Workflow automates account setup across 5 systems
- Customized welcome emails with usage guides
- Slack notifications to customer success team

**Results**:
- Onboarding time reduced to 5 minutes
- Zero errors in account configuration
- Customer success team capacity increased 10x

**Screenshot**: (See `case_studies/customer_onboarding_dashboard.png`)

## Migration & Version History

### Version History

**v1.0.0 (2024-01)**: Initial workflow system
- Basic step types (navigate, click, input, extract)
- Manual triggers only
- Sequential execution

**v1.5.0 (2024-06)**: Flow control enhancements
- Added conditional branching
- Loop support (foreach, while)
- Retry mechanism with exponential backoff

**v2.0.0 (2025-01)**: Parallel execution & CodeAgent
- Parallel step execution
- Python code execution (CodeAgent)
- Cowork integration for file system access

**v2.5.0 (2025-06)**: Enterprise features
- Secrets management
- Sub-workflow composition
- Advanced error handling
- Monitoring and observability

**v3.0.0 (2026-01)**: AI-powered workflows (workflow-use)
- Generation mode from natural language
- Self-healing with semantic mapping
- Deterministic replay mode
- MCP tool integration

### Migration Guides

**From v1.x to v2.x:**
- Update `version` field in workflow definition
- Replace manual file I/O with `read_file`/`write_file` steps
- Refactor complex logic into `execute_code` steps
- Test parallel execution for performance gains

**From v2.x to v3.x:**
- Adopt `.workflow.json` format (backward compatible)
- Leverage self-healing for brittle selectors
- Enable deterministic mode for production workflows
- Integrate MCP tools for custom capabilities

## Appendices

### Glossary

- **Agent**: AI entity that executes workflow steps with browser context
- **Browser Context**: Isolated browser instance for workflow execution
- **CodeAgent**: Python execution environment within workflows
- **Cowork**: Feature enabling local file system access from browser workflows
- **Deterministic Mode**: Workflow execution without AI inference, using pre-recorded selectors
- **MCP**: Model Context Protocol for tool integration
- **Self-Healing**: Automatic recovery from step failures using AI-powered element detection
- **Semantic Selector**: Human-readable element description that AI maps to actual selectors
- **Step**: Atomic unit of workflow execution
- **Variable Interpolation**: Substituting `{{variable}}` with runtime values
- **Workflow**: Sequence of steps that automate browser-based tasks

### Acronyms

- **API**: Application Programming Interface
- **CLI**: Command Line Interface
- **CRM**: Customer Relationship Management
- **CSP**: Content Security Policy
- **CSV**: Comma-Separated Values
- **GDPR**: General Data Protection Regulation
- **GUI**: Graphical User Interface
- **HTTP**: Hypertext Transfer Protocol
- **JSON**: JavaScript Object Notation
- **MCP**: Model Context Protocol
- **NLP**: Natural Language Processing
- **OCR**: Optical Character Recognition
- **OPFS**: Origin Private File System
- **REST**: Representational State Transfer
- **RPA**: Robotic Process Automation
- **SaaS**: Software as a Service
- **TTY**: Teletypewriter (Terminal)
- **URI**: Uniform Resource Identifier
- **VM**: Virtual Machine
- **XSS**: Cross-Site Scripting
- **YAML**: YAML Ain't Markup Language

### FAQ

**Q: Can workflows run without internet access?**
A: Yes, if targeting local HTML files or localhost servers. External website access requires internet.

**Q: How do I debug a failing workflow?**
A: Use screenshot steps, enable verbose logging, inspect variable state at each step, and leverage the workflow replay feature.

**Q: What's the difference between workflow-use and native BrowserOS workflows?**
A: workflow-use is optimized for deterministic, self-healing RPA scenarios. Native workflows offer visual builder and tighter integration with BrowserOS features.

**Q: Can I use TypeScript/JavaScript instead of Python for code steps?**
A: Currently, Python is the only supported language for CodeAgent. JavaScript can be executed via shell commands if Node.js is installed.

**Q: How do I share workflows across team members?**
A: Export workflows as `.workflow.json` files, store in version control (Git), and import into other BrowserOS workspaces.

**Q: Are there rate limits for workflow execution?**
A: Yes, see the Limitations & Constraints section for details on concurrent workflows, parallel steps, and API call timeouts.

**Q: Can workflows interact with native desktop applications?**
A: Indirectly via shell commands and file system operations. Direct UI automation of desktop apps is not supported.

**Q: How secure is the secrets management?**
A: Secrets are encrypted at rest using AES-256, in transit via TLS 1.3, and never logged or exposed in workflow definitions.

### License

This knowledge base is provided under the MIT License. See the repository LICENSE file for details.

**Copyright (c) 2026 BrowserOS Workflows Contributors**

Permission is hereby granted, free of charge, to any person obtaining a copy of this documentation and associated materials, to deal in the documentation without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the documentation, and to permit persons to whom the documentation is furnished to do so, subject to the above copyright notice and permission notice being included in all copies or substantial portions of the documentation.
