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

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import resilience utilities
from utils.resilience import (
    ResilientLogger, validate_api_key, safe_file_read,
    safe_file_write, check_dependencies
)

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

def validate_api_key_format(key: str, provider: str) -> bool:
    """
    Validate API key format with enhanced checks.
    
    Args:
        key: The API key to validate
        provider: Provider name for context
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not key or key == "your-api-key-here" or key.startswith("your-"):
        return False
    
    # Basic length check
    if len(key) < 20:
        return False
    
    # Format validation - alphanumeric, hyphens, underscores, dots
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', key):
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
        self.logger = ResilientLogger(__name__)
        
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
                # Use safe_file_read
                content = safe_file_read(str(self.env_file), logger=self.logger)
                if not content:
                    self.logger.warn("Could not read .env file or file is empty")
                    return
                
                # Parse with validation
                line_num = 0
                for line in content.split('\n'):
                    line_num += 1
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Validate line format
                    if '=' not in line:
                        self.logger.warn(f"Malformed .env entry at line {line_num}: missing '=' separator")
                        continue
                    
                    # Split and validate
                    parts = line.split('=', 1)
                    if len(parts) != 2:
                        self.logger.warn(f"Malformed .env entry at line {line_num}: invalid format")
                        continue
                    
                    key, value = parts[0].strip(), parts[1].strip()
                    
                    # Validate key format (should be uppercase with underscores)
                    if not key or not re.match(r'^[A-Z_][A-Z0-9_]*$', key):
                        self.logger.warn(f"Malformed .env entry at line {line_num}: invalid key format '{key}'")
                        continue
                    
                    self.config[key] = value
                
                print_success(f"Loaded {len(self.config)} configuration values")
                self.logger.info(f"Successfully loaded {len(self.config)} config entries from .env")
            except Exception as e:
                print_warning(f"Could not load existing config: {e}")
                self.logger.error(f"Failed to load .env file: {e}", exc_info=True)
    
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
        print_info("Format: alphanumeric with hyphens/underscores (min 20 chars)")
        print_info("Example: ollama_sk_abc123def456ghi789jkl012mno345pqr")
        current = self.config.get('OLLAMA_API_KEY', '')
        has_valid = validate_api_key_format(current, 'ollama')
        
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
                elif validate_api_key_format(key, 'ollama'):
                    self.config['OLLAMA_API_KEY'] = key
                    print_success("Ollama API key saved")
                    self.logger.info("Ollama API key configured")
                    break
                else:
                    print_error("Invalid API key format. Key must be 20+ chars, alphanumeric with -/_ allowed")
                    self.logger.warn(f"Invalid Ollama API key format provided")
        
        # OpenRouter API Key
        print("\n" + "─" * 40)
        print("OpenRouter API Key:")
        print_info("Format: alphanumeric with hyphens/underscores (min 20 chars)")
        print_info("Example: sk-or-v1-abc123def456ghi789jkl012mno345pqr")
        current = self.config.get('OPENROUTER_API_KEY', '')
        has_valid = validate_api_key_format(current, 'openrouter')
        
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
                elif validate_api_key_format(key, 'openrouter'):
                    self.config['OPENROUTER_API_KEY'] = key
                    print_success("OpenRouter API key saved")
                    self.logger.info("OpenRouter API key configured")
                    break
                else:
                    print_error("Invalid API key format. Key must be 20+ chars, alphanumeric with -/_ allowed")
                    self.logger.warn(f"Invalid OpenRouter API key format provided")
        
        # GitHub Token
        print("\n" + "─" * 40)
        print("GitHub Token:")
        print_info("Format: alphanumeric with hyphens/underscores (min 20 chars)")
        print_info("Example: ghp_abc123def456ghi789jkl012mno345pqr")
        current = self.config.get('GITHUB_TOKEN', '')
        has_valid = validate_api_key_format(current, 'github')
        
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
                elif validate_api_key_format(token, 'github'):
                    self.config['GITHUB_TOKEN'] = token
                    print_success("GitHub token saved")
                    self.logger.info("GitHub token configured")
                    break
                else:
                    print_error("Invalid token format. Key must be 20+ chars, alphanumeric with -/_ allowed")
                    self.logger.warn(f"Invalid GitHub token format provided")
    
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
        """Configure AI models with cascading fallback (Swarm -> FB1 -> FB2)"""
        print_section("Step 4: Tiered Model Selection")
        
        print("""
Select your primary reasoning strategy and cascading fallbacks:

  1. Primary Strategy - Can be 'Swarm Mode' (dynamic routing) or a static model.
  2. First Fallback  - Static model used if primary fails.
  3. Second Fallback - Final static model used if all else fails.

