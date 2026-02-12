#!/usr/bin/env python3
"""
BrowserOS Knowledge Base - Interactive Setup Wizard
Guides users through complete system configuration
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess

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
    UNDERLINE = '\033[4m'

import subprocess

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

def print_section(text: str):
    """Print a section header"""
    print(f"\n{Colors.OKBLUE}{'─' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'─' * 80}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def get_choice(prompt: str, options: list, default: int = 0) -> int:
    """Get user choice from a list of options"""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        marker = "→" if i == default + 1 else " "
        print(f"  {marker} {i}. {option}")
    
    while True:
        choice = input(f"\nEnter choice [1-{len(options)}]" + 
                      (f" (default: {default + 1})" if default else "") + 
                      ": ").strip()
        if not choice and default >= 0:
            return default
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

def validate_api_key(key: str, provider: str) -> bool:
    """Validate API key format"""
    if not key or key == "your-api-key-here" or key.startswith("your-"):
        return False
    
    # Basic length check
    if len(key) < 20:
        return False
    
    return True

def test_python_imports() -> Dict[str, bool]:
    """Test if required Python packages are installed"""
    packages = {
        'requests': False,
        'yaml': False,
        'dotenv': False,
        'bs4': False,
        'github': False,
        'ollama': False,
        'openai': False
    }
    
    for package in packages:
        try:
            __import__(package)
            packages[package] = True
        except ImportError:
            packages[package] = False
    
    return packages

class SetupWizard:
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.env_file = Path('.env')
        self.repo_root = Path(__file__).parent.parent
        
    def run(self):
        """Run the complete setup wizard"""
        clear_screen()
        self.show_welcome()
        
        # Load existing config if available
        self.load_existing_config()
        
        # Configuration steps
        self.configure_agent_mode()
        self.configure_api_keys()
        self.configure_connection_modes()
        self.configure_models()
        self.configure_research_options()
        self.configure_performance()
        self.configure_logging()
        self.configure_optional_features()
        
        # Save and validate
        self.save_configuration()
        self.validate_configuration()
        self.show_summary()
        
        # Offer to run system
        if yes_no("\nWould you like to launch BrowserOS Knowledge Base now?", default=True):
            self.launch_run_bat()
        else:
            print_info("\nYou can start the system later by running: run.bat")
    
    def show_welcome(self):
        """Display welcome message"""
        print_header("BrowserOS Knowledge Base - Setup Wizard")
        
        print("""
Welcome to the BrowserOS Knowledge Base Setup Wizard!

This wizard will guide you through configuring your installation:

  ✓ Agent Connection Mode (SDK, MCP, HTTP, Docker, Local, Hybrid)
  ✓ API Keys (Ollama Cloud, OpenRouter, GitHub)
  ✓ Connection Settings (endpoints, timeouts, retries)
  ✓ Model Selection (LLM models for analysis)
  ✓ Research Pipeline (sources, AI analysis, caching)
  ✓ Performance Tuning (workers, batch size, concurrency)
  ✓ Logging & Monitoring
  ✓ Optional Features (Docker, MCP, security)

You can always reconfigure later using the config_manager.py tool.
""")
        input("\nPress Enter to continue...")
    
    def load_existing_config(self):
        """Load existing configuration if available"""
        if self.env_file.exists():
            print_section("Loading Existing Configuration")
            print_info(f"Found existing configuration in {self.env_file}")
            
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = value.strip()
                
                print_success(f"Loaded {len(self.config)} configuration values")
            except Exception as e:
                print_warning(f"Could not load existing config: {e}")
    
    def configure_agent_mode(self):
        """Configure agent connection mode"""
        print_section("Step 1: Agent Connection Mode")
        
        print("""
The agent mode determines how the system connects to AI services:

  • SDK     - Use official Python SDK libraries (ollama, openai)
  • MCP     - Model Context Protocol server connection
  • HTTP    - Direct REST API calls (most compatible)
  • LOCAL   - Local execution without external services
  • DOCKER  - Containerized execution with Docker
  • HYBRID  - Automatically try multiple methods (recommended)
