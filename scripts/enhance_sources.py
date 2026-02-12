"""
Enhance sources.json with Content Integrity Hashing

This script adds sha256 content hashing to the sources manifest to enable
delta detection and prevent unnecessary reprocessing of unchanged sources.
"""

import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import os

# Configuration
REPO_ROOT = Path(__file__).parent.parent
SOURCES_PATH = REPO_ROOT / "BrowserOS" / "Research" / "sources.json"
RAW_DIR = REPO_ROOT / "BrowserOS" / "Research" / "raw"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


class SourceIntegrityManager:
    """Manage source integrity hashing and delta detection"""
    
    def __init__(self):
        self.sources_path = SOURCES_PATH
        self.raw_dir = RAW_DIR
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
    
    def load_sources(self) -> List[Dict[str, Any]]:
        """Load sources manifest"""
        if not self.sources_path.exists():
            return []
        return json.loads(self.sources_path.read_text())
    
    def save_sources(self, sources: List[Dict[str, Any]]) -> None:
        """Save updated sources manifest"""
        self.sources_path.write_text(json.dumps(sources, indent=2))
    
    def fetch_content(self, url: str) -> str:
        """Fetch content from URL"""
        try:
            headers = {
                'User-Agent': 'BrowserOS-KB-Bot/1.0',
                'Accept': 'text/html,application/xhtml+xml,application/json'
            }
            
            # Properly validate GitHub URLs before adding authentication
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            if GITHUB_TOKEN and parsed_url.netloc == 'github.com':
                headers['Authorization'] = f'token {GITHUB_TOKEN}'
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  ⚠️ Could not fetch {url}: {e}")
            return ""
    
    def compute_content_hash(self, content: str) -> str:
        """Compute SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get_cached_hash(self, url: str) -> str:
        """Get cached content hash from raw archive"""
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        archive_path = self.raw_dir / f"{url_hash}.html"
        
        if archive_path.exists():
            content = archive_path.read_text(encoding='utf-8', errors='ignore')
            return self.compute_content_hash(content)
        return ""
    
    def detect_changes(self, source: Dict[str, Any], fresh_hash: str) -> bool:
        """Detect if source has changed since last processing"""
        last_hash = source.get('last_processed_hash', '')
        
        if not last_hash:
            return True  # First time processing
        
        return fresh_hash != last_hash
    
    def enhance_source(self, source: Dict[str, Any], update_content: bool = False) -> Dict[str, Any]:
        """Enhance source with integrity information"""
        url = source['url']
        
        # Try to get hash from cache first
        cached_hash = self.get_cached_hash(url)
        
        if cached_hash:
            content_hash = cached_hash
            source['last_processed_hash'] = content_hash
            source['hash_updated_at'] = datetime.now().isoformat()
            print(f"  ✓ {url[:60]}... (cached)")
        elif update_content:
            # Fetch fresh content
            content = self.fetch_content(url)
            if content:
                content_hash = self.compute_content_hash(content)
                
                # Archive content
                url_hash = hashlib.sha256(url.encode()).hexdigest()
                archive_path = self.raw_dir / f"{url_hash}.html"
                archive_path.write_text(content, encoding='utf-8')
                
                # Detect changes
                has_changed = self.detect_changes(source, content_hash)
                
                source['last_processed_hash'] = content_hash
                source['hash_updated_at'] = datetime.now().isoformat()
                source['content_changed'] = has_changed
                
                print(f"  ✓ {url[:60]}... ({'changed' if has_changed else 'unchanged'})")
            else:
                print(f"  ⚠️ {url[:60]}... (fetch failed)")
        else:
            print(f"  • {url[:60]}... (skipped)")
        
        return source
    
    def add_provenance_tracking(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Add provenance metadata to source"""
        if 'provenance' not in source:
            source['provenance'] = {
                'first_indexed': source.get('accessed', datetime.now().isoformat()),
                'update_count': 0,
                'last_validation': None
            }
        
        # Increment update count if hash changed
        if source.get('content_changed', False):
            source['provenance']['update_count'] += 1
            source['provenance']['last_validation'] = datetime.now().isoformat()
        
        return source
    
    def generate_delta_report(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate report of source changes"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_sources': len(sources),
            'changed_sources': 0,
            'unchanged_sources': 0,
            'new_sources': 0,
            'failed_sources': 0,
            'changes': []
        }
        
        for source in sources:
            if not source.get('last_processed_hash'):
                report['new_sources'] += 1
            elif source.get('content_changed', False):
                report['changed_sources'] += 1
                report['changes'].append({
                    'url': source['url'],
                    'type': source.get('type', 'unknown'),
                    'hash': source['last_processed_hash'][:16] + '...'
                })
            else:
                report['unchanged_sources'] += 1
        
        return report
    
    def run(self, update_content: bool = False):
        """Execute source enhancement"""
        print("=" * 60)
        print("🔐 Enhancing Sources with Content Integrity Hashing")
        print("=" * 60)
        
        # Load sources
        print("\n📚 Loading sources manifest...")
        sources = self.load_sources()
        print(f"  ✓ Loaded {len(sources)} sources")
        
        # Enhance each source
        print("\n🔍 Processing sources...")
        enhanced_sources = []
        for source in sources:
            enhanced = self.enhance_source(source, update_content)
            enhanced = self.add_provenance_tracking(enhanced)
            enhanced_sources.append(enhanced)
        
        # Generate delta report
        print("\n📊 Generating delta report...")
        report = self.generate_delta_report(enhanced_sources)
        
        # Save enhanced sources
        print("\n💾 Saving enhanced sources...")
        self.save_sources(enhanced_sources)
        
        # Save delta report
        report_path = self.sources_path.parent / "source_delta_report.json"
        report_path.write_text(json.dumps(report, indent=2))
        
        print("\n" + "=" * 60)
        print("✅ Source enhancement complete!")
        print(f"  • Total sources: {report['total_sources']}")
        print(f"  • Changed: {report['changed_sources']}")
        print(f"  • Unchanged: {report['unchanged_sources']}")
        print(f"  • New: {report['new_sources']}")
        print("=" * 60)


def main():
    """Main entry point"""
    import sys
    
    # Check for --update flag to fetch fresh content
    update_content = '--update' in sys.argv
    
    manager = SourceIntegrityManager()
    manager.run(update_content=update_content)


if __name__ == "__main__":
    main()
