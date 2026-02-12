#!/usr/bin/env python3
"""
BrowserOS Knowledge Base - Configuration Manager
Post-setup tool for modifying configuration settings
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

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

def clear_screen():
    """Clear the console screen safely"""
    try:
        if os.name == 'nt':
            subprocess.run(['cmd', '/c', 'cls'], check=False)
        else:
            subprocess.run(['clear'], check=False)
    except Exception:
        # If clearing fails, just continue
        pass

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

def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def get_choice(prompt: str, options: list) -> int:
    """Get user choice from a list of options"""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        choice = input(f"\nEnter choice [1-{len(options)}]: ").strip()
        try:
            choice_int = int(choice) - 1
            if 0 <= choice_int < len(options):
                return choice_int
            print_error(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print_error("Please enter a valid number")

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

class ConfigManager:
    """Configuration manager for BrowserOS Knowledge Base"""
    
    def __init__(self):
        self.env_file = Path('.env')
        self.config: Dict[str, str] = {}
        self.modified = False
        
    def run(self):
        """Main configuration manager loop"""
        if not self.load_config():
            print_error("No configuration found!")
            print_info("Please run the setup wizard first: python scripts\\setup_wizard.py")
            sys.exit(1)
        
        while True:
            clear_screen()
            self.show_main_menu()
            
    def load_config(self) -> bool:
        """Load configuration from .env file"""
        if not self.env_file.exists():
            return False
        
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.config[key.strip()] = value.strip()
            return True
        except Exception as e:
            print_error(f"Failed to load configuration: {e}")
            return False
    
    def save_config(self):
        """Save configuration to .env file"""
        try:
            # Create backup
            if self.env_file.exists():
                backup = self.env_file.with_suffix(f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                shutil.copy(self.env_file, backup)
                print_info(f"Backed up config to {backup}")
            
            # Write new configuration
            with open(self.env_file, 'w') as f:
                f.write("# " + "=" * 76 + "\n")
                f.write("# BrowserOS Knowledge Base - Configuration\n")
                f.write(f"# Modified: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# " + "=" * 76 + "\n\n")
                
                for key, value in sorted(self.config.items()):
                    f.write(f"{key}={value}\n")
            
            print_success("Configuration saved successfully")
            self.modified = False
        except Exception as e:
            print_error(f"Failed to save configuration: {e}")
    
    def show_main_menu(self):
        """Display main configuration menu"""
        print_header("BrowserOS Knowledge Base - Configuration Manager")
        
        print(f"""
Current Configuration Status:
  Agent Mode:        {self.config.get('AGENT_MODE', 'Not set')}
  Ollama API Key:    {'✓ Configured' if self.config.get('OLLAMA_API_KEY') else '✗ Not set'}
  OpenRouter Key:    {'✓ Configured' if self.config.get('OPENROUTER_API_KEY') else '✗ Not set'}
  GitHub Token:      {'✓ Configured' if self.config.get('GITHUB_TOKEN') else '✗ Not set'}
  Log Level:         {self.config.get('LOG_LEVEL', 'INFO')}
  
{'  ⚠ UNSAVED CHANGES' if self.modified else ''}