""")
        
        modes = ["hybrid", "sdk", "http", "mcp", "local", "docker"]
        current = self.config.get('AGENT_MODE', 'hybrid')
        
        try:
            default_idx = modes.index(current.lower())
        except ValueError:
            default_idx = 0
        
        choice = get_choice("Select agent mode:", 
                          [m.upper() for m in modes],
                          default=default_idx)
        
        self.config['AGENT_MODE'] = modes[choice]
        print_success(f"Agent mode set to: {modes[choice].upper()}")
    
    def configure_api_keys(self):
        """Configure API keys"""
        print_section("Step 2: API Keys Configuration")
        
        print("""
API keys are required for cloud services:

  • Ollama Cloud API Key - For Kimi and other Ollama Cloud models
    Get from: https://ollama.ai/keys

  • OpenRouter API Key - For Claude, GPT-4, and other models
    Get from: https://openrouter.ai/keys

  • GitHub Token - For accessing repositories and issues
    Get from: https://github.com/settings/tokens

Note: You can skip keys and use local mode, but functionality will be limited.
""")
        
        # Ollama API Key
        print("\n" + "─" * 40)
        print("Ollama Cloud API Key:")
        current = self.config.get('OLLAMA_API_KEY', '')
        has_valid = validate_api_key(current, 'ollama')
        
        if has_valid:
            print_success(f"Current key: {current[:10]}...{current[-4:]}")
            if not yes_no("Keep this key?", default=True):
                has_valid = False
        
        if not has_valid:
            while True:
                key = get_input("Enter Ollama API key (or 'skip' to skip)", 
                              default=current if current else "")
                if key.lower() == 'skip':
                    print_warning("Skipping Ollama API key - local features only")
                    self.config['OLLAMA_API_KEY'] = ''
                    break
                elif validate_api_key(key, 'ollama'):
                    self.config['OLLAMA_API_KEY'] = key
                    print_success("Ollama API key saved")
                    break
                else:
                    print_error("Invalid API key format. Please try again or type 'skip'")
        
        # OpenRouter API Key
        print("\n" + "─" * 40)
        print("OpenRouter API Key:")
        current = self.config.get('OPENROUTER_API_KEY', '')
        has_valid = validate_api_key(current, 'openrouter')
        
        if has_valid:
            print_success(f"Current key: {current[:10]}...{current[-4:]}")
            if not yes_no("Keep this key?", default=True):
                has_valid = False
        
        if not has_valid:
            while True:
                key = get_input("Enter OpenRouter API key (or 'skip' to skip)", 
                              default=current if current else "")
                if key.lower() == 'skip':
                    print_warning("Skipping OpenRouter API key")
                    self.config['OPENROUTER_API_KEY'] = ''
                    break
                elif validate_api_key(key, 'openrouter'):
                    self.config['OPENROUTER_API_KEY'] = key
                    print_success("OpenRouter API key saved")
                    break
                else:
                    print_error("Invalid API key format. Please try again or type 'skip'")
        
        # GitHub Token
        print("\n" + "─" * 40)
        print("GitHub Token:")
        current = self.config.get('GITHUB_TOKEN', '')
        has_valid = validate_api_key(current, 'github')
        
        if has_valid:
            print_success(f"Current token: {current[:10]}...{current[-4:]}")
            if not yes_no("Keep this token?", default=True):
                has_valid = False
        
        if not has_valid:
            while True:
                token = get_input("Enter GitHub token (or 'skip' for public access only)", 
                                default=current if current else "")
                if token.lower() == 'skip':
                    print_warning("Skipping GitHub token - public repos only")
                    self.config['GITHUB_TOKEN'] = ''
                    break
                elif validate_api_key(token, 'github'):
                    self.config['GITHUB_TOKEN'] = token
                    print_success("GitHub token saved")
                    break
                else:
                    print_error("Invalid token format. Please try again or type 'skip'")
    
    def configure_connection_modes(self):
        """Configure connection modes for services"""
        print_section("Step 3: Connection Modes")
        
        print("""
Configure how to connect to each service:

  • HTTP   - REST API calls (most reliable, works everywhere)
  • SDK    - Python client libraries (more features, requires packages)
  • MCP    - Model Context Protocol (advanced, requires MCP server)
  • DOCKER - Containerized services (isolated, requires Docker)
  • LOCAL  - Local binary execution (fast, requires local install)
