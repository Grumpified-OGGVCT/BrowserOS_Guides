"""
Generate Executable Library Artifacts from Knowledge Base

This script extracts structured workflow patterns from the knowledge base
and generates executable JSON templates that can be consumed by BrowserOS agents.
"""

import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

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
        self.templates_dir = TEMPLATES_DIR
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.schema = self.load_schema()
        
    def load_schema(self) -> Dict:
        """Load the GraphDefinition schema"""
        if not SCHEMA_PATH.exists():
            return {}
        return json.loads(SCHEMA_PATH.read_text())
    
    def extract_step_types_from_kb(self) -> List[Dict[str, Any]]:
        """Extract step types documentation from KB"""
        if not KB_PATH.exists():
            print("⚠️ Knowledge base not found")
            return []
        
        content = KB_PATH.read_text()
        step_types = []
        
        # Find Step Types Catalog section (table format)
        step_section_match = re.search(
            r'##\s+Step Types Catalog.*?(?=##|\Z)', 
            content, 
            re.DOTALL
        )
        
        if not step_section_match:
            print("⚠️ Step Types Catalog not found in KB")
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
    
    def generate_step_templates(self, step_types: List[Dict]) -> None:
        """Generate individual step templates"""
        step_templates_dir = self.templates_dir / "steps"
        step_templates_dir.mkdir(exist_ok=True)
        
        for step in step_types:
            step_type = step['type']
            
            # Create minimal valid template
            template = {
                "type": step_type,
                "name": f"Sample {step_type.title()} Step",
                "description": step['description'],
                "_template_info": {
                    "generated_from": "BrowserOS_Workflows_KnowledgeBase.md",
                    "section": "Step Types Catalog",
                    "generated_at": datetime.now().isoformat(),
                    "parameters": step['parameters']
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
            template_path.write_text(json.dumps(template, indent=2))
            print(f"  ✓ Generated {step_type} template")
    
    def extract_workflow_patterns(self) -> List[Dict]:
        """Extract common workflow patterns from existing workflows"""
        patterns = []
        
        if not WORKFLOWS_DIR.exists():
            return patterns
        
        # Scan workflow directories
        for workflow_file in WORKFLOWS_DIR.rglob("*.json"):
            try:
                workflow = json.loads(workflow_file.read_text())
                
                # Extract pattern metadata
                pattern = {
                    "name": workflow.get("name", ""),
                    "category": workflow.get("category", ""),
                    "difficulty": workflow.get("difficulty", ""),
                    "tags": workflow.get("tags", []),
                    "step_types": [step.get("type") for step in workflow.get("steps", [])],
                    "source_file": str(workflow_file.relative_to(REPO_ROOT)),
                    "has_error_handling": "error_handling" in workflow,
                    "has_scheduling": "schedule" in workflow
                }
                
                patterns.append(pattern)
            except Exception as e:
                print(f"  ⚠️ Could not parse {workflow_file}: {e}")
        
        return patterns
    
    def generate_pattern_index(self, patterns: List[Dict]) -> None:
        """Generate searchable pattern index"""
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
            index["categories"][cat].append(pattern["name"])
        
        # Aggregate by step types
        for pattern in patterns:
            for step_type in pattern.get("step_types", []):
                if step_type not in index["step_types"]:
                    index["step_types"][step_type] = []
                index["step_types"][step_type].append(pattern["name"])
        
        index_path.write_text(json.dumps(index, indent=2))
        print(f"  ✓ Generated pattern index with {len(patterns)} patterns")
    
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
        
        base_dir = self.templates_dir / "base_workflows"
        base_dir.mkdir(exist_ok=True)
        
        for template in base_templates:
            # Create safe filename
            filename = template["name"].lower().replace(" ", "_") + ".json"
            filepath = base_dir / filename
            filepath.write_text(json.dumps(template, indent=2))
            print(f"  ✓ Generated {template['name']}")
    
    def run(self):
        """Execute full library generation"""
        print("=" * 60)
        print("🏗️  Generating Executable Library Artifacts")
        print("=" * 60)
        
        # Step 1: Extract step types from KB
        print("\n📚 Extracting step types from Knowledge Base...")
        step_types = self.extract_step_types_from_kb()
        print(f"  ✓ Found {len(step_types)} step types")
        
        # Step 2: Generate step templates
        if step_types:
            print("\n🔧 Generating step templates...")
            self.generate_step_templates(step_types)
        
        # Step 3: Extract workflow patterns
        print("\n🔍 Analyzing existing workflows...")
        patterns = self.extract_workflow_patterns()
        print(f"  ✓ Analyzed {len(patterns)} workflow patterns")
        
        # Step 4: Generate pattern index
        if patterns:
            print("\n📊 Generating pattern index...")
            self.generate_pattern_index(patterns)
        
        # Step 5: Generate base workflow templates
        print("\n🎯 Generating base workflow templates...")
        self.generate_base_workflows()
        
        print("\n" + "=" * 60)
        print("✅ Library generation complete!")
        print(f"📁 Artifacts location: {self.templates_dir}")
        print("=" * 60)


def main():
    """Main entry point"""
    generator = LibraryGenerator()
    generator.run()


if __name__ == "__main__":
    main()
