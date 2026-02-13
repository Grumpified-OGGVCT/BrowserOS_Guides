#!/usr/bin/env python3
"""
Semantic Bridge Monitor - "The Watchtower"
Monitors active browser tab via CDP, scores relevance against objective using Ollama,
and maintains a "drift" status.
"""

import time
import json
import argparse
import requests
import os
from datetime import datetime
import sys

# Configuration
CDP_URL = "http://localhost:9222" # Default, can be passed as arg
STATUS_FILE = os.path.join("logs", "semantic_bridge_status.json")
KB_FILE = os.path.join("BrowserOS", "Research", "knowledge_base.md")

def get_active_tab_content(cdp_port):
    """Fetch title and url of active tab from Chrome/BrowserOS"""
    try:
        response = requests.get(f"http://localhost:{cdp_port}/json")
        response.raise_for_status()
        tabs = response.json()
        
        # Find active page
        for tab in tabs:
            if tab['type'] == 'page' and tab.get('url'):
                # In a real scenario, we might need WebSocket to get full DOM
                # For now, we'll stick to Title + URL + potentially visible text if available via other endpoints
                # or just use the title/url as a proxy for "context" to save tokens
                return {
                    "title": tab.get('title', ''),
                    "url": tab.get('url', ''),
                    "id": tab.get('id', '')
                }
    except Exception as e:
        print(f"[Error] CDP Connection failed: {e}", file=sys.stderr)
    return None

def score_relevance(objective, content, model="llama3"):
    """Ask Ollama to score the relevance of the content to the objective"""
    if not content:
        return 0, "No content available"

    prompt = f"""
    Objective: "{objective}"
    Current Context:
    - Title: {content['title']}
    - URL: {content['url']}
    
    Task: Rate the relevance of this context to the objective on a scale of 0-100.
    If the user is distracted or off-track, give a low score.
    If the user is researching relevant info, give a high score.
    
    Return ONLY a JSON object: {{"score": <int>, "reasoning": "<string>"}}
    """
    
    try:
        # We use requests directly to avoid 'ollama' lib dependency issues if not installed
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '{}')
            parsed = json.loads(response_text)
            return parsed.get('score', 0), parsed.get('reasoning', 'No reasoning provided')
            
    except Exception as e:
        print(f"[Error] Ollama scoring failed: {e}", file=sys.stderr)
        
    return 0, "Scoring failed"

def update_status(status_data):
    """Write status to JSON file for MCP server to read"""
    try:
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        with open(STATUS_FILE, 'w') as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"[Error] Failed to write status file: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Semantic Bridge Monitor")
    parser.add_argument("--objective", required=True, help="Current user objective")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")
    parser.add_argument("--port", type=int, default=9000, help="CDP Port (usually 9222 or 9000)")
    parser.add_argument("--model", default="llama3", help="Ollama model to use")
    
    args = parser.parse_args()
    
    print(f"Starting Semantic Bridge Monitor...", flush=True)
    print(f"Objective: {args.objective}", flush=True)
    print(f"Target: CDP Port {args.port}", flush=True)
    
    while True:
        timestamp = datetime.now().isoformat()
        content = get_active_tab_content(args.port)
        
        if content:
            score, reasoning = score_relevance(args.objective, content, args.model)
            status = {
                "active": True,
                "timestamp": timestamp,
                "objective": args.objective,
                "current_tab": content,
                "relevance_score": score,
                "reasoning": reasoning,
                "status": "DRIFT_WARNING" if score < 40 else "ON_TRACK"
            }
            
            print(f"[{timestamp}] Score: {score}/100 - {status['status']} - {content['title'][:50]}...", flush=True)
            
            if score < 40:
                print(f"   DRIFT WARNING: {reasoning}", flush=True)
            
            # Auto-KB Update for high relevance
            if score >= 80:
                try:
                    t_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    kb_entry = f"\n\n## Insight Captured: {content['title']} ({t_now})\n" \
                               f"- **Source**: {content['url']}\n" \
                               f"- **Relevance**: {score}/100\n" \
                               f"- **Context**: {reasoning}\n" \
                               f"- **Objective**: {args.objective}\n"
                    
                    os.makedirs(os.path.dirname(KB_FILE), exist_ok=True)
                    with open(KB_FILE, 'a', encoding='utf-8') as kb:
                        kb.write(kb_entry)
                    print(f"   [+] Saved insight to knowledge_base.md", flush=True)
                    
                    # Add to status so frontend knows
                    status["kb_update"] = "Insight saved"
                except Exception as e:
                    print(f"   [!] Failed to update KB: {e}", file=sys.stderr)
                
        else:
            status = {
                "active": True,
                "timestamp": timestamp,
                "objective": args.objective,
                "error": "Could not fetch browser content",
                "status": "DISCONNECTED"
            }
            print(f"[{timestamp}] CDP Disconnected", flush=True)

        update_status(status)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
