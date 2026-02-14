import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise RuntimeError(
        "Missing OPENROUTER_API_KEY environment variable. "
        "Please set it before running this test script."
    )
url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/Grumpified-OGGVCT/BrowserOS_Guides",
    "X-Title": "BrowserOS KB Research"
}

data = {
    "model": "anthropic/claude-3-sonnet",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7,
    "max_tokens": 100
}

print(f"DEBUG: URL: {url}")
print(f"DEBUG: Headers: {json.dumps(headers, indent=2)}")
print(f"DEBUG: Data: {json.dumps(data, indent=2)}")

# Test 1: List Models
print("\n--- Testing GET /models ---")
try:
    models_url = "https://openrouter.ai/api/v1/models"
    resp = requests.get(models_url, headers={"Authorization": f"Bearer {api_key}"})
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✓ Models endpoint works")
    else:
        print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Chat Completion
print("\n--- Testing POST /chat/completions ---")
try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
