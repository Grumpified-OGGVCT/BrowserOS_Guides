"""
BrowserOS Workflows Knowledge Base - AI-Powered Research Pipeline

This script uses Ollama and OpenRouter APIs to automatically research and compile
information about BrowserOS Workflows from various sources.

Now includes direct GitHub repository tracking for intelligent incremental updates.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from datetime import datetime
from utils.resilience import (
    ResilientLogger, retry_with_backoff, validate_api_key,
    resilient_request, validate_url, safe_file_write, safe_file_read
)

# Force UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

from pathlib import Path
from typing import List, Dict, Any
import hashlib

# Initialize logger
logger = ResilientLogger(__name__)

# Add repo tracker
try:
    from repo_tracker import GitHubRepoTracker
    TRACKER_AVAILABLE = True
except ImportError:
    TRACKER_AVAILABLE = False
    logger.warn("repo_tracker not available")

# Load configuration via config_loader (with env var fallback)
try:
    from config_loader import get_config
    _cfg = get_config()
    _ollama_cfg = _cfg.ollama.http if _cfg.ollama else {}
    _openrouter_cfg = _cfg.openrouter.http if _cfg.openrouter else {}
except Exception as e:
    logger.error(f"Failed to load config from config_loader: {e}")
    logger.info("Falling back to environment variables")
    _ollama_cfg = {}
    _openrouter_cfg = {}

# Configuration
REPO_ROOT = Path(__file__).parent.parent
KB_PATH = REPO_ROOT / "BrowserOS" / "Research" / "BrowserOS_Workflows_KnowledgeBase.md"
SOURCES_PATH = REPO_ROOT / "BrowserOS" / "Research" / "sources.json"
RAW_DIR = REPO_ROOT / "BrowserOS" / "Research" / "raw"
BROWSEROS_REPO = RAW_DIR / "browseros-ai-BrowserOS"
REPO_STATE_PATH = REPO_ROOT / "BrowserOS" / "Research" / "repo_state.json"

# API Configuration (config_loader values take precedence, env vars as fallback)
OLLAMA_API_KEY = _ollama_cfg.get("api_key") or os.getenv("OLLAMA_API_KEY")
OPENROUTER_API_KEY = _openrouter_cfg.get("api_key") or os.getenv("OPENROUTER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FORCE_UPDATE = os.getenv("FORCE_UPDATE", "false").lower() == "true"

# Validate API keys (allow placeholders since they're optional)
try:
    if OLLAMA_API_KEY:
        validate_api_key(OLLAMA_API_KEY, "OLLAMA_API_KEY", allow_placeholder=True)
except ValueError as e:
    logger.warn(f"OLLAMA_API_KEY validation warning: {e}")

try:
    if OPENROUTER_API_KEY:
        validate_api_key(OPENROUTER_API_KEY, "OPENROUTER_API_KEY", allow_placeholder=True)
except ValueError as e:
    logger.warn(f"OPENROUTER_API_KEY validation warning: {e}")


class AIResearcher:
    """AI-powered research assistant using Ollama and OpenRouter"""
    
    def __init__(self):
        # Use local Ollama instance by default
        self.ollama_url = "http://localhost:11434/v1/chat/completions"
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        logger.info(f"OpenRouter URL: {self.openrouter_url}")
        self.session = requests.Session()
    
    @retry_with_backoff(max_attempts=3, base_delay=2.0)
    def query_ollama(self, prompt: str, model: str = "llama3") -> str:
        """Query Ollama API for research"""
        # For local Ollama, we don't strictly need a key, even if env var has a placeholder
        
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            # valid key check
            if OLLAMA_API_KEY and "your-ollama-api-key" not in OLLAMA_API_KEY:
                 headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
            
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
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                raise ValueError("Empty response from Ollama API")
            return content
        
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    @retry_with_backoff(max_attempts=3, base_delay=2.0)
    def query_openrouter(self, prompt: str, model: str = "x-ai/grok-4.1-fast") -> str:
        """Query OpenRouter API for enhanced research"""
        if not OPENROUTER_API_KEY or "your-openrouter-api-key" in OPENROUTER_API_KEY:
            logger.warn("OpenRouter API key not configured, skipping...")
            raise ValueError("OpenRouter API key not configured")
        
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
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                raise ValueError("Empty response from OpenRouter API")
            return content
        
        except Exception as e:
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"OpenRouter API error: {e}")
                logger.error(f"Response body: {e.response.text}")
            else:
                logger.error(f"OpenRouter API error: {e}")
            raise


class SourceArchiver:
    """Archive web sources for KB research"""
    
    def __init__(self):
        self.raw_dir = RAW_DIR
        self.raw_dir.mkdir(parents=True, exist_ok=True)
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def fetch_and_archive(self, url: str) -> str:
        """Fetch URL content and archive it"""
        try:
            # Validate URL before fetching
            if not validate_url(url):
                logger.warn(f"Invalid URL format: {url}")
                raise ValueError(f"Invalid URL format: {url}")
            
            # Create hash for filename
            url_hash = hashlib.sha256(url.encode()).hexdigest()
            archive_path = self.raw_dir / f"{url_hash}.html"
            
            # Skip if recently archived (within 7 days)
            if archive_path.exists():
                age_days = (datetime.now().timestamp() - archive_path.stat().st_mtime) / 86400
                if age_days < 7 and not FORCE_UPDATE:
                    logger.info(f"Using cached: {url}")
                    return safe_file_read(archive_path)
            
            # Fetch fresh content
            logger.info(f"Fetching: {url}")
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
            safe_file_write(archive_path, content)
            logger.info(f"Archived: {url}")
            
            return content
        
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise


class KBResearcher:
    """Main KB research coordinator with GitHub tracking"""
    
    def __init__(self):
        self.ai = AIResearcher()
        self.archiver = SourceArchiver()
        self.sources = self.load_sources()
        
        # Initialize GitHub repo tracker
        self.repo_tracker = None
        if TRACKER_AVAILABLE:
            try:
                self.repo_tracker = GitHubRepoTracker(
                    repo_name="browseros-ai/BrowserOS",
                    state_file=REPO_STATE_PATH
                )
                logger.info("GitHub repository tracker initialized")
            except Exception as e:
                logger.warn(f"Could not initialize repo tracker: {e}")
    
    def load_sources(self) -> List[Dict[str, Any]]:
        """Load source manifest"""
        if not SOURCES_PATH.exists():
            return []
        try:
            content = safe_file_read(SOURCES_PATH)
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load sources from {SOURCES_PATH}: {e}")
            return []
    
    def save_sources(self):
        """Save updated source manifest"""
        try:
            safe_file_write(SOURCES_PATH, json.dumps(self.sources, indent=2))
        except Exception as e:
            logger.error(f"Failed to save sources to {SOURCES_PATH}: {e}")
            raise
    
    def research_from_repo(self) -> Dict[str, str]:
        """Extract information from cloned BrowserOS repository"""
        findings = {}
        
        if not BROWSEROS_REPO.exists():
            logger.warn("BrowserOS repository not found")
            return findings
        
        logger.info("Analyzing BrowserOS repository...")
        
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
                try:
                    logger.info(f"Reading {file_path}")
                    content = safe_file_read(full_path)
                    findings[file_path] = content[:10000]  # Limit size
                except Exception as e:
                    logger.error(f"Failed to read {file_path}: {e}")
        
        return findings
    
    def research_from_web(self) -> Dict[str, str]:
        """Fetch and analyze web sources"""
        findings = {}
        
        for source in self.sources[:6]:  # Limit to avoid rate limits
            url = source['url']
            try:
                content = self.archiver.fetch_and_archive(url)
                if content:
                    # Extract key information (simplified extraction)
                    findings[url] = content[:5000]
                    
                    # Update access timestamp
                    source['accessed'] = datetime.now().isoformat()
            except Exception as e:
                logger.warn(f"Skipping source {url} due to error: {e}")
                continue
        
        self.save_sources()
        return findings
    
    def get_github_updates(self) -> Dict[str, Any]:
        """Get updates directly from GitHub (commits, releases)"""
        if not self.repo_tracker:
            logger.warn("GitHub tracker not available, skipping direct repo updates")
            return {}
        
        logger.info("Checking GitHub repository for updates...")
        
        # Check if this is first run
        if not self.repo_tracker.state.last_commit_sha:
            logger.info("First run detected - initializing repository database...")
            return self.repo_tracker.initialize_from_scratch()
        else:
            logger.info("Getting incremental updates since last run...")
            return self.repo_tracker.get_incremental_updates()
    
    def synthesize_kb_updates(self, repo_findings: Dict, web_findings: Dict, github_updates: Dict = None) -> str:
        """Use AI to synthesize findings into KB updates"""
        logger.info("Synthesizing knowledge base updates with AI...")
        
        # Create research summary
        summary = "# Research Findings Summary\n\n"
        summary += f"## Repository Analysis ({len(repo_findings)} files)\n"
        for file, content in repo_findings.items():
            summary += f"\n### {file}\n{content[:1000]}...\n"
        
        # Add GitHub updates if available
        if github_updates and github_updates.get('has_updates'):
            summary += f"\n## GitHub Repository Updates\n"
            
            if github_updates.get('new_commits'):
                summary += f"\n### New Commits ({len(github_updates['new_commits'])})\n"
                for commit in github_updates['new_commits'][:10]:  # Limit to 10
                    summary += f"- {commit['message'].split(chr(10))[0]} ({commit['sha'][:7]})\n"
                
                # Add commit analysis
                if github_updates.get('commit_analysis'):
                    summary += "\n### Changes by Category:\n"
                    for category, items in github_updates['commit_analysis'].items():
                        if items:
                            summary += f"- {category.title()}: {len(items)} commits\n"
            
            if github_updates.get('new_releases'):
                summary += f"\n### New Releases ({len(github_updates['new_releases'])})\n"
                for release in github_updates['new_releases']:
                    summary += f"- {release['name']} ({release['tag']}) - {release['published_at']}\n"
                    if release['body']:
                        summary += f"  {release['body'][:300]}...\n"
        
        summary += f"\n## Web Sources ({len(web_findings)} sources)\n"
        for url in list(web_findings.keys())[:3]:
            summary += f"\n### {url}\n{web_findings[url][:500]}...\n"
        
        # Use AI to generate insights
        prompt = f"""Analyze these research findings about BrowserOS Workflows and identify:
