"""
Generate Executable Library Artifacts from Knowledge Base

This script extracts structured workflow patterns from the knowledge base
and generates executable JSON templates that can be consumed by BrowserOS agents.
"""

import json
import hashlib
import re
import traceback
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Import resilience utilities
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils.resilience import (
    ResilientLogger,
    safe_file_write,
    safe_file_read,
    safe_json_load
)

# Configuration
REPO_ROOT = Path(__file__).parent.parent
KB_PATH = REPO_ROOT / "BrowserOS" / "Research" / "BrowserOS_Workflows_KnowledgeBase.md"
WORKFLOWS_DIR = REPO_ROOT / "BrowserOS" / "Workflows"
LIBRARY_DIR = REPO_ROOT / "library"
TEMPLATES_DIR = LIBRARY_DIR / "templates"
SCHEMA_PATH = LIBRARY_DIR / "schemas" / "graph_definition.json"


class LibraryGenerator:
    """Generate executable library artifacts from workflows and KB"""
    
    def __init__(self):
        self.logger = ResilientLogger(__name__)
        self.templates_dir = TEMPLATES_DIR
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.schema = self.load_schema()
        
    def load_schema(self) -> Dict:
        """Load the GraphDefinition schema with validation"""
        if not SCHEMA_PATH.exists():
            self.logger.warn(f"Schema file not found at {SCHEMA_PATH}. Using empty schema.")
            return {}
        
        try:
            content = safe_file_read(str(SCHEMA_PATH), default="{}", logger=self.logger)
            schema = safe_json_load(content, default={}, logger=self.logger)
            
            # Validate schema structure
            if not schema:
                self.logger.warn("Schema is empty or invalid")
                return {}
                
            required_schema_fields = ["$schema", "type"]
            missing_fields = [field for field in required_schema_fields if field not in schema]
            
            if missing_fields:
                self.logger.warn(
                    f"Schema is missing required fields: {missing_fields}. "
                    f"Expected fields: {required_schema_fields}. "
                    f"Schema may be incomplete or invalid."
                )
            
            self.logger.debug(f"Loaded schema with {len(schema)} top-level keys")
            return schema
            
        except Exception as e:
            self.logger.error(
                f"Failed to load schema from {SCHEMA_PATH}: {e}",
                exc_info=True
            )
            return {}
    
    def extract_step_types_from_kb(self) -> List[Dict[str, Any]]:
        """Extract step types documentation from KB"""
        if not KB_PATH.exists():
            self.logger.warn(
                f"Knowledge base not found at {KB_PATH}. "
                f"Action: Ensure the KB file exists or update KB_PATH configuration."
            )
            return []
        
        try:
            content = safe_file_read(str(KB_PATH), default="", logger=self.logger)
            if not content:
                self.logger.warn("Knowledge base file is empty")
                return []
            
            step_types = []
            
            # Find Step Types Catalog section (table format)
            step_section_match = re.search(
                r'##\s+Step Types Catalog.*?(?=##|\Z)', 
                content, 
                re.DOTALL
            )
            
            if not step_section_match:
                self.logger.warn(
                    "Step Types Catalog section not found in KB. "
                    "Action: Verify KB structure includes '## Step Types Catalog' section."
                )
                return []
            
            step_section = step_section_match.group(0)
            
            # Extract step types from table format
            # Format: | **step_name** | description | config | example |
            table_pattern = r'\|\s*\*\*(\w+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|'
            matches = re.finditer(table_pattern, step_section)
            
            for match in matches:
                step_type = match.group(1).strip()
                description = match.group(2).strip()
                config = match.group(3).strip()
                example = match.group(4).strip()
                
                # Parse config parameters
                param_pattern = r'`([^`]+)`'
                param_matches = re.findall(param_pattern, config)
                parameters = [
                    {"name": param.strip(), "description": f"Configuration for {step_type}"}
                    for param in param_matches
                ]
                
                step_types.append({
                    "type": step_type,
                    "description": description,
                    "parameters": parameters,
                    "example": example
                })
            
            return step_types
            
        except Exception as e:
            self.logger.error(
                f"Failed to extract step types from KB: {e}",
                exc_info=True
            )
            return []
    
    def generate_step_templates(self, step_types: List[Dict]) -> None:
        """Generate individual step templates"""
        step_templates_dir = self.templates_dir / "steps"
        step_templates_dir.mkdir(exist_ok=True)
        
        for step in step_types:
            try:
                step_type = step.get('type')
                if not step_type:
                    self.logger.warn(f"Step missing 'type' field: {step}")
                    continue
                
                # Create minimal valid template
                template = {
                    "type": step_type,
                    "name": f"Sample {step_type.title()} Step",
                    "description": step.get('description', ''),
                    "_template_info": {
                        "generated_from": "BrowserOS_Workflows_KnowledgeBase.md",
                        "section": "Step Types Catalog",
                        "generated_at": datetime.now().isoformat(),
                        "parameters": step.get('parameters', [])
                    }
                }
                
                # Add common parameters based on step type
                if step_type == "navigate":
                    template.update({
                        "url": "https://example.com",
                        "wait_for": "networkidle",
                        "timeout": 30000
                    })
                elif step_type == "click":
                    template.update({
                        "selector": "#button-id",
                        "wait_after": 500
                    })
                elif step_type == "extract":
                    template.update({
                        "selector": ".data-element",
                        "attribute": "text",
                        "output": "extracted_data"
                    })
                elif step_type == "wait":
                    template.update({
                        "duration": 1000
                    })
                elif step_type == "conditional":
                    template.update({
                        "condition": "{{variable}} === true",
                        "then": [],
                        "else": []
                    })
                elif step_type == "loop":
                    template.update({
                        "iterator": "$.config.items",
                        "variable": "item",
                        "steps": []
                    })
                
                # Write template file
                template_path = step_templates_dir / f"{step_type}_template.json"
                success = safe_file_write(
                    str(template_path),
                    json.dumps(template, indent=2),
                    logger=self.logger
                )
                
                if success:
                    self.logger.info(f"  ✓ Generated {step_type} template")
                else:
                    self.logger.error(
                        f"Failed to write template for {step_type}. "
                        f"Action: Check directory permissions for {step_templates_dir}"
                    )
                    
            except Exception as e:
                self.logger.error(
                    f"Failed to generate template for step {step.get('type', 'unknown')}: {e}",
                    exc_info=True
                )
    
    def extract_workflow_patterns(self) -> List[Dict]:
        """Extract common workflow patterns from existing workflows"""
        patterns = []
        
        if not WORKFLOWS_DIR.exists():
            self.logger.warn(
                f"Workflows directory not found at {WORKFLOWS_DIR}. "
                f"Action: Create directory or update WORKFLOWS_DIR configuration."
            )
            return patterns
        
        # Scan workflow directories
        for workflow_file in WORKFLOWS_DIR.rglob("*.json"):
            try:
                content = safe_file_read(str(workflow_file), default=None, logger=self.logger)
                if not content:
                    self.logger.warn(f"Could not read workflow file: {workflow_file}")
                    continue
                    
                workflow = safe_json_load(content, default=None, logger=self.logger)
                if not workflow:
                    self.logger.warn(f"Could not parse JSON in workflow file: {workflow_file}")
                    continue
                
                # Validate workflow has required fields before accessing
                required_fields = ["name"]
                missing_fields = [field for field in required_fields if field not in workflow]
                
                if missing_fields:
                    self.logger.warn(
                        f"Workflow in {workflow_file} is missing required fields: {missing_fields}. "
                        f"Action: Add missing fields to workflow file."
                    )
                    # Continue processing with defaults for optional fields
                
                # Extract pattern metadata with safe defaults
                pattern = {
                    "name": workflow.get("name", "Unnamed Workflow"),
                    "category": workflow.get("category", "uncategorized"),
                    "difficulty": workflow.get("difficulty", "unknown"),
                    "tags": workflow.get("tags", []),
                    "step_types": [
                        step.get("type", "unknown") 
                        for step in workflow.get("steps", []) 
                        if isinstance(step, dict)
                    ],
                    "source_file": str(workflow_file.relative_to(REPO_ROOT)),
                    "has_error_handling": "error_handling" in workflow,
                    "has_scheduling": "schedule" in workflow
                }
                
                patterns.append(pattern)
                
            except Exception as e:
                self.logger.error(
                    f"Failed to parse workflow {workflow_file}: {e}",
                    exc_info=True
                )
                self.logger.error(
                    f"Action: Verify {workflow_file} contains valid JSON and required fields."
                )
        
        return patterns
    
    def generate_pattern_index(self, patterns: List[Dict]) -> None:
        """Generate searchable pattern index"""
        try:
            index_path = self.templates_dir / "pattern_index.json"
            
            index = {
                "generated_at": datetime.now().isoformat(),
                "total_patterns": len(patterns),
                "categories": {},
                "step_types": {},
                "patterns": patterns
            }
            
            # Aggregate by category
            for pattern in patterns:
                cat = pattern.get("category", "uncategorized")
                if cat not in index["categories"]:
                    index["categories"][cat] = []
                index["categories"][cat].append(pattern.get("name", "unnamed"))
            
            # Aggregate by step types
            for pattern in patterns:
                for step_type in pattern.get("step_types", []):
                    if step_type and step_type != "unknown":
                        if step_type not in index["step_types"]:
                            index["step_types"][step_type] = []
                        index["step_types"][step_type].append(pattern.get("name", "unnamed"))
            
            success = safe_file_write(
                str(index_path),
                json.dumps(index, indent=2),
                logger=self.logger
            )
            
            if success:
                self.logger.info(f"  ✓ Generated pattern index with {len(patterns)} patterns")
            else:
                self.logger.error(
                    f"Failed to write pattern index to {index_path}. "
                    f"Action: Check directory permissions for {self.templates_dir}"
                )
                
        except Exception as e:
            self.logger.error(
                f"Failed to generate pattern index: {e}",
                exc_info=True
            )
    
    def generate_base_workflows(self) -> None:
        """Generate minimal base workflow templates"""
        base_templates = [
            {
                "name": "Simple Navigation Workflow",
                "description": "Navigate to a URL and wait for page load",
                "version": "1.0.0",
                "category": "data-extraction",
                "difficulty": "beginner",
                "steps": [
                    {
                        "type": "navigate",
                        "name": "Navigate to Target URL",
                        "url": "{{config.target_url}}",
                        "wait_for": "networkidle"
                    }
                ]
            },
            {
                "name": "Click and Extract Workflow",
                "description": "Click an element and extract data",
                "version": "1.0.0",
                "category": "data-extraction",
                "difficulty": "beginner",
                "steps": [
                    {
                        "type": "click",
                        "name": "Click Target Element",
                        "selector": "{{config.button_selector}}"
                    },
                    {
                        "type": "wait",
                        "name": "Wait for Content",
                        "duration": 1000
                    },
                    {
                        "type": "extract",
                        "name": "Extract Data",
                        "selector": "{{config.data_selector}}",
                        "attribute": "text",
                        "output": "extracted_data"
                    }
                ]
            },
            {
                "name": "Conditional Navigation Workflow",
                "description": "Navigate with conditional logic",
                "version": "1.0.0",
                "category": "advanced-techniques",
                "difficulty": "intermediate",
                "steps": [
                    {
                        "type": "navigate",
                        "name": "Navigate to Page",
                        "url": "{{config.url}}"
                    },
                    {
                        "type": "conditional",
                        "name": "Check Element Existence",
                        "condition": "{{element_exists}}",
                        "then": [
                            {
                                "type": "click",
                                "name": "Click Element",
                                "selector": "{{config.element}}"
                            }
                        ],
                        "else": [
                            {
                                "type": "comment",
                                "name": "Element not found - skip"
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Loop Processing Workflow",
                "description": "Process multiple items in a loop",
                "version": "1.0.0",
                "category": "data-extraction",
                "difficulty": "intermediate",
                "steps": [
                    {
                        "type": "loop",
                        "name": "Process Each Item",
                        "iterator": "$.config.items",
                        "variable": "item",
                        "steps": [
                            {
                                "type": "navigate",
                                "name": "Navigate to Item",
                                "url": "{{item.url}}"
                            },
                            {
                                "type": "extract",
                                "name": "Extract Item Data",
                                "selector": ".item-data",
                                "attribute": "text",
                                "output": "item_{{item.id}}_data"
                            }
                        ]
                    }
                ]
            }
        ]
        
        try:
            base_dir = self.templates_dir / "base_workflows"
            base_dir.mkdir(exist_ok=True)
            
            for template in base_templates:
                try:
                    # Create safe filename
                    filename = template["name"].lower().replace(" ", "_") + ".json"
                    filepath = base_dir / filename
                    
                    success = safe_file_write(
                        str(filepath),
                        json.dumps(template, indent=2),
                        logger=self.logger
                    )
                    
                    if success:
                        self.logger.info(f"  ✓ Generated {template['name']}")
                    else:
                        self.logger.error(
                            f"Failed to write base workflow: {template['name']}. "
                            f"Action: Check directory permissions for {base_dir}"
                        )
                        
                except Exception as e:
                    self.logger.error(
                        f"Failed to generate base workflow {template.get('name', 'unknown')}: {e}",
                        exc_info=True
                    )
                    
        except Exception as e:
            self.logger.error(
                f"Failed to create base workflows directory: {e}",
                exc_info=True
            )
    
    def run(self):
        """Execute full library generation"""
        self.logger.info("=" * 60)
        self.logger.info("🏗️  Generating Executable Library Artifacts")
        self.logger.info("=" * 60)
        
        try:
            # Step 1: Extract step types from KB
            self.logger.info("\n📚 Extracting step types from Knowledge Base...")
            step_types = self.extract_step_types_from_kb()
            self.logger.info(f"  ✓ Found {len(step_types)} step types")
            
            # Step 2: Generate step templates
            if step_types:
                self.logger.info("\n🔧 Generating step templates...")
                self.generate_step_templates(step_types)
            else:
                self.logger.warn(
                    "No step types found - skipping step template generation. "
                    "Action: Verify KB file exists and contains Step Types Catalog."
                )
            
            # Step 3: Extract workflow patterns
            self.logger.info("\n🔍 Analyzing existing workflows...")
            patterns = self.extract_workflow_patterns()
            self.logger.info(f"  ✓ Analyzed {len(patterns)} workflow patterns")
            
            # Step 4: Generate pattern index
            if patterns:
                self.logger.info("\n📊 Generating pattern index...")
                self.generate_pattern_index(patterns)
            else:
                self.logger.warn(
                    "No workflow patterns found - skipping pattern index generation. "
                    "Action: Add workflow JSON files to the workflows directory."
                )
            
            # Step 5: Generate base workflow templates
            self.logger.info("\n🎯 Generating base workflow templates...")
            self.generate_base_workflows()
            
            self.logger.info("\n" + "=" * 60)
            self.logger.info("✅ Library generation complete!")
            self.logger.info(f"📁 Artifacts location: {self.templates_dir}")
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.critical(
                f"Library generation failed with unexpected error: {e}",
                exc_info=True
            )
            self.logger.critical(
                "Action: Review the error traceback above and ensure all dependencies are installed."
            )
            raise


def main():
    """Main entry point"""
    try:
        generator = LibraryGenerator()
        generator.run()
    except KeyboardInterrupt:
        logger = ResilientLogger(__name__)
        logger.warn("Library generation interrupted by user")
    except Exception as e:
        logger = ResilientLogger(__name__)
        logger.critical(
            f"Fatal error in library generation: {e}",
            exc_info=True
        )
        logger.critical(
            "Action: Check the error traceback above for details. "
            "Ensure all paths are correctly configured and dependencies are installed."
        )
        raise


if __name__ == "__main__":
    main()
