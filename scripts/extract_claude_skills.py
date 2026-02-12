#!/usr/bin/env python3
"""
Extract and adapt skills from awesome-claude-skills repository
Transforms Composio/Claude skills into BrowserOS workflows
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

REPO_ROOT = Path(__file__).parent.parent
SKILLS_REPO_PATH = Path("/tmp/awesome-claude-skills")
WORKFLOWS_DIR = REPO_ROOT / "BrowserOS" / "Workflows"
EXTRACTED_DIR = WORKFLOWS_DIR / "Community-Contributed" / "claude-skills-adapted"

# Security patterns to detect malicious code
SECURITY_PATTERNS = [
    (r'<script[^>]*>', "Script tag injection"),
    (r'javascript:', "JavaScript protocol"),
    (r'\beval\s*\(', "eval() execution"),
    (r'\bexec\s*\(', "exec() execution"),
    (r'__proto__', "Prototype pollution"),
    (r'on\w+\s*=', "Event handler injection"),
    (r'document\.write', "document.write XSS"),
    (r'innerHTML\s*=', "innerHTML XSS"),
]

class SkillExtractor:
    """Extract and transform Claude skills to BrowserOS workflows"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.extracted_skills = []
        self.skipped_skills = []
        
    def log(self, message: str):
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def clone_skills_repo(self):
        """Clone or update awesome-claude-skills repo"""
        if SKILLS_REPO_PATH.exists():
            self.log(f"Updating existing repo at {SKILLS_REPO_PATH}")
            subprocess.run(
                ["git", "-C", str(SKILLS_REPO_PATH), "pull"],
                check=True,
                capture_output=True
            )
        else:
            self.log(f"Cloning awesome-claude-skills to {SKILLS_REPO_PATH}")
            subprocess.run(
                ["git", "clone", "https://github.com/Grumpified-OGGVCT/awesome-claude-skills.git",
                 str(SKILLS_REPO_PATH)],
                check=True,
                capture_output=True
            )
    
    def load_skill_index(self) -> Dict:
        """Load the SKILL-INDEX.json"""
        index_path = SKILLS_REPO_PATH / "SKILL-INDEX.json"
        with open(index_path) as f:
            return json.load(f)
    
    def is_browseros_compatible(self, skill: Dict) -> bool:
        """Determine if skill can be adapted to BrowserOS"""
        # Skills involving web automation, scraping, or browser interaction
        browser_keywords = [
            "web", "browser", "scrape", "extract", "automation",
            "click", "fill", "form", "page", "dom", "screenshot",
            "download", "upload", "navigation"
        ]
        
        description = skill.get("description", "").lower()
        name = skill.get("name", "").lower()
        
        return any(kw in description or kw in name for kw in browser_keywords)
    
    def read_skill_file(self, skill: Dict) -> Optional[str]:
        """Read the SKILL.md file for a skill"""
        skill_file = SKILLS_REPO_PATH / skill["skill_file"]
        if skill_file.exists():
            content = skill_file.read_text()
            # Security check before processing
            if self.validate_content_security(content, skill["name"]):
                return content
            else:
                self.log(f"⚠️  Security check failed for: {skill['name']}")
                return None
        return None
    
    def validate_content_security(self, content: str, skill_name: str) -> bool:
        """Validate content for security issues"""
        threats_found = []
        
        for pattern, description in SECURITY_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                threats_found.append(description)
        
        if threats_found:
            self.log(f"🚨 SECURITY ALERT in {skill_name}: {', '.join(threats_found)}")
            self.skipped_skills.append(f"{skill_name}: Security threat - {', '.join(threats_found)}")
            return False
        
        return True
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize content by removing potentially dangerous patterns"""
        # Remove script tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        # Remove event handlers
        content = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        # Remove javascript: protocols
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        return content
    
    def transform_to_browseros_workflow(self, skill: Dict, skill_content: str) -> Dict:
        """Transform Claude skill to BrowserOS workflow format"""
        # Sanitize content first
        skill_content = self.sanitize_content(skill_content)
        
        # Extract use cases from skill content
        use_cases = re.findall(r'(?:use case|example|scenario):?\s*(.+?)(?:\n|$)', 
                               skill_content, re.IGNORECASE)
        
        # Clean and filter use cases - remove artifacts like "|", ".com", empty strings
        cleaned_use_cases = []
        for uc in use_cases[:5]:
            uc = uc.strip()
            # Skip if it's just a placeholder, domain fragment, or too short
            if uc and len(uc) > 3 and uc not in ["|", ".com", "...", "-"]:
                # Skip if it's just a domain or URL fragment
                if not re.match(r'^[\w.-]+\.(com|org|net|io)$', uc, re.IGNORECASE):
                    cleaned_use_cases.append(uc)
        
        # Generate stable ID from name (snake_case)
        stable_id = skill["name"].replace("-", "_").lower()
        
        # Create ISO 8601 timestamp with UTC timezone
        created_timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        workflow = {
            "name": skill["name"].replace("-", "_"),
            "id": stable_id,
            "description": skill["description"],
            "version": "1.0.0",
            "source": "adapted-from-claude-skill",
            "original_skill": skill["name"],
            "category": skill.get("category", "Other"),
            "tags": skill.get("tags", []) + ["claude-skill", "community"],
            "metadata": {
                "created": created_timestamp,
                "adapted_from": "awesome-claude-skills",
                "requires_mcp": skill.get("requires", {}).get("mcp", []),
                "use_cases": cleaned_use_cases if cleaned_use_cases else []
            },
            "steps": [
                {
                    "name": "navigate",
                    "type": "navigate",
                    "url": "{{target_url}}",
                    "description": "Navigate to target website"
                },
                {
                    "name": "extract_data",
                    "type": "extract",
                    "selector": "{{data_selector}}",
                    "description": f"Extract relevant data for {skill['name']}"
                },
                {
                    "name": "process_results",
                    "type": "custom",
                    "description": "Process extracted data",
                    "notes": "Adapted from Claude skill - implement custom logic here"
                }
            ],
            "configuration": {
                "target_url": {
                    "type": "string",
                    "required": True,
                    "description": "Target website URL"
                },
                "data_selector": {
                    "type": "string",
                    "required": True,
                    "description": "CSS selector for data extraction"
                }
            },
            "notes": [
                f"This workflow was automatically adapted from the Claude skill: {skill['name']}",
                "Original skill description: " + skill["description"],
                "Additional customization required for production use",
                "See original skill at: https://github.com/Grumpified-OGGVCT/awesome-claude-skills",
                "⚠️ SECURITY: This workflow has been scanned and sanitized, but review before production use",
                "Content hash: " + hashlib.sha256(skill_content.encode()).hexdigest()[:16]
            ]
        }
        
        return workflow
    
    def save_workflow(self, workflow: Dict, skill_name: str):
        """Save transformed workflow to file"""
        EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
        
        output_file = EXTRACTED_DIR / f"{skill_name}.json"
        with open(output_file, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        self.log(f"Saved workflow: {output_file}")
        return output_file
    
    def create_category_readme(self):
        """Create README for claude-skills-adapted category"""
        readme_content = f"""# Claude Skills Adapted to BrowserOS

