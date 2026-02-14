@echo off
REM ============================================================================
REM BrowserOS Knowledge Base - Windows Installation Script
REM ============================================================================
REM This script installs all dependencies and launches the setup wizard
REM Phase 8 Enhanced: Rollback, Progress Tracking, Better Error Messages
REM ============================================================================

setlocal enabledelayedexpansion
color 0A

REM ============================================================================
REM Configuration and State Management
REM ============================================================================
set "STATE_FILE=.installation_state"
set "BACKUP_DIR=.install_backups"
set "REQUIREMENTS_BACKUP=%BACKUP_DIR%\requirements.txt.backup"
set "ENV_BACKUP=%BACKUP_DIR%\.env.backup"
set "MIN_DISK_SPACE_MB=500"

REM ============================================================================
REM Function: Save Installation State
REM ============================================================================
:save_state
    echo %~1 > "%STATE_FILE%"
    echo [STATE] Saved: %~1
    exit /b 0

REM ============================================================================
REM Function: Load Last State
REM ============================================================================
:load_state
    if exist "%STATE_FILE%" (
        set /p LAST_STATE=<"%STATE_FILE%"
        echo.
        echo Previous installation detected: %LAST_STATE%
        echo Do you want to resume from this step?
        choice /C YN /N /M "Resume (Y/N): "
        if errorlevel 2 (
            del "%STATE_FILE%" 2>nul
            set "LAST_STATE="
        )
    )
    exit /b 0

REM ============================================================================
REM Function: Create Backup
REM ============================================================================
:create_backup
    if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
    
    if exist requirements.txt (
        copy /Y requirements.txt "%REQUIREMENTS_BACKUP%" >nul 2>&1
        if errorlevel 1 (
            echo WARNING: Could not backup requirements.txt
        ) else (
            echo [BACKUP] Created requirements.txt backup
        )
    )
    
    if exist .env (
        copy /Y .env "%ENV_BACKUP%" >nul 2>&1
        if not errorlevel 1 (
            echo [BACKUP] Created .env backup
        )
    )
    exit /b 0

REM ============================================================================
REM Function: Restore from Backup
REM ============================================================================
:restore_backup
    echo.
    echo [ROLLBACK] Restoring from backup...
    
    if exist "%REQUIREMENTS_BACKUP%" (
        copy /Y "%REQUIREMENTS_BACKUP%" requirements.txt >nul 2>&1
        if not errorlevel 1 (
            echo [ROLLBACK] Restored requirements.txt
        )
    )
    
    if exist "%ENV_BACKUP%" (
        copy /Y "%ENV_BACKUP%" .env >nul 2>&1
        if not errorlevel 1 (
            echo [ROLLBACK] Restored .env
        )
    )
    exit /b 0

REM ============================================================================
REM Function: Check Disk Space
REM ============================================================================
:check_disk_space
    echo Checking disk space...
    for /f "tokens=3" %%a in ('dir /-c ^| findstr /C:"bytes free"') do set FREE_BYTES=%%a
    set FREE_BYTES=%FREE_BYTES:,=%
    set /a FREE_MB=%FREE_BYTES% / 1048576
    
    if %FREE_MB% LSS %MIN_DISK_SPACE_MB% (
        echo.
        echo ERROR: Insufficient disk space
        echo   Required: %MIN_DISK_SPACE_MB% MB
        echo   Available: %FREE_MB% MB
        echo.
        echo NEXT STEPS:
        echo   1. Free up at least %MIN_DISK_SPACE_MB% MB of disk space
        echo   2. Run this installer again
        echo   3. Consider moving installation to a drive with more space
        echo.
        exit /b 1
    )
    echo OK: Sufficient disk space (%FREE_MB% MB available)
    exit /b 0

