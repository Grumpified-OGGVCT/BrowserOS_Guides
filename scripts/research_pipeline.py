"""
BrowserOS Workflows Knowledge Base - AI-Powered Research Pipeline

This script uses Ollama and OpenRouter APIs to automatically research and compile
information about BrowserOS Workflows from various sources.
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import hashlib

# Configuration
REPO_ROOT = Path(__file__).parent.parent
KB_PATH = REPO_ROOT / "BrowserOS" / "Research" / "BrowserOS_Workflows_KnowledgeBase.md"
SOURCES_PATH = REPO_ROOT / "BrowserOS" / "Research" / "sources.json"
RAW_DIR = REPO_ROOT / "BrowserOS" / "Research" / "raw"
BROWSEROS_REPO = RAW_DIR / "browseros-ai-BrowserOS"

# API Configuration
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FORCE_UPDATE = os.getenv("FORCE_UPDATE", "false").lower() == "true"


class AIResearcher:
    """AI-powered research assistant using Ollama and OpenRouter"""
    
    def __init__(self):
        self.ollama_url = "https://api.ollama.ai/v1/chat/completions"
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.session = requests.Session()
    
    def query_ollama(self, prompt: str, model: str = "llama2") -> str:
        """Query Ollama API for research"""
        if not OLLAMA_API_KEY:
            print("⚠️ Ollama API key not configured, skipping...")
            return ""
        
        try:
            headers = {
                "Authorization": f"Bearer {OLLAMA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = self.session.post(
                self.ollama_url, 
                headers=headers, 
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        except Exception as e:
            print(f"❌ Ollama API error: {e}")
            return ""
    
    def query_openrouter(self, prompt: str, model: str = "anthropic/claude-3-sonnet") -> str:
        """Query OpenRouter API for enhanced research"""
        if not OPENROUTER_API_KEY:
            print("⚠️ OpenRouter API key not configured, skipping...")
            return ""
        
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Grumpified-OGGVCT/BrowserOS_Guides",
                "X-Title": "BrowserOS KB Research"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            response = self.session.post(
                self.openrouter_url,
                headers=headers,
                json=data,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        except Exception as e:
            print(f"❌ OpenRouter API error: {e}")
            return ""


class SourceArchiver:
    """Archive web sources for KB research"""
    
    def __init__(self):
        self.raw_dir = RAW_DIR
        self.raw_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_and_archive(self, url: str) -> str:
        """Fetch URL content and archive it"""
        try:
            # Create hash for filename
            url_hash = hashlib.sha256(url.encode()).hexdigest()
            archive_path = self.raw_dir / f"{url_hash}.html"
            
            # Skip if recently archived (within 7 days)
            if archive_path.exists():
                age_days = (datetime.now().timestamp() - archive_path.stat().st_mtime) / 86400
                if age_days < 7 and not FORCE_UPDATE:
                    print(f"✓ Using cached: {url}")
                    return archive_path.read_text(encoding='utf-8', errors='ignore')
            
            # Fetch fresh content
            print(f"📥 Fetching: {url}")
            headers = {
                'User-Agent': 'BrowserOS-KB-Bot/1.0',
                'Accept': 'text/html,application/xhtml+xml'
            }
            
            if GITHUB_TOKEN and 'github.com' in url:
                headers['Authorization'] = f'token {GITHUB_TOKEN}'
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Archive content
            content = response.text
            archive_path.write_text(content, encoding='utf-8')
            print(f"✅ Archived: {url}")
            
            return content
        
        except Exception as e:
            print(f"❌ Failed to fetch {url}: {e}")
            return ""


class KBResearcher:
    """Main KB research coordinator"""
    
    def __init__(self):
        self.ai = AIResearcher()
        self.archiver = SourceArchiver()
        self.sources = self.load_sources()
    
    def load_sources(self) -> List[Dict[str, Any]]:
        """Load source manifest"""
        if not SOURCES_PATH.exists():
            return []
        return json.loads(SOURCES_PATH.read_text())
    
    def save_sources(self):
        """Save updated source manifest"""
        SOURCES_PATH.write_text(json.dumps(self.sources, indent=2))
    
    def research_from_repo(self) -> Dict[str, str]:
        """Extract information from cloned BrowserOS repository"""
        findings = {}
        
        if not BROWSEROS_REPO.exists():
            print("⚠️ BrowserOS repository not found")
            return findings
        
        print("📚 Analyzing BrowserOS repository...")
        
        # Key files to analyze
        key_files = [
            "README.md",
            "docs/workflows.md",
            "docs/README.md",
            "CHANGELOG.md"
        ]
        
        for file_path in key_files:
            full_path = BROWSEROS_REPO / file_path
            if full_path.exists():
                print(f"  📄 Reading {file_path}")
                content = full_path.read_text(encoding='utf-8', errors='ignore')
                findings[file_path] = content[:10000]  # Limit size
        
        return findings
    
    def research_from_web(self) -> Dict[str, str]:
        """Fetch and analyze web sources"""
        findings = {}
        
        for source in self.sources[:6]:  # Limit to avoid rate limits
            url = source['url']
            content = self.archiver.fetch_and_archive(url)
            if content:
                # Extract key information (simplified extraction)
                findings[url] = content[:5000]
                
                # Update access timestamp
                source['accessed'] = datetime.now().isoformat()
        
        self.save_sources()
        return findings
    
    def synthesize_kb_updates(self, repo_findings: Dict, web_findings: Dict) -> str:
        """Use AI to synthesize findings into KB updates"""
        print("\n🤖 Synthesizing knowledge base updates with AI...")
        
        # Create research summary
        summary = "# Research Findings Summary\n\n"
        summary += f"## Repository Analysis ({len(repo_findings)} files)\n"
        for file, content in repo_findings.items():
            summary += f"\n### {file}\n{content[:1000]}...\n"
        
        summary += f"\n## Web Sources ({len(web_findings)} sources)\n"
        for url in list(web_findings.keys())[:3]:
            summary += f"\n### {url}\n{web_findings[url][:500]}...\n"
        
        # Use AI to generate insights
        prompt = f"""Analyze these research findings about BrowserOS Workflows and identify:
