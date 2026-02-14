#!/usr/bin/env python3
"""
Predict Upcoming BrowserOS Features
Analyzes commits between releases to predict what's coming next
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import resilience utilities for hardened automation
sys.path.insert(0, str(Path(__file__).parent))
from utils.resilience import (
    ResilientLogger, retry_with_backoff, resilient_request, safe_file_write
)

load_dotenv()

REPO_ROOT = Path(__file__).parent.parent
PREDICTIONS_PATH = REPO_ROOT / "BrowserOS" / "Research" / "upcoming_features.json"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class FeaturePredictor:
    """Analyzes commits to predict upcoming features"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.predictions = []
        self.logger = ResilientLogger(__name__)
        
    def log(self, message: str):
        if self.verbose:
            self.logger.info(message)
    
    @retry_with_backoff(max_attempts=3, base_delay=2.0)
    def get_latest_release(self, owner: str, repo: str) -> Optional[Dict]:
        """Get the latest release from GitHub"""
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        headers = {}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
        response = resilient_request(url, headers=headers, timeout=10, logger=self.logger)
        if response and response.status_code == 200:
            return response.json()
        elif response and response.status_code == 404:
            self.log(f"No releases found for {owner}/{repo}")
            return None
        else:
            self.log(f"Error fetching releases: {response.status_code if response else 'No response'}")
            return None
    
    @retry_with_backoff(max_attempts=3, base_delay=2.0)
    def get_commits_since_release(self, owner: str, repo: str, release_tag: Optional[str] = None) -> List[Dict]:
        """Get commits since the latest release using GitHub compare API"""
        headers = {}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"

        # If we have a release tag, use the compare API to get commits between
        # that tag and the main branch.
        if release_tag:
            compare_url = f"https://api.github.com/repos/{owner}/{repo}/compare/{release_tag}...main"
            response = resilient_request(compare_url, headers=headers, timeout=10, logger=self.logger)
            if response and response.status_code == 200:
                compare_data = response.json()
                commits = compare_data.get("commits", [])
                self.log(f"Found {len(commits)} commits since {release_tag}")
                return commits
            else:
                self.log(f"Error fetching compare data: {response.status_code if response else 'No response'}")
                return []

        # If no release tag is provided, fall back to returning recent commits
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"per_page": 100}
        response = resilient_request(url, headers=headers, params=params, timeout=10, logger=self.logger)
        if response and response.status_code == 200:
            all_commits = response.json()
            return all_commits[:30]  # Return last 30 commits if no release
        else:
            self.log(f"Error fetching commits: {response.status_code if response else 'No response'}")
            return []
    
    def analyze_commit_patterns(self, commits: List[Dict]) -> Dict[str, Any]:
        """Analyze commit messages for patterns"""
        patterns = {
            "new_features": [],
            "bug_fixes": [],
            "performance": [],
            "ui_changes": [],
            "api_changes": [],
            "documentation": [],
            "other": []
        }
        
        feature_keywords = ["feat", "feature", "add", "new", "implement"]
        fix_keywords = ["fix", "bug", "patch", "resolve"]
        perf_keywords = ["perf", "performance", "optimize", "speed"]
        ui_keywords = ["ui", "ux", "design", "style", "interface"]
        api_keywords = ["api", "endpoint", "route", "breaking"]
        doc_keywords = ["docs", "documentation", "readme"]
        
        for commit in commits:
            msg = commit["commit"]["message"].lower()
            
            if any(kw in msg for kw in feature_keywords):
                patterns["new_features"].append(commit)
            elif any(kw in msg for kw in fix_keywords):
                patterns["bug_fixes"].append(commit)
            elif any(kw in msg for kw in perf_keywords):
                patterns["performance"].append(commit)
            elif any(kw in msg for kw in ui_keywords):
                patterns["ui_changes"].append(commit)
            elif any(kw in msg for kw in api_keywords):
                patterns["api_changes"].append(commit)
            elif any(kw in msg for kw in doc_keywords):
                patterns["documentation"].append(commit)
            else:
                patterns["other"].append(commit)
        
        return patterns
    
    def predict_with_ai(self, commits: List[Dict], patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use AI to predict upcoming features based on commits"""
        
        # Build context from commits
        commit_summary = []
        for commit in commits[:20]:  # Top 20 commits
            msg = commit["commit"]["message"].split("\n")[0]  # First line only
            author = commit["commit"]["author"]["name"]
            date = commit["commit"]["author"]["date"]
            commit_summary.append(f"- {msg} (by {author}, {date[:10]})")
        
        context = "\n".join(commit_summary)
        
        prompt = f"""Analyze these recent commits from the BrowserOS repository to predict upcoming features:

{context}

Based on these commits, predict 3-5 upcoming features that are likely to be released soon.

For each prediction:
1. Feature name (short, catchy)
2. Confidence level (high/medium/low)
3. Description (1-2 sentences)
4. Evidence (which commits suggest this)

Respond in JSON format:
[
  {{
    "name": "Feature name",
    "confidence": "high",
    "description": "What this feature does",
    "evidence": "Commits mention X, Y, Z",
    "category": "new_feature|improvement|ui_enhancement|performance"
  }}
]
"""
        
        # Try OpenRouter first, fallback to Ollama
        predictions = self._query_ai(prompt)
        
        if not predictions:
            # Return basic predictions from pattern analysis
            return self._basic_predictions(patterns)
        
        return predictions
    
    @retry_with_backoff(max_attempts=2, base_delay=1.0)
    def _query_ai(self, prompt: str) -> List[Dict[str, Any]]:
        """Query AI service for predictions"""
        
        # Try OpenRouter
        if OPENROUTER_API_KEY and OPENROUTER_API_KEY not in ["your-openrouter-api-key-here", "placeholder"]:
            try:
                response = resilient_request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    method="POST",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3.5-sonnet",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3
                    },
                    timeout=30,
                    logger=self.logger
                )
                
                if response and response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    # Extract JSON from response
                    import re
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
            except Exception as e:
                self.logger.error(f"OpenRouter error: {e}", exc_info=True)
        
        # Try Ollama if explicitly enabled
        if USE_OLLAMA:
            try:
                # Health check first
                health_url = f"{OLLAMA_BASE_URL}/api/tags"
                health_response = resilient_request(health_url, timeout=2, logger=self.logger)
                if not health_response or health_response.status_code != 200:
                    self.log("Ollama service not available, skipping")
                    return []
                
                response = resilient_request(
                    f"{OLLAMA_BASE_URL}/v1/chat/completions",
                    method="POST",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": "llama3",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3
                    },
                    timeout=30,
                    logger=self.logger
                )
                
                if response and response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    import re
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
            except Exception as e:
                self.logger.error(f"Ollama error: {e}", exc_info=True)
        
        return []
    
    def _basic_predictions(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate basic predictions from patterns without AI"""
        predictions = []
        
        if len(patterns["new_features"]) > 3:
            predictions.append({
                "name": "Major Feature Release",
                "confidence": "high",
                "description": f"Based on {len(patterns['new_features'])} feature commits, a significant update is likely coming.",
                "evidence": f"{len(patterns['new_features'])} feature-related commits detected",
                "category": "new_feature"
            })
        
        if len(patterns["ui_changes"]) > 2:
            predictions.append({
                "name": "UI/UX Improvements",
                "confidence": "medium",
                "description": "Interface enhancements and design updates are in progress.",
                "evidence": f"{len(patterns['ui_changes'])} UI-related commits",
                "category": "ui_enhancement"
            })
        
        if len(patterns["performance"]) > 1:
            predictions.append({
                "name": "Performance Optimizations",
                "confidence": "medium",
                "description": "Performance improvements and optimizations are being implemented.",
                "evidence": f"{len(patterns['performance'])} performance commits",
                "category": "performance"
            })
        
        return predictions
    
    def analyze_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze a repository for upcoming features"""
        self.log(f"Analyzing {owner}/{repo}...")
        
        # Get latest release
        release = self.get_latest_release(owner, repo)
        release_tag = release["tag_name"] if release else None
        release_date = release["published_at"] if release else None
        
        self.log(f"Latest release: {release_tag or 'None'}")
        
        # Get commits since release
        commits = self.get_commits_since_release(owner, repo, release_tag)
        self.log(f"Found {len(commits)} commits since release")
        
        if not commits:
            return None
        
        # Analyze patterns
        patterns = self.analyze_commit_patterns(commits)
        
        # Predict features
        predictions = self.predict_with_ai(commits, patterns)
        
        return {
            "repository": f"{owner}/{repo}",
            "latest_release": release_tag,
            "release_date": release_date,
            "commits_since_release": len(commits),
            "predictions": predictions,
            "commit_patterns": {
                "new_features": len(patterns["new_features"]),
                "bug_fixes": len(patterns["bug_fixes"]),
                "performance": len(patterns["performance"]),
                "ui_changes": len(patterns["ui_changes"]),
                "api_changes": len(patterns["api_changes"])
            },
            "analyzed_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def run(self):
        """Main execution"""
        repos_to_analyze = [
            ("browseros-ai", "BrowserOS"),
            ("browseros-ai", "BrowserOS-agent"),
            ("browseros-ai", "moltyflow")
        ]
        
        all_predictions = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "repositories": []
        }
        
        for owner, repo in repos_to_analyze:
            result = self.analyze_repository(owner, repo)
            if result:
                all_predictions["repositories"].append(result)
        
        # Save predictions
        PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        predictions_json = json.dumps(all_predictions, indent=2)
        success = safe_file_write(
            str(PREDICTIONS_PATH),
            predictions_json,
            create_dirs=True,
            logger=self.logger
        )
        
        if success:
            self.log(f"\n✓ Predictions saved to {PREDICTIONS_PATH}")
        else:
            self.logger.error(f"Failed to save predictions to {PREDICTIONS_PATH}")
        
        return len(all_predictions["repositories"])

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Predict upcoming BrowserOS features")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    try:
        predictor = FeaturePredictor(verbose=args.verbose)
        count = predictor.run()
        print(f"\n✓ Analyzed {count} repositories and generated predictions")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