""")
        
        # Ollama Mode
        modes = ["http", "sdk", "mcp", "docker", "local"]
        current = self.config.get('OLLAMA_MODE', 'http')
        try:
            default_idx = modes.index(current.lower())
        except ValueError:
            default_idx = 0
        
        choice = get_choice("Ollama connection mode:", 
                          [m.upper() for m in modes],
                          default=default_idx)
        self.config['OLLAMA_MODE'] = modes[choice]
        
        # OpenRouter Mode
        modes = ["http", "sdk", "mcp"]
        current = self.config.get('OPENROUTER_MODE', 'http')
        try:
            default_idx = modes.index(current.lower())
        except ValueError:
            default_idx = 0
        
        choice = get_choice("OpenRouter connection mode:", 
                          [m.upper() for m in modes],
                          default=default_idx)
        self.config['OPENROUTER_MODE'] = modes[choice]
        
        print_success("Connection modes configured")
    
    def configure_models(self):
        """Configure AI models"""
        print_section("Step 4: Model Selection")
        
        print("""
Select which AI models to use for analysis:

Ollama Cloud Models:
  • kimi-k2.5:cloud - Kimi K2.5 (recommended for workflow validation)
  • llama2 - Meta Llama 2
  • codellama - Code Llama (optimized for code)

OpenRouter Models:
  • anthropic/claude-3-sonnet - Claude 3 Sonnet (recommended)
  • anthropic/claude-3-opus - Claude 3 Opus (most capable)
  • openai/gpt-4-turbo - GPT-4 Turbo
  • meta-llama/llama-3-70b - Llama 3 70B
""")
        
        # Ollama Model
        current = self.config.get('OLLAMA_MODEL', 'kimi-k2.5:cloud')
        model = get_input("Ollama model", default=current)
        self.config['OLLAMA_MODEL'] = model
        
        # OpenRouter Model
        current = self.config.get('OPENROUTER_MODEL', 'anthropic/claude-3-sonnet')
        model = get_input("OpenRouter model", default=current)
        self.config['OPENROUTER_MODEL'] = model
        
        print_success("Models configured")
    
    def configure_research_options(self):
        """Configure research pipeline options"""
        print_section("Step 5: Research Pipeline")
        
        print("""
Configure the automated research pipeline:
""")
        
        # Force update
        current = self.config.get('FORCE_UPDATE', 'false').lower() == 'true'
        force = yes_no("Force full KB regeneration on every run?", default=current)
        self.config['FORCE_UPDATE'] = 'true' if force else 'false'
        
        # Source fetching
        current = self.config.get('FETCH_GITHUB_REPOS', 'true').lower() == 'true'
        fetch_gh = yes_no("Fetch from GitHub repositories?", default=current)
        self.config['FETCH_GITHUB_REPOS'] = 'true' if fetch_gh else 'false'
        
        current = self.config.get('FETCH_GITHUB_ISSUES', 'true').lower() == 'true'
        fetch_issues = yes_no("Fetch GitHub issues and PRs?", default=current)
        self.config['FETCH_GITHUB_ISSUES'] = 'true' if fetch_issues else 'false'
        
        current = self.config.get('FETCH_WEB_SOURCES', 'true').lower() == 'true'
        fetch_web = yes_no("Fetch from web documentation sources?", default=current)
        self.config['FETCH_WEB_SOURCES'] = 'true' if fetch_web else 'false'
        
        print_success("Research pipeline configured")
    
    def configure_performance(self):
        """Configure performance settings"""
        print_section("Step 6: Performance Settings")
        
        print("""
