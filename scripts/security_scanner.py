#!/usr/bin/env python3
"""
Security Scanner for BrowserOS_Guides Repository
Detects malicious code patterns, injection attempts, and security vulnerabilities
Especially important when extracting content from external repositories
"""

import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent

class SecurityScanner:
    """Comprehensive security scanner"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.alerts = []
        self.warnings = []
        self.safe_count = 0
        
    def log(self, message: str, level: str = "INFO"):
        if self.verbose or level in ["ERROR", "WARNING", "CRITICAL"]:
            print(f"[{level}] {message}")
    
    def scan_all(self) -> Tuple[List[Dict], List[Dict]]:
        """Run all security scans"""
        self.log("=" * 60)
        self.log("SECURITY SCAN STARTING", "INFO")
        self.log("=" * 60)
        
        # Scan different file types
        self.scan_python_files()
        self.scan_json_files()
        self.scan_markdown_files()
        self.scan_html_files()
        self.scan_javascript_files()
        self.scan_shell_scripts()
        self.scan_workflow_files()
        
        # Summary
        self.log("\n" + "=" * 60)
        self.log("SECURITY SCAN COMPLETE", "INFO")
        self.log(f"Files Scanned: {self.safe_count}")
        self.log(f"Warnings: {len(self.warnings)}")
        self.log(f"CRITICAL ALERTS: {len(self.alerts)}")
        self.log("=" * 60)
        
        return self.alerts, self.warnings
    
    def scan_python_files(self):
        """Scan Python files for malicious patterns"""
        self.log("\n--- Scanning Python Files ---")
        
        dangerous_patterns = [
            (r'\beval\s*\(', "CRITICAL", "eval() can execute arbitrary code"),
            (r'\bexec\s*\(', "CRITICAL", "exec() can execute arbitrary code"),
            (r'\b__import__\s*\(', "HIGH", "Dynamic imports can be dangerous"),
            (r'subprocess\.call\([^)]*shell\s*=\s*True', "CRITICAL", "Shell injection vulnerability"),
            (r'os\.system\s*\(', "CRITICAL", "Command injection vulnerability"),
            (r'pickle\.loads?\s*\(', "HIGH", "Pickle deserialization can execute code"),
            (r'input\s*\([^)]*\)\s*\)', "MEDIUM", "User input without validation"),
            (r'open\s*\([^)]*[\'"]w[\'"]', "LOW", "File write operation"),
            (r'requests\.get\([^)]*verify\s*=\s*False', "MEDIUM", "SSL verification disabled"),
            (r'\.execute\s*\([^)]*%', "HIGH", "Potential SQL injection"),
            (r'eval\(f[\'"]', "CRITICAL", "F-string in eval() - code execution"),
            (r'__file__.*\.\.', "MEDIUM", "Path traversal attempt"),
            (r'os\.environ\[[\'"][A-Z_]+[\'"]\]\s*=', "LOW", "Environment variable modification"),
            (r'sys\.path\.insert\s*\(', "MEDIUM", "Python path manipulation"),
            (r'compile\s*\(.*,.*[\'"]eval[\'"]', "HIGH", "Dynamic code compilation"),
        ]
        
        for py_file in REPO_ROOT.rglob("*.py"):
            # Skip virtual environments and hidden directories
            if any(part.startswith('.') or part == 'venv' or part == '__pycache__' 
                   for part in py_file.parts):
                continue
            
            try:
                content = py_file.read_text()
                self.safe_count += 1
                
                for pattern, severity, description in dangerous_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        alert = {
                            "file": str(py_file.relative_to(REPO_ROOT)),
                            "line": line_num,
                            "severity": severity,
                            "pattern": pattern,
                            "description": description,
                            "code_snippet": self._get_line(content, line_num)
                        }
                        
                        if severity == "CRITICAL":
                            self.alerts.append(alert)
                            self.log(f"🚨 CRITICAL: {py_file.name}:{line_num} - {description}", "CRITICAL")
                        else:
                            self.warnings.append(alert)
                            if self.verbose:
                                self.log(f"⚠️  {severity}: {py_file.name}:{line_num} - {description}", "WARNING")
                
            except Exception as e:
                self.log(f"Error scanning {py_file}: {e}", "ERROR")
    
    def scan_json_files(self):
        """Scan JSON files for malicious content"""
        self.log("\n--- Scanning JSON Files ---")
        
        dangerous_patterns = [
            (r'<script[^>]*>', "CRITICAL", "Script tag in JSON - XSS attempt"),
            (r'javascript:', "HIGH", "JavaScript protocol - XSS attempt"),
            (r'on\w+\s*=', "HIGH", "Event handler - XSS attempt"),
            (r'eval\s*\(', "CRITICAL", "eval() in JSON"),
            (r'__proto__', "HIGH", "Prototype pollution attempt"),
            (r'constructor\s*\[', "HIGH", "Constructor injection attempt"),
        ]
        
        for json_file in REPO_ROOT.rglob("*.json"):
            if any(part.startswith('.') for part in json_file.parts):
                continue
            
            try:
                content = json_file.read_text()
                self.safe_count += 1
                
                # Validate JSON structure
                try:
                    data = json.loads(content)
                    # Check for suspicious keys
                    self._check_json_keys(data, json_file)
                except json.JSONDecodeError as e:
                    self.warnings.append({
                        "file": str(json_file.relative_to(REPO_ROOT)),
                        "severity": "LOW",
                        "description": f"Invalid JSON: {e}"
                    })
                
                # Pattern matching
                for pattern, severity, description in dangerous_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        alert = {
                            "file": str(json_file.relative_to(REPO_ROOT)),
                            "line": line_num,
                            "severity": severity,
                            "description": description,
                            "code_snippet": self._get_line(content, line_num)
                        }
                        
                        if severity == "CRITICAL":
                            self.alerts.append(alert)
                            self.log(f"🚨 CRITICAL: {json_file.name}:{line_num} - {description}", "CRITICAL")
                        else:
                            self.warnings.append(alert)
                
            except Exception as e:
                self.log(f"Error scanning {json_file}: {e}", "ERROR")
    
    def scan_markdown_files(self):
        """Scan markdown files for malicious content"""
        self.log("\n--- Scanning Markdown Files ---")
        
        dangerous_patterns = [
            (r'<script[^>]*>', "CRITICAL", "Script tag in markdown"),
            (r'<iframe[^>]*>', "HIGH", "Iframe injection attempt"),
            (r'javascript:', "HIGH", "JavaScript protocol"),
            (r'data:text/html', "MEDIUM", "Data URI HTML"),
            (r'\[.*\]\(javascript:', "HIGH", "JavaScript in link"),
            (r'<img[^>]*onerror\s*=', "HIGH", "Image with error handler - XSS"),
            (r'<\s*svg[^>]*onload\s*=', "HIGH", "SVG with onload - XSS"),
        ]
        
        for md_file in REPO_ROOT.rglob("*.md"):
            if any(part.startswith('.') for part in md_file.parts):
                continue
            
            try:
                content = md_file.read_text()
                self.safe_count += 1
                
                for pattern, severity, description in dangerous_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        alert = {
                            "file": str(md_file.relative_to(REPO_ROOT)),
                            "line": line_num,
                            "severity": severity,
                            "description": description,
                            "code_snippet": self._get_line(content, line_num)
                        }
                        
                        if severity == "CRITICAL":
                            self.alerts.append(alert)
                            self.log(f"🚨 CRITICAL: {md_file.name}:{line_num} - {description}", "CRITICAL")
                        else:
                            self.warnings.append(alert)
                
            except Exception as e:
                self.log(f"Error scanning {md_file}: {e}", "ERROR")
    
    def scan_html_files(self):
        """Scan HTML files for XSS and other vulnerabilities"""
        self.log("\n--- Scanning HTML Files ---")
        
        dangerous_patterns = [
            (r'<script[^>]*src\s*=\s*["\']https?://(?!cdn\.)', "HIGH", "External script from non-CDN"),
            (r'eval\s*\(', "CRITICAL", "eval() in JavaScript"),
            (r'innerHTML\s*=', "MEDIUM", "innerHTML assignment - potential XSS"),
            (r'document\.write\s*\(', "HIGH", "document.write() - XSS vector"),
            (r'on\w+\s*=\s*["\'][^"\']*["\']', "MEDIUM", "Inline event handler"),
            (r'<iframe[^>]*>', "MEDIUM", "Iframe usage"),
        ]
        
        for html_file in REPO_ROOT.rglob("*.html"):
            if any(part.startswith('.') for part in html_file.parts):
                continue
            
            try:
                content = html_file.read_text()
                self.safe_count += 1
                
                for pattern, severity, description in dangerous_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        alert = {
                            "file": str(html_file.relative_to(REPO_ROOT)),
                            "line": line_num,
                            "severity": severity,
                            "description": description,
                            "code_snippet": self._get_line(content, line_num)
                        }
                        
                        if severity == "CRITICAL":
                            self.alerts.append(alert)
                            self.log(f"🚨 CRITICAL: {html_file.name}:{line_num} - {description}", "CRITICAL")
                        else:
                            self.warnings.append(alert)
                
            except Exception as e:
                self.log(f"Error scanning {html_file}: {e}", "ERROR")
    
    def scan_javascript_files(self):
        """Scan JavaScript files"""
        self.log("\n--- Scanning JavaScript Files ---")
        
        dangerous_patterns = [
            (r'\beval\s*\(', "CRITICAL", "eval() can execute arbitrary code"),
            (r'Function\s*\(', "HIGH", "Function constructor - code execution"),
            (r'setTimeout\s*\([^,)]*[\'"]', "MEDIUM", "String in setTimeout"),
            (r'setInterval\s*\([^,)]*[\'"]', "MEDIUM", "String in setInterval"),
            (r'document\.write\s*\(', "HIGH", "document.write() - XSS vector"),
            (r'innerHTML\s*=\s*(?![\'"]).', "MEDIUM", "Dynamic innerHTML"),
        ]
        
        for js_file in REPO_ROOT.rglob("*.js"):
            if any(part.startswith('.') or part == 'node_modules' for part in js_file.parts):
                continue
            
            try:
                content = js_file.read_text()
                self.safe_count += 1
                
                for pattern, severity, description in dangerous_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        alert = {
                            "file": str(js_file.relative_to(REPO_ROOT)),
                            "line": line_num,
                            "severity": severity,
                            "description": description,
                            "code_snippet": self._get_line(content, line_num)
                        }
                        
                        if severity == "CRITICAL":
                            self.alerts.append(alert)
                            self.log(f"🚨 CRITICAL: {js_file.name}:{line_num} - {description}", "CRITICAL")
                        else:
                            self.warnings.append(alert)
                
            except Exception as e:
                self.log(f"Error scanning {js_file}: {e}", "ERROR")
    
    def scan_shell_scripts(self):
        """Scan shell scripts for command injection"""
        self.log("\n--- Scanning Shell Scripts ---")
        
        dangerous_patterns = [
            (r'\$\([^)]*\$', "HIGH", "Nested command substitution"),
            (r'eval\s+', "CRITICAL", "eval in shell script"),
            (r'curl.*\|\s*bash', "CRITICAL", "Piping curl to bash"),
            (r'wget.*\|\s*sh', "CRITICAL", "Piping wget to shell"),
            (r'rm\s+-rf\s+/', "CRITICAL", "Recursive delete from root"),
            (r'chmod\s+777', "MEDIUM", "Overly permissive chmod"),
        ]
        
        for sh_file in list(REPO_ROOT.rglob("*.sh")) + list(REPO_ROOT.rglob("*.ps1")):
            if any(part.startswith('.') for part in sh_file.parts):
                continue
            
            try:
                content = sh_file.read_text()
                self.safe_count += 1
                
                for pattern, severity, description in dangerous_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        alert = {
                            "file": str(sh_file.relative_to(REPO_ROOT)),
                            "line": line_num,
                            "severity": severity,
                            "description": description,
                            "code_snippet": self._get_line(content, line_num)
                        }
                        
                        if severity == "CRITICAL":
                            self.alerts.append(alert)
                            self.log(f"🚨 CRITICAL: {sh_file.name}:{line_num} - {description}", "CRITICAL")
                        else:
                            self.warnings.append(alert)
                
            except Exception as e:
                self.log(f"Error scanning {sh_file}: {e}", "ERROR")
    
    def scan_workflow_files(self):
        """Scan workflow JSON files for malicious steps"""
        self.log("\n--- Scanning Workflow Files ---")
        
        workflows_dir = REPO_ROOT / "BrowserOS" / "Workflows"
        if not workflows_dir.exists():
            return
        
        for workflow_file in workflows_dir.rglob("*.json"):
            try:
                with open(workflow_file) as f:
                    workflow = json.load(f)
                
                self.safe_count += 1
                
                # Check for suspicious steps
                if isinstance(workflow, dict) and "steps" in workflow:
                    for idx, step in enumerate(workflow["steps"]):
                        step_type = step.get("type", "")
                        
                        # Check for code execution steps
                        if step_type in ["exec", "shell", "eval", "code"]:
                            self.warnings.append({
                                "file": str(workflow_file.relative_to(REPO_ROOT)),
                                "severity": "HIGH",
                                "description": f"Step {idx}: Code execution step type '{step_type}'",
                                "step": step.get("name", f"step_{idx}")
                            })
                        
                        # Check for external URLs
                        if "url" in step:
                            url = step["url"]
                            if not url.startswith(("https://", "{{")):
                                self.warnings.append({
                                    "file": str(workflow_file.relative_to(REPO_ROOT)),
                                    "severity": "MEDIUM",
                                    "description": f"Step {idx}: Non-HTTPS URL: {url}",
                                    "step": step.get("name", f"step_{idx}")
                                })
                
            except Exception as e:
                self.log(f"Error scanning workflow {workflow_file}: {e}", "ERROR")
    
    def _check_json_keys(self, data, file_path):
        """Recursively check JSON for suspicious keys"""
        suspicious_keys = ["__proto__", "constructor", "prototype", "eval", "exec"]
        
        if isinstance(data, dict):
            for key in data.keys():
                if key in suspicious_keys:
                    self.alerts.append({
                        "file": str(file_path.relative_to(REPO_ROOT)),
                        "severity": "HIGH",
                        "description": f"Suspicious JSON key: {key}",
                        "key": key
                    })
                self._check_json_keys(data[key], file_path)
        elif isinstance(data, list):
            for item in data:
                self._check_json_keys(item, file_path)
    
    def _get_line(self, content: str, line_num: int) -> str:
        """Get specific line from content"""
        lines = content.split('\n')
        if 0 <= line_num - 1 < len(lines):
            return lines[line_num - 1].strip()
        return ""
    
    def generate_report(self) -> Dict:
        """Generate security report"""
        report = {
            "scan_timestamp": datetime.now().isoformat(),
            "files_scanned": self.safe_count,
            "critical_alerts": len([a for a in self.alerts if a.get("severity") == "CRITICAL"]),
            "high_alerts": len([a for a in self.alerts + self.warnings if a.get("severity") == "HIGH"]),
            "medium_alerts": len([a for a in self.warnings if a.get("severity") == "MEDIUM"]),
            "low_alerts": len([a for a in self.warnings if a.get("severity") == "LOW"]),
            "alerts": self.alerts,
            "warnings": self.warnings
        }
        
        # Save report
        report_file = REPO_ROOT / "SECURITY-SCAN-REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"\n📄 Security report saved: {report_file}")
        
        return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Security scanner for BrowserOS_Guides")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fail-on-critical", action="store_true", help="Exit with error if critical issues found")
    
    args = parser.parse_args()
    
    scanner = SecurityScanner(verbose=args.verbose)
    alerts, warnings = scanner.scan_all()
    report = scanner.generate_report()
    
    # Print summary
    print("\n" + "=" * 60)
    print("SECURITY SCAN SUMMARY")
    print("=" * 60)
    print(f"Files Scanned: {report['files_scanned']}")
    print(f"🚨 Critical Alerts: {report['critical_alerts']}")
    print(f"⚠️  High Alerts: {report['high_alerts']}")
    print(f"⚠️  Medium Alerts: {report['medium_alerts']}")
    print(f"ℹ️  Low Alerts: {report['low_alerts']}")
    print("=" * 60)
    
    if report['critical_alerts'] > 0:
        print("\n🚨 CRITICAL ISSUES FOUND! Review immediately!")
        for alert in alerts:
            if alert.get("severity") == "CRITICAL":
                print(f"  - {alert['file']}:{alert.get('line', '?')} - {alert['description']}")
        
        if args.fail_on_critical:
            return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
