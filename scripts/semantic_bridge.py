#!/usr/bin/env python3
"""
Semantic Bridge Monitor - "The Watchtower"
Monitors active browser tab via CDP, scores relevance against objective using Ollama,
and maintains a "drift" status.

Enhancements (Phase 7.5):
- Model Pool: Fallback resilience (Minimax -> Llama3 -> Phi3)
- Telemetry: Structured JSON logging to logs/telemetry.json
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
TELEMETRY_FILE = os.path.join("logs", "telemetry.json")
KB_FILE = os.path.join("BrowserOS", "Research", "knowledge_base.md")

# Model Pool Configuration
# The script will try these models in order until one succeeds
MODEL_POOL = [
    "glm-5:cloud",
    "gemini-3-flash-preview:cloud",
    "minimax-m2.5:cloud",
    "llama3.2:latest",
    "phi3:mini"
]

def get_active_tab_content(cdp_port):
    """Fetch title and url of active tab from Chrome/BrowserOS"""
    try:
        response = requests.get(f"http://localhost:{cdp_port}/json")
        response.raise_for_status()
        tabs = response.json()
        
        # Find active page
        for tab in tabs:
            if tab['type'] == 'page' and tab.get('url'):
                return {
                    "title": tab.get('title', ''),
                    "url": tab.get('url', ''),
                    "id": tab.get('id', '')
                }
    except Exception as e:
        print(f"[Error] CDP Connection failed: {e}", file=sys.stderr)
    return None

def score_relevance_with_pool(objective, content, initial_model=None):
    """
    Score relevance using a pool of models for resilience.
    Returns: (score, reasoning, model_used)
    """
    if not content:
        return 0, "No content available", "none"

    # If a specific model is requested via CLI, put it first in the list
    pool = list(MODEL_POOL)
    if initial_model and initial_model not in pool:
        pool.insert(0, initial_model)
    elif initial_model:
         # Move to front if already in list
        pool.remove(initial_model)
        pool.insert(0, initial_model)

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

    for model in pool:
        try:
            # We use requests directly to avoid 'ollama' lib dependency issues
            response = requests.post('http://localhost:11434/api/generate', json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }, timeout=30) # Increased timeout for larger models
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '{}')
                parsed = json.loads(response_text)
                return parsed.get('score', 0), parsed.get('reasoning', 'No reasoning provided'), model
            else:
                print(f"[Warn] Model {model} failed with status {response.status_code}", flush=True)
                
        except Exception as e:
            print(f"[Warn] Model {model} error: {e}", flush=True)
            continue # Try next model

    return 0, "All models failed to score content", "failures"

def update_status(status_data):
    """Write status to JSON file for MCP server to read"""
    try:
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        with open(STATUS_FILE, 'w') as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"[Error] Failed to write status file: {e}", file=sys.stderr)

def log_telemetry(data):
    """Append structured telemetry to a log file"""
    try:
        os.makedirs(os.path.dirname(TELEMETRY_FILE), exist_ok=True)
        # We append JSON lines for easier parsing later
        with open(TELEMETRY_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        print(f"[Error] Failed to write telemetry: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Semantic Bridge Monitor")
    parser.add_argument("--objective", required=True, help="Current user objective")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")
    parser.add_argument("--port", type=int, default=9000, help="CDP Port (usually 9222 or 9000)")
    parser.add_argument("--model", default="llama3", help="Preferred primary model")
    
    args = parser.parse_args()
    
    print(f"Starting Semantic Bridge Monitor (Enhanced)...", flush=True)
    print(f"Objective: {args.objective}", flush=True)
    print(f"Target: CDP Port {args.port}", flush=True)
    print(f"Model Strategy: {args.model} -> Fallback Pool", flush=True)
    
    while True:
        timestamp = datetime.now().isoformat()
        content = get_active_tab_content(args.port)
        
        if content:
            score, reasoning, model_used = score_relevance_with_pool(args.objective, content, args.model)
            
            decision = "ON_TRACK"
            if score < 40: decision = "DRIFT_WARNING"
            
            status = {
                "active": True,
                "timestamp": timestamp,
                "objective": args.objective,
                "current_tab": content,
                "relevance_score": score,
                "reasoning": reasoning,
                "model_used": model_used,
                "status": decision
            }
            
            print(f"[{timestamp}] Score: {score}/100 ({model_used}) - {decision} - {content['title'][:50]}...", flush=True)
            
            if score < 40:
                print(f"   DRIFT WARNING: {reasoning}", flush=True)
            
            # Telemetry Data
            telemetry_entry = {
                "timestamp": timestamp,
                "url": content['url'],
                "title": content['title'],
                "model_used": model_used,
                "score": score,
                "reasoning": reasoning,
                "decision": decision
            }
            
            # Auto-KB Update for high relevance
            if score >= 80:
                try:
                    t_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    kb_entry = f"\n\n## Insight Captured: {content['title']} ({t_now})\n" \
                               f"- **Source**: {content['url']}\n" \
                               f"- **Relevance**: {score}/100\n" \
                               f"- **Context**: {reasoning}\n" \
                               f"- **Objective**: {args.objective}\n" \
                               f"- **Model**: {model_used}\n"
                    
                    os.makedirs(os.path.dirname(KB_FILE), exist_ok=True)
                    with open(KB_FILE, 'a', encoding='utf-8') as kb:
                        kb.write(kb_entry)
                    print(f"   [+] Saved insight to knowledge_base.md", flush=True)
                    
                    status["kb_update"] = "Insight saved"
                    telemetry_entry["decision"] = "SAVED_TO_KB"
                    
                except Exception as e:
                    print(f"   [!] Failed to update KB: {e}", file=sys.stderr)
            
            # Log Telemetry
            log_telemetry(telemetry_entry)
                
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