What would you like to configure?
""")
        
        options = [
            "Agent Connection Settings",
            "API Keys & Tokens",
            "Model Selection",
            "Research Pipeline",
            "Performance & Concurrency",
            "Logging & Monitoring",
            "Optional Features",
            "View Current Configuration",
            "Reset to Defaults",
            "Save and Exit" if self.modified else "Exit"
        ]
        
        choice = get_choice("Select category:", options)
        
        handlers = [
            self.configure_agent_settings,
            self.configure_api_keys,
            self.configure_models,
            self.configure_research,
            self.configure_performance,
            self.configure_logging,
            self.configure_optional,
            self.view_configuration,
            self.reset_config,
            self.exit_manager
        ]
        
        handlers[choice]()
    
    def configure_agent_settings(self):
        """Configure agent connection settings"""
        clear_screen()
        print_header("Agent Connection Settings")
        
        # Agent Mode
        print("\nAgent Mode:")
        modes = ["hybrid", "sdk", "http", "mcp", "local", "docker"]
        current = self.config.get('AGENT_MODE', 'hybrid')
        print(f"Current: {current}")
        
        if yes_no("Change agent mode?", default=False):
            choice = get_choice("Select mode:", [m.upper() for m in modes])
            self.config['AGENT_MODE'] = modes[choice]
            self.modified = True
            print_success(f"Agent mode changed to: {modes[choice]}")
        
        # Ollama Mode
        print("\nOllama Connection Mode:")
        modes = ["http", "sdk", "mcp", "docker", "local"]
        current = self.config.get('OLLAMA_MODE', 'http')
        print(f"Current: {current}")
        
        if yes_no("Change Ollama mode?", default=False):
            choice = get_choice("Select mode:", [m.upper() for m in modes])
            self.config['OLLAMA_MODE'] = modes[choice]
            self.modified = True
            print_success(f"Ollama mode changed to: {modes[choice]}")
        
        # OpenRouter Mode
        print("\nOpenRouter Connection Mode:")
        modes = ["http", "sdk", "mcp"]
        current = self.config.get('OPENROUTER_MODE', 'http')
        print(f"Current: {current}")
        
        if yes_no("Change OpenRouter mode?", default=False):
            choice = get_choice("Select mode:", [m.upper() for m in modes])
            self.config['OPENROUTER_MODE'] = modes[choice]
            self.modified = True
            print_success(f"OpenRouter mode changed to: {modes[choice]}")
        
        input("\nPress Enter to continue...")
    
    def configure_api_keys(self):
        """Configure API keys"""
        clear_screen()
        print_header("API Keys & Tokens")
        
        # Ollama API Key
        print("\nOllama Cloud API Key:")
        current = self.config.get('OLLAMA_API_KEY', '')
        if current:
            print_success(f"Current: {current[:10]}...{current[-4:]}")
        else:
            print_warning("Not set")
        
        if yes_no("Update Ollama API key?", default=False):
            key = get_input("Enter new API key (or 'clear' to remove)", default=current)
            if key.lower() == 'clear':
                self.config['OLLAMA_API_KEY'] = ''
                print_info("Ollama API key cleared")
            else:
                self.config['OLLAMA_API_KEY'] = key
                print_success("Ollama API key updated")
            self.modified = True
        
        # OpenRouter API Key
        print("\nOpenRouter API Key:")
        current = self.config.get('OPENROUTER_API_KEY', '')
        if current:
            print_success(f"Current: {current[:10]}...{current[-4:]}")
        else:
            print_warning("Not set")
        
        if yes_no("Update OpenRouter API key?", default=False):
            key = get_input("Enter new API key (or 'clear' to remove)", default=current)
            if key.lower() == 'clear':
                self.config['OPENROUTER_API_KEY'] = ''
                print_info("OpenRouter API key cleared")
            else:
                self.config['OPENROUTER_API_KEY'] = key
                print_success("OpenRouter API key updated")
            self.modified = True
        
        # GitHub Token
        print("\nGitHub Token:")
        current = self.config.get('GITHUB_TOKEN', '')
        if current:
            print_success(f"Current: {current[:10]}...{current[-4:]}")
        else:
            print_warning("Not set")
        
        if yes_no("Update GitHub token?", default=False):
            token = get_input("Enter new token (or 'clear' to remove)", default=current)
            if token.lower() == 'clear':
                self.config['GITHUB_TOKEN'] = ''
                print_info("GitHub token cleared")
            else:
                self.config['GITHUB_TOKEN'] = token
                print_success("GitHub token updated")
            self.modified = True
        
        input("\nPress Enter to continue...")
    
    def configure_models(self):
        """Configure AI models"""
        clear_screen()
        print_header("Model Selection")
        
        # Ollama Model
        print("\nOllama Model:")
        current = self.config.get('OLLAMA_MODEL', 'kimi-k2.5:cloud')
        print(f"Current: {current}")
        
        if yes_no("Change Ollama model?", default=False):
            model = get_input("Enter model name", default=current)
            self.config['OLLAMA_MODEL'] = model
            self.modified = True
            print_success(f"Ollama model changed to: {model}")
        
        # OpenRouter Model
        print("\nOpenRouter Model:")
        current = self.config.get('OPENROUTER_MODEL', 'anthropic/claude-3-sonnet')
        print(f"Current: {current}")
        
        if yes_no("Change OpenRouter model?", default=False):
            model = get_input("Enter model name", default=current)
            self.config['OPENROUTER_MODEL'] = model
            self.modified = True
            print_success(f"OpenRouter model changed to: {model}")
        
        input("\nPress Enter to continue...")
    
    def configure_research(self):
        """Configure research pipeline"""
        clear_screen()
        print_header("Research Pipeline")
        
        # Force update
        current = self.config.get('FORCE_UPDATE', 'false').lower() == 'true'
        print(f"\nForce full regeneration: {current}")
        if yes_no("Change this setting?", default=False):
            force = yes_no("Force full KB regeneration?", default=current)
            self.config['FORCE_UPDATE'] = 'true' if force else 'false'
            self.modified = True
        
        # GitHub repos
        current = self.config.get('FETCH_GITHUB_REPOS', 'true').lower() == 'true'
        print(f"\nFetch GitHub repos: {current}")
        if yes_no("Change this setting?", default=False):
            fetch = yes_no("Fetch from GitHub repos?", default=current)
            self.config['FETCH_GITHUB_REPOS'] = 'true' if fetch else 'false'
            self.modified = True
        
        # GitHub issues
        current = self.config.get('FETCH_GITHUB_ISSUES', 'true').lower() == 'true'
        print(f"\nFetch GitHub issues: {current}")
        if yes_no("Change this setting?", default=False):
            fetch = yes_no("Fetch GitHub issues?", default=current)
            self.config['FETCH_GITHUB_ISSUES'] = 'true' if fetch else 'false'
            self.modified = True
        
        # Web sources
        current = self.config.get('FETCH_WEB_SOURCES', 'true').lower() == 'true'
        print(f"\nFetch web sources: {current}")
        if yes_no("Change this setting?", default=False):
            fetch = yes_no("Fetch from web sources?", default=current)
            self.config['FETCH_WEB_SOURCES'] = 'true' if fetch else 'false'
            self.modified = True
        
        input("\nPress Enter to continue...")
    
    def configure_performance(self):
        """Configure performance settings"""
        clear_screen()
        print_header("Performance & Concurrency")
        
        # Max workers
        current = self.config.get('MAX_WORKERS', '5')
        print(f"\nMaximum workers: {current}")
        if yes_no("Change this setting?", default=False):
            workers = get_input("Max workers (1-20)", default=current)
            try:
                if 1 <= int(workers) <= 20:
                    self.config['MAX_WORKERS'] = workers
                    self.modified = True
                else:
                    print_error("Value must be between 1 and 20")
            except ValueError:
                print_error("Invalid number")
        
        # Request timeout
        current = self.config.get('REQUEST_TIMEOUT', '60')
        print(f"\nRequest timeout: {current}s")
        if yes_no("Change this setting?", default=False):
            timeout = get_input("Timeout in seconds (30-300)", default=current)
            try:
                if 30 <= int(timeout) <= 300:
                    self.config['REQUEST_TIMEOUT'] = timeout
                    self.modified = True
                else:
                    print_error("Value must be between 30 and 300")
            except ValueError:
                print_error("Invalid number")
        
        # Cache duration
        current = self.config.get('CACHE_DURATION', '7')
        print(f"\nCache duration: {current} days")
        if yes_no("Change this setting?", default=False):
            cache = get_input("Cache duration in days (1-30)", default=current)
            try:
                if 1 <= int(cache) <= 30:
                    self.config['CACHE_DURATION'] = cache
                    self.modified = True
                else:
                    print_error("Value must be between 1 and 30")
            except ValueError:
                print_error("Invalid number")
        
        input("\nPress Enter to continue...")
    
    def configure_logging(self):
        """Configure logging settings"""
        clear_screen()
        print_header("Logging & Monitoring")
        
        # Log level
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        current = self.config.get('LOG_LEVEL', 'INFO')
        print(f"\nLog level: {current}")
        
        if yes_no("Change log level?", default=False):
            try:
                default_idx = levels.index(current)
            except ValueError:
                default_idx = 1
            choice = get_choice("Select log level:", levels)
            self.config['LOG_LEVEL'] = levels[choice]
            self.modified = True
            print_success(f"Log level changed to: {levels[choice]}")
        
        # Metrics
        current = self.config.get('ENABLE_METRICS', 'false').lower() == 'true'
        print(f"\nMetrics enabled: {current}")
        if yes_no("Change this setting?", default=False):
            enable = yes_no("Enable metrics?", default=current)
            self.config['ENABLE_METRICS'] = 'true' if enable else 'false'
            self.modified = True
            
            if enable:
                port = get_input("Metrics port", default=self.config.get('METRICS_PORT', '9091'))
                self.config['METRICS_PORT'] = port
        
        input("\nPress Enter to continue...")
    
    def configure_optional(self):
        """Configure optional features"""
        clear_screen()
        print_header("Optional Features")
        
        # Docker
        current = self.config.get('COMPOSE_PROJECT_NAME', '')
        print(f"\nDocker project: {current if current else 'Not configured'}")
        if yes_no("Configure Docker?", default=False):
            name = get_input("Docker project name", default=current if current else 'browseros-kb')
            self.config['COMPOSE_PROJECT_NAME'] = name
            self.modified = True
        
        # Encryption
        current = self.config.get('ENCRYPTION_KEY', '')
        print(f"\nEncryption: {'Enabled' if current else 'Disabled'}")
        if yes_no("Configure encryption?", default=False):
            if current:
                if yes_no("Remove encryption key?", default=False):
                    self.config['ENCRYPTION_KEY'] = ''
                    self.modified = True
                    print_info("Encryption disabled")
            else:
                key = get_input("Enter encryption key (min 32 chars)", default="")
                if len(key) >= 32:
                    self.config['ENCRYPTION_KEY'] = key
                    self.modified = True
                    print_success("Encryption enabled")
                else:
                    print_error("Key too short")
        
        input("\nPress Enter to continue...")
    
    def view_configuration(self):
        """View current configuration"""
        clear_screen()
        print_header("Current Configuration")
        
        print("\nAgent Settings:")
        print(f"  Agent Mode:        {self.config.get('AGENT_MODE', 'Not set')}")
        print(f"  Ollama Mode:       {self.config.get('OLLAMA_MODE', 'Not set')}")
        print(f"  OpenRouter Mode:   {self.config.get('OPENROUTER_MODE', 'Not set')}")
        
        print("\nAPI Keys:")
        print(f"  Ollama:            {'✓ Set' if self.config.get('OLLAMA_API_KEY') else '✗ Not set'}")
        print(f"  OpenRouter:        {'✓ Set' if self.config.get('OPENROUTER_API_KEY') else '✗ Not set'}")
        print(f"  GitHub:            {'✓ Set' if self.config.get('GITHUB_TOKEN') else '✗ Not set'}")
        
        print("\nModels:")
        print(f"  Ollama:            {self.config.get('OLLAMA_MODEL', 'Not set')}")
        print(f"  OpenRouter:        {self.config.get('OPENROUTER_MODEL', 'Not set')}")
        
        print("\nResearch:")
        print(f"  Force Update:      {self.config.get('FORCE_UPDATE', 'false')}")
        print(f"  GitHub Repos:      {self.config.get('FETCH_GITHUB_REPOS', 'true')}")
        print(f"  GitHub Issues:     {self.config.get('FETCH_GITHUB_ISSUES', 'true')}")
        print(f"  Web Sources:       {self.config.get('FETCH_WEB_SOURCES', 'true')}")
        
        print("\nPerformance:")
        print(f"  Max Workers:       {self.config.get('MAX_WORKERS', '5')}")
        print(f"  Timeout:           {self.config.get('REQUEST_TIMEOUT', '60')}s")
        print(f"  Cache Duration:    {self.config.get('CACHE_DURATION', '7')} days")
        
        print("\nLogging:")
        print(f"  Log Level:         {self.config.get('LOG_LEVEL', 'INFO')}")
        print(f"  Metrics:           {self.config.get('ENABLE_METRICS', 'false')}")
        
        print(f"\nConfiguration file: {self.env_file}")
        print(f"Total settings: {len(self.config)}")
        
        input("\nPress Enter to continue...")
    
    def reset_config(self):
        """Reset configuration to defaults"""
        clear_screen()
        print_header("Reset Configuration")
        
        print_warning("This will reset ALL configuration to defaults!")
        print_warning("Your API keys and custom settings will be lost!")
        
        if not yes_no("\nAre you sure you want to reset?", default=False):
            return
        
        if not yes_no("Really reset? This cannot be undone!", default=False):
            return
        
        # Copy template
        template = Path('.env.template')
        if template.exists():
            shutil.copy(template, self.env_file)
            self.load_config()
            self.modified = False
            print_success("Configuration reset to defaults")
        else:
            print_error(".env.template not found")
        
        input("\nPress Enter to continue...")
    
    def exit_manager(self):
        """Exit configuration manager"""
        if self.modified:
            print_warning("\nYou have unsaved changes!")
            if yes_no("Save before exiting?", default=True):
                self.save_config()
        
        print_success("\nExiting configuration manager")
        sys.exit(0)

def main():
    """Main entry point"""
    try:
        manager = ConfigManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
