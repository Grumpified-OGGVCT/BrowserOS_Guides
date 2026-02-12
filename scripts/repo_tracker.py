"""
GitHub Repository State Tracker

Maintains database of commits, releases, and changes from official BrowserOS repo.
Enables incremental updates by tracking what's been processed.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    from github import Github, Repository, Commit, GitRelease
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("⚠️ PyGithub not installed. Install with: pip install PyGithub")


@dataclass
class RepoState:
    """Track repository processing state"""
    repo_name: str
    last_commit_sha: Optional[str] = None
    last_commit_date: Optional[str] = None
    last_release_tag: Optional[str] = None
    last_release_date: Optional[str] = None
    last_updated: Optional[str] = None
    total_commits_processed: int = 0
    total_releases_processed: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RepoState':
        return cls(**data)


class GitHubRepoTracker:
    """Track and analyze GitHub repository changes"""
    
    def __init__(self, repo_name: str = "browseros-ai/BrowserOS", 
                 state_file: Path = None):
        self.repo_name = repo_name
        self.state_file = state_file or Path("BrowserOS/Research/repo_state.json")
        self.state = self.load_state()
        
        # Initialize GitHub client
        self.github = None
        self.repo = None
        self._initialize_github()
    
    def _initialize_github(self):
        """Initialize GitHub API client"""
        if not GITHUB_AVAILABLE:
            print("⚠️ GitHub API not available - install PyGithub")
            return
        
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            print("⚠️ GITHUB_TOKEN not set - using public API (limited rate)")
            self.github = Github()
        else:
            self.github = Github(github_token)
        
        try:
            self.repo = self.github.get_repo(self.repo_name)
            print(f"✓ Connected to {self.repo_name}")
        except Exception as e:
            # Handle connection errors gracefully
            error_msg = str(e) if hasattr(e, '__str__') else type(e).__name__
            print(f"❌ Failed to connect to {self.repo_name}: {error_msg}")
            print("   This may be due to rate limiting or network issues.")
            print("   Set GITHUB_TOKEN environment variable for higher rate limits.")
            self.repo = None
    
    def load_state(self) -> RepoState:
        """Load repository state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                return RepoState.from_dict(data)
            except Exception as e:
                print(f"⚠️ Failed to load state: {e}")
        
        # Return new state
        return RepoState(repo_name=self.repo_name)
    
    def save_state(self):
        """Save repository state to file"""
        self.state.last_updated = datetime.now().isoformat()
        
        # Ensure directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.state_file, 'w') as f:
            json.dump(self.state.to_dict(), f, indent=2)
        
        print(f"✓ Saved repo state: {self.state_file}")
    
    def get_new_commits(self, max_count: int = 50) -> List[Dict[str, Any]]:
        """Get commits since last processed commit"""
        if not self.repo:
            return []
        
        print(f"\n📊 Fetching new commits from {self.repo_name}...")
        
        commits_data = []
        
        try:
            # Get commits since last processed
            if self.state.last_commit_sha:
                # Get commits since specific SHA
                all_commits = self.repo.get_commits()
                for commit in all_commits:
                    if commit.sha == self.state.last_commit_sha:
                        break
                    commits_data.append(self._extract_commit_info(commit))
                    if len(commits_data) >= max_count:
                        break
            else:
                # First run - get recent commits
                commits = self.repo.get_commits()[:max_count]
                for commit in commits:
                    commits_data.append(self._extract_commit_info(commit))
            
            print(f"✓ Found {len(commits_data)} new commits")
            
            # Update state with latest commit
            if commits_data:
                self.state.last_commit_sha = commits_data[0]['sha']
                self.state.last_commit_date = commits_data[0]['date']
                self.state.total_commits_processed += len(commits_data)
        
        except Exception as e:
            print(f"❌ Error fetching commits: {e}")
        
        return commits_data
    
    def _extract_commit_info(self, commit) -> Dict[str, Any]:
        """Extract relevant information from commit"""
        return {
            'sha': commit.sha,
            'date': commit.commit.author.date.isoformat(),
            'author': commit.commit.author.name,
            'message': commit.commit.message,
            'url': commit.html_url,
            'files_changed': [f.filename for f in commit.files] if commit.files else [],
            'stats': {
                'additions': commit.stats.additions if commit.stats else 0,
                'deletions': commit.stats.deletions if commit.stats else 0,
                'total': commit.stats.total if commit.stats else 0
            }
        }
    
    def get_new_releases(self) -> List[Dict[str, Any]]:
        """Get releases since last processed release"""
        if not self.repo:
            return []
        
        print(f"\n🎉 Fetching new releases from {self.repo_name}...")
        
        releases_data = []
        
        try:
            all_releases = self.repo.get_releases()
            
            for release in all_releases:
                # Stop if we've seen this release before
                if self.state.last_release_tag == release.tag_name:
                    break
                
                releases_data.append(self._extract_release_info(release))
            
            print(f"✓ Found {len(releases_data)} new releases")
            
            # Update state with latest release
            if releases_data:
                self.state.last_release_tag = releases_data[0]['tag']
                self.state.last_release_date = releases_data[0]['published_at']
                self.state.total_releases_processed += len(releases_data)
        
        except Exception as e:
            print(f"❌ Error fetching releases: {e}")
        
        return releases_data
    
    def _extract_release_info(self, release) -> Dict[str, Any]:
        """Extract relevant information from release"""
        return {
            'tag': release.tag_name,
            'name': release.title,
            'published_at': release.published_at.isoformat() if release.published_at else None,
            'author': release.author.login if release.author else None,
            'body': release.body,
            'url': release.html_url,
            'is_prerelease': release.prerelease,
            'is_draft': release.draft,
            'assets': [
                {
                    'name': asset.name,
                    'download_url': asset.browser_download_url,
                    'size': asset.size
                }
                for asset in release.get_assets()
            ] if release.get_assets() else []
        }
    
    def analyze_commits_for_changes(self, commits: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze commits to identify significant changes"""
        changes = {
            'features': [],
            'bug_fixes': [],
            'breaking_changes': [],
            'documentation': [],
            'deprecations': [],
            'other': []
        }
        
        # Keywords for categorization
        keywords = {
            'features': ['feat', 'feature', 'add', 'implement', 'new'],
            'bug_fixes': ['fix', 'bug', 'issue', 'resolve', 'patch'],
            'breaking_changes': ['breaking', 'break', 'major', 'remove'],
            'documentation': ['docs', 'doc', 'documentation', 'readme'],
            'deprecations': ['deprecate', 'deprecated', 'obsolete']
        }
        
        for commit in commits:
            message = commit['message'].lower()
            categorized = False
            
            for category, kw_list in keywords.items():
                if any(kw in message for kw in kw_list):
                    changes[category].append({
                        'message': commit['message'].split('\n')[0],  # First line
                        'sha': commit['sha'][:7],
                        'date': commit['date'],
                        'files': commit['files_changed']
                    })
                    categorized = True
                    break
            
            if not categorized:
                changes['other'].append({
                    'message': commit['message'].split('\n')[0],
                    'sha': commit['sha'][:7]
                })
        
        return changes
    
    def get_changelog_entries(self) -> Dict[str, Any]:
        """Extract structured changelog entries"""
        if not self.repo:
            return {}
        
        try:
            # Try to get CHANGELOG.md
            changelog_content = self.repo.get_contents("CHANGELOG.md")
            changelog_text = changelog_content.decoded_content.decode('utf-8')
            
            return self._parse_changelog(changelog_text)
        except:
            return {}
    
    def _parse_changelog(self, text: str) -> Dict[str, Any]:
        """Parse changelog markdown into structured data"""
        entries = {}
        current_version = None
        current_content = []
        
        for line in text.split('\n'):
            # Detect version headers (e.g., ## [1.0.0] - 2024-01-01)
            if line.startswith('## '):
                if current_version:
                    entries[current_version] = '\n'.join(current_content)
                current_version = line.replace('##', '').strip()
                current_content = []
            elif current_version:
                current_content.append(line)
        
        # Add last version
        if current_version:
            entries[current_version] = '\n'.join(current_content)
        
        return entries
    
    def initialize_from_scratch(self):
        """Initialize repository state from scratch"""
        print(f"\n🚀 Initializing repository state for {self.repo_name}...")
        
        # Get all releases
        releases = self.get_new_releases()
        print(f"✓ Loaded {len(releases)} releases")
        
        # Get recent commits
        commits = self.get_new_commits(max_count=100)
        print(f"✓ Loaded {len(commits)} recent commits")
        
        # Save initial state
        self.save_state()
        
        return {
            'releases': releases,
            'commits': commits,
            'initialized': True
        }
    
    def get_incremental_updates(self) -> Dict[str, Any]:
        """Get updates since last run (incremental)"""
        print(f"\n🔄 Checking for updates since last run...")
        
        updates = {
            'has_updates': False,
            'new_commits': [],
            'new_releases': [],
            'commit_analysis': {},
            'last_state': self.state.to_dict()
        }
        
        # Get new commits
        new_commits = self.get_new_commits()
        if new_commits:
            updates['has_updates'] = True
            updates['new_commits'] = new_commits
            updates['commit_analysis'] = self.analyze_commits_for_changes(new_commits)
        
        # Get new releases
        new_releases = self.get_new_releases()
        if new_releases:
            updates['has_updates'] = True
            updates['new_releases'] = new_releases
        
        # Save updated state
        if updates['has_updates']:
            self.save_state()
        
        return updates
    
    def get_summary(self) -> str:
        """Get summary of repository state"""
        summary = f"""
Repository State Summary
========================
Repository: {self.state.repo_name}
Last Commit: {self.state.last_commit_sha or 'None'} ({self.state.last_commit_date or 'N/A'})
Last Release: {self.state.last_release_tag or 'None'} ({self.state.last_release_date or 'N/A'})
Total Commits Processed: {self.state.total_commits_processed}
Total Releases Processed: {self.state.total_releases_processed}
Last Updated: {self.state.last_updated or 'Never'}
"""
        return summary


def main():
    """Test the tracker"""
    tracker = GitHubRepoTracker()
    
    # Check if initialized
    if not tracker.state.last_commit_sha:
        print("First run detected - initializing...")
        data = tracker.initialize_from_scratch()
        print(f"\n✓ Initialized with {len(data['releases'])} releases, {len(data['commits'])} commits")
    else:
        print("Checking for incremental updates...")
        updates = tracker.get_incremental_updates()
        
        if updates['has_updates']:
            print(f"\n✓ Found updates:")
            print(f"  - New commits: {len(updates['new_commits'])}")
            print(f"  - New releases: {len(updates['new_releases'])}")
            
            if updates['commit_analysis']:
                print("\n  Commit analysis:")
                for category, items in updates['commit_analysis'].items():
                    if items:
                        print(f"    - {category}: {len(items)}")
        else:
            print("\n✓ No updates since last run")
    
    print(tracker.get_summary())


if __name__ == "__main__":
    main()