This directory contains workflows automatically adapted from the [awesome-claude-skills](https://github.com/Grumpified-OGGVCT/awesome-claude-skills) repository.

## About

The awesome-claude-skills repository contains 107+ ready-to-use AI workflows (called "skills") for Claude AI. We've automatically extracted and transformed the browser-compatible skills into BrowserOS workflow format.

## Credit

**Huge credit to the awesome-claude-skills community and maintainers!** 🙏

- Original Repository: https://github.com/Grumpified-OGGVCT/awesome-claude-skills
- Original Maintainers: Composio HQ and contributors
- License: Apache 2.0

## What Was Extracted

We automatically identified skills that involve:
- Web automation
- Browser interaction
- Data scraping/extraction
- Form filling
- Page navigation
- Screenshot capture

## How These Workflows Work

Each workflow in this directory:
1. **Was automatically generated** from a Claude skill
2. **Requires customization** for production use
3. **Maintains attribution** to the original skill
4. **Follows BrowserOS** workflow format

## Usage

These workflows are **starting templates** that need customization:

1. Choose a workflow that matches your use case
2. Update the `target_url` and `data_selector` configuration
3. Customize the extraction steps for your specific needs
4. Test thoroughly before production use

## Contributing

If you improve one of these adapted workflows:
1. Test it thoroughly
2. Add detailed documentation
3. Submit a pull request
4. Consider contributing back to awesome-claude-skills!

## Statistics

- **Total Skills in Source**: 107+
- **Extracted for BrowserOS**: {len(self.extracted_skills)}
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d')}

## Categories Extracted

{self._generate_category_stats()}

---

*Automatically generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*  
*Source: [awesome-claude-skills](https://github.com/Grumpified-OGGVCT/awesome-claude-skills)*
"""
        
        readme_file = EXTRACTED_DIR / "README.md"
        readme_file.write_text(readme_content)
        self.log(f"Created README: {readme_file}")
    
    def _generate_category_stats(self) -> str:
        """Generate statistics by category"""
        categories = {}
        for skill in self.extracted_skills:
            cat = skill.get("category", "Other")
            categories[cat] = categories.get(cat, 0) + 1
        
        stats = []
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            stats.append(f"- **{cat}**: {count} workflows")
        
        return "\n".join(stats) if stats else "- No categories yet"
    
    def extract_all_skills(self):
        """Main extraction process"""
        self.log("Starting skill extraction process...")
        
        # Clone/update repo
        self.clone_skills_repo()
        
        # Load skill index
        index = self.load_skill_index()
        total_skills = index["total_skills"]
        
        self.log(f"Found {total_skills} skills in index")
        
        # Process each skill
        for skill in index["skills"]:
            if self.is_browseros_compatible(skill):
                skill_content = self.read_skill_file(skill)
                if skill_content:
                    workflow = self.transform_to_browseros_workflow(skill, skill_content)
                    self.save_workflow(workflow, skill["name"])
                    self.extracted_skills.append(workflow)
                    self.log(f"✓ Extracted: {skill['name']}")
                else:
                    self.skipped_skills.append(f"{skill['name']}: No skill file")
            else:
                self.skipped_skills.append(f"{skill['name']}: Not browser-compatible")
        
        # Create category README
        self.create_category_readme()
        
        # Summary
        self.log("\n" + "=" * 60)
        self.log(f"Extraction Complete!")
        self.log(f"Total Skills Processed: {total_skills}")
        self.log(f"Extracted: {len(self.extracted_skills)}")
        self.log(f"Skipped: {len(self.skipped_skills)}")
        self.log("=" * 60)
        
        return len(self.extracted_skills)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract Claude skills to BrowserOS workflows")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--dry-run", action="store_true", help="Don't save files, just report")
    
    args = parser.parse_args()
    
    extractor = SkillExtractor(verbose=args.verbose)
    
    if not args.dry_run:
        count = extractor.extract_all_skills()
        print(f"\n✓ Successfully extracted {count} skills to {EXTRACTED_DIR}")
        return 0
    else:
        print("Dry run - no files created")
        return 0

if __name__ == "__main__":
    sys.exit(main())
