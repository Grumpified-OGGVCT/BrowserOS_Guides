#!/usr/bin/env python3
"""
WhatsApp Integration Monitor
Actively monitors BrowserOS repositories for signs of WhatsApp/social feature development.

This script checks:
- Code search results for WhatsApp-related keywords
- Recent commits for social feature mentions
- New branches with messaging-related names
- Open issues/PRs about social platforms
- Dependency changes (package.json, requirements.txt)

When detection occurs, it triggers alerts and knowledge compilation.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class WhatsAppMonitor:
    """Monitor for WhatsApp integration development in BrowserOS repos."""
    
    def __init__(self):
        self.repo_root = project_root
        self.sources_file = self.repo_root / "BrowserOS" / "Research" / "sources.json"
        self.report_file = self.repo_root / "WHATSAPP_WATCH_REPORT.md"
        
        # Keywords to monitor
        self.keywords = [
            "whatsapp",
            "whatsapp-web",
            "social media",
            "messaging platform",
            "chat automation",
            "telegram",
            "discord automation",
            "instagram dm",
            "facebook messenger"
        ]
        
        # BrowserOS repositories to monitor
        self.repos = [
            {
                "owner": "browseros-ai",
                "name": "BrowserOS",
                "priority": "critical"
            },
            {
                "owner": "browseros-ai",
                "name": "BrowserOS-agent",
                "priority": "high"
            },
            {
                "owner": "browseros-ai",
                "name": "moltyflow",
                "priority": "medium"
            }
        ]
        
        self.detections = []
        self.last_check = datetime.utcnow().isoformat() + "Z"
    
    def search_code(self, owner: str, repo: str, keyword: str) -> Dict[str, Any]:
        """Search for keyword in repository code using gh CLI."""
        try:
            cmd = [
                "gh", "search", "code",
                f"{keyword} repo:{owner}/{repo}",
                "--json", "path,repository,textMatches",
                "--limit", "10"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "keyword": keyword,
                    "repo": f"{owner}/{repo}",
                    "found": len(data) > 0,
                    "count": len(data),
                    "results": data[:3]  # First 3 results
                }
            else:
                return {
                    "keyword": keyword,
                    "repo": f"{owner}/{repo}",
                    "found": False,
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "keyword": keyword,
                "repo": f"{owner}/{repo}",
                "found": False,
                "error": str(e)
            }
    
    def check_recent_commits(self, owner: str, repo: str) -> Dict[str, Any]:
        """Check recent commits for WhatsApp-related keywords."""
        try:
            cmd = [
                "gh", "api",
                f"/repos/{owner}/{repo}/commits",
                "-q", ".[] | {sha: .sha, message: .commit.message, date: .commit.author.date}",
                "--paginate"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            commit = json.loads(line)
                            # Check if any keyword in commit message
                            message_lower = commit['message'].lower()
                            for keyword in self.keywords:
                                if keyword.lower() in message_lower:
                                    commits.append({
                                        "sha": commit['sha'][:7],
                                        "message": commit['message'],
                                        "date": commit['date'],
                                        "matched_keyword": keyword
                                    })
                                    break
                        except json.JSONDecodeError:
                            continue
                
                return {
                    "repo": f"{owner}/{repo}",
                    "commits_checked": len(result.stdout.strip().split('\n')),
                    "matches_found": len(commits),
                    "matching_commits": commits[:5]  # First 5 matches
                }
            else:
                return {
                    "repo": f"{owner}/{repo}",
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "repo": f"{owner}/{repo}",
                "error": str(e)
            }
    
    def check_branches(self, owner: str, repo: str) -> Dict[str, Any]:
        """Check for branches with social/messaging-related names."""
        try:
            cmd = [
                "gh", "api",
                f"/repos/{owner}/{repo}/branches",
                "-q", ".[].name"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                branches = result.stdout.strip().split('\n')
                matching = []
                
                for branch in branches:
                    branch_lower = branch.lower()
                    for keyword in self.keywords:
                        if keyword.lower().replace(" ", "-") in branch_lower or \
                           keyword.lower().replace(" ", "_") in branch_lower:
                            matching.append({
                                "branch": branch,
                                "matched_keyword": keyword
                            })
                            break
                
                return {
                    "repo": f"{owner}/{repo}",
                    "total_branches": len(branches),
                    "matching_branches": matching
                }
            else:
                return {
                    "repo": f"{owner}/{repo}",
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "repo": f"{owner}/{repo}",
                "error": str(e)
            }
    
    def check_issues(self, owner: str, repo: str) -> Dict[str, Any]:
        """Check open issues for WhatsApp-related requests."""
        try:
            matching_issues = []
            
            for keyword in self.keywords:
                cmd = [
                    "gh", "search", "issues",
                    f"{keyword} repo:{owner}/{repo} state:open",
                    "--json", "number,title,url,createdAt",
                    "--limit", "5"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for issue in data:
                        matching_issues.append({
                            "number": issue['number'],
                            "title": issue['title'],
                            "url": issue['url'],
                            "created": issue['createdAt'],
                            "matched_keyword": keyword
                        })
            
            return {
                "repo": f"{owner}/{repo}",
                "matching_issues": matching_issues[:10]  # First 10
            }
        except Exception as e:
            return {
                "repo": f"{owner}/{repo}",
                "error": str(e)
            }
    
    def run_monitoring(self) -> Dict[str, Any]:
        """Run complete monitoring sweep across all repos."""
        print("🔍 Starting WhatsApp Integration Monitor...")
        print(f"⏰ Check time: {self.last_check}")
        print(f"📋 Monitoring {len(self.repos)} repositories")
        print(f"🔑 Tracking {len(self.keywords)} keywords\n")
        
        results = {
            "timestamp": self.last_check,
            "status": "no_detection",
            "repos_checked": len(self.repos),
            "keywords_tracked": len(self.keywords),
            "detections": [],
            "code_searches": [],
            "commit_checks": [],
            "branch_checks": [],
            "issue_checks": []
        }
        
        for repo in self.repos:
            owner = repo['owner']
            name = repo['name']
            priority = repo['priority']
            
            print(f"\n{'='*60}")
            print(f"📦 Checking {owner}/{name} (priority: {priority})")
            print(f"{'='*60}")
            
            # Code search
            print("\n🔎 Searching code...")
            for keyword in self.keywords[:3]:  # Check top 3 keywords
                search_result = self.search_code(owner, name, keyword)
                results['code_searches'].append(search_result)
                
                if search_result.get('found'):
                    print(f"  ✅ FOUND: '{keyword}' - {search_result['count']} results")
                    results['detections'].append({
                        "type": "code_search",
                        "repo": f"{owner}/{name}",
                        "keyword": keyword,
                        "count": search_result['count'],
                        "priority": priority
                    })
                else:
                    print(f"  ⚪ Not found: '{keyword}'")
            
            # Commit check
            print("\n📝 Checking recent commits...")
            commit_result = self.check_recent_commits(owner, name)
            results['commit_checks'].append(commit_result)
            
            if commit_result.get('matches_found', 0) > 0:
                print(f"  ✅ FOUND: {commit_result['matches_found']} matching commits")
                results['detections'].append({
                    "type": "commits",
                    "repo": f"{owner}/{name}",
                    "count": commit_result['matches_found'],
                    "priority": priority
                })
            else:
                print(f"  ⚪ No matching commits found")
            
            # Branch check
            print("\n🌿 Checking branches...")
            branch_result = self.check_branches(owner, name)
            results['branch_checks'].append(branch_result)
            
            if branch_result.get('matching_branches'):
                print(f"  ✅ FOUND: {len(branch_result['matching_branches'])} matching branches")
                results['detections'].append({
                    "type": "branches",
                    "repo": f"{owner}/{name}",
                    "branches": branch_result['matching_branches'],
                    "priority": priority
                })
            else:
                print(f"  ⚪ No matching branches found")
            
            # Issue check
            print("\n📋 Checking issues...")
            issue_result = self.check_issues(owner, name)
            results['issue_checks'].append(issue_result)
            
            if issue_result.get('matching_issues'):
                print(f"  ✅ FOUND: {len(issue_result['matching_issues'])} matching issues")
                results['detections'].append({
                    "type": "issues",
                    "repo": f"{owner}/{name}",
                    "count": len(issue_result['matching_issues']),
                    "priority": priority
                })
            else:
                print(f"  ⚪ No matching issues found")
        
        # Determine overall status
        if results['detections']:
            results['status'] = "DETECTION"
            print(f"\n{'='*60}")
            print(f"🚨 ALERT: {len(results['detections'])} detection(s) found!")
            print(f"{'='*60}")
        else:
            print(f"\n{'='*60}")
            print(f"✅ No detections - WhatsApp development not yet started")
            print(f"{'='*60}")
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate markdown report of monitoring results."""
        report = f"""# WhatsApp Integration Watch Report

**Last Updated**: {results['timestamp']}  
**Status**: {results['status']}  
**Repositories Monitored**: {results['repos_checked']}  
**Keywords Tracked**: {results['keywords_tracked']}

---

## Detection Status

"""
        
        if results['status'] == "DETECTION":
            report += f"### 🚨 ALERT: {len(results['detections'])} Detection(s) Found!\n\n"
            
            for detection in results['detections']:
                report += f"#### {detection['type'].title()} Detection\n"
                report += f"- **Repository**: {detection['repo']}\n"
                report += f"- **Priority**: {detection['priority']}\n"
                
                if 'keyword' in detection:
                    report += f"- **Keyword**: {detection['keyword']}\n"
                    report += f"- **Results**: {detection['count']}\n"
                elif 'branches' in detection:
                    report += f"- **Matching Branches**:\n"
                    for branch in detection['branches']:
                        report += f"  - `{branch['branch']}` (keyword: {branch['matched_keyword']})\n"
                elif 'count' in detection:
                    report += f"- **Matches**: {detection['count']}\n"
                
                report += "\n"
            
            report += """
### 🎯 Recommended Actions

1. ⚡ **Immediate**: Clone detected branches/commits for analysis
2. 📊 **Analysis**: Review code changes and extract patterns
3. 📚 **KB Update**: Generate initial knowledge base entries
4. 🔄 **Schema Update**: Update whatsapp_tools.json if needed
5. 🚨 **Alert Team**: Create GitHub issue for manual review

"""
        else:
            report += """### ✅ No Detection

WhatsApp integration development has not yet started in monitored repositories.

**Current Status**: Standby mode - continuing daily monitoring.

"""
        
        report += f"""---

## Monitoring Coverage

### Repositories Checked

"""
        
        for repo in self.repos:
            report += f"- **{repo['owner']}/{repo['name']}** (priority: {repo['priority']})\n"
        
        report += f"""
### Keywords Tracked

"""
        
        for keyword in self.keywords:
            report += f"- `{keyword}`\n"
        
        report += f"""

---

## Detailed Results

### Code Search Results

"""
        
        for search in results['code_searches']:
            if search.get('found'):
                report += f"✅ **{search['repo']}** - `{search['keyword']}`: {search['count']} results\n"
        
        if not any(s.get('found') for s in results['code_searches']):
            report += "No code matches found.\n"
        
        report += """
### Recent Commits Check

"""
        
        for commit_check in results['commit_checks']:
            if commit_check.get('matches_found', 0) > 0:
                report += f"✅ **{commit_check['repo']}**: {commit_check['matches_found']} matching commits\n"
        
        if not any(c.get('matches_found', 0) > 0 for c in results['commit_checks']):
            report += "No matching commits found.\n"
        
        report += """
### Branch Check

"""
        
        for branch_check in results['branch_checks']:
            if branch_check.get('matching_branches'):
                report += f"✅ **{branch_check['repo']}**: {len(branch_check['matching_branches'])} matching branches\n"
        
        if not any(b.get('matching_branches') for b in results['branch_checks']):
            report += "No matching branches found.\n"
        
        report += """
### Issue Check

"""
        
        for issue_check in results['issue_checks']:
            if issue_check.get('matching_issues'):
                report += f"✅ **{issue_check['repo']}**: {len(issue_check['matching_issues'])} matching issues\n"
        
        if not any(i.get('matching_issues') for i in results['issue_checks']):
            report += "No matching issues found.\n"
        
        report += f"""

---

## Next Check

**Scheduled**: Daily at 00:00 UTC  
**Manual Trigger**: Run `python scripts/monitor_whatsapp.py`  
**GitHub Actions**: `.github/workflows/whatsapp-monitor.yml`

---

*This is an automated monitoring system. Report generated by WhatsApp Integration Monitor.*
"""
        
        return report
    
    def save_report(self, results: Dict[str, Any]):
        """Save monitoring report to file."""
        report = self.generate_report(results)
        
        with open(self.report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {self.report_file}")
    
    def create_alert_issue(self, results: Dict[str, Any]):
        """Create GitHub issue if detection occurs (requires gh CLI auth)."""
        if results['status'] != "DETECTION":
            return
        
        print("\n🚨 Creating alert issue...")
        
        issue_title = f"🚨 WhatsApp Integration Detected in BrowserOS Repositories"
        issue_body = f"""# WhatsApp Integration Detection Alert

**Timestamp**: {results['timestamp']}  
**Detections**: {len(results['detections'])}

## Summary

Our automated monitoring system has detected WhatsApp-related development in BrowserOS repositories!

## Detections

"""
        
        for detection in results['detections']:
            issue_body += f"- **{detection['type'].title()}** in {detection['repo']}\n"
        
        issue_body += """
## Recommended Actions

1. Review detection details in `WHATSAPP_WATCH_REPORT.md`
2. Clone and analyze detected branches/commits
3. Update knowledge base with findings
4. Update schemas if API patterns change
5. Test integration compatibility

## Monitoring Report

See full report: [WHATSAPP_WATCH_REPORT.md](./WHATSAPP_WATCH_REPORT.md)

---

*This issue was automatically created by the WhatsApp Integration Monitor.*
"""
        
        try:
            cmd = [
                "gh", "issue", "create",
                "--title", issue_title,
                "--body", issue_body,
                "--label", "alert,whatsapp,automation"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Alert issue created: {result.stdout.strip()}")
            else:
                print(f"⚠️  Could not create issue: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Could not create issue: {e}")


def main():
    """Main execution function."""
    print("""
╔════════════════════════════════════════════════════════════╗
║       WhatsApp Integration Monitor for BrowserOS           ║
║                                                            ║
║  Actively monitoring for WhatsApp feature development     ║
╚════════════════════════════════════════════════════════════╝
""")
    
    monitor = WhatsAppMonitor()
    
    # Run monitoring
    results = monitor.run_monitoring()
    
    # Save report
    monitor.save_report(results)
    
    # Create alert if detection
    if results['status'] == "DETECTION":
        monitor.create_alert_issue(results)
    
    print(f"\n{'='*60}")
    print(f"✅ Monitoring complete!")
    print(f"📊 Status: {results['status']}")
    print(f"📄 Report: WHATSAPP_WATCH_REPORT.md")
    print(f"{'='*60}\n")
    
    # Exit with code based on status
    if results['status'] == "DETECTION":
        sys.exit(0)  # Success with detection
    else:
        sys.exit(0)  # Success, no detection


if __name__ == "__main__":
    main()