1. New features or capabilities discovered
2. Updates to existing documentation
3. Important changes or deprecations
4. Security considerations
5. Best practices and patterns

Research Summary:
{summary[:8000]}

Provide a concise summary of key findings that should update the knowledge base."""
        
        # Try OpenRouter first (more capable), fallback to Ollama
        insights = self.ai.query_openrouter(prompt)
        if not insights:
            insights = self.ai.query_ollama(prompt)
        
        if insights:
            print("✅ AI synthesis complete")
            return insights
        else:
            print("⚠️ AI synthesis unavailable, using direct findings")
            return "Manual review needed - AI analysis unavailable"
    
    def update_kb(self, insights: str) -> bool:
        """Update knowledge base with new insights"""
        if not KB_PATH.exists():
            print("❌ Knowledge base file not found")
            return False
        
        print("\n📝 Updating knowledge base...")
        
        # Read current KB
        kb_content = KB_PATH.read_text()
        
        # Add update section (append to end before license section)
        update_section = f"""

---

## Latest Updates (Auto-generated {datetime.now().strftime('%Y-%m-%d')})

{insights}

**Note**: This section was automatically generated by the AI-powered research pipeline.
For the most current information, always refer to the official sources listed in the knowledge base.

"""
        
        # Check if we need to update (avoid duplicate updates)
        today = datetime.now().strftime('%Y-%m-%d')
        if f"Auto-generated {today}" in kb_content and not FORCE_UPDATE:
            print("ℹ️ KB already updated today, skipping...")
            return False
        
        # Insert before license section
        if "## License" in kb_content:
            kb_content = kb_content.replace("## License", f"{update_section}\n## License")
        else:
            kb_content += update_section
        
        # Write updated KB
        KB_PATH.write_text(kb_content)
        print("✅ Knowledge base updated")
        return True
    
    def run(self):
        """Execute full research pipeline"""
        print("=" * 60)
        print("🚀 Starting AI-Powered KB Research Pipeline")
        print("=" * 60)
        
        # Step 1: Research from cloned repository
        repo_findings = self.research_from_repo()
        
        # Step 2: Research from web sources
        web_findings = self.research_from_web()
        
        # Step 3: Synthesize with AI
        insights = self.synthesize_kb_updates(repo_findings, web_findings)
        
        # Step 4: Update KB
        if insights and insights != "Manual review needed - AI analysis unavailable":
            updated = self.update_kb(insights)
            if updated:
                print("\n✅ Pipeline completed successfully")
                return 0
            else:
                print("\nℹ️ No updates needed")
                return 0
        else:
            print("\n⚠️ Pipeline completed with warnings")
            return 1


def main():
    """Main entry point"""
    researcher = KBResearcher()
    return researcher.run()


if __name__ == "__main__":
    sys.exit(main())
