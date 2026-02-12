# ============================================================================
# BrowserOS Workflows Knowledge Base Update Script
# ============================================================================
# This script automates the weekly update of the BrowserOS Workflows KB.
# It pulls the latest changes, runs the research pipeline, commits updates,
# and tags the new version.
#
# Schedule this script in Windows Task Scheduler to run weekly.
# ============================================================================

param(
    [string]$RepositoryPath = (Get-Location).Path,
    [switch]$DryRun = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Log function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path "$RepositoryPath/Research/update_kb.log" -Value $logMessage
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

try {
    Write-Log "Starting BrowserOS Knowledge Base update process"
    
    # Step 1: Pull latest changes from remote
    Write-Log "Pulling latest changes from Git repository..."
    Push-Location $RepositoryPath
    
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Log "Uncommitted changes detected. Stashing..." "WARN"
        git stash save "Auto-stash before KB update $(Get-Date -Format 'yyyy-MM-dd-HHmmss')"
    }
    
    git pull origin main
    if ($LASTEXITCODE -ne 0) {
        throw "Git pull failed with exit code $LASTEXITCODE"
    }
    Write-Log "Successfully pulled latest changes"
    
    # Step 2: Clone/update official BrowserOS repository for research
    $browserOSRepoPath = "$RepositoryPath/Research/raw/browseros-ai-BrowserOS"
    Write-Log "Syncing official BrowserOS repository..."
    
    if (Test-Path $browserOSRepoPath) {
        Write-Log "Updating existing BrowserOS repository clone..."
        Push-Location $browserOSRepoPath
        git fetch origin
        git pull origin main
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to update BrowserOS repo, continuing anyway..." "WARN"
        }
        Pop-Location
    } else {
        Write-Log "Cloning official BrowserOS repository..."
        $parentDir = Split-Path -Parent $browserOSRepoPath
        if (-not (Test-Path $parentDir)) {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }
        git clone https://github.com/browseros-ai/BrowserOS.git $browserOSRepoPath
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to clone BrowserOS repo" "WARN"
        }
    }
    Write-Log "BrowserOS repository sync complete"
    
    # Step 3: Run the research pipeline
    # NOTE: Replace this with the actual command that invokes the research pipeline
    # This could be a Python script, Node.js script, or another PowerShell script
    Write-Log "Running research pipeline..."
    
    if (-not $DryRun) {
        # Example: Invoke the research pipeline
        # & python "$RepositoryPath/scripts/run_browseros_research.py"
        # OR
        # & node "$RepositoryPath/scripts/research-pipeline.js"
        # OR
        # & pwsh "$RepositoryPath/scripts/research-pipeline.ps1"
        
        # For now, we'll just log that this step would be executed
        Write-Log "Research pipeline execution placeholder - implement actual command here" "WARN"
    } else {
        Write-Log "DRY RUN: Skipping research pipeline execution"
    }
    
    # Step 4: Check for changes
    $changes = git status --porcelain
    if (-not $changes) {
        Write-Log "No changes detected after research pipeline. Exiting."
        Pop-Location
        exit 0
    }
    
    # Step 5: Stage all changes
    Write-Log "Staging changes..."
    git add -A
    
    # Step 6: Commit changes
    $commitMessage = "Automated KB update - $(Get-Date -Format 'yyyy-MM-dd')"
    Write-Log "Committing changes: $commitMessage"
    
    if (-not $DryRun) {
        git commit -m $commitMessage
        if ($LASTEXITCODE -ne 0) {
            throw "Git commit failed with exit code $LASTEXITCODE"
        }
    } else {
        Write-Log "DRY RUN: Would commit with message: $commitMessage"
    }
    
    # Step 7: Create version tag
    $tagName = "kb-$(Get-Date -Format 'yyyy.MM.dd')"
    Write-Log "Creating tag: $tagName"
    
    if (-not $DryRun) {
        git tag -a $tagName -m "Knowledge Base update $(Get-Date -Format 'yyyy-MM-dd')"
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Tag creation failed (tag may already exist)" "WARN"
        }
    } else {
        Write-Log "DRY RUN: Would create tag: $tagName"
    }
    
    # Step 8: Push changes and tags
    Write-Log "Pushing changes to remote repository..."
    
    if (-not $DryRun) {
        git push origin main
        if ($LASTEXITCODE -ne 0) {
            throw "Git push failed with exit code $LASTEXITCODE"
        }
        
        git push origin $tagName
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Tag push failed" "WARN"
        }
    } else {
        Write-Log "DRY RUN: Would push changes and tag to remote"
    }
    
    Write-Log "Knowledge Base update completed successfully"
    
} catch {
    Write-Log "ERROR: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    Pop-Location
    exit 1
    
} finally {
    Pop-Location
}

# ============================================================================
# SCHEDULING INSTRUCTIONS
# ============================================================================
# To schedule this script in Windows Task Scheduler:
#
# 1. Open Task Scheduler (taskschd.msc)
# 2. Create Basic Task...
# 3. Name: "BrowserOS KB Weekly Update"
# 4. Trigger: Weekly, select day/time
# 5. Action: Start a program
#    Program/script: powershell.exe
#    Arguments: -ExecutionPolicy Bypass -File "<path-to-repo>\update_kb.ps1"
# 6. Finish and test the task
#
# For testing, run with -DryRun switch:
#    powershell.exe -ExecutionPolicy Bypass -File "update_kb.ps1" -DryRun
# ============================================================================