Note: Signify frontier models with size/cloud tags (e.g., ':cloud', ':123b-cloud').
""")
        
        # Swarm Toggle
        print("--- Mode Toggle ---")
        use_swarm = yes_no("Enable Swarm Mode as primary logic?", 
                          default=(self.config.get("USE_SWARM", "true").lower() == "true"))
        self.config["USE_SWARM"] = "true" if use_swarm else "false"
        
        if use_swarm:
            self.config["PRIMARY_MODEL"] = "swarm"
            print_success("Primary strategy: AGENT SWARM")
        else:
            current_p = self.config.get("PRIMARY_MODEL", "glm-5:cloud")
            if current_p == "swarm": current_p = "glm-5:cloud"
            p = get_input("Static Primary Model", default=current_p)
            self.config["PRIMARY_MODEL"] = p
            print_success(f"Primary model: {p}")

        # Fallback 1
        print("\n--- First Fallback (Tier 2/Ollama Cloud) ---")
        current_fb1 = self.config.get("FALLBACK_MODEL_1", "deepseek-v3.2:cloud")
        fb1 = get_input("1st Fallback Model", default=current_fb1)
        self.config["FALLBACK_MODEL_1"] = fb1
        
        # Fallback 2
        print("\n--- Second Fallback (Tier 3/OpenRouter) ---")
        current_fb2 = self.config.get("FALLBACK_MODEL_2", "anthropic/claude-3-sonnet")
        fb2 = get_input("2nd Fallback Model", default=current_fb2)
        self.config["FALLBACK_MODEL_2"] = fb2

        # Support old logic
        self.config["OLLAMA_MODEL"] = self.config["PRIMARY_MODEL"]
        self.config["OPENROUTER_MODEL"] = fb2
        
        print_success("Tiered model routing configured")
    
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
        print_info("Valid range: 1-20 workers")
        workers = get_input("Maximum concurrent workers", default=current)
        try:
            workers_int = int(workers)
            if 1 <= workers_int <= 20:
                self.config['MAX_WORKERS'] = str(workers_int)
                self.logger.info(f"Max workers set to {workers_int}")
            else:
                print_error(f"Value {workers_int} is out of range (1-20)")
                print_warning("Using default: 5")
                self.config['MAX_WORKERS'] = '5'
                self.logger.warn(f"Invalid max workers value {workers_int}, using default")
        except ValueError:
            print_error(f"'{workers}' is not a valid integer")
            print_warning("Using default: 5")
            self.config['MAX_WORKERS'] = '5'
            self.logger.warn(f"Invalid max workers input '{workers}', using default")
        
        # Request timeout
        current = self.config.get('REQUEST_TIMEOUT', '60')
        print_info("Valid range: 30-300 seconds")
        timeout = get_input("Request timeout in seconds", default=current)
        try:
            timeout_int = int(timeout)
            if 30 <= timeout_int <= 300:
                self.config['REQUEST_TIMEOUT'] = str(timeout_int)
                self.logger.info(f"Request timeout set to {timeout_int}s")
            else:
                print_error(f"Value {timeout_int} is out of range (30-300)")
                print_warning("Using default: 60")
                self.config['REQUEST_TIMEOUT'] = '60'
                self.logger.warn(f"Invalid timeout value {timeout_int}, using default")
        except ValueError:
            print_error(f"'{timeout}' is not a valid integer")
            print_warning("Using default: 60")
            self.config['REQUEST_TIMEOUT'] = '60'
            self.logger.warn(f"Invalid timeout input '{timeout}', using default")
        
        # Cache duration
        current = self.config.get('CACHE_DURATION', '7')
        print_info("Valid range: 1-30 days")
        cache = get_input("Cache duration in days", default=current)
        try:
            cache_int = int(cache)
            if 1 <= cache_int <= 30:
                self.config['CACHE_DURATION'] = str(cache_int)
                self.logger.info(f"Cache duration set to {cache_int} days")
            else:
                print_error(f"Value {cache_int} is out of range (1-30)")
                print_warning("Using default: 7")
                self.config['CACHE_DURATION'] = '7'
                self.logger.warn(f"Invalid cache duration value {cache_int}, using default")
        except ValueError:
            print_error(f"'{cache}' is not a valid integer")
            print_warning("Using default: 7")
            self.config['CACHE_DURATION'] = '7'
            self.logger.warn(f"Invalid cache duration input '{cache}', using default")
        
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
            print_info("Valid range: 1024-65535 (ports below 1024 require root)")
            port = get_input("Metrics port", default=current)
            try:
                port_int = int(port)
                if 1 <= port_int <= 65535:
                    self.config['METRICS_PORT'] = str(port_int)
                    if port_int < 1024:
                        print_warning("Port below 1024 may require root/admin privileges")
                    self.logger.info(f"Metrics port set to {port_int}")
                else:
                    print_error(f"Port {port_int} is out of range (1-65535)")
                    print_warning("Using default: 9090")
                    self.config['METRICS_PORT'] = '9090'
                    self.logger.warn(f"Invalid port value {port_int}, using default")
            except ValueError:
                print_error(f"'{port}' is not a valid port number")
                print_warning("Using default: 9090")
                self.config['METRICS_PORT'] = '9090'
                self.logger.warn(f"Invalid port input '{port}', using default")
        
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
                self.logger.info(f"Created backup: {backup}")
            
            # Build configuration content
            content = []
            content.append("# " + "=" * 76)
            content.append("# BrowserOS Knowledge Base - Configuration")
            content.append("# Generated by setup wizard")
            content.append("# " + "=" * 76)
            content.append("")
            
            # Write configuration values
            for key, value in sorted(self.config.items()):
                content.append(f"{key}={value}")
            
            config_text = '\n'.join(content)
            
            # Use safe_file_write
            success = safe_file_write(
                str(self.env_file),
                config_text,
                mode='w',
                encoding='utf-8',
                create_dirs=False,
                logger=self.logger
            )
            
            if success:
                print_success(f"Configuration saved to {self.env_file}")
                self.logger.info(f"Configuration written to {self.env_file}")
            else:
                print_error(f"Failed to save configuration")
                self.logger.error("Failed to write configuration file")
                sys.exit(1)
        except Exception as e:
            print_error(f"Failed to save configuration: {e}")
            self.logger.error(f"Configuration save error: {e}", exc_info=True)
            sys.exit(1)
    
    def validate_configuration(self):
        """Validate the configuration"""
        print_section("Validating Configuration")
        
        issues = []
        warnings = []
        
        # Validate model names are not empty
        primary_model = self.config.get('PRIMARY_MODEL', '')
        if not primary_model or primary_model.strip() == '':
            issues.append("Primary model name is empty")
        
        fallback1 = self.config.get('FALLBACK_MODEL_1', '')
        if not fallback1 or fallback1.strip() == '':
            warnings.append("Fallback model 1 is not set - may have limited failover")
        
        # Validate port numbers
        if self.config.get('ENABLE_METRICS') == 'true':
            try:
                port = int(self.config.get('METRICS_PORT', '9090'))
                if not (1 <= port <= 65535):
                    issues.append(f"Metrics port {port} is out of valid range (1-65535)")
            except ValueError:
                issues.append(f"Metrics port is not a valid number")
        
        # Validate timeout is positive
        try:
            timeout = int(self.config.get('REQUEST_TIMEOUT', '60'))
            if timeout <= 0:
                issues.append(f"Request timeout must be positive, got {timeout}")
        except ValueError:
            issues.append("Request timeout is not a valid number")
        
        # Check API keys
        if not self.config.get('OLLAMA_API_KEY'):
            warnings.append("Ollama API key not set - local features only")
        
        if not self.config.get('OPENROUTER_API_KEY'):
            warnings.append("OpenRouter API key not set - limited AI features")
        
        if not self.config.get('GITHUB_TOKEN'):
            warnings.append("GitHub token not set - public repos only")
        
        # Check Python packages using check_dependencies
        print_info("Checking Python dependencies...")
        critical_deps = ['requests', 'yaml', 'dotenv']
        optional_deps = ['bs4', 'github', 'ollama', 'openai']
        
        critical_installed, critical_missing = check_dependencies(critical_deps, logger=self.logger)
        optional_installed, optional_missing = check_dependencies(optional_deps, logger=self.logger)
        
        if critical_missing:
            issues.append(f"CRITICAL packages missing: {', '.join(critical_missing)}")
            print_error(f"  ✗ Critical dependencies missing: {', '.join(critical_missing)}")
            print_info(f"    Install with: pip install {' '.join(critical_missing)}")
        
        if optional_missing:
            warnings.append(f"Optional packages missing: {', '.join(optional_missing)}")
            print_warning(f"  ⚠ Optional dependencies missing: {', '.join(optional_missing)}")
        
        # Display results
        if issues:
            print_error("\nConfiguration issues found:")
            for issue in issues:
                print(f"  ✗ {issue}")
            self.logger.error(f"Configuration validation failed with {len(issues)} issues")
        
        if warnings:
            print_warning("\nConfiguration warnings:")
            for warning in warnings:
                print(f"  ⚠ {warning}")
            self.logger.warn(f"Configuration has {len(warnings)} warnings")
        
        if not issues and not warnings:
            print_success("Configuration is valid!")
            self.logger.info("Configuration validation passed")
        elif not issues:
            print_success("Configuration is valid (with warnings)")
            self.logger.info("Configuration validation passed with warnings")
        else:
            print_error("\nPlease fix the issues above before proceeding")
            if not yes_no("\nContinue anyway?", default=False):
                self.logger.error("Setup aborted due to validation issues")
                sys.exit(1)
            else:
                self.logger.warn("User chose to continue despite validation issues")
    
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
        # Use logger if wizard was initialized
        try:
            logger = ResilientLogger(__name__)
            logger.error(f"Setup failed with exception: {e}", exc_info=True)
        except Exception:
            # If secondary logging fails, continue with traceback
            pass
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
