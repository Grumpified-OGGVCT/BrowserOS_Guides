#!/usr/bin/env python3
"""
AI Chat Handler for BrowserOS MCP
Allows direct conversational interaction with the configured AI models (Ollama/OpenRouter).
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, Any

# Configuration
try:
    from config_loader import get_config
    _cfg = get_config()
    _ollama_cfg = _cfg.ollama.http if _cfg.ollama else {}
    _openrouter_cfg = _cfg.openrouter.http if _cfg.openrouter else {}
except ImportError:
    # Fallback if config_loader not available
    _ollama_cfg = {}
    _openrouter_cfg = {}

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_API_KEY = _ollama_cfg.get("api_key") or os.getenv("OLLAMA_API_KEY")
OPENROUTER_API_KEY = _openrouter_cfg.get("api_key") or os.getenv("OPENROUTER_API_KEY")

def query_ollama(prompt: str, model: str, system_prompt: str = None) -> str:
    """Query Ollama API"""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    
    headers = {}
    if OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
    
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    if system_prompt:
        data["system"] = system_prompt
        
    try:
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        return f"Error querying {model}: {str(e)}"

def query_openrouter(prompt: str, model: str, system_prompt: str = None) -> str:
    """Query OpenRouter API"""
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY not set."
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Grumpified-OGGVCT/BrowserOS_Guides",
        "X-Title": "BrowserOS MCP Chat"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": model,
        "messages": messages
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Error querying OpenRouter: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="AI Chat Handler")
    parser.add_argument("prompt", help="The user prompt")
    parser.add_argument("--model", default="llama3", help="Model to use (e.g., llama3, google/gemini-flash-1.5)")
    parser.add_argument("--system", help="Optional system prompt/context")
    parser.add_argument("--json-output", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Determine provider based on model name or config
    model = args.model
    response_text = ""
    
    # Simple heuristic: if it has a slash, it's likely OpenRouter (e.g. google/gemini), else Ollama
    if "/" in model or "gpt" in model or "claude" in model:
        response_text = query_openrouter(args.prompt, model, args.system)
    else:
        response_text = query_ollama(args.prompt, model, args.system)
        
    if args.json_output:
        import json
        print(json.dumps({"response": response_text}))
    else:
        print(response_text)

if __name__ == "__main__":
    main()
