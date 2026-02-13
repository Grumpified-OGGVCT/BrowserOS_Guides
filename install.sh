#!/bin/bash
# ============================================================================
# BrowserOS Knowledge Base - Unix Installation Script
# ============================================================================
# Works on: macOS, Linux (Ubuntu/Debian/CentOS/Fedora/Arch)
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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
    echo "  2. Install Python dependencies"
    echo "  3. Install Node.js dependencies"
    echo "  4. Create configuration directory structure"
    echo "  5. Launch the interactive setup wizard"
    echo
    echo "Press Enter to continue or Ctrl+C to cancel..."
    read

    # Detect operating system
    detect_os
    print_info "Detected OS: $OS"
    if [ "$OS" == "Linux" ]; then
        print_info "Distribution: $DISTRO"
    fi
    echo

    # Check Python installation
    echo "[1/8] Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed or not in PATH"
        echo
        echo "Please install Python 3.11 or higher:"
        if [ "$OS" == "macOS" ]; then
            echo "  brew install python@3.11"
            echo "  or download from: https://www.python.org/downloads/"
        elif [ "$OS" == "Linux" ]; then
            echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3.11 python3-pip"
            echo "  CentOS/RHEL: sudo yum install python3.11"
            echo "  Fedora: sudo dnf install python3.11"
            echo "  Arch: sudo pacman -S python"
        fi
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
        exit 1
    fi
    print_success "Python version is compatible"
    echo

    # Check Node.js installation
    echo "[2/8] Checking Node.js installation..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version 2>&1 | sed 's/v//')
        print_success "Found: Node.js $NODE_VERSION"
        
        # Check version is 14+
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
        if [ "$NODE_MAJOR" -lt 14 ]; then
            print_warning "Node.js 14+ recommended, found v$NODE_VERSION"
            echo "Some MCP server features may not work properly"
        fi
    else
        print_warning "Node.js is not installed or not in PATH"
        echo "Node.js is required for the MCP server"
        echo
        echo "Install Node.js 14+:"
        if [ "$OS" == "macOS" ]; then
            echo "  brew install node"
            echo "  or download from: https://nodejs.org/"
        elif [ "$OS" == "Linux" ]; then
            echo "  Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt install nodejs"
            echo "  CentOS/RHEL: curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash - && sudo yum install nodejs"
            echo "  Fedora: sudo dnf install nodejs"
            echo "  Arch: sudo pacman -S nodejs npm"
        fi
        echo
        echo "Press Enter to continue without Node.js (MCP server will not be available)..."
        read
    fi
    echo

    # Check Git installation
    echo "[3/8] Checking Git installation..."
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | awk '{print $3}')
        print_success "Found: Git $GIT_VERSION"
    else
        print_warning "Git is not installed or not in PATH"
        echo "Git is optional but recommended for version control"
        echo
        echo "Install Git:"
        if [ "$OS" == "macOS" ]; then
            echo "  brew install git"
            echo "  or use Xcode: xcode-select --install"
        elif [ "$OS" == "Linux" ]; then
            echo "  Ubuntu/Debian: sudo apt install git"
            echo "  CentOS/RHEL: sudo yum install git"
            echo "  Fedora: sudo dnf install git"
            echo "  Arch: sudo pacman -S git"
        fi
        echo
        echo "Press Enter to continue without Git..."
        read
    fi
    echo

    # Check pip
    echo "[4/8] Checking pip installation..."
    
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        print_success "pip is available"
    else
        print_error "pip is not available"
        echo
        echo "Installing pip..."
        $PYTHON_CMD -m ensurepip --default-pip
        if [ $? -ne 0 ]; then
            print_error "Failed to install pip"
            exit 1
        fi
    fi
    echo

    # Install Python dependencies
    echo "[5/8] Installing Python dependencies..."
    echo "This may take a few minutes..."
    echo

    # Upgrade pip, setuptools, wheel
    $PYTHON_CMD -m pip install --upgrade pip setuptools wheel --quiet
    if [ $? -ne 0 ]; then
        print_error "Failed to upgrade pip"
        exit 1
    fi

    # Install requirements
    if [ -f requirements.txt ]; then
        $PYTHON_CMD -m pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            print_error "Failed to install dependencies"
            echo
            echo "Please check your internet connection and try again"
            exit 1
        fi
        print_success "All dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        echo "Please run this script from the repository root directory"
        exit 1
    fi
    echo

    # Install Node.js dependencies
    echo "[6/8] Installing Node.js dependencies..."
    
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        if [ -f package.json ]; then
            npm install --quiet
            if [ $? -ne 0 ]; then
                print_warning "Failed to install Node.js dependencies"
                echo "MCP server may not work properly"
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

    # Create directory structure
    echo "[7/8] Creating directory structure..."
    
    mkdir -p logs
    mkdir -p BrowserOS/Research
    mkdir -p BrowserOS/Workflows
    mkdir -p library/templates
    mkdir -p library/schemas
    
    print_success "Directories created"
    echo

    # Check/Create .env file
    echo "[8/8] Checking configuration..."
    
    if [ ! -f .env ]; then
        if [ -f .env.template ]; then
            cp .env.template .env
            print_success "Created .env from template"
            echo "You will configure this in the setup wizard"
        else
            print_warning ".env.template not found"
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

    # Installation complete
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
    echo "Press Enter to launch the setup wizard..."
    read

    # Launch setup wizard
    $PYTHON_CMD scripts/setup_wizard.py
    if [ $? -ne 0 ]; then
        echo
        print_error "Setup wizard encountered an error"
        echo "You can run it again later with: python3 scripts/setup_wizard.py"
        exit 1
    fi

    echo
    print_header "Setup Complete!"
    
    echo
    echo "You can now use run.sh to start the BrowserOS Knowledge Base"
    echo
    
    # Make run.sh executable if it exists
    if [ -f run.sh ]; then
        chmod +x run.sh
        print_success "Made run.sh executable"
    fi
    
    echo
}

# Run main function
main
