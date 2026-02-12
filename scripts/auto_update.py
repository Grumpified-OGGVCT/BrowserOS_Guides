#!/usr/bin/env python3
"""
BrowserOS Knowledge Base - Auto Update System
Bulletproof auto-update mechanism that safely syncs with remote repository
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, List
import json

# Color codes for Windows console
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no response from user"""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{prompt} [{default_str}]: ").strip().lower()
        if not response:
            return default
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print_error("Please enter 'y' or 'n'")

def run_command(cmd: List[str], capture_output: bool = True, check: bool = False) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, check=check)
            return result.returncode, "", ""
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout if hasattr(e, 'stdout') else "", e.stderr if hasattr(e, 'stderr') else ""
    except Exception as e:
        return 1, "", str(e)

class AutoUpdater:
    """Bulletproof auto-update system"""
    
    def __init__(self, silent: bool = False):
        self.repo_root = Path(__file__).parent.parent
        self.backup_dir = self.repo_root / '.update_backups'
        self.update_log = self.repo_root / 'logs' / 'update.log'
        self.silent = silent
        self.config_file = self.repo_root / '.env'
        
        # Ensure logs directory exists
        self.update_log.parent.mkdir(exist_ok=True)
        
    def log(self, message: str):
        """Log message to file and optionally print"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        
        try:
            with open(self.update_log, 'a', encoding='utf-8') as f:
                f.write(log_msg + '\n')
        except Exception:
            pass  # Don't fail if logging fails
        
        if not self.silent:
            print(message)
    
    def check_prerequisites(self) -> bool:
        """Check if git is available and we're in a git repo"""
        # Check git is installed
        returncode, _, _ = run_command(['git', '--version'])
        if returncode != 0:
            print_error("Git is not installed or not in PATH")
            self.log("ERROR: Git not available")
            return False
        
        # Check we're in a git repository
        returncode, _, _ = run_command(['git', 'rev-parse', '--git-dir'])
        if returncode != 0:
            print_warning("Not a git repository - skipping auto-update")
            self.log("WARNING: Not in a git repository")
            return False
        
        return True
    
    def get_update_mode(self) -> str:
        """Get update mode from configuration"""
        # Default is 'prompt'
        mode = 'prompt'
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    for line in f:
                        if line.strip().startswith('AUTO_UPDATE_MODE='):
                            mode = line.split('=', 1)[1].strip()
                            break
            except Exception:
                pass
        
        return mode
    
    def check_uncommitted_changes(self) -> Tuple[bool, List[str]]:
        """Check for uncommitted changes"""
        returncode, stdout, _ = run_command(['git', 'status', '--porcelain'])
        
        if returncode != 0:
            return False, []
        
        changes = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
        return len(changes) > 0, changes
    
    def get_current_branch(self) -> Optional[str]:
        """Get current git branch"""
        returncode, stdout, _ = run_command(['git', 'branch', '--show-current'])
        
        if returncode == 0 and stdout.strip():
            return stdout.strip()
        return None
    
    def get_remote_info(self) -> Optional[str]:
        """Get remote repository URL"""
        returncode, stdout, _ = run_command(['git', 'remote', 'get-url', 'origin'])
        
        if returncode == 0 and stdout.strip():
            return stdout.strip()
        return None
    
    def fetch_updates(self) -> bool:
        """Fetch updates from remote"""
        print_info("Fetching updates from remote...")
        self.log("Fetching updates from remote...")
        
        returncode, stdout, stderr = run_command(['git', 'fetch', 'origin'])
        
        if returncode != 0:
            print_error(f"Failed to fetch updates: {stderr}")
            self.log(f"ERROR: Fetch failed - {stderr}")
            return False
        
        print_success("Successfully fetched updates")
        self.log("Successfully fetched updates")
        return True
    
    def check_updates_available(self) -> Tuple[bool, int, str]:
        """Check if updates are available"""
        branch = self.get_current_branch()
        if not branch:
            return False, 0, ""
        
        # Get commits behind
        returncode, stdout, _ = run_command([
            'git', 'rev-list', '--count', f'HEAD..origin/{branch}'
        ])
        
        if returncode != 0:
            return False, 0, ""
        
        commits_behind = int(stdout.strip()) if stdout.strip() else 0
        
        # Get update summary
        if commits_behind > 0:
            returncode, stdout, _ = run_command([
                'git', 'log', '--oneline', f'HEAD..origin/{branch}', '-n', '5'
            ])
            summary = stdout.strip() if returncode == 0 else ""
        else:
            summary = ""
        
        return commits_behind > 0, commits_behind, summary
    
    def create_backup(self) -> Optional[Path]:
        """Create backup of important files before update"""
        try:
            # Create backup directory with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.backup_dir / timestamp
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup critical files
            critical_files = [
                '.env',
                'config.yml',
                'logs',
                'BrowserOS/Research/BrowserOS_Workflows_KnowledgeBase.md'
            ]
            
            for file_path in critical_files:
                src = self.repo_root / file_path
                if src.exists():
                    dst = backup_path / file_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    
                    if src.is_file():
                        shutil.copy2(src, dst)
                    elif src.is_dir():
                        shutil.copytree(src, dst, dirs_exist_ok=True)
            
            print_success(f"Created backup at: {backup_path}")
            self.log(f"Created backup at: {backup_path}")
            return backup_path
            
        except Exception as e:
            print_error(f"Failed to create backup: {e}")
            self.log(f"ERROR: Backup failed - {e}")
            return None
    
    def stash_changes(self) -> bool:
        """Stash uncommitted changes"""
        print_info("Stashing uncommitted changes...")
        self.log("Stashing uncommitted changes...")
        
        returncode, stdout, stderr = run_command([
            'git', 'stash', 'push', '-u', '-m', 
            f'Auto-stash before update {datetime.now().isoformat()}'
        ])
        
        if returncode != 0:
            print_error(f"Failed to stash changes: {stderr}")
            self.log(f"ERROR: Stash failed - {stderr}")
            return False
        
        print_success("Changes stashed successfully")
        self.log("Changes stashed successfully")
        return True
    
    def pull_updates(self) -> bool:
        """Pull updates from remote"""
        branch = self.get_current_branch()
        if not branch:
            print_error("Could not determine current branch")
            self.log("ERROR: Could not determine current branch")
            return False
        
        print_info(f"Pulling updates for branch: {branch}")
        self.log(f"Pulling updates for branch: {branch}")
        
        returncode, stdout, stderr = run_command([
            'git', 'pull', 'origin', branch
        ])
        
        if returncode != 0:
            print_error(f"Failed to pull updates: {stderr}")
            self.log(f"ERROR: Pull failed - {stderr}")
            
            # Check for merge conflicts
            if 'CONFLICT' in stderr or 'conflict' in stderr.lower():
                print_error("Merge conflicts detected!")
                self.log("ERROR: Merge conflicts detected")
                return False
            
            return False
        
        print_success("Successfully pulled updates")
        self.log(f"Successfully pulled updates: {stdout[:200]}")
        return True
    
    def pop_stash(self) -> bool:
        """Pop stashed changes back"""
        print_info("Restoring stashed changes...")
        self.log("Restoring stashed changes...")
        
        # Check if there are stashes
        returncode, stdout, _ = run_command(['git', 'stash', 'list'])
        if returncode != 0 or not stdout.strip():
            print_info("No stashed changes to restore")
            return True
        
        returncode, stdout, stderr = run_command(['git', 'stash', 'pop'])
        
        if returncode != 0:
            print_warning(f"Could not automatically restore stashed changes: {stderr}")
            print_warning("You may need to manually resolve conflicts")
            print_info("Run 'git stash list' to see stashed changes")
            self.log(f"WARNING: Stash pop failed - {stderr}")
            return False
        
        print_success("Stashed changes restored")
        self.log("Stashed changes restored")
        return True
    
    def validate_update(self) -> bool:
        """Validate repository after update"""
        print_info("Validating repository integrity...")
        self.log("Validating repository integrity...")
        
        # Check git status
        returncode, stdout, stderr = run_command(['git', 'status'])
        if returncode != 0:
            print_error("Repository validation failed")
            self.log("ERROR: Validation failed")
            return False
        
        # Check for critical files
        critical_files = ['requirements.txt', 'config.yml', 'run.bat', 'install.bat']
        missing_files = []
        
        for file_path in critical_files:
            if not (self.repo_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print_warning(f"Some files are missing: {', '.join(missing_files)}")
            self.log(f"WARNING: Missing files - {', '.join(missing_files)}")
        
        print_success("Repository validation passed")
        self.log("Repository validation passed")
        return True
    
    def restore_backup(self, backup_path: Path) -> bool:
        """Restore from backup"""
        try:
            print_warning(f"Restoring from backup: {backup_path}")
            self.log(f"Restoring from backup: {backup_path}")
            
            # Restore backed up files
            for item in backup_path.rglob('*'):
                if item.is_file():
                    relative = item.relative_to(backup_path)
                    dst = self.repo_root / relative
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dst)
            
            print_success("Backup restored successfully")
            self.log("Backup restored successfully")
            return True
            
        except Exception as e:
            print_error(f"Failed to restore backup: {e}")
            self.log(f"ERROR: Backup restore failed - {e}")
            return False
    
    def cleanup_old_backups(self, keep: int = 5):
        """Keep only the most recent backups"""
        if not self.backup_dir.exists():
            return
        
        try:
            backups = sorted(self.backup_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
            
            for backup in backups[keep:]:
                if backup.is_dir():
                    shutil.rmtree(backup)
                    self.log(f"Cleaned up old backup: {backup.name}")
        
        except Exception as e:
            self.log(f"WARNING: Failed to cleanup old backups - {e}")
    
    def run(self) -> bool:
        """Run the auto-update process"""
        print_header("BrowserOS Knowledge Base - Auto Update")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Get update mode
        update_mode = self.get_update_mode()
        self.log(f"Update mode: {update_mode}")
        
        if update_mode == 'disabled':
            print_info("Auto-update is disabled")
            self.log("Auto-update is disabled")
            return True
        
        # Get repository info
        branch = self.get_current_branch()
        remote = self.get_remote_info()
        
        print_info(f"Current branch: {branch}")
        print_info(f"Remote: {remote}")
        
        # Check for uncommitted changes
        has_changes, changes = self.check_uncommitted_changes()
        
        if has_changes:
            print_warning(f"Found {len(changes)} uncommitted change(s)")
            if not self.silent:
                print("\nUncommitted changes:")
                for change in changes[:10]:  # Show first 10
                    print(f"  {change}")
                if len(changes) > 10:
                    print(f"  ... and {len(changes) - 10} more")
        
        # Fetch updates
        if not self.fetch_updates():
            return False
        
        # Check if updates are available
        updates_available, commits_behind, summary = self.check_updates_available()
        
        if not updates_available:
            print_success("Repository is up to date!")
            self.log("Repository is up to date")
            return True
        
        # Updates are available
        print_warning(f"\nUpdates available! ({commits_behind} commit(s) behind)")
        self.log(f"Updates available: {commits_behind} commits behind")
        
        if summary:
            print("\nRecent changes:")
            for line in summary.split('\n')[:5]:
                print(f"  {line}")
        
        # Decide whether to update based on mode
        should_update = False
        
        if update_mode == 'auto' or update_mode == '':
            should_update = True
            print_info("\nAuto-update mode: Installing updates automatically...")
            self.log("Auto-update mode: Installing automatically")
        elif update_mode == 'prompt':
            if not self.silent:
                should_update = yes_no("\nWould you like to install these updates now?", default=True)
            else:
                should_update = False
        else:
            print_warning(f"Unknown update mode: {update_mode}, defaulting to auto-install")
            should_update = True
        
        if not should_update:
            print_info("Skipping update installation")
            self.log("Update installation skipped by user")
            return True
        
        # Create backup before updating
        backup_path = self.create_backup()
        if not backup_path:
            print_error("Failed to create backup - aborting update")
            return False
        
        # Stash changes if any
        if has_changes:
            if not self.stash_changes():
                print_error("Failed to stash changes - aborting update")
                return False
        
        # Pull updates
        update_success = self.pull_updates()
        
        if not update_success:
            print_error("Update installation failed!")
            
            # Offer to restore backup
            if not self.silent:
                if yes_no("Would you like to restore from backup?", default=True):
                    self.restore_backup(backup_path)
            
            return False
        
        # Pop stashed changes back
        if has_changes:
            self.pop_stash()
        
        # Validate update
        if not self.validate_update():
            print_warning("Validation failed - check repository status")
        
        # Cleanup old backups
        self.cleanup_old_backups(keep=5)
        
        print_success("\n" + "=" * 80)
        print_success("  Updates installed successfully!")
        print_success("=" * 80)
        self.log("Updates installed successfully")
        
        # Check if we need to reinstall dependencies
        print_info("\nChecking if dependencies need to be updated...")
        returncode, _, _ = run_command(['git', 'diff', 'HEAD@{1}', 'HEAD', '--', 'requirements.txt'])
        if returncode == 0:
            print_info("Requirements may have changed. Updating dependencies...")
            ret, _, _ = run_command(['python', '-m', 'pip', 'install', '-r', 'requirements.txt', '--upgrade'])
            if ret == 0:
                print_success("Dependencies updated successfully")
            else:
                print_warning("Failed to update dependencies automatically")
                print_info("Please run: python -m pip install -r requirements.txt")
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BrowserOS KB Auto-Update System')
    parser.add_argument('--silent', action='store_true', 
                       help='Run in silent mode (no prompts)')
    parser.add_argument('--mode', choices=['auto', 'prompt', 'disabled'],
                       help='Override update mode from config')
    
    args = parser.parse_args()
    
    try:
        updater = AutoUpdater(silent=args.silent)
        
        # Override mode if specified
        if args.mode:
            updater.config_file = None  # Disable config reading
            if args.mode == 'disabled':
                print_info("Update check disabled by command line")
                sys.exit(0)
        
        success = updater.run()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nUpdate cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUpdate failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
