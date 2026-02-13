#!/usr/bin/env python3
"""
Comprehensive Self-Test System for BrowserOS_Guides Repository
Runs after every update, detects breaking changes, auto-fixes when possible,
and creates GitHub issues for manual review when needed.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import urllib.request
import urllib.error

# Force UTF-8 output for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Configuration
REPO_ROOT = Path(__file__).parent.parent
KB_PATH = REPO_ROOT / "BrowserOS" / "Research" / "BrowserOS_Workflows_KnowledgeBase.md"
SEARCH_INDEX = REPO_ROOT / "docs" / "search-index.json"
TEST_RESULTS_FILE = REPO_ROOT / "BrowserOS" / "Research" / "test_results.json"
CHECKSUM_FILE = KB_PATH.parent / f"{KB_PATH.name}.checksum"

class TestResult:
    """Represents the result of a single test"""
    def __init__(self, name: str, passed: bool, message: str = "", 
                 fixable: bool = False, fixed: bool = False):
        self.name = name
        self.passed = passed
        self.message = message
        self.fixable = fixable
        self.fixed = fixed
        self.severity = "high" if not passed else "info"

class SelfTest:
    """Main self-test runner"""
    
    def __init__(self, auto_fix: bool = False, verbose: bool = False):
        self.auto_fix = auto_fix
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.fixes_applied: List[str] = []
        self.manual_review_needed: List[Dict] = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose"""
        if self.verbose or level in ["ERROR", "WARNING"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
    
    def run_all_tests(self) -> bool:
        """Run all test categories"""
        self.log("=" * 60)
        self.log("Starting Comprehensive Self-Test", "INFO")
        self.log("=" * 60)
        
        start_time = datetime.now()
        
        # Run test categories
        self.test_kb_completeness()
        self.test_search_index()
        self.test_website_assets()
        self.test_workflow_examples()
        self.test_ai_integration()
        self.test_github_actions()
        self.test_documentation_links()
        self.test_python_scripts()
        
        # Calculate results
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = sum(1 for r in self.results if not r.passed)
        fixed_tests = sum(1 for r in self.results if r.fixed)
        
        # Generate report
        self.generate_report(duration, passed_tests, failed_tests, fixed_tests)
        
        # Create issues if needed
        if self.manual_review_needed:
            self.create_github_issue()
        
        return failed_tests == 0 or (self.auto_fix and not self.manual_review_needed)
    
    def test_kb_completeness(self):
        """Test Knowledge Base completeness (C01-C06)"""
        self.log("\n--- Testing KB Completeness ---")
        
        # C01: Check required sections
        required_sections = [
            "Overview & Scope", "Architecture Diagram", "Step Types Catalog",
            "Execution Flow Control Primer", "Trigger & Integration Matrix",
            "Configuration Schema Reference", "Advanced / Enterprise Features",
            "Limitations & Constraints", "Security Best Practices",
            "Community Patterns & Case Studies", "Migration & Version History",
            "Appendices"
        ]
        
        if KB_PATH.exists():
            content = KB_PATH.read_text(encoding='utf-8')
            missing_sections = []
            for section in required_sections:
                if not re.search(rf'^##\s+{re.escape(section)}', content, re.MULTILINE):
                    missing_sections.append(section)
            
            if missing_sections:
                self.results.append(TestResult(
                    "C01_sections",
                    False,
                    f"Missing sections: {', '.join(missing_sections)}",
                    fixable=False
                ))
                self.manual_review_needed.append({
                    "test": "C01_sections",
                    "issue": f"Missing KB sections: {', '.join(missing_sections)}",
                    "severity": "high",
                    "suggested_fix": "Add missing sections to Knowledge Base"
                })
            else:
                self.results.append(TestResult("C01_sections", True, "All required sections present"))
            
            # C02: Check for placeholders
            placeholders = ["TODO", "TBD", "INSERT", "FIXME", "XXX"]
            found_placeholders = []
            for placeholder in placeholders:
                if placeholder in content:
                    found_placeholders.append(placeholder)
            
            if found_placeholders:
                self.results.append(TestResult(
                    "C02_placeholders",
                    False,
                    f"Found placeholders: {', '.join(found_placeholders)}",
                    fixable=False
                ))
                self.manual_review_needed.append({
                    "test": "C02_placeholders",
                    "issue": f"Placeholder tokens found: {', '.join(found_placeholders)}",
                    "severity": "medium",
                    "suggested_fix": "Replace placeholders with actual content"
                })
            else:
                self.results.append(TestResult("C02_placeholders", True, "No placeholder tokens"))
        else:
            self.results.append(TestResult(
                "KB_exists",
                False,
                "Knowledge Base file not found",
                fixable=False
            ))
        
        # C05: Check checksum
        if KB_PATH.exists() and CHECKSUM_FILE.exists():
            import hashlib
            current_hash = hashlib.sha256(KB_PATH.read_bytes()).hexdigest()
            stored_hash = CHECKSUM_FILE.read_text(encoding='utf-8').strip()
            
            if current_hash != stored_hash:
                if self.auto_fix:
                    CHECKSUM_FILE.write_text(current_hash)
                    self.fixes_applied.append("Updated KB checksum")
                    self.results.append(TestResult("C05_checksum", True, "Checksum updated", fixable=True, fixed=True))
                else:
                    self.results.append(TestResult("C05_checksum", False, "Checksum mismatch", fixable=True))
            else:
                self.results.append(TestResult("C05_checksum", True, "Checksum matches"))
        elif KB_PATH.exists():
            # Create checksum if missing
            if self.auto_fix:
                import hashlib
                current_hash = hashlib.sha256(KB_PATH.read_bytes()).hexdigest()
                CHECKSUM_FILE.write_text(current_hash)
                self.fixes_applied.append("Created KB checksum")
                self.results.append(TestResult("C05_checksum", True, "Checksum created", fixable=True, fixed=True))
    
    def test_search_index(self):
        """Test search index validity"""
        self.log("\n--- Testing Search Index ---")
        
        if SEARCH_INDEX.exists():
            try:
                with open(SEARCH_INDEX, encoding='utf-8') as f:
                    index = json.load(f)
                
                # Check structure
                documents = index
                if isinstance(index, dict) and "documents" in index:
                    documents = index["documents"]
                elif not isinstance(index, list):
                    raise ValueError("Search index must be a list or dict with 'documents' key")
                
                # Check document count
                if len(documents) < 10:
                    self.log(f"WARNING: Only {len(index)} documents in search index", "WARNING")
                
                # Check required fields
                required_fields = ["title", "description", "category", "path"]
                for doc in documents:
                    missing = [f for f in required_fields if f not in doc]
                    if missing:
                        raise ValueError(f"Document missing fields: {missing}")
                
                self.results.append(TestResult("search_index", True, f"Valid index with {len(index)} documents"))
                
            except Exception as e:
                if self.auto_fix:
                    # Regenerate search index
                    try:
                        subprocess.run([
                            sys.executable,
                            str(REPO_ROOT / "scripts" / "generate_search_index.py")
                        ], check=True, capture_output=True)
                        self.fixes_applied.append("Regenerated search index")
                        self.results.append(TestResult("search_index", True, "Regenerated index", fixable=True, fixed=True))
                    except subprocess.CalledProcessError as regen_error:
                        self.results.append(TestResult("search_index", False, f"Failed to regenerate: {regen_error}", fixable=True))
                        self.manual_review_needed.append({
                            "test": "search_index",
                            "issue": f"Search index broken and regeneration failed: {regen_error}",
                            "severity": "high",
                            "suggested_fix": "Manually run: python scripts/generate_search_index.py"
                        })
                else:
                    self.results.append(TestResult("search_index", False, f"Invalid: {e}", fixable=True))
        else:
            if self.auto_fix:
                # Generate missing index
                try:
                    subprocess.run([
                        sys.executable,
                        str(REPO_ROOT / "scripts" / "generate_search_index.py")
                    ], check=True, capture_output=True)
                    self.fixes_applied.append("Created search index")
                    self.results.append(TestResult("search_index", True, "Created index", fixable=True, fixed=True))
                except subprocess.CalledProcessError as e:
                    self.results.append(TestResult("search_index", False, f"Failed to create: {e}", fixable=True))
            else:
                self.results.append(TestResult("search_index", False, "Index file missing", fixable=True))
    
    def test_website_assets(self):
        """Test website HTML/CSS/JS"""
        self.log("\n--- Testing Website Assets ---")
        
        docs_dir = REPO_ROOT / "docs"
        
        # Check HTML
        index_html = docs_dir / "index.html"
        if index_html.exists():
            content = index_html.read_text(encoding='utf-8')
            if "</html>" in content and "<head>" in content and "<body>" in content:
                self.results.append(TestResult("website_html", True, "Valid HTML structure"))
            else:
                self.results.append(TestResult("website_html", False, "Invalid HTML structure", fixable=False))
        else:
            self.results.append(TestResult("website_html", False, "index.html missing", fixable=False))
        
        # Check CSS
        styles_css = docs_dir / "styles.css"
        if styles_css.exists():
            content = styles_css.read_text(encoding='utf-8')
            if len(content) > 100:  # Basic check
                self.results.append(TestResult("website_css", True, "CSS file present"))
            else:
                self.results.append(TestResult("website_css", False, "CSS file too small", fixable=False))
        else:
            self.results.append(TestResult("website_css", False, "styles.css missing", fixable=False))
        
        # Check JavaScript
        app_js = docs_dir / "app.js"
        if app_js.exists():
            content = app_js.read_text(encoding='utf-8')
            # Basic syntax check for common errors
            if content.count("{") == content.count("}") and content.count("[") == content.count("]"):
                self.results.append(TestResult("website_js", True, "JavaScript syntax looks valid"))
            else:
                self.results.append(TestResult("website_js", False, "Possible JavaScript syntax error", fixable=False))
        else:
            self.results.append(TestResult("website_js", False, "app.js missing", fixable=False))
    
    def test_workflow_examples(self):
        """Test workflow JSON examples"""
        self.log("\n--- Testing Workflow Examples ---")
        
        workflows_dir = REPO_ROOT / "BrowserOS" / "Workflows"
        if workflows_dir.exists():
            json_files = list(workflows_dir.rglob("*.json"))
            valid_count = 0
            invalid_files = []
            
            for json_file in json_files:
                try:
                    with open(json_file, encoding='utf-8') as f:
                        data = json.load(f)
                    # Basic workflow validation
                    if isinstance(data, dict) and ("steps" in data or "name" in data):
                        valid_count += 1
                    else:
                        invalid_files.append(str(json_file.name))
                except Exception as e:
                    invalid_files.append(f"{json_file.name}: {e}")
            
            if invalid_files:
                self.results.append(TestResult(
                    "workflow_json",
                    False,
                    f"Invalid workflows: {', '.join(invalid_files)}",
                    fixable=False
                ))
                self.manual_review_needed.append({
                    "test": "workflow_json",
                    "issue": f"Invalid workflow files: {', '.join(invalid_files)}",
                    "severity": "medium",
                    "suggested_fix": "Fix JSON syntax in workflow files"
                })
            else:
                self.results.append(TestResult("workflow_json", True, f"{valid_count} valid workflow files"))
        else:
            self.results.append(TestResult("workflow_json", False, "Workflows directory missing", fixable=False))
    
    def test_ai_integration(self):
        """Test AI service connectivity"""
        self.log("\n--- Testing AI Integration ---")
        
        # Check Ollama API key exists (OPTIONAL)
        ollama_key = os.getenv("OLLAMA_API_KEY")
        if ollama_key:
            self.results.append(TestResult("ollama_key", True, "OLLAMA_API_KEY found (optional)"))
        else:
            # OLLAMA is optional - this is just an INFO warning, not a failure
            self.results.append(TestResult("ollama_key", True, "OLLAMA_API_KEY not set (optional - Ollama is not required)"))
            self.log("  ℹ️  OLLAMA_API_KEY not set (this is optional)")
        
        # Check OpenRouter API key
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            self.results.append(TestResult("openrouter_key", True, "OPENROUTER_API_KEY found"))
        else:
            # OPENROUTER is optional - just a warning
            self.results.append(TestResult("openrouter_key", True, "OPENROUTER_API_KEY not set (optional)"))
            self.log("  ℹ️  OPENROUTER_API_KEY not set (this is optional)")
    
    def test_github_actions(self):
        """Test GitHub Actions workflow files"""
        self.log("\n--- Testing GitHub Actions ---")
        
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        if workflows_dir.exists():
            yaml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            valid_count = 0
            invalid_files = []
            
            for yaml_file in yaml_files:
                try:
                    content = yaml_file.read_text(encoding='utf-8')
                    # Basic YAML check
                    if "name:" in content and ("on:" in content or "jobs:" in content):
                        valid_count += 1
                    else:
                        invalid_files.append(yaml_file.name)
                except Exception as e:
                    invalid_files.append(f"{yaml_file.name}: {e}")
            
            if invalid_files:
                self.results.append(TestResult(
                    "github_actions",
                    False,
                    f"Invalid workflows: {', '.join(invalid_files)}",
                    fixable=False
                ))
            else:
                self.results.append(TestResult("github_actions", True, f"{valid_count} valid workflow files"))
        else:
            self.results.append(TestResult("github_actions", False, "Workflows directory missing", fixable=False))
    
    def test_documentation_links(self):
        """Test internal documentation links"""
        self.log("\n--- Testing Documentation Links ---")
        
        # Find all markdown files
        md_files = list(REPO_ROOT.rglob("*.md"))
        broken_links = []
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                # Find markdown links
                links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
                for link_text, link_path in links:
                    # Skip external links
                    if link_path.startswith(('http://', 'https://', 'mailto:', '#')):
                        continue
                    
                    # Strip anchor
                    if '#' in link_path:
                        link_path = link_path.split('#')[0]
                    
                    if not link_path:
                        continue
                        
                    # Check if file exists (relative to current file)
                    target = (md_file.parent / link_path).resolve()
                    if not target.exists():
                        broken_links.append(f"{md_file.name} -> {link_path}")
            except Exception as e:
                self.log(f"Error checking {md_file}: {e}", "WARNING")
        
        if broken_links:
            self.results.append(TestResult(
                "doc_links",
                True,  # Non-fatal warning
                f"Broken links found (see report): {', '.join(broken_links[:5])}...",
                fixable=False
            ))
            self.manual_review_needed.append({
                "test": "doc_links",
                "issue": f"Broken internal links: {', '.join(broken_links[:5])}",
                "severity": "low",
                "suggested_fix": "Fix broken links in documentation"
            })
        else:
            self.results.append(TestResult("doc_links", True, "All internal links valid"))
    
    def test_python_scripts(self):
        """Test Python scripts for syntax errors"""
        self.log("\n--- Testing Python Scripts ---")
        
        scripts_dir = REPO_ROOT / "scripts"
        if scripts_dir.exists():
            py_files = list(scripts_dir.glob("*.py"))
            valid_count = 0
            invalid_files = []
            
            for py_file in py_files:
                try:
                    # Compile Python file to check syntax
                    with open(py_file, encoding='utf-8') as f:
                        compile(f.read(), py_file.name, 'exec')
                    valid_count += 1
                except SyntaxError as e:
                    invalid_files.append(f"{py_file.name}:{e.lineno}")
            
            if invalid_files:
                self.results.append(TestResult(
                    "python_syntax",
                    False,
                    f"Syntax errors: {', '.join(invalid_files)}",
                    fixable=False
                ))
                self.manual_review_needed.append({
                    "test": "python_syntax",
                    "issue": f"Python syntax errors in: {', '.join(invalid_files)}",
                    "severity": "high",
                    "suggested_fix": "Fix Python syntax errors"
                })
            else:
                self.results.append(TestResult("python_syntax", True, f"{valid_count} valid Python scripts"))
        else:
            self.results.append(TestResult("python_syntax", False, "Scripts directory missing", fixable=False))
    
    def generate_report(self, duration: float, passed: int, failed: int, fixed: int):
        """Generate test report"""
        self.log("\n" + "=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        self.log(f"Duration: {duration:.1f}s")
        self.log(f"Total Tests: {len(self.results)}")
        self.log(f"Passed: {passed} ✓")
        self.log(f"Failed: {failed} ✗")
        self.log(f"Auto-Fixed: {fixed} 🔧")
        self.log("=" * 60)
        
        if self.fixes_applied:
            self.log("\nFixes Applied:")
            for fix in self.fixes_applied:
                self.log(f"  ✓ {fix}")
        
        if self.manual_review_needed:
            self.log("\nManual Review Needed:")
            for item in self.manual_review_needed:
                self.log(f"  ✗ [{item['severity'].upper()}] {item['test']}: {item['issue']}")
        
        # Save results to JSON
        report = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "total_tests": len(self.results),
                "passed": passed,
                "failed": failed,
                "fixed": fixed
            },
            "results": {r.name: "PASS" if r.passed else ("FIXED" if r.fixed else "FAIL") for r in self.results},
            "fixes_applied": self.fixes_applied,
            "manual_review_needed": self.manual_review_needed
        }
        
        TEST_RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TEST_RESULTS_FILE, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"\nReport saved to: {TEST_RESULTS_FILE}")
    
    def create_github_issue(self):
        """Create GitHub issue for manual review items"""
        if not self.manual_review_needed:
            return
        
        issue_title = f"[Self-Test] {len(self.manual_review_needed)} Issues Require Manual Attention"
        
        issue_body = "## Self-Test Found Issues Requiring Manual Review\n\n"
        issue_body += f"**Test Run:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        issue_body += f"**Total Issues:** {len(self.manual_review_needed)}\n\n"
        
        for item in self.manual_review_needed:
            issue_body += f"### {item['test']} [{item['severity'].upper()}]\n\n"
            issue_body += f"**Issue:** {item['issue']}\n\n"
            issue_body += f"**Suggested Fix:** {item['suggested_fix']}\n\n"
            issue_body += "---\n\n"
        
        issue_body += "\n## What To Do\n\n"
        issue_body += "1. Review each issue above\n"
        issue_body += "2. Apply suggested fixes\n"
        issue_body += "3. Run self-test again: `python scripts/self_test.py`\n"
        issue_body += "4. Close this issue when all tests pass\n"
        
        # Write issue to file for GitHub Actions to create
        issue_file = REPO_ROOT / ".github" / "issue_draft.md"
        issue_file.parent.mkdir(parents=True, exist_ok=True)
        with open(issue_file, 'w') as f:
            f.write(f"# {issue_title}\n\n{issue_body}")
        
        self.log(f"\nGitHub issue draft created: {issue_file}")
        self.log("GitHub Actions will create the actual issue.")

def main():
    parser = argparse.ArgumentParser(description="Run self-tests on BrowserOS_Guides repository")
    parser.add_argument("--auto-fix", action="store_true", help="Automatically fix issues when possible")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--category", help="Run specific test category only")
    parser.add_argument("--report-only", action="store_true", help="Generate report from last run")
    
    args = parser.parse_args()
    
    if args.report_only:
        if TEST_RESULTS_FILE.exists():
            with open(TEST_RESULTS_FILE) as f:
                report = json.load(f)
            print(json.dumps(report, indent=2))
            return 0
        else:
            print("No test results found. Run tests first.")
            return 1
    
    tester = SelfTest(auto_fix=args.auto_fix, verbose=args.verbose)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