Configure performance and concurrency:
""")
        
        # Max workers
        current = self.config.get('MAX_WORKERS', '5')
        workers = get_input("Maximum concurrent workers (1-20)", default=current)
        try:
            workers_int = int(workers)
            if 1 <= workers_int <= 20:
                self.config['MAX_WORKERS'] = str(workers_int)
            else:
                print_warning("Using default: 5")
                self.config['MAX_WORKERS'] = '5'
        except ValueError:
            print_warning("Using default: 5")
            self.config['MAX_WORKERS'] = '5'
        
        # Request timeout
        current = self.config.get('REQUEST_TIMEOUT', '60')
        timeout = get_input("Request timeout in seconds (30-300)", default=current)
        try:
            timeout_int = int(timeout)
            if 30 <= timeout_int <= 300:
                self.config['REQUEST_TIMEOUT'] = str(timeout_int)
            else:
                print_warning("Using default: 60")
                self.config['REQUEST_TIMEOUT'] = '60'
        except ValueError:
            print_warning("Using default: 60")
            self.config['REQUEST_TIMEOUT'] = '60'
        
        # Cache duration
        current = self.config.get('CACHE_DURATION', '7')
        cache = get_input("Cache duration in days (1-30)", default=current)
        try:
            cache_int = int(cache)
            if 1 <= cache_int <= 30:
                self.config['CACHE_DURATION'] = str(cache_int)
            else:
                print_warning("Using default: 7")
                self.config['CACHE_DURATION'] = '7'
        except ValueError:
            print_warning("Using default: 7")
            self.config['CACHE_DURATION'] = '7'
        
        print_success("Performance settings configured")
    
    def configure_logging(self):
        """Configure logging settings"""
        print_section("Step 7: Logging Configuration")
        
        print("""
Configure logging and monitoring:
""")
        
        # Log level
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        current = self.config.get('LOG_LEVEL', 'INFO')
        try:
            default_idx = levels.index(current.upper())
        except ValueError:
            default_idx = 1
        
        choice = get_choice("Log level:", levels, default=default_idx)
        self.config['LOG_LEVEL'] = levels[choice]
        
        # Metrics
        current = self.config.get('ENABLE_METRICS', 'false').lower() == 'true'
        metrics = yes_no("Enable Prometheus metrics?", default=current)
        self.config['ENABLE_METRICS'] = 'true' if metrics else 'false'
        
        if metrics:
            current = self.config.get('METRICS_PORT', '9090')
            port = get_input("Metrics port", default=current)
            self.config['METRICS_PORT'] = port
        
        print_success("Logging configured")
    
    def configure_optional_features(self):
        """Configure optional features"""
        print_section("Step 8: Optional Features")
        
        print("""
Configure additional features:
""")
        
        # Auto-update mode
        print("Auto-Update Configuration:")
        print("  This controls how the system handles updates on startup.")
        modes = ["auto", "prompt", "disabled"]
        descriptions = [
            "AUTO - Automatically check and install updates (recommended)",
            "PROMPT - Ask before installing updates",
            "DISABLED - Skip update checks entirely"
        ]
        current = self.config.get('AUTO_UPDATE_MODE', 'auto')
        try:
            default_idx = modes.index(current.lower())
        except ValueError:
            default_idx = 0
        
        choice = get_choice("Select auto-update mode:", descriptions, default=default_idx)
        self.config['AUTO_UPDATE_MODE'] = modes[choice]
        print_success(f"Auto-update mode set to: {modes[choice].upper()}")
        
        # Docker
        print("\n" + "─" * 40)
        print("Docker Configuration:")
        current = self.config.get('COMPOSE_PROJECT_NAME', '')
        if current:
            docker_enabled = True
        else:
            docker_enabled = yes_no("Enable Docker support?", default=False)
        
        if docker_enabled:
            current = self.config.get('COMPOSE_PROJECT_NAME', 'browseros-kb')
            name = get_input("Docker project name", default=current)
            self.config['COMPOSE_PROJECT_NAME'] = name
        
        # Encryption
        print("\n" + "─" * 40)
        print("Secrets Encryption:")
        encrypt = yes_no("Enable secrets encryption?", default=False)
        if encrypt:
            print_warning("You will need to provide an encryption key")
            key = get_input("Encryption key (min 32 characters)", default="")
            if len(key) >= 32:
                self.config['ENCRYPTION_KEY'] = key
            else:
                print_error("Key too short, encryption disabled")
        
        print_success("Optional features configured")
    
    def save_configuration(self):
        """Save configuration to .env file"""
        print_section("Saving Configuration")
        
        try:
            # Backup existing file
            if self.env_file.exists():
                backup = self.env_file.with_suffix('.env.backup')
                import shutil
                shutil.copy(self.env_file, backup)
                print_info(f"Backed up existing config to {backup}")
            
            # Write new configuration
            with open(self.env_file, 'w') as f:
                f.write("# " + "=" * 76 + "\n")
                f.write("# BrowserOS Knowledge Base - Configuration\n")
                f.write("# Generated by setup wizard\n")
                f.write("# " + "=" * 76 + "\n\n")
                
                # Write configuration values
                for key, value in sorted(self.config.items()):
                    f.write(f"{key}={value}\n")
            
            print_success(f"Configuration saved to {self.env_file}")
        except Exception as e:
            print_error(f"Failed to save configuration: {e}")
            sys.exit(1)
    
    def validate_configuration(self):
        """Validate the configuration"""
        print_section("Validating Configuration")
        
        issues = []
        warnings = []
        
        # Check API keys
        if not self.config.get('OLLAMA_API_KEY'):
            warnings.append("Ollama API key not set - local features only")
        
        if not self.config.get('OPENROUTER_API_KEY'):
            warnings.append("OpenRouter API key not set - limited AI features")
        
        if not self.config.get('GITHUB_TOKEN'):
            warnings.append("GitHub token not set - public repos only")
        
        # Check Python packages
        print_info("Checking Python dependencies...")
        packages = test_python_imports()
        
        missing = [pkg for pkg, installed in packages.items() if not installed]
        if missing:
            issues.append(f"Missing packages: {', '.join(missing)}")
        
        # Display results
        if issues:
            print_error("\nConfiguration issues found:")
            for issue in issues:
                print(f"  ✗ {issue}")
        
        if warnings:
            print_warning("\nConfiguration warnings:")
            for warning in warnings:
                print(f"  ⚠ {warning}")
        
        if not issues and not warnings:
            print_success("Configuration is valid!")
        elif not issues:
            print_success("Configuration is valid (with warnings)")
        else:
            print_error("\nPlease fix the issues above before proceeding")
            if not yes_no("\nContinue anyway?", default=False):
                sys.exit(1)
    
    def show_summary(self):
        """Show configuration summary"""
        print_section("Configuration Summary")
        
        print(f"""
