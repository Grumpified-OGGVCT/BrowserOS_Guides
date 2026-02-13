#!/usr/bin/env python3
"""
Search Index Generator for BrowserOS Knowledge Hub
Scans all markdown and JSON files and creates a searchable index with semantic content
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
import hashlib

def extract_markdown_content(filepath):
    """Extract title, headings, and content from markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else os.path.basename(filepath)
        
        # Extract all headings
        headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        
        # Extract description (first paragraph after title)
        desc_match = re.search(r'^#\s+.+?\n\n(.+?)\n\n', content, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        description = description[:200] + "..." if len(description) > 200 else description
        
        # Remove markdown syntax for full text search
        clean_content = re.sub(r'[#*_`\[\]()]', ' ', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Extract keywords (words that appear frequently)
        words = re.findall(r'\b[a-z]{4,}\b', clean_content.lower())
        word_freq = {}
        for word in words:
            if word not in ['that', 'this', 'with', 'from', 'have', 'will', 'been', 'were', 'workflow', 'automation']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords = [k[0] for k in keywords]
        
        return {
            'title': title,
            'description': description,
            'headings': headings[:10],  # First 10 headings
            'keywords': keywords,
            'content': clean_content[:1000],  # First 1000 chars for preview
            'word_count': len(words)
        }
    except Exception as e:
        print(f"Error processing MD {filepath}: {e}")
        return None

def extract_json_content(filepath):
    """Extract content from JSON workflow files"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        title = data.get('name', os.path.basename(filepath))
        description = data.get('description', '')
        
        # Build content for search from various fields
        content_parts = [
            title,
            description,
            data.get('category', ''),
            " ".join(data.get('tags', [])),
            " ".join(data.get('metadata', {}).get('use_cases', [])),
            " ".join(note for note in data.get('notes', []) if isinstance(note, str))
        ]
        
        # Add steps descriptions
        for step in data.get('steps', []):
            content_parts.append(step.get('name', ''))
            content_parts.append(step.get('description', ''))
            
        full_text = " ".join(part for part in content_parts if isinstance(part, str))
        clean_content = re.sub(r'\s+', ' ', full_text).strip()
        
        # Extract keywords
        keywords = data.get('tags', [])
        words = re.findall(r'\b[a-z]{4,}\b', clean_content.lower())
        word_freq = {}
        for word in words:
            if word not in ['that', 'this', 'with', 'from', 'have', 'will', 'been', 'were', 'workflow', 'automation', 'step', 'type']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        additional_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        keywords.extend([k[0] for k in additional_keywords])
        
        return {
            'title': title,
            'description': description,
            'headings': ['Overview', 'Steps', 'Configuration', 'Notes'],
            'keywords': list(set(keywords))[:10],
            'content': clean_content[:1000],
            'word_count': len(words)
        }
    except Exception as e:
        print(f"Error processing JSON {filepath}: {e}")
        return None

def generate_search_index(base_path):
    """Generate search index from all markdown and JSON files"""
    index = {
        'generated_at': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'total_documents': 0,
        'documents': []
    }
    
    # Directories to scan
    scan_configs = [
        {'dir': 'BrowserOS', 'ext': '.md'},
        {'dir': 'BrowserOS/Workflows', 'ext': '.json'},
        {'dir': 'docs', 'ext': '.md'},
        {'dir': 'library', 'ext': '.json', 'skip_schemas': True}, 
        {'dir': '.', 'ext': '.md', 'root_only': True}
    ]
    
    # Files to include at root
    root_files_allowlist = [
        'README.md',
        'AUTOMATION_QUICKSTART.md',
        'DEPLOYMENT.md',
        'REPO_TRACKING.md',
        'SECURITY_AUDIT.md',
        'TRANSFORMATION_SUMMARY.md'
    ]
    
    base = Path(base_path)
    
    for config in scan_configs:
        scan_dir = config['dir']
        file_ext = config['ext']
        
        dir_path = base / scan_dir
        if not dir_path.exists():
            continue
            
        print(f"Scanning {scan_dir} for {file_ext}...")
        
        # Iterate files
        if config.get('root_only'):
            files_to_scan = [dir_path / f for f in root_files_allowlist if (dir_path / f).exists()]
        else:
            files_to_scan = dir_path.rglob(f'*{file_ext}')
            
        for file_path in files_to_scan:
            # Skip excludes
            rel_path = file_path.relative_to(base)
            path_str = str(rel_path)
            
            if any(skip in path_str for skip in ['node_modules', 'vendor', '.git', 'raw', 'schemas']):
                continue
                
            # Process file based on extension
            metadata = None
            if file_ext == '.md':
                metadata = extract_markdown_content(file_path)
            elif file_ext == '.json':
                metadata = extract_json_content(file_path)
                
            if not metadata:
                continue
            
            # Determine category
            category = 'Documentation'
            if 'Workflows' in path_str and 'Community-Contributed' in path_str:
                category = 'Community Workflow'
            elif 'Workflows' in path_str:
                category = 'Core Workflow'
            elif 'library' in path_str:
                category = 'Library Template'
            elif 'USE_CASE_MATRIX' in path_str:
                category = 'Use Case'
            elif 'ADVANCED_TECHNIQUES' in path_str:
                category = 'Advanced Guide'
            elif 'KnowledgeBase' in path_str:
                category = 'Knowledge Base'
            
            # Create document entry
            doc = {
                'id': hashlib.md5(path_str.encode()).hexdigest()[:12],
                'title': metadata['title'],
                'description': metadata['description'],
                'category': category,
                'path': path_str.replace('\\', '/'),
                'url': f"../{path_str.replace('\\', '/')}",
                'headings': metadata['headings'],
                'keywords': metadata['keywords'],
                'preview': metadata['content'],
                'word_count': metadata['word_count']
            }
            
            index['documents'].append(doc)
            
            if len(index['documents']) % 100 == 0:
                print(f"  Indexed {len(index['documents'])} documents...")
    
    index['total_documents'] = len(index['documents'])
    
    # Sort by category and title
    index['documents'].sort(key=lambda x: (x['category'], x['title']))
    
    return index

def main():
    """Generate and save search index"""
    base_path = Path(__file__).parent.parent
    
    print("="*60)
    print("Generating Comprehensive Search Index (MD + JSON)")
    print("="*60)
    
    index = generate_search_index(base_path)
    
    # Save to docs directory
    output_file = base_path / 'docs' / 'search-index.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Search index generated successfully!")
    print(f"   Total documents: {index['total_documents']}")
    print(f"   Output: {output_file}")
    print(f"   Size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
    
    # Print category breakdown
    categories = {}
    for doc in index['documents']:
        cat = doc['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 Category Breakdown:")
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count} documents")

if __name__ == '__main__':
    main()
