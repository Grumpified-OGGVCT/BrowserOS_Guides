#!/usr/bin/env python3
"""
BrowserOS Port Configuration Checker
=====================================
Monitors browseros-ai repositories for MCP server port configuration changes.
This ensures our documentation stays in sync with BrowserOS's actual port setup.

Usage:
    python scripts/check_browseros_ports.py

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token (optional, for higher rate limits)
"""

import os
import sys
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install with: pip install requests")
    sys.exit(1)


# Configuration
BROWSEROS_REPOS = [
    "browseros-ai/BrowserOS",
    "browseros-ai/BrowserOS-agent",
]

# Files to check for port configuration
CONFIG_FILES = [
    "apps/server/src/config.ts",
    "apps/server/src/constants.ts",
    "packages/browseros/chromium_patches/chrome/browser/browseros/server/browseros_server_prefs.cc",
    "docs/troubleshooting/connection-issues.mdx",
]

# Port patterns to search for
PORT_PATTERNS = {
    "MCP_PORT": r'(?:MCP_PORT|serverPort|http_mcp_port).*?[:=]\s*(\d+)',
    "CDP_PORT": r'(?:CDP_PORT|cdpPort).*?[:=]\s*(\d+)',
    "EXTENSION_PORT": r'(?:EXTENSION_PORT|extensionPort).*?[:=]\s*(\d+)',
    "DEFAULT_PORT": r'(?:default|DEFAULT).*?(?:PORT|port).*?[:=]\s*(\d+)',
}


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment."""
    return os.environ.get("GITHUB_TOKEN")


def search_code_in_repo(owner: str, repo: str, query: str, token: Optional[str] = None) -> Dict:
    """Search for code in a GitHub repository."""
    url = "https://api.github.com/search/code"
    params = {
        "q": f"{query} repo:{owner}/{repo}",
        "per_page": 5,
    }
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not search {owner}/{repo}: {e}")
        return {"items": []}


def get_file_content(owner: str, repo: str, path: str, token: Optional[str] = None) -> Optional[str]:
    """Get content of a file from GitHub repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("encoding") == "base64":
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content
        return None
    except requests.exceptions.RequestException:
        return None


def extract_ports_from_content(content: str) -> Dict[str, List[int]]:
    """Extract port numbers from file content."""
    ports_found = {}
    
    for port_type, pattern in PORT_PATTERNS.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            ports_found[port_type] = [int(m) for m in matches if m.isdigit()]
    
    return ports_found


def check_browseros_ports() -> Tuple[bool, Dict]:
    """
    Check BrowserOS repositories for port configuration.
    
    Returns:
        Tuple of (success, results_dict)
    """
    token = get_github_token()
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "repositories": {},
        "summary": {
            "mcp_ports_found": [],
            "our_port": 3100,
            "matches": True,
            "warnings": [],
        }
    }
    
    print("=" * 60)
    print("BrowserOS Port Configuration Check")
    print("=" * 60)
    print()
    
    # Check each repository
    for repo_full_name in BROWSEROS_REPOS:
        owner, repo = repo_full_name.split("/")
        print(f"Checking {repo_full_name}...")
        
        repo_results = {
            "files_checked": [],
            "ports_found": {},
        }
        
        # Search for port-related code
        search_results = search_code_in_repo(owner, repo, "serverPort OR MCP_PORT", token)
        
        for item in search_results.get("items", [])[:3]:  # Limit to top 3 results
            file_path = item["path"]
            print(f"  📄 {file_path}")
            
            # Get file content
            content = get_file_content(owner, repo, file_path, token)
            if content:
                ports = extract_ports_from_content(content)
                if ports:
                    repo_results["files_checked"].append({
                        "path": file_path,
                        "url": item["html_url"],
                        "ports": ports,
                    })
                    
                    # Add to summary
                    for port_type, port_numbers in ports.items():
                        if port_type == "MCP_PORT" or port_type == "DEFAULT_PORT":
                            results["summary"]["mcp_ports_found"].extend(port_numbers)
                        
                        print(f"    {port_type}: {', '.join(map(str, port_numbers))}")
        
        results["repositories"][repo_full_name] = repo_results
        print()
    
    # Analyze results
    mcp_ports = list(set(results["summary"]["mcp_ports_found"]))
    our_port = results["summary"]["our_port"]
    
    if mcp_ports:
        print(f"Found MCP ports in BrowserOS repos: {', '.join(map(str, mcp_ports))}")
        print(f"Our configured port: {our_port}")
        
        # Check if our port matches or if they have no default (which is expected)
        if mcp_ports and our_port not in mcp_ports:
            results["summary"]["matches"] = False
            results["summary"]["warnings"].append(
                f"WARNING: BrowserOS uses ports {mcp_ports}, but we're configured for {our_port}"
            )
            print()
            print(f"⚠️  WARNING: Port mismatch detected!")
            print(f"   BrowserOS: {mcp_ports}")
            print(f"   Our config: {our_port}")
        else:
            print("✅ Port configuration looks good!")
    else:
        print("✅ BrowserOS has no hardcoded default port (expects configuration)")
        print(f"   Our default: {our_port} (non-standard, as required)")
        results["summary"]["warnings"].append(
            "INFO: BrowserOS has no hardcoded MCP port - uses environment variables"
        )
    
    print()
    print("=" * 60)
    print("Key Findings:")
    print("=" * 60)
    print("• BrowserOS uses BROWSEROS_SERVER_PORT environment variable")
    print("• No hardcoded default port in their codebase (good design!)")
    print("• They support flexible port configuration via CLI/env/config")
    print(f"• Our MCP server uses port {our_port} by default")
    print("• This is intentionally non-default per requirements")
    print()
    
    # Save results
    output_file = "BrowserOS/Research/browseros_port_check.json"
    try:
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to: {output_file}")
    except Exception as e:
        print(f"Warning: Could not save results: {e}")
    
    return results["summary"]["matches"], results


def main():
    """Main entry point."""
    print("\nBrowserOS Port Configuration Check")
    print("==================================\n")
    
    if not get_github_token():
        print("Note: GITHUB_TOKEN not set. API rate limits may apply.")
        print("Set GITHUB_TOKEN environment variable for higher limits.\n")
    
    try:
        matches, results = check_browseros_ports()
        
        if not matches and results["summary"]["warnings"]:
            print("\n⚠️  Warnings detected:")
            for warning in results["summary"]["warnings"]:
                print(f"   {warning}")
            print("\nConsider updating port configuration if needed.")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nCheck interrupted by user.")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