REM ============================================================================
REM Function: Check Internet Connectivity
REM ============================================================================
:check_internet
    echo Checking internet connectivity...
    ping -n 1 8.8.8.8 >nul 2>&1
    if errorlevel 1 (
        ping -n 1 1.1.1.1 >nul 2>&1
        if errorlevel 1 (
            echo.
            echo WARNING: No internet connection detected
            echo.
            echo NEXT STEPS:
            echo   1. Check your network connection
            echo   2. Verify firewall settings
            echo   3. If behind a proxy, configure pip proxy settings
            echo      Example: set HTTP_PROXY=http://proxy:port
            echo.
            echo Press any key to continue anyway or Ctrl+C to cancel...
            pause >nul
            exit /b 0
        )
    )
    echo OK: Internet connection available
    exit /b 0

REM ============================================================================
REM Main Installation
REM ============================================================================

echo ================================================================================
echo    BrowserOS Knowledge Base - Installation Script
echo ================================================================================
echo.
echo This script will:
echo   1. Check system requirements (Python 3.11+, Git)
echo   2. Validate prerequisites (disk space, internet)
echo   3. Create backups for rollback capability
echo   4. Install Python dependencies
echo   5. Create configuration directory structure
echo   6. Launch the interactive setup wizard
echo.
echo Enhanced Features:
echo   - Automatic rollback on failure
echo   - Progress tracking and resume capability
echo   - Comprehensive error messages with solutions
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Check for resume
call :load_state

REM Create backup directory and backups
call :create_backup

REM ============================================================================
REM Prerequisites Check
REM ============================================================================
echo.
echo [0/9] Checking prerequisites...

REM Check disk space
call :check_disk_space
if errorlevel 1 (
    pause
    exit /b 1
)

REM Check internet connectivity
call :check_internet

call :save_state "prerequisites_checked"

REM ============================================================================
REM Check Python Installation
REM ============================================================================
echo.
echo [1/9] Checking Python installation...

REM Resume logic: Skip this step only if LAST_STATE is exactly this checkpoint
REM Note: Steps before LAST_STATE will re-run (safe but redundant)
if defined LAST_STATE if "%LAST_STATE%"=="python_checked" goto skip_python_check

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo NEXT STEPS:
    echo   1. Download Python 3.11+ from: https://www.python.org/downloads/
    echo   2. Run the installer and CHECK "Add Python to PATH"
    echo   3. Restart your command prompt
    echo   4. Run this installer again
    echo.
    echo TROUBLESHOOTING:
    echo   - If already installed, add to PATH manually:
    echo     System Properties ^> Environment Variables ^> Path ^> Add Python directory
    echo   - Verify installation: python --version
    echo.
    echo Documentation: https://docs.python.org/3/using/windows.html
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
    echo.
    echo NEXT STEPS:
    echo   1. Uninstall current Python version
    echo   2. Download Python 3.11+ from: https://www.python.org/downloads/
    echo   3. Install with "Add to PATH" checked
    echo   4. Run this installer again
    echo.
    pause
    exit /b 1
)
if %MAJOR% EQU 3 if %MINOR% LSS 11 (
    echo ERROR: Python 3.11+ required, found %PYTHON_VERSION%
    echo.
    echo NEXT STEPS:
    echo   1. Download Python 3.11+ from: https://www.python.org/downloads/
    echo   2. Install alongside current version
    echo   3. Update PATH to use Python 3.11+
    echo   4. Run this installer again
    echo.
    pause
    exit /b 1
)
echo OK: Python version is compatible

:skip_python_check
call :save_state "python_checked"

REM ============================================================================
REM Check Node.js Installation
REM ============================================================================
echo.
echo [2/9] Checking Node.js installation...

if defined LAST_STATE if "%LAST_STATE%"=="node_checked" goto skip_node_check

where node >nul 2>&1
if errorlevel 1 (
    echo WARNING: Node.js is not installed or not in PATH
    echo Node.js is required for the MCP server
    echo.
    echo NEXT STEPS TO INSTALL NODE.JS:
    echo   1. Download from: https://nodejs.org/ (LTS version recommended)
    echo   2. Run installer with default settings
    echo   3. Restart command prompt
    echo   4. Optional: Run this installer again to complete Node.js setup
    echo.
    echo IMPACT: MCP server features will not be available
    echo.
    echo Press any key to continue without Node.js...
    pause >nul
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    set NODE_VERSION=!NODE_VERSION:v=!
    echo Found: Node.js !NODE_VERSION!
    
    REM Check version is 14+
    for /f "tokens=1 delims=." %%a in ("!NODE_VERSION!") do set NODE_MAJOR=%%a
    if !NODE_MAJOR! LSS 14 (
        echo WARNING: Node.js 14+ recommended, found v!NODE_VERSION!
        echo.
        echo NEXT STEPS:
        echo   1. Update Node.js from: https://nodejs.org/
        echo   2. Choose LTS (Long Term Support) version
        echo.
        echo IMPACT: Some MCP server features may not work properly
    )
)

