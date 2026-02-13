@echo off
REM ============================================================================
REM BrowserOS Knowledge Base - Windows Installation Script
REM ============================================================================
REM This script installs all dependencies and launches the setup wizard
REM ============================================================================

setlocal enabledelayedexpansion
color 0A

echo ================================================================================
echo    BrowserOS Knowledge Base - Installation Script
echo ================================================================================
echo.
echo This script will:
echo   1. Check system requirements (Python 3.11+, Git)
echo   2. Install Python dependencies
echo   3. Create configuration directory structure
echo   4. Launch the interactive setup wizard
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM ============================================================================
REM Check Python Installation
REM ============================================================================
echo.
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found: Python %PYTHON_VERSION%

REM Check Python version is 3.11+
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)
if %MAJOR% LSS 3 (
    echo ERROR: Python 3.11+ required, found %PYTHON_VERSION%
    pause
    exit /b 1
)
if %MAJOR% EQU 3 if %MINOR% LSS 11 (
    echo ERROR: Python 3.11+ required, found %PYTHON_VERSION%
    pause
    exit /b 1
)
echo OK: Python version is compatible

REM ============================================================================
REM Check Node.js Installation
REM ============================================================================
echo.
echo [2/8] Checking Node.js installation...

where node >nul 2>&1
if errorlevel 1 (
    echo WARNING: Node.js is not installed or not in PATH
    echo Node.js is required for the MCP server
    echo.
    echo Install Node.js 14+:
    echo   Download from: https://nodejs.org/
    echo.
    echo Press any key to continue without Node.js ^(MCP server will not be available^)...
    pause >nul
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    set NODE_VERSION=!NODE_VERSION:v=!
    echo Found: Node.js !NODE_VERSION!
    
    REM Check version is 14+
    for /f "tokens=1 delims=." %%a in ("!NODE_VERSION!") do set NODE_MAJOR=%%a
    if !NODE_MAJOR! LSS 14 (
        echo WARNING: Node.js 14+ recommended, found v!NODE_VERSION!
        echo Some MCP server features may not work properly
    )
)

REM ============================================================================
REM Check Git Installation
REM ============================================================================
echo.
echo [3/8] Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Git is not installed or not in PATH
    echo Git is optional but recommended for version control
    echo.
    echo Download from: https://git-scm.com/download/win
    echo.
    echo Press any key to continue without Git...
    pause >nul
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do set GIT_VERSION=%%i
    echo Found: Git %GIT_VERSION%
)

REM ============================================================================
REM Check pip
REM ============================================================================
echo.
echo [4/8] Checking pip installation...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo.
    echo Installing pip...
    python -m ensurepip --default-pip
    if errorlevel 1 (
        echo ERROR: Failed to install pip
        pause
        exit /b 1
    )
)
echo OK: pip is available

REM ============================================================================
REM Install Python Dependencies
REM ============================================================================
echo.
echo [5/8] Installing Python dependencies...
echo This may take a few minutes...
echo.

python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)

if exist requirements.txt (
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo.
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
    echo OK: All dependencies installed successfully
) else (
    echo ERROR: requirements.txt not found
    echo Please run this script from the repository root directory
    pause
    exit /b 1
)

REM ============================================================================
REM Install Node.js Dependencies
REM ============================================================================
echo.
echo [6/8] Installing Node.js dependencies...

where node >nul 2>&1
if not errorlevel 1 (
    where npm >nul 2>&1
    if not errorlevel 1 (
        if exist package.json (
            npm install
            if errorlevel 1 (
                echo WARNING: Failed to install Node.js dependencies
                echo MCP server may not work properly
            ) else (
                echo OK: Node.js dependencies installed
            )
        ) else (
            echo WARNING: package.json not found
        )
    )
) else (
    echo Skipping Node.js dependencies ^(Node.js not installed^)
)

REM ============================================================================
REM Create Directory Structure
REM ============================================================================
echo.
echo [7/8] Creating directory structure...

if not exist logs mkdir logs
if not exist BrowserOS\Research mkdir BrowserOS\Research
if not exist BrowserOS\Workflows mkdir BrowserOS\Workflows
if not exist library\templates mkdir library\templates
if not exist library\schemas mkdir library\schemas

echo OK: Directories created

REM ============================================================================
REM Check/Create .env file
REM ============================================================================
echo.
echo [8/8] Checking configuration...

if not exist .env (
    if exist .env.template (
        copy .env.template .env >nul
        echo Created .env from template
        echo You will configure this in the setup wizard
    ) else (
        echo WARNING: .env.template not found
    )
) else (
    echo Found existing .env file
    echo.
    echo Do you want to keep your existing configuration?
    echo   Y = Keep existing (you can modify it later)
    echo   N = Start fresh with setup wizard
    choice /C YN /N /M "Your choice (Y/N): "
    if errorlevel 2 (
        if exist .env.template (
            copy .env.template .env >nul
            echo Reset .env from template
        )
    ) else (
        echo Keeping existing configuration
    )
)

REM ============================================================================
REM Installation Complete
REM ============================================================================
echo.
echo ================================================================================
echo    Installation Complete!
echo ================================================================================
echo.
echo Next step: Configure your BrowserOS Knowledge Base
echo.
echo The setup wizard will guide you through:
echo   - Agent mode selection
echo   - API key configuration
echo   - Connection settings
echo   - Performance tuning
echo   - And more...
echo.
echo Press any key to launch the setup wizard...
pause >nul

REM Launch setup wizard
python scripts\setup_wizard.py
if errorlevel 1 (
    echo.
    echo Setup wizard encountered an error
    echo You can run it again later with: python scripts\setup_wizard.py
    pause
    exit /b 1
)

echo.
echo [Setup] Generating initial library artifacts...
python scripts\generate_library.py
if errorlevel 1 (
    echo WARNING: Failed to generate library artifacts
    echo You can run this later from the main menu
)

echo.
echo ================================================================================
echo    Setup Complete!
echo ================================================================================
echo.
echo You can now use run.bat to start the BrowserOS Knowledge Base
echo.
pause
exit /b 0
