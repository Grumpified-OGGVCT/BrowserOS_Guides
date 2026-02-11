"""
Knowledge Base Validation Script

Validates the KB structure and completeness similar to the PowerShell script.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Configuration
REPO_ROOT = Path(__file__).parent.parent
KB_PATH = REPO_ROOT / "BrowserOS" / "Research" / "BrowserOS_Workflows_KnowledgeBase.md"
SOURCES_PATH = REPO_ROOT / "BrowserOS" / "Research" / "sources.json"

REQUIRED_SECTIONS = [
    "Overview & Scope",
    "Architecture Diagram",
    "Step Types Catalog",
    "Execution Flow Control Primer",
    "Trigger & Integration Matrix",
    "Configuration Schema Reference",
    "Advanced / Enterprise Features",
    "Limitations & Constraints",
    "Security Best Practices",
    "Community Patterns & Case Studies",
    "Migration & Version History",
    "Appendices"
]

PLACEHOLDER_MARKERS = ["TODO", "TBD", "INSERT", "FIXME", "PLACEHOLDER"]


def validate_sections() -> list:
    """C01: Verify all required sections are present"""
    failures = []
    
    if not KB_PATH.exists():
        return ["Knowledge base file not found"]
    
    content = KB_PATH.read_text()
    
    # Extract H2 sections
    found_sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    found_sections = [s.strip() for s in found_sections]
    
    for section in REQUIRED_SECTIONS:
        if section not in found_sections:
            failures.append(f"Missing required section: '{section}'")
    
    return failures


def validate_placeholders() -> list:
    """C02: Check for placeholder markers"""
    failures = []
    
    if not KB_PATH.exists():
        return ["Knowledge base file not found"]
    
    content = KB_PATH.read_text()
    
    for marker in PLACEHOLDER_MARKERS:
        if marker in content:
            count = content.count(marker)
            failures.append(f"Found {count} instance(s) of '{marker}'")
    
    return failures


def validate_sources() -> list:
    """C03: Validate sources manifest"""
    failures = []
    
    if not SOURCES_PATH.exists():
        return ["Sources manifest not found"]
    
    try:
        sources = json.loads(SOURCES_PATH.read_text())
        
        if not isinstance(sources, list):
            failures.append("Sources must be a list")
        elif len(sources) == 0:
            failures.append("Sources list is empty")
        
        # Validate source structure
        required_fields = ['url', 'accessed', 'author', 'type', 'abstract']
        for i, source in enumerate(sources):
            for field in required_fields:
                if field not in source:
                    failures.append(f"Source {i} missing field: {field}")
    
    except json.JSONDecodeError as e:
        failures.append(f"Invalid JSON in sources.json: {e}")
    
    return failures


def validate_checksum() -> list:
    """C05: Update checksum"""
    import hashlib
    
    failures = []
    checksum_path = KB_PATH.with_suffix('.md.checksum')
    
    if not KB_PATH.exists():
        return ["Knowledge base file not found"]
    
    # Calculate current hash
    content = KB_PATH.read_bytes()
    current_hash = hashlib.sha256(content).hexdigest()
    
    # Update checksum file
    checksum_path.write_text(current_hash)
    
    return failures


def main():
    """Run all validation checks"""
    print("=" * 60)
    print("🔍 Validating BrowserOS Knowledge Base")
    print("=" * 60)
    
    all_failures = []
    
    # C01: Section presence
    print("\n📋 C01: Checking section presence...")
    failures = validate_sections()
    if failures:
        print(f"  ❌ Failed: {len(failures)} issue(s)")
        all_failures.extend(failures)
    else:
        print("  ✅ Passed")
    
    # C02: Placeholder markers
    print("\n🔍 C02: Checking for placeholders...")
    failures = validate_placeholders()
    if failures:
        print(f"  ❌ Failed: {len(failures)} issue(s)")
        all_failures.extend(failures)
    else:
        print("  ✅ Passed")
    
    # C03: Sources validation
    print("\n📚 C03: Validating sources...")
    failures = validate_sources()
    if failures:
        print(f"  ❌ Failed: {len(failures)} issue(s)")
        all_failures.extend(failures)
    else:
        print("  ✅ Passed")
    
    # C05: Checksum update
    print("\n🔐 C05: Updating checksum...")
    failures = validate_checksum()
    if failures:
        print(f"  ❌ Failed: {len(failures)} issue(s)")
        all_failures.extend(failures)
    else:
        print("  ✅ Passed")
    
    # Summary
    print("\n" + "=" * 60)
    if all_failures:
        print(f"❌ Validation FAILED with {len(all_failures)} issue(s):")
        for failure in all_failures:
            print(f"  • {failure}")
        return 1
    else:
        print("✅ All validation checks PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
