#!/bin/bash
# ============================================================================
# BrowserOS Knowledge Base - Unix Installation Script
# ============================================================================
# Works on: macOS, Linux (Ubuntu/Debian/CentOS/Fedora/Arch)
# Phase 8 Enhanced: Rollback, Progress Tracking, Better Error Messages
# ============================================================================

set -e  # Exit on error

# Configuration
STATE_FILE=".installation_state"
BACKUP_DIR=".install_backups"
REQUIREMENTS_BACKUP="${BACKUP_DIR}/requirements.txt.backup"
ENV_BACKUP="${BACKUP_DIR}/.env.backup"
MIN_DISK_SPACE_MB=500

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Functions
# ============================================================================

print_header() {
    echo -e "${BLUE}================================================================================${NC}"
    echo -e "${BLUE}   $1${NC}"
    echo -e "${BLUE}================================================================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Save installation state
save_state() {
    echo "$1" > "$STATE_FILE"
    echo "[STATE] Saved: $1"
}

# Load last state
load_state() {
    if [ -f "$STATE_FILE" ]; then
        LAST_STATE=$(cat "$STATE_FILE")
        echo
        print_info "Previous installation detected: $LAST_STATE"
        read -p "Resume from this step? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            rm -f "$STATE_FILE"
            LAST_STATE=""
        fi
    fi
}

# Create backup
create_backup() {
    mkdir -p "$BACKUP_DIR"
    
    if [ -f requirements.txt ]; then
        cp requirements.txt "$REQUIREMENTS_BACKUP" 2>/dev/null || {
            print_warning "Could not backup requirements.txt"
        }
        [ -f "$REQUIREMENTS_BACKUP" ] && echo "[BACKUP] Created requirements.txt backup"
    fi
    
    if [ -f .env ]; then
        cp .env "$ENV_BACKUP" 2>/dev/null
        [ -f "$ENV_BACKUP" ] && echo "[BACKUP] Created .env backup"
    fi
}

# Restore from backup
restore_backup() {
    echo
    print_warning "[ROLLBACK] Restoring from backup..."
    
    if [ -f "$REQUIREMENTS_BACKUP" ]; then
        cp "$REQUIREMENTS_BACKUP" requirements.txt 2>/dev/null
        [ $? -eq 0 ] && echo "[ROLLBACK] Restored requirements.txt"
    fi
    
    if [ -f "$ENV_BACKUP" ]; then
        cp "$ENV_BACKUP" .env 2>/dev/null
        [ $? -eq 0 ] && echo "[ROLLBACK] Restored .env"
    fi
}

# Check disk space
check_disk_space() {
    print_info "Checking disk space..."
    
    if command -v df &> /dev/null; then
        FREE_MB=$(df -m . | awk 'NR==2 {print $4}')
        
        if [ "$FREE_MB" -lt "$MIN_DISK_SPACE_MB" ]; then
            echo
            print_error "Insufficient disk space"
            echo "  Required: ${MIN_DISK_SPACE_MB} MB"
            echo "  Available: ${FREE_MB} MB"
            echo
            echo "NEXT STEPS:"
            echo "  1. Free up at least ${MIN_DISK_SPACE_MB} MB of disk space"
            echo "  2. Run this installer again"
            echo "  3. Consider moving installation to a location with more space"
            echo
            return 1
        fi
        print_success "Sufficient disk space (${FREE_MB} MB available)"
    else
        print_warning "Could not check disk space (df command not available)"
    fi
    return 0
}

# Check internet connectivity
check_internet() {
    print_info "Checking internet connectivity..."
    
    if ping -c 1 8.8.8.8 &> /dev/null || ping -c 1 1.1.1.1 &> /dev/null; then
        print_success "Internet connection available"
        return 0
    else
        echo
        print_warning "No internet connection detected"
        echo
        echo "NEXT STEPS:"
        echo "  1. Check your network connection"
        echo "  2. Verify firewall settings"
        echo "  3. If behind a proxy, configure environment:"
        echo "     export HTTP_PROXY=http://proxy:port"
        echo "     export HTTPS_PROXY=https://proxy:port"
        echo
        read -p "Press Enter to continue anyway or Ctrl+C to cancel..."
    fi
    return 0
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
        # Detect Linux distribution
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$ID
        fi
    else
        OS="Unknown"
    fi
}

# Main installation
main() {
    clear
    print_header "BrowserOS Knowledge Base - Installation Script"
    
    echo "This script will:"
    echo "  1. Check system requirements (Python 3.11+, Node.js 14+, Git)"
    echo "  2. Validate prerequisites (disk space, internet)"
    echo "  3. Create backups for rollback capability"
    echo "  4. Install Python dependencies"
    echo "  5. Install Node.js dependencies"
    echo "  6. Create configuration directory structure"
    echo "  7. Launch the interactive setup wizard"
    echo
    echo "Enhanced Features:"
    echo "  - Automatic rollback on failure"
    echo "  - Progress tracking and resume capability"
    echo "  - Comprehensive error messages with solutions"
    echo
    echo "Press Enter to continue or Ctrl+C to cancel..."
    read

    # Check for resume
    load_state
    
    # Create backup directory and backups
    create_backup

    # ============================================================================
    # Prerequisites Check
    # ============================================================================
    echo
    echo "[0/9] Checking prerequisites..."
    
    # Detect operating system
    detect_os
    print_info "Detected OS: $OS"
    if [ "$OS" == "Linux" ]; then
        print_info "Distribution: ${DISTRO:-Unknown}"
    fi
    echo
    
    # Check disk space
    if ! check_disk_space; then
        exit 1
    fi
    
    # Check internet connectivity
    check_internet
    
    save_state "prerequisites_checked"

    # ============================================================================
    # Check Python installation
    # ============================================================================
    echo
    echo "[1/9] Checking Python installation..."
    
    if [ "$LAST_STATE" != "python_checked" ] && [ "$LAST_STATE" != "pip_checked" ] && \
       [ "$LAST_STATE" != "dependencies_installed" ] && [ "$LAST_STATE" != "node_dependencies_installed" ] && \
       [ "$LAST_STATE" != "directories_created" ] && [ "$LAST_STATE" != "env_configured" ] && \
       [ "$LAST_STATE" != "setup_complete" ]; then
        
        if command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
        elif command -v python &> /dev/null; then
            PYTHON_CMD="python"
        else
            print_error "Python is not installed or not in PATH"
            echo
            echo "NEXT STEPS TO INSTALL PYTHON:"
            if [ "$OS" == "macOS" ]; then
                echo "  Option 1: brew install python@3.11"
                echo "  Option 2: Download from https://www.python.org/downloads/"
                echo
                echo "After installation:"
                echo "  - Restart terminal"
                echo "  - Verify: python3 --version"
                echo "  - Run this installer again"
            elif [ "$OS" == "Linux" ]; then
                case "$DISTRO" in
                    ubuntu|debian)
                        echo "  sudo apt update && sudo apt install python3.11 python3-pip python3-venv"
                        ;;
                    centos|rhel)
                        echo "  sudo yum install python3.11 python3-pip"
                        ;;
                    fedora)
                        echo "  sudo dnf install python3.11 python3-pip"
                        ;;
                    arch)
                        echo "  sudo pacman -S python python-pip"
                        ;;
                    *)
                        echo "  Install Python 3.11+ using your distribution's package manager"
                        ;;
                esac
                echo
                echo "After installation:"
                echo "  - Verify: python3 --version"
                echo "  - Run this installer again"
            fi
            echo
            echo "Documentation: https://docs.python.org/3/using/unix.html"
            echo
            exit 1
        fi

        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
        print_success "Found: Python $PYTHON_VERSION"

        # Check Python version is 3.11+
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]); then
            print_error "Python 3.11+ required, found $PYTHON_VERSION"
            echo
            echo "NEXT STEPS:"
            echo "  1. Install Python 3.11 or higher"
            echo "  2. Update PATH if multiple versions installed"
            echo "  3. Verify with: python3 --version"
            echo "  4. Run this installer again"
            echo
            exit 1
        fi
        print_success "Python version is compatible"
        echo
    fi
    
    save_state "python_checked"

    # ============================================================================
    # Check Node.js installation
    # ============================================================================
    echo
    echo "[2/9] Checking Node.js installation..."
    
    if [ "$LAST_STATE" != "node_checked" ] && [ "$LAST_STATE" != "git_checked" ] && \
       [ "$LAST_STATE" != "pip_checked" ] && [ "$LAST_STATE" != "dependencies_installed" ] && \
       [ "$LAST_STATE" != "node_dependencies_installed" ] && [ "$LAST_STATE" != "directories_created" ] && \
       [ "$LAST_STATE" != "env_configured" ] && [ "$LAST_STATE" != "setup_complete" ]; then
        
        if command -v node &> /dev/null; then
            NODE_VERSION=$(node --version 2>&1 | sed 's/v//')
            print_success "Found: Node.js $NODE_VERSION"
            
            # Check version is 14+
            NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
            if [ "$NODE_MAJOR" -lt 14 ]; then
                print_warning "Node.js 14+ recommended, found v$NODE_VERSION"
                echo
                echo "NEXT STEPS:"
                echo "  1. Update Node.js to version 14 or higher"
                echo "  2. Use nvm (Node Version Manager) for easy version management"
                echo
                echo "IMPACT: Some MCP server features may not work properly"
            fi
        else
            print_warning "Node.js is not installed or not in PATH"
            echo "Node.js is required for the MCP server"
            echo
            echo "NEXT STEPS TO INSTALL NODE.JS:"
            if [ "$OS" == "macOS" ]; then
                echo "  Option 1: brew install node"
                echo "  Option 2: Download from https://nodejs.org/ (LTS recommended)"
                echo "  Option 3: Use nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
            elif [ "$OS" == "Linux" ]; then
                case "$DISTRO" in
                    ubuntu|debian)
                        echo "  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -"
                        echo "  sudo apt install nodejs"
                        ;;
                    centos|rhel)
                        echo "  curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -"
                        echo "  sudo yum install nodejs"
                        ;;
                    fedora)
                        echo "  sudo dnf install nodejs npm"
                        ;;
                    arch)
                        echo "  sudo pacman -S nodejs npm"
                        ;;
                    *)
                        echo "  Install Node.js 14+ using your package manager"
                        echo "  Or use nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
                        ;;
                esac
            fi
            echo
            echo "IMPACT: MCP server will not be available"
            echo
            read -p "Press Enter to continue without Node.js..."
        fi
        echo
    fi
    
    save_state "node_checked"

    # ============================================================================
    # Check Git installation
    # ============================================================================
    echo
    echo "[3/9] Checking Git installation..."
    
    if [ "$LAST_STATE" != "git_checked" ] && [ "$LAST_STATE" != "pip_checked" ] && \
       [ "$LAST_STATE" != "dependencies_installed" ] && [ "$LAST_STATE" != "node_dependencies_installed" ] && \
       [ "$LAST_STATE" != "directories_created" ] && [ "$LAST_STATE" != "env_configured" ] && \
       [ "$LAST_STATE" != "setup_complete" ]; then
        
        if command -v git &> /dev/null; then
            GIT_VERSION=$(git --version | awk '{print $3}')
            print_success "Found: Git $GIT_VERSION"
        else
            print_warning "Git is not installed or not in PATH"
            echo "Git is optional but recommended for version control"
            echo
            echo "NEXT STEPS TO INSTALL GIT:"
            if [ "$OS" == "macOS" ]; then
                echo "  Option 1: brew install git"
                echo "  Option 2: xcode-select --install"
            elif [ "$OS" == "Linux" ]; then
                case "$DISTRO" in
                    ubuntu|debian)
                        echo "  sudo apt install git"
                        ;;
                    centos|rhel)
                        echo "  sudo yum install git"
                        ;;
                    fedora)
                        echo "  sudo dnf install git"
                        ;;
                    arch)
                        echo "  sudo pacman -S git"
                        ;;
                    *)
                        echo "  Install git using your package manager"
                        ;;
                esac
            fi
            echo
            echo "IMPACT: Version control features will not be available"
            echo
            read -p "Press Enter to continue without Git..."
        fi
        echo
    fi
    
    save_state "git_checked"

    # ============================================================================
    # Check pip
    # ============================================================================
    echo
    echo "[4/9] Checking pip installation..."
    
    if [ "$LAST_STATE" != "pip_checked" ] && [ "$LAST_STATE" != "dependencies_installed" ] && \
       [ "$LAST_STATE" != "node_dependencies_installed" ] && [ "$LAST_STATE" != "directories_created" ] && \
       [ "$LAST_STATE" != "env_configured" ] && [ "$LAST_STATE" != "setup_complete" ]; then
        
        if $PYTHON_CMD -m pip --version &> /dev/null; then
            print_success "pip is available"
        else
            print_error "pip is not available"
            echo
            echo "Installing pip..."
            $PYTHON_CMD -m ensurepip --default-pip
            if [ $? -ne 0 ]; then
                print_error "Failed to install pip"
                echo
                echo "NEXT STEPS:"
                echo "  1. Ensure Python was installed correctly"
                echo "  2. Try: $PYTHON_CMD -m ensurepip --upgrade"
                echo "  3. Or download get-pip.py:"
                echo "     curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
                echo "     $PYTHON_CMD get-pip.py"
                echo "  4. Run this installer again"
                echo
                echo "Documentation: https://pip.pypa.io/en/stable/installation/"
                echo
                exit 1
            fi
            print_success "pip installed successfully"
        fi
        echo
    fi
    
    save_state "pip_checked"

    # ============================================================================
    # Install Python dependencies
    # ============================================================================
    echo
    echo "[5/9] Installing Python dependencies..."
    echo "This may take a few minutes..."
    echo

    if [ "$LAST_STATE" != "dependencies_installed" ] && [ "$LAST_STATE" != "node_dependencies_installed" ] && \
       [ "$LAST_STATE" != "directories_created" ] && [ "$LAST_STATE" != "env_configured" ] && \
       [ "$LAST_STATE" != "setup_complete" ]; then

        # Upgrade pip, setuptools, wheel
        $PYTHON_CMD -m pip install --upgrade pip setuptools wheel --quiet
        if [ $? -ne 0 ]; then
            print_error "Failed to upgrade pip"
            echo
            echo "NEXT STEPS:"
            echo "  1. Check internet connection"
            echo "  2. If behind proxy, set environment variables:"
            echo "     export HTTP_PROXY=http://proxy:port"
            echo "     export HTTPS_PROXY=https://proxy:port"
            echo "  3. Try with user install: $PYTHON_CMD -m pip install --upgrade pip --user"
            echo "  4. Clear pip cache: $PYTHON_CMD -m pip cache purge"
            echo "  5. Run this installer again"
            echo
            echo "TROUBLESHOOTING:"
            echo "  - Check firewall/antivirus settings"
            echo "  - Try different network connection"
            echo "  - Verify DNS resolution"
            echo
            restore_backup
            exit 1
        fi

        # Install requirements
        if [ -f requirements.txt ]; then
            $PYTHON_CMD -m pip install -r requirements.txt
            if [ $? -ne 0 ]; then
                print_error "Failed to install dependencies"
                echo
                echo "NEXT STEPS:"
                echo "  1. Check your internet connection"
                echo "  2. Verify requirements.txt is not corrupted: cat requirements.txt"
                echo "  3. Try with user install: $PYTHON_CMD -m pip install -r requirements.txt --user"
                echo "  4. Check for conflicts: $PYTHON_CMD -m pip check"
                echo "  5. Run this installer again"
                echo
                echo "COMMON ISSUES:"
                echo "  - Permission denied: Use --user flag or run with sudo (not recommended)"
                echo "  - SSL errors: $PYTHON_CMD -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt"
                echo "  - Timeout: Increase timeout with --timeout 300"
                echo "  - Build failures: Install build tools for your distribution"
                echo
                echo "Documentation: https://pip.pypa.io/en/stable/user_guide/"
                echo
                restore_backup
                exit 1
            fi
            print_success "All dependencies installed successfully"
        else
            print_error "requirements.txt not found"
            echo
            echo "NEXT STEPS:"
            echo "  1. Verify you are in the repository root directory: pwd"
            echo "  2. Check if file exists: ls -l requirements.txt"
            echo "  3. If missing, clone repository again"
            echo "  4. Run installer from correct directory"
            echo
            restore_backup
            exit 1
        fi
        echo
    fi
    
    save_state "dependencies_installed"

    # ============================================================================
    # Install Node.js dependencies
    # ============================================================================
    echo
    echo "[6/9] Installing Node.js dependencies..."
    
    if [ "$LAST_STATE" != "node_dependencies_installed" ] && [ "$LAST_STATE" != "directories_created" ] && \
       [ "$LAST_STATE" != "env_configured" ] && [ "$LAST_STATE" != "setup_complete" ]; then
        
        if command -v node &> /dev/null && command -v npm &> /dev/null; then
            if [ -f package.json ]; then
                npm install --quiet
                if [ $? -ne 0 ]; then
                    print_warning "Failed to install Node.js dependencies"
                    echo
                    echo "NEXT STEPS:"
                    echo "  1. Check internet connection"
                    echo "  2. Clear cache: npm cache clean --force"
                    echo "  3. Remove node_modules: rm -rf node_modules"
                    echo "  4. Try again: npm install"
                    echo "  5. Check npm configuration: npm config list"
                    echo
                    echo "IMPACT: MCP server may not work properly"
                    echo
                    read -p "Press Enter to continue..."
                else
                    print_success "Node.js dependencies installed"
                fi
            else
                print_warning "package.json not found"
            fi
        else
            print_warning "Skipping Node.js dependencies (Node.js not installed)"
        fi
        echo
    fi
    
    save_state "node_dependencies_installed"

    # ============================================================================
    # Create directory structure
    # ============================================================================
    echo
    echo "[7/9] Creating directory structure..."
    
    if [ "$LAST_STATE" != "directories_created" ] && [ "$LAST_STATE" != "env_configured" ] && \
       [ "$LAST_STATE" != "setup_complete" ]; then
        
        mkdir -p logs
        mkdir -p BrowserOS/Research
        mkdir -p BrowserOS/Workflows
        mkdir -p library/templates
        mkdir -p library/schemas
        
        print_success "Directories created"
        echo
    fi
    
    save_state "directories_created"

    # ============================================================================
    # Check/Create .env file
    # ============================================================================
    echo
    echo "[8/9] Checking configuration..."
    
    if [ "$LAST_STATE" != "env_configured" ] && [ "$LAST_STATE" != "setup_complete" ]; then
        
        if [ ! -f .env ]; then
            if [ -f .env.template ]; then
                cp .env.template .env
                print_success "Created .env from template"
                echo "You will configure this in the setup wizard"
            else
                print_warning ".env.template not found"
                echo
                echo "NEXT STEPS:"
                echo "  1. Verify you are in the repository root"
                echo "  2. Check if .env.template exists: ls -l .env.template"
                echo "  3. Clone repository again if file is missing"
                echo
            fi
        else
            print_success "Found existing .env file"
            echo
            echo "Do you want to keep your existing configuration?"
            echo "  y = Keep existing (you can modify it later)"
            echo "  n = Start fresh with setup wizard"
            read -p "Your choice (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Nn]$ ]]; then
                if [ -f .env.template ]; then
                    cp .env.template .env
                    print_success "Reset .env from template"
                fi
            else
                print_success "Keeping existing configuration"
            fi
        fi
        echo
    fi
    
    save_state "env_configured"

    # ============================================================================
    # Installation complete
    # ============================================================================
    print_header "Installation Complete!"
    
    echo
    echo "Next step: Configure your BrowserOS Knowledge Base"
    echo
    echo "The setup wizard will guide you through:"
    echo "  - Agent mode selection"
    echo "  - API key configuration"
    echo "  - Connection settings"
    echo "  - Performance tuning"
    echo "  - And more..."
    echo
    read -p "Press Enter to launch the setup wizard..."

    # Launch setup wizard
    echo
    echo "[9/9] Launching setup wizard..."
    $PYTHON_CMD scripts/setup_wizard.py
    if [ $? -ne 0 ]; then
        echo
        print_error "Setup wizard encountered an error"
        echo
        echo "NEXT STEPS:"
        echo "  1. Check error messages above"
        echo "  2. Verify all dependencies installed correctly: $PYTHON_CMD -m pip list"
        echo "  3. Try running manually: $PYTHON_CMD scripts/setup_wizard.py"
        echo "  4. Check logs in the logs directory"
        echo "  5. Review documentation: README.md"
        echo
        echo "TROUBLESHOOTING:"
        echo "  - Ensure .env file exists: ls -l .env"
        echo "  - Verify Python packages: $PYTHON_CMD -m pip check"
        echo "  - Check for missing files: ls -l scripts/"
        echo
        exit 1
    fi

    save_state "setup_complete"

    echo
    print_header "Setup Complete!"
    
    echo
    echo "SUCCESS! Your BrowserOS Knowledge Base is ready to use."
    echo
    echo "NEXT STEPS:"
    echo "  1. Run: ./run.sh to start the application"
    echo "  2. Review your configuration in: .env"
    echo "  3. Check documentation: README.md"
    echo
    echo "TIPS:"
    echo "  - Backups are stored in: $BACKUP_DIR"
    echo "  - Installation state saved for resume capability"
    echo "  - Run ./install.sh again to update or reconfigure"
    echo
    echo "Need help? Check:"
    echo "  - README.md for usage guide"
    echo "  - QUICKSTART_MCP.md for MCP setup"
    echo "  - TROUBLESHOOTING.md for common issues"
    echo
    
    # Make run.sh executable if it exists
    if [ -f run.sh ]; then
        chmod +x run.sh
        print_success "Made run.sh executable"
    fi
    
    # Clean up state file on successful completion
    rm -f "$STATE_FILE" 2>/dev/null
    
    echo
}

# Run main function
main
