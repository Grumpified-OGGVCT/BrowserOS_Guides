# BrowserOS Anti-Patterns & Runtime Constraints Catalog

## Overview

This document captures the **negative space** of BrowserOS workflows - what doesn't work, known limitations, common mistakes, and runtime constraints. Understanding these boundaries is critical for agent self-awareness and reliability.

**Purpose**: An agent with true "Self-Awareness" needs to know not just what it can do, but what it **cannot** do, and why.

---

## Table of Contents

1. [Runtime Constraints](#runtime-constraints)
2. [Known Limitations](#known-limitations)
3. [Anti-Patterns](#anti-patterns)
4. [Browser Compatibility Issues](#browser-compatibility-issues)
5. [Security Boundaries](#security-boundaries)
6. [Performance Pitfalls](#performance-pitfalls)

---

## Runtime Constraints

### Cross-Origin Restrictions (CORS)

**Constraint**: BrowserOS workflows cannot bypass browser CORS policies.

**Impact**: 
- Cannot make direct HTTP requests to APIs without proper CORS headers
- Cannot access iframes from different origins
- Cannot read cookies from other domains

**Workaround**:
- Use proxy servers for cross-origin API calls
- Implement server-side endpoints that handle CORS
- Use browser extensions that relax CORS for development (not production)

**Example Failure**:
```json
{
  "type": "http",
  "url": "https://api.example.com/data",
  "error": "CORS policy: No 'Access-Control-Allow-Origin' header"
}
```

---

### File System Access Limitations

**Constraint**: Browser-based workflows have restricted file system access.

**Impact**:
- Cannot write to arbitrary file system locations
- Requires user permission for file downloads
- Limited to specific directories (Downloads, User-selected folders)

**Workaround**:
- Use File System Access API with user permission
- Leverage browser's download mechanism
- Use IndexedDB for browser-local storage

---

### Execution Context Limits

**Constraint**: Workflows execute in browser sandbox with memory and CPU limits.

**Impact**:
- Large data processing may crash browser tab
- Long-running workflows may trigger "page unresponsive" warnings
- Maximum execution time varies by browser (typically 30-60 seconds per script)

**Workaround**:
- Break large workflows into smaller chunks
- Use Web Workers for heavy computation
- Implement pagination for large datasets

---

## Known Limitations

### 1. Dynamic Content Loading

**Issue**: Shadow DOM and dynamically loaded content may not be immediately accessible.

**Symptoms**:
- Selectors fail even though element is visually present
- Race conditions with SPA frameworks (React, Vue, Angular)

**Mitigation**:
```json
{
  "type": "wait",
  "selector": "#dynamic-element",
  "timeout": 10000,
  "poll_interval": 500
}
```

### 2. Authentication Flow Interruptions

**Issue**: OAuth redirects and complex login flows may break workflow execution.

**Symptoms**:
- Workflow loses context after redirect
- Session tokens not properly maintained

**Mitigation**:
- Pre-authenticate in separate step
- Use persistent browser contexts
- Implement explicit wait-for-redirect steps

### 3. Rate Limiting and Bot Detection

**Issue**: Many sites implement anti-bot measures that block automated workflows.

**Symptoms**:
- CAPTCHAs appear unexpectedly
- IP blocks after repeated requests
- "Access Denied" pages

**Mitigation**:
- Add random delays between actions
- Rotate user agents (but be ethical)
- Respect robots.txt
- Use official APIs when available

---

## Anti-Patterns

### ❌ Anti-Pattern #1: Hardcoded Selectors

**Problem**: Using brittle CSS selectors that break with minor UI changes.

**Bad Example**:
```json
{
  "type": "click",
  "selector": "#app > div.container > div:nth-child(3) > button"
}
```

**Good Example**:
```json
{
  "type": "click",
  "selector": "button[data-testid='submit-button']"
}
```

**Why**: Structural selectors break easily. Use semantic selectors (IDs, data attributes, ARIA labels).

---

### ❌ Anti-Pattern #2: No Error Handling

**Problem**: Workflows that don't handle failures gracefully.

**Bad Example**:
```json
{
  "steps": [
    {"type": "click", "selector": "#button"},
    {"type": "extract", "selector": ".data"}
  ]
}
```

**Good Example**:
```json
{
  "steps": [
    {"type": "click", "selector": "#button"},
    {"type": "conditional", 
     "condition": "{{element_exists('.data')}}",
     "then": [{"type": "extract", "selector": ".data"}],
     "else": [{"type": "comment", "name": "Data not available"}]
    }
  ]
}
```

---

### ❌ Anti-Pattern #3: Infinite Loops Without Exit Conditions

**Problem**: Loop steps without termination conditions can hang the browser.

**Bad Example**:
```json
{
  "type": "loop",
  "iterator": "$.items",
  "steps": [
    {"type": "click", "selector": ".next-page"}
  ]
}
```

**Good Example**:
```json
{
  "type": "loop",
  "iterator": "$.items",
  "max_iterations": 100,
  "steps": [
    {"type": "click", "selector": ".next-page"},
    {"type": "conditional",
     "condition": "{{has_next_page}} === false",
     "then": [{"type": "break"}]
    }
  ]
}
```

---

### ❌ Anti-Pattern #4: Ignoring Rate Limits

**Problem**: Rapid-fire requests that trigger rate limiting or IP bans.

**Bad Example**:
```json
{
  "type": "loop",
  "iterator": "$.urls",
  "steps": [
    {"type": "http", "url": "{{item}}"}
  ]
}
```

**Good Example**:
```json
{
  "type": "loop",
  "iterator": "$.urls",
  "steps": [
    {"type": "http", "url": "{{item}}"},
    {"type": "wait", "duration": 2000}
  ]
}
```

---

## Browser Compatibility Issues

### Chrome-Only Features

**Features**: File System Access API (advanced), Chrome DevTools Protocol

**Impact**: Workflows using these features won't work in Firefox or Safari.

**Detection**:
```javascript
if (!('showOpenFilePicker' in window)) {
  console.error('File System Access API not supported');
}
```

### Firefox Restrictions

**Issue**: Stricter content security policies in Firefox.

**Impact**: Some script-based steps may be blocked.

### Safari Limitations

**Issue**: Limited Web Worker support, stricter CORS enforcement.

**Impact**: Heavy computation workflows may not perform well.

---

## Security Boundaries

### 1. Cannot Execute Arbitrary System Commands

**Constraint**: BrowserOS workflows run in browser sandbox, not OS shell.

**What Fails**:
```json
{
  "type": "script",
  "language": "bash",  // ❌ Not possible in browser
  "code": "rm -rf /"   // ❌ Good thing this fails!
}
```

### 2. Cannot Access Local Network Resources

**Constraint**: Browsers block access to `localhost` and local network IPs from public pages.

**What Fails**:
- Accessing `http://192.168.1.x`
- Connecting to `http://localhost:8080` from remote page

### 3. Cannot Disable HTTPS Certificate Validation

**Constraint**: Cannot accept self-signed certificates in workflows.

**Impact**: Testing against local dev servers with self-signed certs fails.

---

## Performance Pitfalls

### 1. Excessive DOM Queries

**Problem**: Running `extract` steps inside tight loops kills performance.

**Bad**: 1000 extract operations = 30+ seconds
**Good**: Batch DOM queries, extract once and process in memory

### 2. Large JSON Payloads

**Problem**: Extracting and storing massive JSON in workflow variables.

**Limit**: Keep variables under 10MB for stable performance.

### 3. Screenshot Overload

**Problem**: Taking screenshots on every step for debugging.

**Impact**: Each screenshot is 1-5MB, can exhaust memory.

**Solution**: Only screenshot on errors or critical checkpoints.

---

## Quick Reference: Common Failure Messages

| Error Message | Meaning | Solution |
|--------------|---------|----------|
| `CORS policy error` | Cross-origin request blocked | Use proxy or server-side call |
| `Element not found` | Selector doesn't match any element | Add wait step, verify selector |
| `Timeout exceeded` | Operation took too long | Increase timeout, optimize workflow |
| `Permission denied` | User didn't grant required permission | Add permission request step |
| `Network error` | Internet connection issue | Add retry logic |
| `Script execution blocked` | CSP or browser security blocked script | Use different approach |
| `Maximum call stack exceeded` | Infinite loop or recursion | Add termination condition |

---

## Validation Against This Catalog

When building workflows, validate against these constraints:

1. ✅ Does workflow respect CORS boundaries?
2. ✅ Are error handlers in place for each critical step?
3. ✅ Are loops bounded with max iterations?
4. ✅ Are rate limits respected with delays?
5. ✅ Are selectors semantic and resilient?
6. ✅ Is browser compatibility considered?

---

## Contributing

This catalog is maintained through automated analysis of GitHub Issues and community feedback. To report new constraints or anti-patterns:

1. Open an issue in the BrowserOS repository
2. Tag with `constraint` or `anti-pattern`
3. Provide reproducible example

Last Updated: Auto-generated from GitHub Issues analysis