Agent Mode:        {self.config.get('AGENT_MODE', 'Not set')}
Ollama Mode:       {self.config.get('OLLAMA_MODE', 'Not set')}
OpenRouter Mode:   {self.config.get('OPENROUTER_MODE', 'Not set')}
Ollama Model:      {self.config.get('OLLAMA_MODEL', 'Not set')}
OpenRouter Model:  {self.config.get('OPENROUTER_MODEL', 'Not set')}

API Keys:
  Ollama:          {'✓ Configured' if self.config.get('OLLAMA_API_KEY') else '✗ Not set'}
  OpenRouter:      {'✓ Configured' if self.config.get('OPENROUTER_API_KEY') else '✗ Not set'}
  GitHub:          {'✓ Configured' if self.config.get('GITHUB_TOKEN') else '✗ Not set'}

Research:
  GitHub Repos:    {self.config.get('FETCH_GITHUB_REPOS', 'true')}
  GitHub Issues:   {self.config.get('FETCH_GITHUB_ISSUES', 'true')}
  Web Sources:     {self.config.get('FETCH_WEB_SOURCES', 'true')}

Performance:
  Max Workers:     {self.config.get('MAX_WORKERS', '5')}
  Timeout:         {self.config.get('REQUEST_TIMEOUT', '60')}s
  Cache:           {self.config.get('CACHE_DURATION', '7')} days
  Log Level:       {self.config.get('LOG_LEVEL', 'INFO')}

Configuration saved to: {self.env_file}
""")
        
        print_success("Setup complete!")
        print_info("\nYou can modify this configuration later using: python scripts\\config_manager.py")
    
    def launch_run_bat(self):
        """Launch run.bat"""
        print_section("Launching BrowserOS Knowledge Base")
        
        run_bat = self.repo_root / 'run.bat'
        if run_bat.exists():
            print_info("Starting run.bat...")
            try:
                if os.name == 'nt':
                    subprocess.run([str(run_bat)], check=False)
                else:
                    print_warning("run.bat is for Windows only")
                    print_info("On Unix systems, use: python scripts/research_pipeline.py")
            except Exception as e:
                print_error(f"Failed to launch run.bat: {e}")
        else:
            print_error("run.bat not found!")
            print_info("Please run: python scripts/research_pipeline.py")

def main():
    """Main entry point"""
    try:
        wizard = SetupWizard()
        wizard.run()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nSetup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
