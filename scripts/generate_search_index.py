#!/usr/bin/env python3
"""
Search Index Generator for BrowserOS Knowledge Hub
Scans all markdown files and creates a searchable index with semantic content
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
            if word not in ['that', 'this', 'with', 'from', 'have', 'will', 'been', 'were']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords = [k[0] for k in keywords]
        
        return {
            'title': title,
            'description': description,
            'headings': headings[:10],  # First 10 headings
            'keywords': keywords,
            'content': clean_content[:500],  # First 500 chars for preview
            'word_count': len(words)
        }
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def generate_search_index(base_path):
    """Generate search index from all markdown files"""
    index = {
        'generated_at': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'total_documents': 0,
        'documents': []
    }
    
    # Directories to scan
    scan_dirs = [
        'BrowserOS',
        'docs',
        '.'
    ]
    
    # Files to include at root
    root_files = [
        'README.md',
        'AUTOMATION_QUICKSTART.md',
        'DEPLOYMENT.md',
        'REPO_TRACKING.md',
        'SECURITY_AUDIT.md',
        'TRANSFORMATION_SUMMARY.md'
    ]
    
    base = Path(base_path)
    
    for scan_dir in scan_dirs:
        dir_path = base / scan_dir
        if not dir_path.exists():
            continue
        
        # Find all markdown files
        for md_file in dir_path.rglob('*.md'):
            # Skip certain directories
            rel_path = md_file.relative_to(base)
            if any(skip in str(rel_path) for skip in ['node_modules', 'vendor', '.git', 'raw']):
                continue
            
            print(f"Indexing: {rel_path}")
            
            metadata = extract_markdown_content(md_file)
            if not metadata:
                continue
            
            # Determine category
            category = 'Documentation'
            if 'Workflows' in str(rel_path):
                category = 'Workflow'
            elif 'USE_CASE_MATRIX' in str(rel_path):
                category = 'Use Case'
            elif 'ADVANCED_TECHNIQUES' in str(rel_path):
                category = 'Advanced Guide'
            elif 'KnowledgeBase' in str(rel_path):
                category = 'Knowledge Base'
            
            # Create document entry
            doc = {
                'id': hashlib.md5(str(rel_path).encode()).hexdigest()[:12],
                'title': metadata['title'],
                'description': metadata['description'],
                'category': category,
                'path': str(rel_path).replace('\\', '/'),
                'url': f"../{str(rel_path).replace('\\', '/')}",
                'headings': metadata['headings'],
                'keywords': metadata['keywords'],
                'preview': metadata['content'],
                'word_count': metadata['word_count']
            }
            
            index['documents'].append(doc)
    
    index['total_documents'] = len(index['documents'])
    
    # Sort by category and title
    index['documents'].sort(key=lambda x: (x['category'], x['title']))
    
    return index

def main():
    """Generate and save search index"""
    base_path = Path(__file__).parent.parent
    
    print("="*60)
    print("Generating Search Index for BrowserOS Knowledge Hub")
    print("="*60)
    
    index = generate_search_index(base_path)
    
    # Save to docs directory
    output_file = base_path / 'docs' / 'search-index.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Search index generated successfully!")
    print(f"   Total documents: {index['total_documents']}")
    print(f"   Output: {output_file}")
    print(f"   Size: {os.path.getsize(output_file) / 1024:.2f} KB")
    
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
