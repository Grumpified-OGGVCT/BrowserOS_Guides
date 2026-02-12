# Security Policy & Guidelines

## 🛡️ Security First Approach

This repository prioritizes security, especially when extracting content from external sources. We implement multiple layers of security scanning to protect against malicious code injection, XSS attacks, and other vulnerabilities.

## 🚨 Recent Security Incidents

### Context: openclaw/awesome-claude-skills Security Issues

The broader Claude skills community has experienced security incidents involving malicious code injection in skill repositories. **We take these threats seriously.**

**Known Attack Vectors:**
- Script injection in markdown files
- Malicious code in workflow JSON
- XSS attempts in HTML/JavaScript
- Command injection in shell scripts
- Prototype pollution in JSON
- Eval/exec code execution

## 🔒 Our Security Measures

### 1. **Automated Security Scanning**

All code is automatically scanned for:
- ✅ Code execution patterns (`eval`, `exec`, `Function()`)
- ✅ Script injection (`<script>`, `javascript:`)
- ✅ XSS vectors (`innerHTML`, `document.write`, event handlers)
- ✅ Command injection (shell `eval`, `system()`, piping to bash)
- ✅ SQL injection patterns
- ✅ Prototype pollution (`__proto__`, `constructor`)
- ✅ Path traversal attempts
- ✅ Unsafe deserialization (`pickle.loads`)
- ✅ SSL verification bypass
- ✅ Suspicious URL patterns

**Scanner:** `scripts/security_scanner.py`

**Run Manually:**
```bash
python scripts/security_scanner.py --verbose --fail-on-critical
```

### 2. **External Content Validation**

When extracting content from `awesome-claude-skills` or other repositories:

1. **Clone to isolated directory** (`/tmp/`)
2. **Security scan before processing**
3. **Content sanitization** (remove dangerous patterns)
4. **Hash verification** (track content integrity)
5. **Manual review required** for production use

**Extractor with Security:** `scripts/extract_claude_skills.py`

### 3. **Automated Security Checks**

#### In GitHub Actions

Every commit and PR triggers:
- Python syntax validation
- Security pattern scanning
- Dependency vulnerability checks
- Workflow JSON validation
- Link and content validation

#### Self-Test Integration

The self-test system (`scripts/self_test.py`) includes security checks that run:
- After every KB update
- Weekly on Sunday
- On manual trigger
- Before any deployment

### 4. **Content Sanitization**

All external content is sanitized:

```python
def sanitize_content(content: str) -> str:
    # Remove script tags
    content = re.sub(r'<script[^>]*>.*?</script>', '', content)
    # Remove event handlers
    content = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', content)
    # Remove javascript: protocols
    content = re.sub(r'javascript:', '', content)
    return content
```

### 5. **Hash Verification**

All extracted workflows include content hash for integrity:

```json
{
  "notes": [
    "Content hash: a1b2c3d4e5f6g7h8"
  ]
}
```

## 🚫 Blocked Patterns

The following patterns are **automatically blocked**:

### Python
- `eval()` with dynamic input
- `exec()` without sandboxing
- `__import__()` with user input
- `subprocess.call()` with `shell=True`
- `os.system()` for command execution
- `pickle.loads()` with untrusted data

### JavaScript
- `eval()` usage
- `Function()` constructor
- `setTimeout/setInterval` with strings
- `document.write()`
- Dynamic `innerHTML` assignments

### HTML/Markdown
- `<script>` tags
- `<iframe>` tags
- `javascript:` protocol
- `data:text/html` URIs
- `on*` event handlers (onclick, onerror, etc.)

### JSON
- `__proto__` keys
- `constructor` manipulation
- `prototype` pollution
- Embedded scripts

### Shell Scripts
- `eval` commands
- Piping curl/wget to bash
- `rm -rf /` patterns
- Nested command substitution with user input

## ⚠️ Security Warnings

### For awesome-claude-skills Content

**⚠️ WARNING:** Content from `awesome-claude-skills` is automatically extracted and transformed. While we scan and sanitize:

1. **Review before production** - Always review adapted workflows
2. **Test in isolation** - Use sandboxed environments first
3. **Verify sources** - Check original skill repository
4. **Report issues** - Alert us if you find problems

### For Custom Workflows

When creating workflows:

1. **Never hardcode secrets** - Use environment variables
2. **Validate user input** - Sanitize all inputs
3. **Use HTTPS only** - No HTTP URLs in production
4. **Limit permissions** - Minimum required access
5. **Error handling** - Fail securely, don't expose internals

## 🐛 Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

**Instead:**

1. **Email:** Create a GitHub issue marked `[SECURITY]` with minimal details
2. **Wait:** We'll respond within 48 hours with secure communication channel
3. **Disclose:** Share full details privately
4. **Fix:** We'll patch and credit you (if desired)

## 🔍 Security Checklist

### Before Adding External Content

- [ ] Source repository is reputable
- [ ] Content has been security scanned
- [ ] Malicious patterns removed
- [ ] Content hash recorded
- [ ] Manual review completed
- [ ] Testing in sandbox done

### Before Deploying Workflows

- [ ] All secrets use environment variables
- [ ] No hardcoded credentials
- [ ] HTTPS only for external URLs
- [ ] Input validation present
- [ ] Error handling secure
- [ ] Rate limiting implemented
- [ ] Logging doesn't expose secrets

### Regular Security Maintenance

- [ ] Weekly security scans (automated)
- [ ] Dependency updates monthly
- [ ] Review extracted content quarterly
- [ ] Update security patterns as needed
- [ ] Monitor GitHub Security Advisories

## 📚 Security Resources

### Internal Tools

- `scripts/security_scanner.py` - Comprehensive scanner
- `scripts/self_test.py` - Self-test with security checks
- `scripts/extract_claude_skills.py` - Secure content extractor

### External Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Advisories](https://github.com/advisories)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

## 🎯 Security Goals

1. **Zero Trust** - Validate everything from external sources
2. **Defense in Depth** - Multiple security layers
3. **Fail Secure** - Errors don't expose vulnerabilities
4. **Transparency** - Clear security documentation
5. **Community** - Report and fix issues quickly

## 📊 Security Metrics

Track security health:

- **Last Security Scan:** Automated daily
- **Critical Issues:** Target 0
- **Scan Coverage:** 100% of code files
- **External Content:** 100% scanned before integration
- **Response Time:** < 48 hours for security issues

## ✅ Verified Safe

The following external integrations have been verified:

- ✅ BrowserOS official repository (browseros-ai/BrowserOS)
- ✅ Kimi-K2.5:cloud API (Ollama Cloud)
- ✅ OpenRouter API
- ⚠️ awesome-claude-skills (scanned + sanitized before use)

## 🔄 Continuous Improvement

Security is never complete. We continuously:

1. Update security patterns
2. Monitor for new threats
3. Review community reports
4. Enhance scanning tools
5. Educate contributors

---

**Last Updated:** 2026-02-11  
**Security Scanner Version:** 1.0.0  
**Policy Version:** 1.0

*Security is everyone's responsibility. Thank you for helping keep this repository safe!* 🛡️