1. New features or capabilities discovered
2. Updates to existing documentation
3. Important changes or deprecations (from commits and releases)
4. Security considerations
5. Best practices and patterns

Research Summary:
{summary[:12000]}

Provide a concise summary of key findings that should update the knowledge base."""
        
        # Try OpenRouter first (more capable), fallback to Ollama
        insights = None
        try:
            insights = self.ai.query_openrouter(prompt)
            logger.info("AI synthesis complete (OpenRouter)")
        except Exception as e:
            logger.warn(f"OpenRouter synthesis failed: {e}, trying Ollama...")
            try:
                insights = self.ai.query_ollama(prompt)
                logger.info("AI synthesis complete (Ollama)")
            except Exception as e2:
                logger.error(f"Ollama synthesis also failed: {e2}")
        
        if insights:
            return insights
        else:
            logger.warn("AI synthesis unavailable, manual review needed")
            return None
    
    def update_kb(self, insights: str) -> bool:
        """Update knowledge base with new insights"""
        if not KB_PATH.exists():
            logger.error("Knowledge base file not found")
            return False
        
        logger.info("Updating knowledge base...")
        
        # Read current KB
        try:
            kb_content = safe_file_read(KB_PATH)
        except Exception as e:
            logger.error(f"Failed to read knowledge base: {e}")
            return False
        
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
            logger.info("KB already updated today, skipping...")
            return False
        
        # Insert before license section
        if "## License" in kb_content:
            kb_content = kb_content.replace("## License", f"{update_section}\n## License")
        else:
            kb_content += update_section
        
        # Write updated KB
        try:
            safe_file_write(KB_PATH, kb_content)
            logger.info("Knowledge base updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to write knowledge base: {e}")
            return False
    
    def run(self):
        """Execute full research pipeline with GitHub tracking"""
        logger.info("=" * 60)
        logger.info("Starting AI-Powered KB Research Pipeline with GitHub Tracking")
        logger.info("=" * 60)
        
        # Step 1: Get GitHub updates (commits, releases)
        github_updates = self.get_github_updates()
        
        # Check if we have meaningful updates
        has_github_updates = github_updates and github_updates.get('has_updates', False)
        
        if has_github_updates:
            logger.info("GitHub updates detected:")
            if github_updates.get('new_commits'):
                logger.info(f"  - {len(github_updates['new_commits'])} new commits")
            if github_updates.get('new_releases'):
                logger.info(f"  - {len(github_updates['new_releases'])} new releases")
        elif github_updates and github_updates.get('initialized'):
            logger.info("Repository database initialized")
        else:
            logger.info("No new GitHub updates since last run")
        
        # Step 2: Research from cloned repository
        repo_findings = self.research_from_repo()
        
        # Step 3: Research from web sources  
        web_findings = self.research_from_web()
        
        # Step 4: Synthesize with AI (including GitHub updates)
        insights = self.synthesize_kb_updates(repo_findings, web_findings, github_updates)
        
        # Step 5: Update KB if we have insights
        if insights:
            updated = self.update_kb(insights)
            if updated:
                logger.info("Pipeline completed successfully")
                
                # Print summary
                if self.repo_tracker:
                    logger.info(self.repo_tracker.get_summary())
                
                return 0
            else:
                logger.info("No updates needed")
                return 0
        else:
            logger.warn("Pipeline completed with warnings - AI synthesis unavailable")
            return 1


def main():
    """Main entry point"""
    researcher = KBResearcher()
    return researcher.run()


if __name__ == "__main__":
    sys.exit(main())
