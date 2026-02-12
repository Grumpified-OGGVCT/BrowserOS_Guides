#!/usr/bin/env python3
"""
Generate Repository Structure JSON
Scans the actual repository and creates a live structure for the repo browser.
This replaces the hardcoded demo data with real, dynamically generated content.
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Files and directories to exclude from the browser
EXCLUDED_PATHS = {
    '.git', '__pycache__', 'node_modules', '.pytest_cache', 
    '.venv', 'venv', 'env', '.DS_Store', '.idea', '.vscode',
    '*.pyc', '*.pyo', '*.pyd', '.Python', 'pip-log.txt',
    'pip-delete-this-directory.txt', '.coverage', 'htmlcov',
    'dist', 'build', '*.egg-info', '.eggs'
}

# File type descriptions
FILE_DESCRIPTIONS = {
    '.md': 'Markdown documentation',
    '.py': 'Python script',
    '.yml': 'YAML configuration',
    '.yaml': 'YAML configuration',
    '.json': 'JSON data',
    '.txt': 'Text file',
    '.html': 'HTML page',
    '.css': 'Stylesheet',
    '.js': 'JavaScript',
    '.sh': 'Shell script',
    '.ps1': 'PowerShell script',
    '.env': 'Environment variables',
    '.gitignore': 'Git ignore rules',
    'Dockerfile': 'Docker container definition',
    'docker-compose.yml': 'Docker compose configuration',
    'requirements.txt': 'Python dependencies',
    'LICENSE': 'License file',
    'README.md': 'Project README'
}

# Special file descriptions
SPECIAL_FILES = {
    'structure.md': 'Primary repository index and structure',
    'BrowserOS_Workflows_KnowledgeBase.md': 'Comprehensive workflows knowledge base',
    'MCP_AGENTIC_GUIDE.md': 'MCP and agentic AI integration guide',
    'USE_CASE_MATRIX.md': '500+ use cases across 25+ industries',
    'ADVANCED_TECHNIQUES.md': 'Advanced and expert-level techniques',
    'AUTOMATION_QUICKSTART.md': 'Quick start guide for automation',
    'DEPLOYMENT.md': 'Deployment guide (6 connection types)',
    'SECURITY-POLICY.md': 'Security policy and guidelines',
    'SECURITY_AUDIT.md': 'Security audit report',
    'REPO_TRACKING.md': 'Repository tracking documentation',
    'config.yml': 'Main configuration (500+ parameters)',
    'self_test.py': 'Self-test automation (42 tests)',
    'security_scanner.py': 'Security vulnerability scanner',
    'workflow_generator.py': 'AI-powered workflow generation',
    'research_pipeline.py': 'Automated research pipeline',
    'repo_tracker.py': 'Repository tracking system',
    'generate_search_index.py': 'Search index generation',
    'update-kb.yml': 'Knowledge base update automation',
    'self-test.yml': 'Automated self-test workflow',
}


def should_exclude(path: Path, repo_root: Path) -> bool:
    """Check if a path should be excluded from the browser"""
    # Get relative path from repo root
    try:
        rel_path = path.relative_to(repo_root)
    except ValueError:
        return True
    
    # Check each part of the path
    for part in rel_path.parts:
        if part in EXCLUDED_PATHS or part.startswith('.'):
            # Allow some dot files
            if part in {'.github', '.env.template', '.gitignore'}:
                continue
            return True
    
    # Check patterns
    name = path.name
    for pattern in EXCLUDED_PATHS:
        if '*' in pattern:
            if pattern.startswith('*') and name.endswith(pattern[1:]):
                return True
            if pattern.endswith('*') and name.startswith(pattern[:-1]):
                return True
    
    return False


def get_file_description(file_path: Path) -> str:
    """Get a description for a file based on its name or extension"""
    name = file_path.name
    
    # Check special files first
    if name in SPECIAL_FILES:
        return SPECIAL_FILES[name]
    
    # Check extension
    ext = file_path.suffix.lower()
    if ext in FILE_DESCRIPTIONS:
        return FILE_DESCRIPTIONS[ext]
    
    # Check full name patterns
    if name == 'Dockerfile':
        return 'Docker container definition'
    
    # Default
    return f'{ext[1:].upper()} file' if ext else 'File'


def get_relative_path_for_web(file_path: Path, repo_root: Path, docs_dir: Path) -> str:
    """
    Get the relative path suitable for web links.
    If the file is in docs/, use relative path from docs/.
    Otherwise, use relative path from repo root with ../ prefix.
    """
    try:
        # Try to get path relative to docs directory
        rel_to_docs = file_path.relative_to(docs_dir)
        return str(rel_to_docs).replace('\\', '/')
    except ValueError:
        # File is outside docs/, use path from repo root with ../ prefix
        try:
            rel_to_repo = file_path.relative_to(repo_root)
            return '../' + str(rel_to_repo).replace('\\', '/')
        except ValueError:
            return file_path.name


def scan_directory(dir_path: Path, repo_root: Path, docs_dir: Path) -> Dict[str, Any]:
    """Recursively scan a directory and build structure"""
    
    if should_exclude(dir_path, repo_root):
        return None
    
    node = {
        'name': dir_path.name,
        'type': 'folder',
        'children': []
    }
    
    try:
        items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        
        for item in items:
            if should_exclude(item, repo_root):
                continue
            
            # Skip symlinks to avoid infinite loops and security issues
            if item.is_symlink():
                continue
            
            if item.is_dir():
                child = scan_directory(item, repo_root, docs_dir)
                if child and child.get('children'):  # Only include non-empty folders
                    node['children'].append(child)
            else:
                # File
                file_node = {
                    'name': item.name,
                    'type': 'file',
                    'description': get_file_description(item),
                    'path': get_relative_path_for_web(item, repo_root, docs_dir),
                    'size': item.stat().st_size,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
                node['children'].append(file_node)
    
    except PermissionError:
        print(f"⚠️ Permission denied: {dir_path}")
        return None
    except Exception as e:
        print(f"⚠️ Error scanning {dir_path}: {e}")
        return None
    
    return node


def count_stats(node: Dict[str, Any]) -> Dict[str, int]:
    """Count files and folders in the structure"""
    stats = {'files': 0, 'folders': 0, 'docs': 0}
    
    def count_recursive(n):
        if n['type'] == 'folder':
            stats['folders'] += 1
            for child in n.get('children', []):
                count_recursive(child)
        else:
            stats['files'] += 1
            if n['name'].endswith(('.md', '.html', '.txt')):
                stats['docs'] += 1
    
    count_recursive(node)
    return stats


def generate_repo_structure(repo_root: str = None, output_file: str = None):
    """Generate the repository structure JSON file"""
    
    # Determine paths
    if repo_root is None:
        repo_root = Path(__file__).parent.parent
    else:
        repo_root = Path(repo_root)
    
    if output_file is None:
        output_file = repo_root / 'docs' / 'repo-structure.json'
    else:
        output_file = Path(output_file)
    
    docs_dir = repo_root / 'docs'
    
    print(f"🔍 Scanning repository: {repo_root}")
    print(f"📊 Generating structure for repo browser...")
    
    # Scan the repository
    structure = scan_directory(repo_root, repo_root, docs_dir)
    
    if not structure:
        print("❌ Failed to generate structure")
        return False
    
    # Calculate statistics
    stats = count_stats(structure)
    
    # Add metadata
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'repository': repo_root.name,
        'stats': stats,
        'structure': structure
    }
    
    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated repository structure:")
    print(f"   📁 Folders: {stats['folders']}")
    print(f"   📄 Files: {stats['files']}")
    print(f"   📝 Documents: {stats['docs']}")
    print(f"   💾 Output: {output_file}")
    
    return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate repository structure JSON for browser'
    )
    parser.add_argument(
        '--repo-root',
        help='Repository root directory (default: auto-detect)',
        default=None
    )
    parser.add_argument(
        '--output',
        help='Output JSON file path (default: docs/repo-structure.json)',
        default=None
    )
    
    args = parser.parse_args()
    
    success = generate_repo_structure(args.repo_root, args.output)
    
    if not success:
        exit(1)
    
    print("\n✨ Repository structure ready for browser!")


if __name__ == '__main__':
    main()
