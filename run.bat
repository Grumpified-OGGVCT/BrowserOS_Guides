@echo off
REM ============================================================================
REM BrowserOS Knowledge Base - Main Execution Script
REM ============================================================================
REM Run after configuration is complete
REM ============================================================================

setlocal enabledelayedexpansion
color 0B

REM ============================================================================
REM Auto-Update Check (runs once at startup)
REM ============================================================================
if not defined UPDATE_CHECKED (
    set UPDATE_CHECKED=1
    echo ================================================================================
    echo    Checking for and installing updates...
    echo ================================================================================
    echo.
    
    python scripts\auto_update.py
    
    if errorlevel 1 (
        echo.
        echo WARNING: Auto-update encountered an issue
        echo The system will continue to run normally
        echo.
        timeout /t 3 >nul
    )
    
    echo.
)

:MAIN_MENU
cls
echo ================================================================================
echo    BrowserOS Knowledge Base - Main Menu
echo ================================================================================
echo.

REM Check if configuration exists
if not exist .env (
    echo ERROR: Configuration not found!
    echo.
    echo Please run the installation and setup first:
    echo   1. Run install.bat to install dependencies
    echo   2. Complete the setup wizard
    echo.
    pause
    exit /b 1
)

REM Display current configuration summary
echo Current Configuration:
echo.
for /f "tokens=1,2 delims==" %%a in ('findstr /v "^#" .env ^| findstr /v "^$"') do (
    set KEY=%%a
    set VALUE=%%b
    
    REM Only show key settings
    if "!KEY!"=="AGENT_MODE" (
        echo   Agent Mode:        !VALUE!
    )
    if "!KEY!"=="LOG_LEVEL" (
        echo   Log Level:         !VALUE!
    )
    if "!KEY!"=="OLLAMA_API_KEY" (
        if not "!VALUE!"=="" (
            echo   Ollama API:        Configured
        ) else (
            echo   Ollama API:        Not set
        )
    )
    if "!KEY!"=="OPENROUTER_API_KEY" (
        if not "!VALUE!"=="" (
            echo   OpenRouter API:    Configured
        ) else (
            echo   OpenRouter API:    Not set
        )
    )
)

echo.
echo ================================================================================
echo.
echo What would you like to do?
echo.
echo   1. Update Knowledge Base (research pipeline)
echo   2. Run Self-Test
echo   3. Generate Workflow
echo   4. Validate Knowledge Base
echo   5. Extract Claude Skills
echo   6. Generate Repository Structure
echo   7. Security Scan
echo   8. Check for and Install System Updates
echo   9. Configure Settings
echo   A. View Documentation
echo   0. Exit
echo.
set /p CHOICE="Enter your choice [0-9,A]: "

if "%CHOICE%"=="1" goto UPDATE_KB
if "%CHOICE%"=="2" goto SELF_TEST
if "%CHOICE%"=="3" goto WORKFLOW_GEN
if "%CHOICE%"=="4" goto VALIDATE_KB
if "%CHOICE%"=="5" goto EXTRACT_SKILLS
if "%CHOICE%"=="6" goto GEN_STRUCTURE
if "%CHOICE%"=="7" goto SECURITY_SCAN
if "%CHOICE%"=="8" goto CHECK_UPDATES
if "%CHOICE%"=="9" goto CONFIGURE
if /i "%CHOICE%"=="A" goto DOCUMENTATION
if "%CHOICE%"=="0" goto EXIT

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto MAIN_MENU

REM ============================================================================
REM Update Knowledge Base
REM ============================================================================
:UPDATE_KB
cls
echo ================================================================================
echo    Update Knowledge Base
echo ================================================================================
echo.
echo This will run the automated research pipeline to update the knowledge base
echo with the latest information from BrowserOS documentation and community.
echo.
echo This may take several minutes depending on your configuration.
echo.
pause

python scripts\research_pipeline.py
if errorlevel 1 (
    echo.
    echo ERROR: Research pipeline failed
    echo Check the logs for details
    pause
) else (
    echo.
    echo SUCCESS: Knowledge Base updated successfully
    pause
)
goto MAIN_MENU

REM ============================================================================
REM Run Self-Test
REM ============================================================================
:SELF_TEST
cls
echo ================================================================================
echo    Self-Test
echo ================================================================================
echo.
echo Running comprehensive self-test to verify system integrity...
echo.

python scripts\self_test.py
if errorlevel 1 (
    echo.
    echo WARNING: Some tests failed
    echo Check the output above for details
    pause
) else (
    echo.
    echo SUCCESS: All tests passed
    pause
)
goto MAIN_MENU