:skip_node_check
call :save_state "node_checked"

REM ============================================================================
REM Check Git Installation
REM ============================================================================
echo.
echo [3/9] Checking Git installation...

if defined LAST_STATE if "%LAST_STATE%"=="git_checked" goto skip_git_check

git --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Git is not installed or not in PATH
    echo Git is optional but recommended for version control
    echo.
    echo NEXT STEPS TO INSTALL GIT:
    echo   1. Download from: https://git-scm.com/download/win
    echo   2. Install with default settings
    echo   3. Restart command prompt
    echo.
    echo IMPACT: Version control features will not be available
    echo.
    echo Press any key to continue without Git...
    pause >nul
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do set GIT_VERSION=%%i
    echo Found: Git %GIT_VERSION%
)

:skip_git_check
call :save_state "git_checked"

REM ============================================================================
REM Check pip
REM ============================================================================
echo.
echo [4/9] Checking pip installation...

if defined LAST_STATE if "%LAST_STATE%"=="pip_checked" goto skip_pip_check

python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: pip is not available
    echo.
    echo Installing pip...
    python -m ensurepip --default-pip
    if errorlevel 1 (
        echo ERROR: Failed to install pip
        echo.
        echo NEXT STEPS:
        echo   1. Ensure Python was installed correctly
        echo   2. Try: python -m ensurepip --upgrade
        echo   3. Or download get-pip.py from: https://bootstrap.pypa.io/get-pip.py
        echo      Then run: python get-pip.py
        echo   4. Run this installer again
        echo.
        echo Documentation: https://pip.pypa.io/en/stable/installation/
        echo.
        pause
        exit /b 1
    )
)
echo OK: pip is available

:skip_pip_check
call :save_state "pip_checked"

REM ============================================================================
REM Install Python Dependencies
REM ============================================================================
echo.
echo [5/9] Installing Python dependencies...
echo This may take a few minutes...
echo.

if defined LAST_STATE if "%LAST_STATE%"=="dependencies_installed" goto skip_dependencies

python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    echo.
    echo NEXT STEPS:
    echo   1. Check internet connection
    echo   2. If behind proxy, set: set HTTP_PROXY=http://proxy:port
    echo   3. Try: python -m pip install --upgrade pip --user
    echo   4. Clear pip cache: python -m pip cache purge
    echo   5. Run this installer again
    echo.
    echo TROUBLESHOOTING:
    echo   - Disable antivirus temporarily
    echo   - Check firewall settings
    echo   - Try different network connection
    echo.
    call :restore_backup
    pause
    exit /b 1
)

if exist requirements.txt (
    echo Installing from requirements.txt...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo.
        echo NEXT STEPS:
        echo   1. Check your internet connection
        echo   2. Verify requirements.txt is not corrupted
        echo   3. Try installing with: python -m pip install -r requirements.txt --user
        echo   4. Check for conflicting packages: python -m pip check
        echo   5. Run this installer again
        echo.
        echo COMMON ISSUES:
        echo   - Permission denied: Run as Administrator or use --user flag
        echo   - SSL errors: python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
        echo   - Timeout: Increase timeout with --timeout 300
        echo.
        echo Documentation: https://pip.pypa.io/en/stable/
        echo.
        call :restore_backup
        pause
        exit /b 1
    )
    echo OK: All dependencies installed successfully
) else (
    echo ERROR: requirements.txt not found
    echo.
    echo NEXT STEPS:
    echo   1. Verify you are in the repository root directory
    echo   2. Check if requirements.txt exists: dir requirements.txt
    echo   3. If missing, clone repository again
    echo   4. Run this installer from the correct directory
    echo.
    call :restore_backup
    pause
    exit /b 1
)

