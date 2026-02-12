#!/usr/bin/env python3
"""
Workflow Trigger Script
Triggers all workflows that support manual execution via workflow_dispatch
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


class WorkflowTrigger:
    def __init__(self, repo_owner="Grumpified-OGGVCT", repo_name="BrowserOS_Guides"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo_full = f"{repo_owner}/{repo_name}"
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "triggered": [],
            "failed": [],
            "skipped": []
        }
    
    def check_gh_cli(self):
        """Check if GitHub CLI is available"""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def trigger_workflow(self, workflow_file, inputs=None):
        """Trigger a workflow via GitHub CLI"""
        cmd = [
            "gh", "workflow", "run", workflow_file,
            "--repo", self.repo_full,
            "--ref", "main"
        ]
        
        if inputs:
            for key, value in inputs.items():
                cmd.extend(["-f", f"{key}={value}"])
        
        print(f"📤 Triggering {workflow_file}...")
        print(f"   Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully triggered {workflow_file}")
                self.results["triggered"].append({
                    "workflow": workflow_file,
                    "status": "triggered",
                    "inputs": inputs,
                    "output": result.stdout
                })
                return True
            else:
                error_msg = result.stderr or result.stdout
                print(f"❌ Failed to trigger {workflow_file}: {error_msg}")
                self.results["failed"].append({
                    "workflow": workflow_file,
                    "error": error_msg
                })
                return False
        
        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout triggering {workflow_file}")
            self.results["failed"].append({
                "workflow": workflow_file,
                "error": "Timeout"
            })
            return False
        except Exception as e:
            print(f"❌ Error triggering {workflow_file}: {e}")
            self.results["failed"].append({
                "workflow": workflow_file,
                "error": str(e)
            })
            return False
    
    def get_workflow_status(self, workflow_file):
        """Get the status of recent workflow runs"""
        cmd = [
            "gh", "run", "list",
            "--repo", self.repo_full,
            "--workflow", workflow_file,
            "--limit", "5",
            "--json", "status,conclusion,createdAt,displayTitle"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return []
        except Exception as e:
            print(f"⚠️ Error getting status for {workflow_file}: {e}")
            return []
    
    def trigger_all_workflows(self):
        """Trigger all dispatchable workflows"""
        workflows = [
            {
                "file": "update-kb.yml",
                "name": "Update BrowserOS Knowledge Base",
                "inputs": {"force_update": "false"},
                "priority": 1,
                "description": "Syncs with official BrowserOS repo and generates new workflows"
            },
            {
                "file": "self-test.yml", 
                "name": "Self-Test & Quality Assurance",
                "inputs": {"force_fix": "true"},
                "priority": 2,
                "description": "Runs comprehensive tests and security scans"
            },
            {
                "file": "deploy-pages.yml",
                "name": "Deploy to GitHub Pages",
                "inputs": None,
                "priority": 3,
                "description": "Deploys website to GitHub Pages"
            }
        ]
        
        print("="*70)
        print("🚀 WORKFLOW TRIGGER PROCESS")
        print("="*70)
        print()
        
        # Check if gh CLI is available
        if not self.check_gh_cli():
            print("❌ GitHub CLI (gh) is not available")
            print("   This script requires GitHub CLI to trigger workflows")
            print("   Install from: https://cli.github.com/")
            print()
            print("📋 ALTERNATIVE: Trigger workflows manually")
            print("-" * 70)
            for wf in workflows:
                print(f"\n{wf['priority']}. {wf['name']}")
                print(f"   File: {wf['file']}")
                print(f"   Description: {wf['description']}")
                print(f"   → Go to: https://github.com/{self.repo_full}/actions")
                print(f"   → Select '{wf['name']}' from left sidebar")
                print(f"   → Click 'Run workflow' button")
                if wf['inputs']:
                    print(f"   → Set inputs: {wf['inputs']}")
            
            self.results["skipped"] = workflows
            return False
        
        # Trigger workflows in priority order
        for wf in sorted(workflows, key=lambda x: x["priority"]):
            print(f"\n{'='*70}")
            print(f"Priority {wf['priority']}: {wf['name']}")
            print(f"{'='*70}")
            print(f"Description: {wf['description']}")
            print()
            
            # Check if already running
            status = self.get_workflow_status(wf['file'])
            if status:
                print(f"📊 Recent runs: {len(status)}")
                for run in status[:2]:
                    print(f"   • {run.get('displayTitle')}: {run.get('status')} - {run.get('conclusion', 'N/A')}")
            
            # Trigger
            success = self.trigger_workflow(wf['file'], wf['inputs'])
            
            if success and wf['priority'] < 3:
                print(f"⏳ Waiting 5 seconds before next trigger...")
                time.sleep(5)
        
        return True
    
    def generate_report(self):
        """Generate a summary report"""
        print("\n" + "="*70)
        print("📊 TRIGGER SUMMARY")
        print("="*70)
        print(f"✅ Successfully triggered: {len(self.results['triggered'])}")
        print(f"❌ Failed: {len(self.results['failed'])}")
        print(f"⏭️ Skipped: {len(self.results['skipped'])}")
        
        if self.results['triggered']:
            print("\n🎯 Triggered workflows:")
            for wf in self.results['triggered']:
                print(f"   • {wf['workflow']}")
        
        if self.results['failed']:
            print("\n❌ Failed workflows:")
            for wf in self.results['failed']:
                print(f"   • {wf['workflow']}: {wf['error']}")
        
        print("\n" + "="*70)
        print("📋 NEXT STEPS:")
        print("="*70)
        print("1. Monitor workflow progress at:")
        print(f"   https://github.com/{self.repo_full}/actions")
        print()
        print("2. Check workflow logs for any errors")
        print()
        print("3. Verify outputs:")
        print("   • Update KB: New workflows in BrowserOS/Workflows/")
        print("   • Self-Test: Test results artifact")
        print("   • Deploy Pages: Updated website")
        print("="*70)
        
        # Save results
        report_file = Path("WORKFLOW_TRIGGER_REPORT.json")
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Report saved to: {report_file}")


def main():
    """Main entry point"""
    print("🚀 BrowserOS_Guides Workflow Trigger Script")
    print(f"⏰ Started at: {datetime.now(timezone.utc).isoformat()}\n")
    
    trigger = WorkflowTrigger()
    trigger.trigger_all_workflows()
    trigger.generate_report()
    
    print("\n✨ Workflow trigger process completed!")


if __name__ == "__main__":
    main()
