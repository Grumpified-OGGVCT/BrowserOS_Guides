"""
Enhanced Provenance Tracker for BrowserOS_Guides

This module adds file-level source code provenance to KB entries,
enabling "forensic accuracy" by linking documentation back to specific
source code locations (file + line ranges + commit SHA).

Supports Scenario 1: "10x Developer" use case
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configuration
REPO_ROOT = Path(__file__).parent.parent
BROWSEROS_REPO = REPO_ROOT / "BrowserOS" / "Research" / "raw" / "browseros-ai-BrowserOS"
KB_PATH = REPO_ROOT / "BrowserOS" / "Research" / "BrowserOS_Workflows_KnowledgeBase.md"
PROVENANCE_OUTPUT = REPO_ROOT / "library" / "provenance_index.json"


class ProvenanceTracker:
    """Track provenance from KB documentation to source code"""
    
    def __init__(self):
        self.browseros_repo = BROWSEROS_REPO
        self.kb_path = KB_PATH
        self.provenance_index = {}
        
    def get_current_commit_sha(self) -> Optional[str]:
        """Get current commit SHA of BrowserOS repo"""
        if not self.browseros_repo.exists():
            print("⚠️ BrowserOS repository not found")
            return None
        
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.browseros_repo,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def find_step_type_in_source(self, step_type: str) -> List[Dict[str, Any]]:
        """Find source code locations for a step type"""
        locations = []
        
        if not self.browseros_repo.exists():
            return locations
        
        # Search patterns for step type definitions
        patterns = [
            # TypeScript/JavaScript patterns
            rf"class\s+{step_type.title()}Step",
            rf"export\s+.*{step_type}",
            rf"type:\s*['\"]({step_type})['\"]",
            rf"stepType:\s*['\"]({step_type})['\"]",
            # Function definitions
            rf"function\s+execute{step_type.title()}",
            rf"async\s+{step_type}\(",
        ]
        
        # Search in source files
        for source_file in self.browseros_repo.rglob("*.ts"):
            # Skip node_modules and test files
            if 'node_modules' in str(source_file) or 'test' in source_file.stem.lower():
                continue
            
            try:
                content = source_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                for pattern in patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        # Find line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Extract context (5 lines)
                        start_line = max(0, line_num - 3)
                        end_line = min(len(lines), line_num + 3)
                        context = '\n'.join(lines[start_line:end_line])
                        
                        locations.append({
                            'file': str(source_file.relative_to(self.browseros_repo)),
                            'line_number': line_num,
                            'line_range': f"{start_line + 1}-{end_line}",
                            'match_pattern': pattern,
                            'context_preview': context[:200] + '...' if len(context) > 200 else context
                        })
                        
                        # Only take first match per file to avoid duplicates
                        break
            
            except Exception as e:
                print(f"  ⚠️ Could not read {source_file}: {e}")
                continue
        
        return locations
    
    def extract_step_types_from_kb(self) -> List[Dict[str, Any]]:
        """Extract step types documented in KB"""
        if not self.kb_path.exists():
            return []
        
        content = self.kb_path.read_text()
        step_types = []
        
        # Extract from table format: | **step_name** | description | config | example |
        table_pattern = r'\|\s*\*\*(\w+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|'
        matches = re.finditer(table_pattern, content)
        
        for match in matches:
            step_type = match.group(1).strip()
            description = match.group(2).strip()
            config = match.group(3).strip()
            example = match.group(4).strip()
            
            step_types.append({
                'step_type': step_type,
                'description': description,
                'config': config,
                'example': example,
                'kb_location': 'BrowserOS_Workflows_KnowledgeBase.md',
                'documented_at': datetime.now().isoformat()
            })
        
        return step_types
    
    def build_provenance_index(self) -> Dict[str, Any]:
        """Build complete provenance index linking KB to source"""
        print("=" * 60)
        print("🔍 Building Enhanced Provenance Index")
        print("=" * 60)
        
        # Get current commit SHA
        commit_sha = self.get_current_commit_sha()
        print(f"\n📌 BrowserOS Commit: {commit_sha[:8] if commit_sha else 'N/A'}")
        
        # Extract step types from KB
        print("\n📚 Extracting step types from KB...")
        kb_step_types = self.extract_step_types_from_kb()
        print(f"  ✓ Found {len(kb_step_types)} documented step types")
        
        # Build provenance for each step type
        print("\n🔗 Linking KB documentation to source code...")
        provenance_index = {
            'generated_at': datetime.now().isoformat(),
            'browseros_commit_sha': commit_sha,
            'kb_version': self.kb_path.stat().st_mtime,
            'step_types': {}
        }
        
        for step_info in kb_step_types:
            step_type = step_info['step_type']
            print(f"  🔍 Searching for '{step_type}'...")
            
            # Find in source code
            source_locations = self.find_step_type_in_source(step_type)
            
            provenance_index['step_types'][step_type] = {
                'description': step_info['description'],
                'kb_documentation': {
                    'file': 'BrowserOS/Research/BrowserOS_Workflows_KnowledgeBase.md',
                    'section': 'Step Types Catalog',
                    'documented_at': step_info['documented_at']
                },
                'source_code_locations': source_locations,
                'provenance_confidence': 'high' if source_locations else 'low',
                'last_verified': datetime.now().isoformat()
            }
            
            if source_locations:
                print(f"    ✓ Found {len(source_locations)} source location(s)")
            else:
                print(f"    ⚠️  No source locations found")
        
        # Summary statistics
        total_steps = len(provenance_index['step_types'])
        steps_with_provenance = sum(
            1 for v in provenance_index['step_types'].values() 
            if v['source_code_locations']
        )
        
        provenance_index['statistics'] = {
            'total_step_types': total_steps,
            'steps_with_source_provenance': steps_with_provenance,
            'provenance_coverage': f"{(steps_with_provenance / total_steps * 100):.1f}%" if total_steps > 0 else "0%"
        }
        
        return provenance_index
    
    def save_provenance_index(self, index: Dict[str, Any]) -> None:
        """Save provenance index to file"""
        PROVENANCE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        PROVENANCE_OUTPUT.write_text(json.dumps(index, indent=2))
        print(f"\n💾 Saved provenance index to {PROVENANCE_OUTPUT}")
    
    def run(self):
        """Execute full provenance tracking"""
        index = self.build_provenance_index()
        self.save_provenance_index(index)
        
        print("\n" + "=" * 60)
        print("✅ Provenance Index Complete!")
        print("=" * 60)
        print(f"📊 Coverage: {index['statistics']['provenance_coverage']}")
        print(f"📁 Output: {PROVENANCE_OUTPUT}")
        print("=" * 60)
        
        return index


def main():
    """Main entry point"""
    try:
        tracker = ProvenanceTracker()
        tracker.run()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nProvenance build interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error building provenance index: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