:skip_dependencies
call :save_state "dependencies_installed"

REM ============================================================================
REM Install Node.js Dependencies
REM ============================================================================
echo.
echo [6/9] Installing Node.js dependencies...

if defined LAST_STATE if "%LAST_STATE%"=="node_dependencies_installed" goto skip_node_dependencies

where node >nul 2>&1
if not errorlevel 1 (
    where npm >nul 2>&1
    if not errorlevel 1 (
        if exist package.json (
            npm install
            if errorlevel 1 (
                echo WARNING: Failed to install Node.js dependencies
                echo.
                echo NEXT STEPS:
                echo   1. Check internet connection
                echo   2. Try: npm cache clean --force
                echo   3. Delete node_modules folder and try again
                echo   4. Check npm configuration: npm config list
                echo.
                echo IMPACT: MCP server may not work properly
                echo.
                echo Press any key to continue...
                pause >nul
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

:skip_node_dependencies
call :save_state "node_dependencies_installed"

REM ============================================================================
REM Create Directory Structure
REM ============================================================================
echo.
echo [7/9] Creating directory structure...

if defined LAST_STATE if "%LAST_STATE%"=="directories_created" goto skip_directories

if not exist logs mkdir logs
if not exist BrowserOS\Research mkdir BrowserOS\Research
if not exist BrowserOS\Workflows mkdir BrowserOS\Workflows
if not exist library\templates mkdir library\templates
if not exist library\schemas mkdir library\schemas

echo OK: Directories created

:skip_directories
call :save_state "directories_created"

REM ============================================================================
REM Check/Create .env file
REM ============================================================================
echo.
echo [8/9] Checking configuration...

if defined LAST_STATE if "%LAST_STATE%"=="env_configured" goto skip_env_config

if not exist .env (
    if exist .env.template (
        copy .env.template .env >nul
        echo Created .env from template
        echo You will configure this in the setup wizard
    ) else (
        echo WARNING: .env.template not found
        echo.
        echo NEXT STEPS:
        echo   1. Verify you are in the repository root
        echo   2. Check if .env.template exists
        echo   3. Clone repository again if file is missing
        echo.
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

:skip_env_config
call :save_state "env_configured"

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
echo.
echo [9/9] Launching setup wizard...
python scripts\setup_wizard.py
if errorlevel 1 (
    echo.
    echo ERROR: Setup wizard encountered an error
    echo.
    echo NEXT STEPS:
    echo   1. Check error messages above
    echo   2. Verify all dependencies are installed correctly
    echo   3. Try running manually: python scripts\setup_wizard.py
    echo   4. Check logs in the logs directory
    echo   5. Review documentation at: README.md
    echo.
    echo TROUBLESHOOTING:
    echo   - Ensure .env file exists
    echo   - Verify Python packages are installed: python -m pip list
    echo   - Check for missing files in scripts directory
    echo.
    pause
    exit /b 1
)

call :save_state "setup_complete"

echo.
echo [Setup] Generating initial library artifacts...
python scripts\generate_library.py
if errorlevel 1 (
    echo WARNING: Failed to generate library artifacts
    echo You can run this later from the main menu
)

REM Clean up state file on successful completion
if exist "%STATE_FILE%" del "%STATE_FILE%" 2>nul

echo.
echo ================================================================================
echo    Setup Complete!
echo ================================================================================
echo.
echo SUCCESS! Your BrowserOS Knowledge Base is ready to use.
echo.
echo NEXT STEPS:
echo   1. Run: run.bat to start the application
echo   2. Review your configuration in: .env
echo   3. Check documentation: README.md
echo.
echo TIPS:
echo   - Backups are stored in: %BACKUP_DIR%
echo   - Installation state saved for resume capability
echo   - Run install.bat again to update or reconfigure
echo.
echo Need help? Check:
echo   - README.md for usage guide
echo   - QUICKSTART_MCP.md for MCP setup
echo   - TROUBLESHOOTING.md for common issues
echo.
pause
exit /b 0
