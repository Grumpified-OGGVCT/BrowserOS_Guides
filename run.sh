#!/bin/bash
# ============================================================================
# BrowserOS Knowledge Base - Main Execution Script (Unix)
# ============================================================================
# Works on: macOS, Linux
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}✗ Python not found${NC}"
    exit 1
fi

# Auto-Update Check (runs once per session)
if [ -z "$UPDATE_CHECKED" ]; then
    export UPDATE_CHECKED=1
    echo -e "${BLUE}================================================================================${NC}"
    echo -e "${BLUE}   Checking for and installing updates...${NC}"
    echo -e "${BLUE}================================================================================${NC}"
    echo
    
    $PYTHON_CMD scripts/auto_update.py
    
    if [ $? -ne 0 ]; then
        echo
        echo -e "${YELLOW}⚠ Auto-update encountered an issue${NC}"
        echo "The system will continue to run normally"
        echo
        sleep 3
    fi
    
    echo
fi

# Main Menu Loop
while true; do
    clear
    echo -e "${BLUE}================================================================================${NC}"
    echo -e "${BLUE}   BrowserOS Knowledge Base - Main Menu${NC}"
    echo -e "${BLUE}================================================================================${NC}"
    echo

    # Check if configuration exists
    if [ ! -f .env ]; then
        echo -e "${RED}ERROR: Configuration not found!${NC}"
        echo
        echo "Please run the installation and setup first:"
        echo "  1. Run ./install.sh to install dependencies"
        echo "  2. Complete the setup wizard"
        echo
        read -p "Press Enter to exit..."
        exit 1
    fi

    # Display current configuration summary
    echo "Current Configuration:"
    echo

    # Read key settings from .env
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ $key =~ ^#.*$ ]] && continue
        [[ -z $key ]] && continue
        
        case $key in
            AGENT_MODE)
                echo "  Agent Mode:        $value"
                ;;
            LOG_LEVEL)
                echo "  Log Level:         $value"
                ;;
            OLLAMA_API_KEY)
                if [ -n "$value" ] && [ "$value" != "your-ollama-api-key-here" ]; then
                    echo "  Ollama API:        Configured"
                else
                    echo "  Ollama API:        Not set"
                fi
                ;;
            OPENROUTER_API_KEY)
                if [ -n "$value" ] && [ "$value" != "your-openrouter-api-key-here" ]; then
                    echo "  OpenRouter API:    Configured"
                else
                    echo "  OpenRouter API:    Not set"
                fi
                ;;
        esac
    done < .env

    echo
    echo -e "${BLUE}================================================================================${NC}"
    echo
    echo "What would you like to do?"
    echo
    echo "  1. Configure Settings"
    echo "  2. Check for and Install System Updates"
    echo "  3. Start MCP Server (Port 3100)"
    echo "  4. Launch Watchtower (Evolution Monitor)"
    echo "  5. Update Knowledge Base (research pipeline)"
    echo "  6. Run Self-Test"
    echo "  7. Validate Knowledge Base"
    echo "  8. Generate Library Artifacts"
    echo "  9. Workflow Generator"
    echo "  A. Monitor WhatsApp Integration"
    echo "  B. Build Provenance Index"
    echo "  C. Security Scan"
    echo "  D. Generate Repository Structure"
    echo "  E. Extract Claude Skills"
    echo "  F. View Documentation"
    echo "  0. Exit"
    echo
    read -p "Enter your choice [0-9,A-F]: " CHOICE

    case $CHOICE in
        1)
            # Configure Settings
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Configuration Manager${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Launching interactive configuration manager..."
            echo
            read -p "Press Enter to continue..."

            $PYTHON_CMD scripts/config_manager.py
            if [ $? -ne 0 ]; then
                echo
                echo -e "${RED}✗ ERROR: Configuration manager encountered an error${NC}"
            else
                echo
                echo -e "${GREEN}✓ Configuration updated successfully${NC}"
            fi
            read -p "Press Enter to continue..."
            ;;

        2)
            # Check for System Updates
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Check for and Install System Updates${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Checking for updates to BrowserOS Knowledge Base from GitHub..."
            echo "Updates will be installed automatically if available."
            echo

            $PYTHON_CMD scripts/auto_update.py
            if [ $? -ne 0 ]; then
                echo
                echo -e "${RED}✗ ERROR: Update check failed${NC}"
            else
                echo
            fi
            read -p "Press Enter to continue..."
            ;;

        3)
            # Start MCP Server
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Start MCP Server${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Starting HTTP MCP server on port 3100..."
            echo
            echo "The server will be available at: http://localhost:3100/mcp"
            echo "SSE endpoint for BrowserOS: http://localhost:3100/sse"
            echo "Health check endpoint: http://localhost:3100/health"
            echo
            echo "To connect from BrowserOS:"
            echo "  1. Open BrowserOS"
            echo "  2. Go to Settings → Connected Apps"
            echo "  3. Click 'Add Custom App'"
            echo "  4. Enter URL: http://localhost:3100/sse"
            echo "  5. Name: BrowserOS Knowledge Base"
            echo
            echo "Press Ctrl+C to stop the server"
            echo
            read -p "Press Enter to start..."

            # Check if Node.js is available
            if command -v node &> /dev/null; then
                MCP_SERVER_PORT=3100 node server/mcp-server.js
            else
                echo -e "${RED}✗ ERROR: Node.js not found${NC}"
                echo "Please install Node.js 14+ to run the MCP server"
            fi
            read -p "Press Enter to continue..."
            ;;

        4)
            # Launch Watchtower
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   The Watchtower (Semantic Bridge Monitor)${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Launching Real-time Learning & Healing Monitor..."
            echo "- Monitoring active browser tab"
            echo "- Detecting drift from objective"
            echo "- Capturing autonomous insights for Knowledge Base"
            echo
            read -p "Enter your current research objective: " OBJ
            if [ -z "$OBJ" ]; then
                OBJ="General BrowserOS Research"
            fi

            echo
            echo "Starting Watchtower with Objective: \"$OBJ\""
            echo

            $PYTHON_CMD scripts/semantic_bridge.py --objective "$OBJ"
            if [ $? -ne 0 ]; then
                echo
                echo -e "${RED}✗ ERROR: Watchtower encountered an error${NC}"
            fi
            read -p "Press Enter to continue..."
            ;;

        5)
            # Update Knowledge Base
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Update Knowledge Base${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "This will run the automated research pipeline to update the knowledge base"
            echo "with the latest information from BrowserOS documentation and community."
            echo
            echo "This may take several minutes depending on your configuration."
            echo
            read -p "Press Enter to continue..."

            $PYTHON_CMD scripts/research_pipeline.py
            if [ $? -ne 0 ]; then
                echo
                echo -e "${RED}✗ ERROR: Research pipeline failed${NC}"
                echo "Check the logs for details"
            else
                echo
                echo -e "${GREEN}✓ SUCCESS: Knowledge Base updated successfully${NC}"
            fi
            read -p "Press Enter to continue..."
            ;;

        6)
            # Run Self-Test
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Self-Test${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Running comprehensive self-test to verify system integrity..."
            echo

            $PYTHON_CMD scripts/self_test.py
            if [ $? -ne 0 ]; then
                echo
                echo -e "${YELLOW}⚠ WARNING: Some tests failed${NC}"
                echo "Check the output above for details"
            else
                echo
                echo -e "${GREEN}✓ SUCCESS: All tests passed${NC}"
            fi
            read -p "Press Enter to continue..."
            ;;

        7)
            # Validate Knowledge Base
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Validate Knowledge Base${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Checking knowledge base for completeness and accuracy..."
            echo

            $PYTHON_CMD scripts/validate_kb.py
            if [ $? -ne 0 ]; then
                echo
                echo -e "${YELLOW}⚠ WARNING: Validation issues found${NC}"
                echo "Check the output above for details"
            else
                echo
                echo -e "${GREEN}✓ SUCCESS: Knowledge Base is valid${NC}"
            fi
            read -p "Press Enter to continue..."
            ;;

        8)
            # Generate Library Artifacts
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Generate Library Artifacts${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Generating executable workflow templates and pattern index..."
            echo

            $PYTHON_CMD scripts/generate_library.py
            if [ $? -ne 0 ]; then
                echo
                echo -e "${RED}✗ ERROR: Library generation failed${NC}"
            else
                echo
                echo -e "${GREEN}✓ SUCCESS: Library artifacts generated${NC}"
            fi
            read -p "Press Enter to continue..."
            ;;

        9)
            # Workflow Generator
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Workflow Generator${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "This tool generates new workflow JSON files using AI."
            echo

            read -p "Enter workflow description (or press Enter to skip): " DESC
            if [ -n "$DESC" ]; then
                $PYTHON_CMD scripts/workflow_generator.py full --use-case "$DESC"
                if [ $? -ne 0 ]; then
                    echo
                    echo -e "${RED}✗ ERROR: Workflow generation failed${NC}"
                else
                    echo
                    echo -e "${GREEN}✓ SUCCESS: Workflow generated${NC}"
                fi
            fi
            read -p "Press Enter to continue..."
            ;;

        [Aa])
            # Monitor WhatsApp Integration
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Monitor WhatsApp Integration${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Checking BrowserOS repositories for WhatsApp integration development..."
            echo "This will search for keywords across multiple repositories."
            echo
            read -p "Press Enter to start monitoring..."

            $PYTHON_CMD scripts/monitor_whatsapp.py
            if [ $? -ne 0 ]; then
                echo
                echo -e "${RED}✗ ERROR: Monitoring failed${NC}"
            else
                echo
                echo -e "${GREEN}✓ SUCCESS: Monitoring complete${NC}"
                echo
                echo "Report saved to: WHATSAPP_WATCH_REPORT.md"
            fi
            read -p "Press Enter to continue..."
            ;;

        [Bb])
            # Build Provenance Index
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Build Provenance Index${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Linking KB documentation to BrowserOS source code..."
            echo "This creates forensic traceability for all documented features."
            echo

            $PYTHON_CMD scripts/build_provenance.py
            if [ $? -ne 0 ]; then
                echo
                echo -e "${RED}✗ ERROR: Provenance build failed${NC}"
            else
                echo
                echo -e "${GREEN}✓ SUCCESS: Provenance index built${NC}"
                echo "See: library/provenance_index.json"
            fi
            read -p "Press Enter to continue..."
            ;;

        [Cc])
            # Security Scan
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Security Scanner${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Scanning code for potential security vulnerabilities..."
            echo

            $PYTHON_CMD scripts/security_scanner.py
            if [ $? -ne 0 ]; then
                echo
                echo -e "${YELLOW}⚠ WARNING: Security issues found${NC}"
                echo "Check the security report for details"
            else
                echo
                echo -e "${GREEN}✓ SUCCESS: No critical security issues found${NC}"
            fi
            read -p "Press Enter to continue..."
            ;;

        [Dd])
            # Generate Repository Structure
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Generate Repository Structure${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Generating repo-structure.json for the repository browser..."
            echo

            $PYTHON_CMD scripts/generate_repo_structure.py
            if [ $? -ne 0 ]; then
                echo
                echo -e "${RED}✗ ERROR: Structure generation failed${NC}"
            else
                echo
                echo -e "${GREEN}✓ SUCCESS: Repository structure generated${NC}"
            fi
            read -p "Press Enter to continue..."
            ;;

        [Ee])
            # Extract Claude Skills
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Extract Claude Skills${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Extracting and adapting Claude skills from community repositories..."
            echo

            $PYTHON_CMD scripts/extract_claude_skills.py
            if [ $? -ne 0 ]; then
                echo
                echo -e "${RED}✗ ERROR: Skill extraction failed${NC}"
            else
                echo
                echo -e "${GREEN}✓ SUCCESS: Skills extracted${NC}"
            fi
            read -p "Press Enter to continue..."
            ;;

        [Ff])
            # View Documentation
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Documentation${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Available Documentation:"
            echo
            echo "  README.md                         - Main repository documentation"
            echo "  AUTOMATION_QUICKSTART.md          - Quick start guide for automation"
            echo "  DEPLOYMENT.md                     - Deployment guide"
            echo "  WORKFLOW_TESTING_COMPLETE.md      - Workflow testing documentation"
            echo "  SECURITY-POLICY.md                - Security policy"
            echo "  WINDOWS_SETUP.md                  - Windows setup guide"
            echo "  CROSS_PLATFORM_SETUP.md           - Cross-platform setup guide"
            echo
            echo "Documentation is available in the repository root directory."
            echo
            
            # Try to open README.md with default viewer
            if command -v xdg-open &> /dev/null; then
                echo "Opening README.md with default viewer..."
                xdg-open README.md &
            elif command -v open &> /dev/null; then
                echo "Opening README.md with default viewer..."
                open README.md
            else
                echo "To view documentation, open the files in your preferred text editor"
            fi
            
            echo
            read -p "Press Enter to continue..."
            ;;

        0)
            # Exit
            clear
            echo -e "${BLUE}================================================================================${NC}"
            echo -e "${BLUE}   Exiting BrowserOS Knowledge Base${NC}"
            echo -e "${BLUE}================================================================================${NC}"
            echo
            echo "Thank you for using BrowserOS Knowledge Base!"
            echo
            echo "For issues or questions, visit:"
            echo "  https://github.com/Grumpified-OGGVCT/BrowserOS_Guides"
            echo
            sleep 2
            exit 0
            ;;

        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            sleep 2
            ;;
    esac
done
