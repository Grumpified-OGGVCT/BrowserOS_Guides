"""
Knowledge Base Validation Script

Validates the KB structure and completeness similar to the PowerShell script.
Now includes Ground Truth Validation against source code.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Import resilience utilities
sys.path.insert(0, str(Path(__file__).parent))
from utils.resilience import ResilientLogger, safe_file_read

# Configuration
REPO_ROOT = Path(__file__).parent.parent
KB_PATH = REPO_ROOT / "BrowserOS" / "Research" / "BrowserOS_Workflows_KnowledgeBase.md"
SOURCES_PATH = REPO_ROOT / "BrowserOS" / "Research" / "sources.json"
LIBRARY_SCHEMA_PATH = REPO_ROOT / "library" / "schemas" / "graph_definition.json"
BROWSEROS_REPO = REPO_ROOT / "BrowserOS" / "Research" / "raw" / "browseros-ai-BrowserOS"

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

# Initialize logger
logger = ResilientLogger("validate_kb")


def validate_sections() -> list:
    """C01: Verify all required sections are present"""
    failures = []
    
    if not Path(KB_PATH).exists():
        logger.error(f"Knowledge base file not found at {KB_PATH}")
        return ["Knowledge base file not found"]
    
    content = safe_file_read(str(KB_PATH), default=None, logger=logger)
    if content is None:
        logger.error(f"Failed to read knowledge base file: {KB_PATH}")
        return ["Failed to read knowledge base file"]
    
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
    
    if not Path(KB_PATH).exists():
        logger.error(f"Knowledge base file not found at {KB_PATH}")
        return ["Knowledge base file not found"]
    
    content = safe_file_read(str(KB_PATH), default=None, logger=logger)
    if content is None:
        logger.error(f"Failed to read knowledge base file: {KB_PATH}")
        return ["Failed to read knowledge base file"]
    
    for marker in PLACEHOLDER_MARKERS:
        if marker in content:
            count = content.count(marker)
            failures.append(f"Found {count} instance(s) of '{marker}'")
    
    return failures


def validate_sources() -> list:
    """C03: Validate sources manifest"""
    failures = []
    
    if not Path(SOURCES_PATH).exists():
        logger.error(f"Sources manifest not found at {SOURCES_PATH}")
        return ["Sources manifest not found"]
    
    try:
        content = safe_file_read(str(SOURCES_PATH), default=None, logger=logger)
        if content is None:
            logger.error(f"Failed to read sources manifest: {SOURCES_PATH}")
            return ["Failed to read sources manifest"]
        
        sources = json.loads(content)
        
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
        logger.error(f"Invalid JSON in sources.json: {e}", exc_info=True)
        failures.append(f"Invalid JSON in sources.json: {e}")
    except Exception as e:
        logger.error(f"Error validating sources: {e}", exc_info=True)
        failures.append(f"Error validating sources: {e}")
    
    return failures


def validate_checksum() -> list:
    """C05: Update checksum"""
    import hashlib
    
    failures = []
    checksum_path = KB_PATH.with_suffix('.md.checksum')
    
    if not Path(KB_PATH).exists():
        logger.error(f"Knowledge base file not found at {KB_PATH}")
        return ["Knowledge base file not found"]
    
    # Calculate current hash
    try:
        content = KB_PATH.read_bytes()
        current_hash = hashlib.sha256(content).hexdigest()
        
        # Update checksum file
        checksum_path.write_text(current_hash)
        logger.info(f"Checksum updated: {current_hash[:16]}...")
    except Exception as e:
        logger.error(f"Failed to update checksum: {e}", exc_info=True)
        failures.append(f"Failed to update checksum: {e}")
    
    return failures


def validate_ground_truth() -> list:
    """C06: Ground Truth Validation - Verify KB against source code"""
    failures = []
    
    if not Path(KB_PATH).exists():
        logger.error(f"Knowledge base file not found at {KB_PATH}")
        return ["Knowledge base file not found"]
    
    content = safe_file_read(str(KB_PATH), default=None, logger=logger)
    if content is None:
        logger.error(f"Failed to read knowledge base file: {KB_PATH}")
        return ["Failed to read knowledge base file"]
    
    kb_content = content
    
    # Extract step types from table format in KB
    # Format: | **step_name** | description | config | example |
    step_type_pattern = r'\|\s*\*\*(\w+)\*\*\s*\|'
    all_types = set(re.findall(step_type_pattern, kb_content))
    
    # Exclude trigger mechanism types (these are not step types)
    # Trigger types are documented in a separate section
    trigger_types = {'Manual', 'Scheduled', 'API', 'Webhook', 'Event'}
    kb_step_types = all_types - trigger_types
    
    if not kb_step_types:
        return ["No step types found in KB"]
    
    # Try to validate against schema if available
    if Path(LIBRARY_SCHEMA_PATH).exists():
        try:
            content = safe_file_read(str(LIBRARY_SCHEMA_PATH), default=None, logger=logger)
            if content is None:
                logger.warn(f"Failed to read schema file: {LIBRARY_SCHEMA_PATH}")
            else:
                schema = json.loads(content)
            
            # Get valid step types from schema
            if 'definitions' in schema and 'step' in schema['definitions']:
                step_def = schema['definitions']['step']
                if 'properties' in step_def and 'type' in step_def['properties']:
                    type_prop = step_def['properties']['type']
                    if 'enum' in type_prop:
                        schema_step_types = set(type_prop['enum'])
                        
                        # Check for KB step types not in schema
                        undocumented = kb_step_types - schema_step_types
                        if undocumented:
                            for step_type in undocumented:
                                failures.append(f"KB mentions undocumented step type: '{step_type}'")
                        
                        # Check for schema types not in KB
                        missing_from_kb = schema_step_types - kb_step_types
                        if missing_from_kb:
                            for step_type in missing_from_kb:
                                failures.append(f"Schema defines '{step_type}' but KB doesn't document it")
        
        except json.JSONDecodeError as e:
            logger.error(f"Schema JSON parsing error: {e}", exc_info=True)
            failures.append(f"Could not validate against schema: Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Schema validation error: {e}", exc_info=True)
            failures.append(f"Could not validate against schema: {e}")
    
    # Check if BrowserOS repo is available for deeper validation
    if BROWSEROS_REPO.exists():
        # Look for step type definitions in source code
        # This is a simplified check - could be enhanced to parse TypeScript
        source_files = []
        for pattern in ['**/*.ts', '**/*.js']:
            source_files.extend(BROWSEROS_REPO.glob(pattern))
        
        # Search for step type definitions in source
        found_in_source = set()
        for source_file in source_files[:50]:  # Limit to avoid performance issues
            try:
                content = source_file.read_text(encoding='utf-8', errors='ignore')
                for step_type in kb_step_types:
                    # Look for step type definitions (simplified pattern)
                    if f"'{step_type}'" in content or f'"{step_type}"' in content:
                        found_in_source.add(step_type)
            except Exception:
                pass
        
        # Warn about step types in KB but not found in source
        not_in_source = kb_step_types - found_in_source
        if not_in_source:
            for step_type in not_in_source:
                # This is a warning, not a failure - source analysis is imperfect
                logger.warn(f"Step type '{step_type}' in KB but not clearly found in source")
                print(f"  ⚠️  Step type '{step_type}' in KB but not clearly found in source")
    
    return failures


def main():
    """Run all validation checks"""
    print("=" * 60)
    print("🔍 Validating BrowserOS Knowledge Base")
    print("=" * 60)
    
    logger.info("Starting KB validation")
    
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
    
    # C06: Ground Truth Validation
    print("\n🔍 C06: Ground truth validation...")
    failures = validate_ground_truth()
    if failures:
        print(f"  ❌ Failed: {len(failures)} issue(s)")
        all_failures.extend(failures)
    else:
        print("  ✅ Passed")
    
    # Summary
    print("\n" + "=" * 60)
    if all_failures:
        print(f"❌ Validation FAILED with {len(all_failures)} issue(s):")
        logger.error(f"Validation failed with {len(all_failures)} issues")
        for failure in all_failures:
            print(f"  • {failure}")
            logger.error(f"  {failure}")
        return 1
    else:
        print("✅ All validation checks PASSED")
        logger.info("All validation checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