REM ============================================================================
REM Generate Workflow
REM ============================================================================
:WORKFLOW_GEN
cls
echo ================================================================================
echo    Workflow Generator
echo ================================================================================
echo.
echo This tool generates new workflow JSON files using AI.
echo.

set /p DESC="Enter workflow description (or press Enter to skip): "
if "%DESC%"=="" goto MAIN_MENU

python scripts\workflow_generator.py --description "%DESC%"
if errorlevel 1 (
    echo.
    echo ERROR: Workflow generation failed
    pause
) else (
    echo.
    echo SUCCESS: Workflow generated
    pause
)
goto MAIN_MENU

REM ============================================================================
REM Validate Knowledge Base
REM ============================================================================
:VALIDATE_KB
cls
echo ================================================================================
echo    Validate Knowledge Base
echo ================================================================================
echo.
echo Checking knowledge base for completeness and accuracy...
echo.

python scripts\validate_kb.py
if errorlevel 1 (
    echo.
    echo WARNING: Validation issues found
    echo Check the output above for details
    pause
) else (
    echo.
    echo SUCCESS: Knowledge Base is valid
    pause
)
goto MAIN_MENU

REM ============================================================================
REM Extract Claude Skills
REM ============================================================================
:EXTRACT_SKILLS
cls
echo ================================================================================
echo    Extract Claude Skills
echo ================================================================================
echo.
echo Extracting and adapting Claude skills from community repositories...
echo.

python scripts\extract_claude_skills.py
if errorlevel 1 (
    echo.
    echo ERROR: Skill extraction failed
    pause
) else (
    echo.
    echo SUCCESS: Skills extracted
    pause
)
goto MAIN_MENU

REM ============================================================================
REM Generate Repository Structure
REM ============================================================================
:GEN_STRUCTURE
cls
echo ================================================================================
echo    Generate Repository Structure
echo ================================================================================
echo.
echo Generating repo-structure.json for the repository browser...
echo.

python scripts\generate_repo_structure.py
if errorlevel 1 (
    echo.
    echo ERROR: Structure generation failed
    pause
) else (
    echo.
    echo SUCCESS: Repository structure generated
    pause
)
goto MAIN_MENU

REM ============================================================================
REM Security Scan
REM ============================================================================
:SECURITY_SCAN
cls
echo ================================================================================
echo    Security Scanner
echo ================================================================================
echo.
echo Scanning code for potential security vulnerabilities...
echo.

python scripts\security_scanner.py
if errorlevel 1 (
    echo.
    echo WARNING: Security issues found
    echo Check the security report for details
    pause
) else (
    echo.
    echo SUCCESS: No critical security issues found
    pause
)
goto MAIN_MENU

REM ============================================================================
REM Check for System Updates
REM ============================================================================
:CHECK_UPDATES
cls
echo ================================================================================
echo    Check for and Install System Updates
echo ================================================================================
echo.
echo Checking for updates to BrowserOS Knowledge Base from GitHub...
echo Updates will be installed automatically if available.
echo.

python scripts\auto_update.py
if errorlevel 1 (
    echo.
    echo ERROR: Update check failed
    pause
) else (
    echo.
    pause
)
goto MAIN_MENU

REM ============================================================================
REM Configure Settings
REM ============================================================================
:CONFIGURE
cls
echo ================================================================================
echo    Configuration Manager
echo ================================================================================
echo.
echo Launching interactive configuration manager...
echo.
pause

python scripts\config_manager.py
goto MAIN_MENU

REM ============================================================================
REM View Documentation
REM ============================================================================
:DOCUMENTATION
cls
echo ================================================================================
echo    Documentation
echo ================================================================================
echo.
echo Available Documentation:
echo.
echo   README.md                         - Main repository documentation
echo   AUTOMATION_QUICKSTART.md          - Quick start guide for automation
echo   DEPLOYMENT.md                     - Deployment guide
echo   WORKFLOW_TESTING_COMPLETE.md      - Workflow testing documentation
echo   SECURITY-POLICY.md                - Security policy
echo.
echo Documentation is available in the repository root directory.
echo.
echo Opening README.md in your default text editor...
if exist README.md (
    start README.md
) else (
    echo ERROR: README.md not found
)
echo.
pause
goto MAIN_MENU

REM ============================================================================
REM Exit
REM ============================================================================
:EXIT
cls
echo ================================================================================
echo    Exiting BrowserOS Knowledge Base
echo ================================================================================
echo.
echo Thank you for using BrowserOS Knowledge Base!
echo.
echo For issues or questions, visit:
echo   https://github.com/Grumpified-OGGVCT/BrowserOS_Guides
echo.
timeout /t 3
exit /b 0
