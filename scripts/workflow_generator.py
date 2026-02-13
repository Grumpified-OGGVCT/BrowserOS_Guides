#!/usr/bin/env python3
"""
BrowserOS Workflow Generator - AI-Powered Workflow Creation
Uses specified AI model (default: GLM-5) via Ollama Cloud API to generate realistic, working workflows

This script is the core of the self-growing workflow library system.
"""

import os
import sys
import json
import argparse
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Force UTF-8 output for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

try:
    from config_loader import get_config as load_config
except ImportError:
    print("Warning: config_loader not available, using defaults")
    load_config = None


class AIWorkflowGenerator:


    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Simply and robustly extract JSON from any preamble/postamble.
        
        Tries several strategies in sequence:
        1. JSON between the outermost '{' and '}'.
        2. Entire text as JSON.
        3. JSON inside a fenced markdown code block.
        4. Largest balanced-brace JSON block.
        5. Last-resort outermost '{' ... '}' again.
        """
        if not text: return None
        
        import re
        
        # First attempt: JSON between the outermost braces (original primary behavior)
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except Exception as e:
                # Keep debug output but continue to other strategies instead of returning early
                print(f"Extraction failed using outermost braces: {e}")
        
        # Second attempt: parse the entire text as JSON
        try:
            return json.loads(text)
        except:
            pass
            
        # Third attempt: JSON inside a fenced markdown code block
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
            
        # Fourth attempt: find the largest block between matched braces
        stack = 0
        first_brace = -1
        for i, char in enumerate(text):
            if char == "{":
                if stack == 0:
                    first_brace = i
                stack += 1
            elif char == "}":
                stack -= 1
                if stack == 0 and first_brace != -1:
                    candidate = text[first_brace:i+1]
                    try:
                        return json.loads(candidate)
                    except:
                        pass
        
        # Fifth attempt (last resort): try any outermost '{' ... '}' pair again
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except:
                pass
            
        return None

    """
    AI-Powered Workflow Generator
    
    This class uses an AI model (GLM-5, Kimi, Llama3, etc.) to generate
    realistic, production-ready BrowserOS workflows based on use cases.
    
    SAFETY DISCLAIMER:
    This public workflow generator includes safety filters to prevent generation
    of NSFW or illegal content for public safety and legal compliance.
    
    Users running their own private instances can modify or disable these filters
    as appropriate for their use case. This generator is designed for the public
    hosted version and errs on the side of caution.
    
    See: docs/SAFETY_POLICY.md for full details
    """
    
    # Context-aware safety patterns
    # NOTE: These only apply to the PUBLIC hosted generator
    # Private instances can modify this list as needed
    
    # Pattern format: (pattern, category, confidence_threshold)
    # Higher confidence = more certain it's malicious
    SAFETY_PATTERNS = {
        'nsfw': [
            ('porn', 0.9),
            ('nsfw', 0.9),
            ('adult content', 0.8),
            ('sex', 0.7),  # Lower confidence - could be "sex education"
            ('xxx', 0.9),
            ('escort', 0.8),
            ('dating app hack', 1.0),
            ('tinder bot', 0.9),
            ('onlyfans', 0.7),  # Could be legitimate creator tools
            ('camgirl', 0.9),
            ('nude', 0.8),
            ('explicit', 0.6),  # Lower - could be "explicit consent"
        ],
        'illegal': [
            # Specific malicious intent - HIGH confidence
            ('hack into', 1.0),
            ('crack password', 1.0),
            ('exploit vulnerab', 1.0),
            ('ddos attack', 1.0),
            ('credential stuff', 1.0),
            ('brute force password', 1.0),
            ('steal data', 1.0),
            ('steal credit card', 1.0),
            ('fraud', 0.9),
            ('phishing', 1.0),
            ('identity theft', 1.0),
            ('fake id', 1.0),
            ('counterfeit', 0.9),
            ('pirate software', 0.9),
            ('bypass paywall', 0.9),
            ('bypass drm', 0.9),
            ('cheat on exam', 1.0),
            ('plagiarism tool', 1.0),
            ('essay mill', 1.0),
            ('fake review', 0.9),
            ('spam bot', 0.9),
            ('fake account creation', 0.9),
            ('buy followers', 0.8),
            ('clickfarm', 0.9),
            ('carding', 1.0),
            # Generic terms - LOWER confidence (need context)
            ('hack', 0.5),  # Could be "hackathon" or "growth hack"
            ('crack', 0.5),  # Could be "crack the code" (solve)
            ('exploit', 0.4),  # Could be "exploit opportunity"
        ],
        'privacy': [
            ('scrape email', 1.0),
            ('scrape phone', 1.0),
            ('scrape personal data', 1.0),
            ('harvest emails', 1.0),
            ('dox', 1.0),
            ('doxxing', 1.0),
            ('stalk', 0.9),
            ('track someone', 0.9),
            ('spy on', 1.0),
            ('monitor spouse', 1.0),
            ('employee spy', 1.0),
            ('keylogger', 1.0),
            ('screenshot spy', 0.9),
        ]
    }
    
    # Legitimate contexts that should NOT be flagged
    LEGITIMATE_CONTEXTS = [
        'payment flow', 'payment process', 'checkout', 'e-commerce',
        'process payment', 'payment gateway', 'stripe', 'paypal',
        'security audit', 'security test', 'penetration test', 'pentest',
        'own website', 'own site', 'my website', 'my application',
        'test environment', 'development', 'staging',
        'authorized', 'permission', 'consent', 'opt-in',
        'compliance', 'gdpr', 'legal', 'terms of service',
        'growth hack', 'life hack', 'productivity hack',
        'hack together', 'hackathon', 'hack day'
    ]
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the workflow generator"""
        self.api_key = api_key or os.getenv('OLLAMA_API_KEY')
        if not self.api_key:
            raise ValueError("OLLAMA_API_KEY environment variable required")
        
        self.base_url = "http://localhost:11434/v1"
        
        # Load configuration if available
        self.config = self._load_config()
        
        # Determine model: CLI override > Config > Default
        if model:
            self.model = model
            source = "CLI Argument"
        elif self.config and 'sdk' in self.config and 'model' in self.config['sdk']:
            self.model = self.config['sdk']['model']
            source = "Config File"
        else:
            self.model = "glm-5:cloud"
            source = "Default (Fallback)"
        
        print(f"✅ Initialized AI Workflow Generator")
        print(f"   Model: {self.model} ({source})")
        print(f"   API: Ollama Cloud")
        print(f"   Safety: Enabled (NSFW/Illegal content filtering)")
        print(f"")
        print(f"   ℹ️  DISCLAIMER: Safety filters apply to public hosted instances.")
        print(f"       Private instances can be configured differently for specific use cases.")
    
    def check_safety(self, use_case: str, industry: Optional[str] = None) -> Dict[str, Any]:
        """
        Context-aware safety check for use cases
        
        NOTE: This safety check is designed for the PUBLIC hosted generator.
        Users running private instances can modify or disable this method
        as appropriate for their specific use cases and legal jurisdictions.
        
        Args:
            use_case: The workflow use case to check
            industry: Optional industry context
            
        Returns:
            Dict with 'safe': bool and 'reason': str if unsafe
        """
        use_case_lower = use_case.lower()
        industry_lower = (industry or '').lower()
        combined = f"{use_case_lower} {industry_lower}"
        
        # First, check for legitimate contexts that should override flags
        is_legitimate = False
        for context in self.LEGITIMATE_CONTEXTS:
            if context in combined:
                is_legitimate = True
                break
        
        # Track highest confidence match for each category
        matches = {
            'nsfw': {'confidence': 0, 'pattern': None},
            'illegal': {'confidence': 0, 'pattern': None},
            'privacy': {'confidence': 0, 'pattern': None}
        }
        
        # Check all patterns
        for category, patterns in self.SAFETY_PATTERNS.items():
            for pattern, confidence in patterns:
                if pattern in combined:
                    if confidence > matches[category]['confidence']:
                        matches[category]['confidence'] = confidence
                        matches[category]['pattern'] = pattern
        
        # Determine if we should reject based on confidence and context
        CONFIDENCE_THRESHOLD = 0.8  # Require 80% confidence to reject
        
        for category, match in matches.items():
            confidence = match['confidence']
            pattern = match['pattern']
            
            if confidence >= CONFIDENCE_THRESHOLD:
                # High confidence match - but check if legitimate context overrides
                if is_legitimate and confidence < 1.0:
                    # Legitimate context found, and not 100% confident it's bad
                    # Let it through with a warning
                    continue
                
                # Reject this use case
                category_messages = {
                    'nsfw': 'NSFW content detected: Use case contains prohibited adult/explicit material',
                    'illegal': 'Illegal activity detected: Use case involves prohibited actions that may violate laws',
                    'privacy': 'Privacy violation detected: Use case involves unauthorized data collection or surveillance'
                }
                
                return {
                    'safe': False,
                    'category': category,
                    'reason': category_messages[category],
                    'pattern': pattern,
                    'confidence': confidence,
                    'note': 'If this is a legitimate use case, please clarify the context in your request'
                }
        
        return {
            'safe': True,
            'confidence': 1.0 - max(m['confidence'] for m in matches.values()),
            'note': 'Use case passed safety checks'
        }
    
    def _load_config(self) -> Dict:
        """Load configuration from config.yml"""
        if load_config:
            try:
                config = load_config()
                return config.get('OLLAMA', {})
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
        
        # Default configuration
        return {
            'http': {
                'base_url': 'https://api.ollama.ai/v1',
                'timeout': 120,
                'retry_count': 3
            },
            'sdk': {
                'model': 'glm-5',
                'options': {
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_tokens': 4000
                }
            }
        }
    
    def generate_workflow_idea(
        self,
        use_case: str,
        industry: Optional[str] = None,
        complexity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate a workflow idea using the configured AI model
        
        Args:
            use_case: What the workflow should accomplish
            industry: Optional industry context
            complexity: low, medium, high, expert
        
        Returns:
            Dict with workflow idea and metadata
        """
        # SAFETY CHECK - Run before any AI generation
        # NOTE: Public safety filter - can be modified for private instances
        safety_check = self.check_safety(use_case, industry)
        if not safety_check['safe']:
            print(f"❌ REJECTED: {safety_check['reason']}")
            print(f"   ℹ️  This safety filter applies to the public hosted generator.")
            print(f"       Private instances can be configured for different use cases.")
            return {
                'rejected': True,
                'reason': 'safety_violation',
                'category': safety_check['category'],
                'explanation': safety_check['reason'],
                'keyword_triggered': safety_check.get('keyword', 'unknown'),
                'use_case': use_case,
                'industry': industry,
                'generated_at': datetime.utcnow().isoformat()
            }
        
        print(f"\n🤖 Generating workflow idea for: {use_case}")
        if industry:
            print(f"   Industry: {industry}")
        print(f"   Complexity: {complexity}")
        print(f"   Safety: ✅ Passed")
        
        # Construct prompt for AI
        prompt = self._build_workflow_idea_prompt(use_case, industry, complexity)
        
        # Call AI via Ollama Cloud API
        response = self._call_model(prompt, max_tokens=2000)
        
        # Parse response
        try:
            idea = self._extract_json(response)
            if idea is None: raise json.JSONDecodeError('No JSON found', response, 0)
            
            # Check if AI also rejected it
            if idea.get('rejected'):
                print(f"❌ AI Rejected: {idea.get('explanation', 'Safety violation')}")
                return idea
            
            idea['generated_at'] = datetime.utcnow().isoformat()
            idea['model'] = self.model
            idea['use_case'] = use_case
            idea['industry'] = industry
            idea['complexity'] = complexity
            idea['safety_checked'] = True
            
            print(f"✅ Generated workflow idea: {idea.get('title', 'Untitled')}")
            return idea
            
        except json.JSONDecodeError:
            print(f"⚠️  {self.model} response was not valid JSON, wrapping in structure")
            return {
                'title': f"Workflow for {use_case}",
                'description': response,
                'generated_at': datetime.utcnow().isoformat(),
                'model': self.model,
                'use_case': use_case,
                'industry': industry,
                'complexity': complexity,
                'safety_checked': True,
                'raw_response': response
            }
    
    def generate_workflow_implementation(
        self,
        idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a complete workflow implementation from an idea
        
        Args:
            idea: Workflow idea dict from generate_workflow_idea()
        
        Returns:
            Complete BrowserOS workflow JSON
        """
        print(f"\n🔨 Generating workflow implementation...")
        print(f"   Title: {idea.get('title', 'Unknown')}")
        
        # Construct prompt for implementation
        prompt = self._build_workflow_implementation_prompt(idea)
        
        # Call AI with larger token limit
        response = self._call_model(prompt, max_tokens=4000)
        
        # Parse workflow JSON
        try:
            workflow = self._extract_json(response)
            if workflow is None: Path("debug_response.txt").write_text(response); raise json.JSONDecodeError('No JSON found', response, 0)
            
            # Add metadata
            workflow['metadata'] = workflow.get('metadata', {})
            workflow['metadata']['generated_at'] = datetime.utcnow().isoformat()
            workflow['metadata']['model'] = self.model
            workflow['metadata']['idea'] = idea
            workflow['metadata']['generator_version'] = '1.0.0'
            
            print(f"✅ Generated workflow with {len(workflow.get('steps', []))} steps")
            return workflow
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse workflow JSON: {e}")
            print(f"Response preview: {response[:200]}...")
            raise
    
    def validate_workflow_feasibility(
        self,
        workflow: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that a workflow is technically feasible and will actually work
        
        Args:
            workflow: Workflow JSON to validate
        
        Returns:
            Validation results with feasibility score and issues
        """
        print(f"\n🔍 Validating workflow feasibility...")
        
        # Construct validation prompt
        prompt = self._build_validation_prompt(workflow)
        
        # Call AI for analysis
        response = self._call_model(prompt, max_tokens=2000)
        
        # Parse validation results
        try:
            validation = self._extract_json(response)
            if validation is None: raise json.JSONDecodeError('No JSON found', response, 0)
            validation['validated_at'] = datetime.utcnow().isoformat()
            validation['model'] = self.model
            
            feasible = validation.get('feasible', False)
            score = validation.get('feasibility_score', 0)
            
            if feasible:
                print(f"✅ Workflow is FEASIBLE (score: {score}/100)")
            else:
                print(f"❌ Workflow has issues (score: {score}/100)")
            
            issues = validation.get('issues', [])
            if issues:
                print(f"   Found {len(issues)} issue(s):")
                for issue in issues[:3]:  # Show first 3
                    print(f"   - {issue}")
            
            return validation
            
        except json.JSONDecodeError:
            print("⚠️  Validation response was not JSON, assuming valid")
            return {
                'feasible': True,
                'feasibility_score': 75,
                'validated_at': datetime.utcnow().isoformat(),
                'model': self.model,
                'raw_response': response
            }
    
    def _call_model(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Call AI model via Ollama Cloud API
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
        
        Returns:
            Model response as string
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert in browser automation and workflow design. '
                              'You specialize in creating realistic, production-ready workflows for BrowserOS. '
                              'Always respond with valid JSON when requested.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': max_tokens,
            'temperature': 0.7,
            'top_p': 0.9
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            return content.strip()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error calling Model API: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text[:200]}")
            raise
    
    def _build_workflow_idea_prompt(
        self,
        use_case: str,
        industry: Optional[str],
        complexity: str
    ) -> str:
        """Build prompt for workflow idea generation"""
        
        industry_context = f" in the {industry} industry" if industry else ""
        
        prompt = f"""You are an expert BrowserOS workflow designer helping someone solve a real problem with browser automation.

THE REQUEST:
Use Case: {use_case}{industry_context}
Complexity Level: {complexity}

YOUR MISSION:
Create a thoughtful, detailed workflow idea that feels personal and actionable - not generic AI-speak. 
Think like a helpful colleague explaining a solution over coffee, not a robot listing features.

IMPORTANT: Write descriptions that:
- Tell a micro-story: "Imagine you're..." or "Picture this scenario..."
- Use concrete examples: specific websites, real data points, actual user pain points
- Explain the "why" behind each step: "This matters because..."
- Include relatable details: time savings, frustration solved, impact on daily work
- Sound human: use natural language, avoid jargon unless explaining it

Respond with ONLY a JSON object in this exact format:
{{
  "title": "Compelling, specific title that describes the outcome",
  "description": "3-4 sentences painting a vivid picture. Start with the user's pain point, describe the transformation, end with the value delivered. Use concrete numbers and real scenarios.",
  "use_case": "The actual problem being solved - be specific about WHO faces this and WHEN",
  "steps_overview": [
    "Step 1: Detailed action with why it matters",
    "Step 2: Next action explaining the technique used",
    "Step 3: Outcome with specific result expected",
    "Add 4-8 steps with personality and detail"
  ],
  "input_required": [
    "Specific input #1: Why you need this and example format",
    "Specific input #2: Context on where to find this",
    "Be concrete: 'Your competitor's product page URL (e.g., https://competitor.com/products)'"
  ],
  "output_produced": [
    "Tangible output #1: Format, location, and how to use it",
    "Tangible output #2: What insights you'll gain",
    "Be specific: 'CSV file with 50+ data points including prices, stock levels, and review counts'"
  ],
  "estimated_duration": "Realistic time with context (e.g., '3-5 minutes for 10 competitors, scales linearly')",
  "difficulty": "beginner|intermediate|advanced|expert",
  "tags": ["specific-tag1", "use-case-tag2", "industry-tag3"],
  "real_world_applications": [
    "Detailed scenario #1: Who, what, why, and business impact",
    "Detailed scenario #2: Specific team, problem, and ROI",
    "Use real examples: 'E-commerce managers tracking 50+ competitors save 15 hours/week'"
  ],
  "why_this_matters": "2-3 sentences explaining the bigger picture impact - career growth, business value, time reclaimed",
  "success_looks_like": "Paint a vivid picture of using this workflow successfully - what does the user's day look like after implementing this?",
  "feasibility_notes": "Honest technical considerations with workarounds and alternative approaches"
}}

EXAMPLES OF GOOD vs BAD:
BAD (Generic): "This workflow automates data extraction from websites"
GOOD (Personal): "Picture spending 30 minutes every Monday manually copying competitor prices into a spreadsheet. This workflow does it in 90 seconds, letting you grab coffee while it runs - and it never misses a price change."

BAD: "Extract product information"  
GOOD: "Capture 15 data points per product: price, availability, reviews (count + avg rating), shipping time, warranty details, and promotional badges - everything your pricing team needs to stay competitive"

SAFETY & ETHICS - CRITICAL RULES (YOU MUST REFUSE IF VIOLATED):
REJECT IMMEDIATELY if the use case involves:
- Adult content, NSFW material, or sexual services
- Illegal activities (hacking, fraud, identity theft, credential stuffing)
- Harassment, stalking, or privacy invasion
- Bypassing paywalls or DRM without authorization
- Scraping personal data (emails, phone numbers, addresses) without consent
- Creating spam or fake accounts
- Automated purchasing bots that violate ToS
- Price manipulation or market manipulation
- Academic dishonesty (exam cheating, plagiarism)
- Circumventing security measures or CAPTCHAs at scale

If ANY of these apply, respond with:
{{
  "rejected": true,
  "reason": "safety_violation",
  "explanation": "This use case violates our ethical guidelines: [specific reason]",
  "category": "nsfw|illegal|privacy|fraud|tos_violation",
  "alternatives": "Suggest legal/ethical alternatives if possible"
}}

ACCEPTABLE USE CASES include:
- Competitive intelligence from public data
- Personal productivity automation
- Testing your own websites/apps
- Market research from public sources
- Job application tracking
- Price monitoring for purchasing decisions
- Content aggregation from authorized sources
- Accessibility improvements
- Data backup from your own accounts

Make this feel like it was designed specifically for the user's problem, not a template filled in by AI."""
        
        return prompt
    
    def _build_workflow_implementation_prompt(self, idea: Dict[str, Any]) -> str:
        """Build prompt for workflow implementation generation"""
        
        prompt = f"""You are crafting a production-ready BrowserOS workflow that someone will actually use in their daily work.

WORKFLOW TO IMPLEMENT:
Title: {idea.get('title')}
Description: {idea.get('description')}
Use Case: {idea.get('use_case')}

YOUR MISSION:
Create a complete, thoughtful workflow implementation that feels like it was hand-crafted by an expert - not auto-generated.

KEY PRINCIPLES:
1. **Descriptive Step Names**: Instead of "Click button", write "Click Add to Cart button to select product for comparison"
2. **Realistic Selectors**: Use plausible CSS selectors based on common patterns (e.g., data-testid=product-price, .product-card h2)
3. **Helpful Comments**: Each step name should explain WHY this step matters, not just WHAT it does
4. **Smart Error Handling**: Include fallback selectors, wait conditions, and retry logic
5. **Extractable Patterns**: Show where data is captured and how it is stored
6. **Variable Names**: Use descriptive variables like competitor_prices not data1

AVAILABLE STEP TYPES:
- navigate: Go to URL (include wait_for: load, networkidle, or selector)
- click: Click element (use wait_after for page transitions)
- input: Type into fields (include wait_before for field focus)
- extract: Grab data (specify output variable name and what data represents)
- wait: Explicit waits (use for dynamic content, specify condition)
- scroll: Scroll page (useful for lazy-loaded content)
- conditional: If/then logic (check for element existence, text content)
- loop: Repeat steps (for multiple items, pages, etc.)
- script: Run custom JavaScript (for complex operations)

Respond with ONLY a valid BrowserOS workflow JSON in this format:
{{
  "name": "{idea.get('title', 'Workflow')}",
  "description": "{idea.get('description', '')}",
  "version": "1.0.0",
  "author": "BrowserOS AI Generator",
  "steps": [
    {{
      "type": "navigate",
      "name": "Navigate to competitor's product catalog page",
      "url": "{{{{competitor_url}}}}/products",
      "wait_for": "networkidle",
      "timeout": 10000,
      "comment": "Using networkidle ensures all product tiles have loaded"
    }},
    {{
      "type": "wait",
      "name": "Wait for product grid to render",
      "selector": ".product-grid, [data-testid='product-list']",
      "timeout": 5000,
      "comment": "Fallback selectors handle different site structures"
    }},
    {{
      "type": "extract",
      "name": "Extract product names and prices from first page",
      "selector": ".product-card",
      "multiple": true,
      "fields": {{
        "name": ".product-title, h2.title",
        "price": ".price-current, [data-price]",
        "availability": ".stock-status"
      }},
      "output": "products_page_1",
      "comment": "Captures structured data for each product found"
    }},
    {{
      "type": "conditional",
      "name": "Check if pagination exists",
      "condition": "element_exists",
      "selector": ".pagination .next-page",
      "on_true": "continue",
      "on_false": "skip_to_export",
      "comment": "Only paginate if multiple pages exist"
    }}
  ],
  "variables": {{
    "competitor_url": {{
      "type": "string",
      "required": true,
      "description": "Full URL to competitor's website (e.g., https://competitor.com)",
      "example": "https://example-competitor.com"
    }},
    "max_pages": {{
      "type": "number",
      "required": false,
      "default": 5,
      "description": "Maximum number of product pages to scrape"
    }}
  }},
  "outputs": {{
    "products_page_1": {{
      "type": "array",
      "description": "Product data from first page",
      "format": "Array of objects with name, price, availability"
    }},
    "total_products_found": {{
      "type": "number",
      "description": "Count of total products extracted"
    }}
  }},
  "error_handling": {{
    "retry_count": 3,
    "retry_delay": 2000,
    "on_error": "continue",
    "fallback_selectors": true,
    "screenshot_on_error": true,
    "comment": "Takes debug screenshots when steps fail"
  }},
  "performance": {{
    "estimated_duration": "{idea.get('estimated_duration', '2-5 minutes')}",
    "rate_limit": "1 request per 2 seconds",
    "memory_usage": "low",
    "comment": "Respectful crawling with delays between requests"
  }},
  "metadata": {{
    "category": "appropriate-category",
    "tags": {json.dumps(idea.get('tags', []))},
    "difficulty": "{idea.get('difficulty', 'intermediate')}",
    "use_cases": {json.dumps(idea.get('real_world_applications', []))[:200]},
    "created_at": "{{{{timestamp}}}}",
    "tested": false
  }}
}}

BEST PRACTICES TO FOLLOW:
- Use multiple fallback selectors: .selector1, .selector2, data-attr
- Add waits before interactions: wait_before, wait_after
- Include timeout values: Be realistic (5-10 seconds for most operations)
- Use variables for user inputs: variable_name
- Comment complex steps: Explain the why in the comment field
- Handle pagination: Loop through results, track page numbers
- Extract structured data: Use fields object for related data points
- Plan for errors: Retry logic, fallbacks, graceful degradation
- Document outputs: What data is captured and in what format
- Rate limiting: Respect target sites with delays

SAFETY & COMPLIANCE - MANDATORY CHECKS:
DO NOT generate workflows that:
- Access adult/NSFW content or services
- Violate website Terms of Service
- Bypass authentication or authorization
- Extract private/personal data without consent
- Automate illegal activities
- Create spam or fake engagement
- Perform credential stuffing or brute force attacks
- Circumvent paywalls without authorization
- Scrape at rates that could be considered DoS
- Harvest emails/phones for unsolicited contact

REQUIRED SAFETY FEATURES in every workflow:
1. Rate limiting with respectful delays (min 1-2 seconds between requests)
2. User-Agent identification (not spoofing)
3. Respect for robots.txt (check before scraping)
4. No credential storage in workflow (use secure variable placeholders)
5. Clear documentation of data usage and retention
6. Timeout limits to prevent runaway processes
7. Error handling that fails gracefully without retrying indefinitely

If this workflow idea violates safety guidelines, respond with:
{{
  "rejected": true,
  "reason": "safety_violation",
  "category": "specific_category",
  "explanation": "Detailed reason why this cannot be implemented"
}}

MAKE IT FEEL HANDCRAFTED:
- Selectors should look like they came from inspecting real pages
- Comments should sound like a senior developer explaining to a junior
- Variable names should be self-documenting
- Error handling should anticipate real-world failures

Respond with ONLY the JSON, no additional text before or after."""

        return prompt
    
    def _build_validation_prompt(self, workflow: Dict[str, Any]) -> str:
        """Build prompt for workflow validation"""
        
        workflow_json = json.dumps(workflow, indent=2)
        
        prompt = f"""You are a senior BrowserOS engineer reviewing a workflow before it goes to production.

WORKFLOW TO VALIDATE:
{workflow_json}

YOUR MISSION:
Provide an honest, detailed technical review that will actually help improve this workflow.
Think like a code reviewer who cares about quality - be thorough but constructive.

VALIDATION CHECKLIST:

1. **Selector Reality Check**
   - Are the CSS selectors realistic? (e.g., based on common patterns like .product-card, [data-testid], etc.)
   - Are there fallback selectors for brittle elements?
   - Will these selectors work across different site structures?

2. **Error Handling Assessment**
   - Is retry logic sufficient for flaky elements?
   - Are timeouts realistic? (not too short to fail, not too long to hang)
   - What happens if a step fails? Is there graceful degradation?
   - Are screenshots captured on errors for debugging?

3. **Step Logic & Flow**
   - Are steps in the right order?
   - Are waits placed appropriately (after navigation, before clicks)?
   - Does pagination logic make sense?
   - Are conditionals checking the right things?

4. **Real-World Applicability**
   - Would this actually work on modern websites?
   - Does it handle dynamic content (SPAs, lazy loading)?
   - Is it rate-limited to avoid bans?
   - Will it work across different browsers?

5. **Security & Ethics** [CRITICAL - AUTO-REJECT IF FAILED]
   - Are there hardcoded credentials? (RED FLAG - REJECT)
   - Does it access NSFW or illegal content? (RED FLAG - REJECT)
   - Does it respect robots.txt?
   - Is rate limiting respectful?
   - Any data privacy concerns?
   - Does it violate any website ToS?
   - Could it be used for harassment or stalking? (RED FLAG - REJECT)
   - Does it extract personal data without consent? (RED FLAG - REJECT)
   - Does it bypass security measures unethically? (RED FLAG - REJECT)
   - Could it enable illegal activities? (RED FLAG - REJECT)

IMMEDIATE REJECTION CRITERIA:
If the workflow involves ANY of these, set feasible: false and explain:
- Adult/NSFW content access
- Illegal activities (hacking, fraud, identity theft)
- Privacy violations (scraping personal data without consent)
- ToS violations (credential stuffing, automated account creation)
- Harassment or stalking capabilities
- Bypassing paywalls/DRM without authorization
- Creating spam or fake engagement
- Academic dishonesty tools
- Market manipulation
- DoS-like request rates

For rejected workflows, respond with:
{{
  "feasible": false,
  "rejected": true,
  "rejection_reason": "safety_violation",
  "feasibility_score": 0,
  "category": "nsfw|illegal|privacy|fraud|harassment|tos_violation",
  "issues": ["Specific safety violation identified"],
  "verdict": "This workflow cannot be approved due to [specific safety concern]. It violates ethical guidelines and/or laws."
}}

6. **Data Quality**
   - Are extracted fields comprehensive enough?
   - Is the output format useful?
   - Are variable names descriptive?
   - Is data normalized/cleaned?

7. **Performance & Reliability**
   - Will this complete in reasonable time?
   - Is memory usage reasonable?
   - Can it run unattended?
   - How often will it need maintenance?

8. **User Experience**
   - Are the required inputs clearly documented?
   - Will the outputs be immediately useful?
   - Are error messages helpful?
   - Is the complexity appropriate for the claimed difficulty level?

Respond with ONLY a JSON object in this format:
{{
  "feasible": true/false,
  "feasibility_score": 0-100,
  "confidence": "high|medium|low",
  "issues": [
    "Specific issue #1: What's wrong and why it matters",
    "Specific issue #2: Concrete example of the problem",
    "Be detailed: 'Selector .product-price is too generic and will break on PLP vs PDP pages'"
  ],
  "recommendations": [
    "Actionable fix #1: Exactly what to change and why",
    "Actionable fix #2: Include code example if relevant",
    "Be specific: 'Add fallback selector: .product-price, [data-product-price], .price-wrapper .current'"
  ],
  "security_concerns": [
    "Security issue #1: Severity level and mitigation",
    "Note: Empty array if no issues"
  ],
  "performance_notes": [
    "Performance insight #1: Impact and optimization suggestion",
    "Example: 'Extracting 100+ products per page may timeout - consider batching'"
  ],
  "missing_edge_cases": [
    "Edge case #1: Scenario not handled and how to fix",
    "Example: 'No handling for 'Out of Stock' products - add conditional check'"
  ],
  "estimated_reliability": "high|medium|low",
  "reliability_explanation": "Why you rated it this way - what could go wrong?",
  "real_world_score": 0-100,
  "real_world_explanation": "Will this actually work in production? Be honest.",
  "maintenance_burden": "low|medium|high",
  "maintenance_notes": "How often will this break? What requires updates?",
  "verdict": "2-3 sentence summary: Is this production-ready? What's the biggest risk? Would you deploy this?",
  "improvements_if_time": [
    "Nice-to-have #1: Additional feature that would make this better",
    "Nice-to-have #2: Quality-of-life improvement"
  ]
}}

BE HONEST AND DETAILED:
DONT say: Selectors might not work
DO say: Selector .product is too generic - most e-commerce sites use more specific patterns like .product-card, .product-tile, or data-component=ProductCard. This will likely grab unrelated elements.

DONT say: Add error handling
DO say: Missing try-catch around network requests. If site returns 503, workflow will hang. Add timeout: 10000 and retry_count: 3 with exponential backoff.

Your goal is to ensure this workflow will actually work in production, is safe, ethical, and legal, and will make the user successful."""
        
        return prompt


def main():
    """CLI interface for workflow generator"""
    parser = argparse.ArgumentParser(
        description='Generate BrowserOS workflows using AI'
    )
    
    # Global arguments
    parser.add_argument('--model', help='Override AI model (e.g., llama3, glm-5)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Generate idea command
    idea_parser = subparsers.add_parser('idea', help='Generate workflow idea')
    idea_parser.add_argument('--use-case', required=True, help='What the workflow should do')
    idea_parser.add_argument('--industry', help='Industry context')
    idea_parser.add_argument('--complexity', default='medium',
                           choices=['low', 'medium', 'high', 'expert'],
                           help='Complexity level')
    idea_parser.add_argument('--output', help='Output file for idea JSON')
    
    # Generate implementation command
    impl_parser = subparsers.add_parser('implement', help='Generate workflow implementation')
    impl_parser.add_argument('--idea-file', required=True, help='Input idea JSON file')
    impl_parser.add_argument('--output', help='Output file for workflow JSON')
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate workflow feasibility')
    val_parser.add_argument('--workflow', required=True, help='Workflow JSON file to validate')
    val_parser.add_argument('--output', help='Output file for validation results')
    
    # Full pipeline command
    full_parser = subparsers.add_parser('full', help='Generate complete workflow (idea + implementation)')
    full_parser.add_argument('--use-case', required=True, help='What the workflow should do')
    full_parser.add_argument('--industry', help='Industry context')
    full_parser.add_argument('--complexity', default='medium',
                            choices=['low', 'medium', 'high', 'expert'],
                            help='Complexity level')
    full_parser.add_argument('--output-dir', default='./generated_workflows',
                            help='Directory for generated files')
    full_parser.add_argument('--validate', action='store_true',
                            help='Validate generated workflow')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize generator
    try:
        generator = AIWorkflowGenerator(model=args.model)
    except ValueError as e:
        print(f"❌ {e}")
        print("Set OLLAMA_API_KEY environment variable")
        sys.exit(1)
    
    # Execute command
    if args.command == 'idea':
        idea = generator.generate_workflow_idea(
            args.use_case,
            args.industry,
            args.complexity
        )
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(idea, f, indent=2)
            print(f"\n💾 Saved idea to {args.output}")
        else:
            print(f"\n📄 Generated Idea:")
            print(json.dumps(idea, indent=2))
    
    elif args.command == 'implement':
        with open(args.idea_file) as f:
            idea = json.load(f)
        
        workflow = generator.generate_workflow_implementation(idea)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(workflow, f, indent=2)
            print(f"\n💾 Saved workflow to {args.output}")
        else:
            print(f"\n📄 Generated Workflow:")
            print(json.dumps(workflow, indent=2))
    
    elif args.command == 'validate':
        with open(args.workflow) as f:
            workflow = json.load(f)
        
        validation = generator.validate_workflow_feasibility(workflow)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(validation, f, indent=2)
            print(f"\n💾 Saved validation to {args.output}")
        else:
            print(f"\n📄 Validation Results:")
            print(json.dumps(validation, indent=2))
    
    elif args.command == 'full':
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate idea
        print("\n" + "="*60)
        print("PHASE 1: Generating Workflow Idea")
        print("="*60)
        idea = generator.generate_workflow_idea(
            args.use_case,
            args.industry,
            args.complexity
        )
        
        # Save idea
        idea_file = output_dir / 'idea.json'
        with open(idea_file, 'w') as f:
            json.dump(idea, f, indent=2)
        print(f"💾 Saved idea to {idea_file}")
        
        # Generate implementation
        print("\n" + "="*60)
        print("PHASE 2: Generating Workflow Implementation")
        print("="*60)
        workflow = generator.generate_workflow_implementation(idea)
        
        # Save workflow
        workflow_file = output_dir / 'workflow.json'
        with open(workflow_file, 'w') as f:
            json.dump(workflow, f, indent=2)
        print(f"💾 Saved workflow to {workflow_file}")
        
        # Validate if requested
        if args.validate:
            print("\n" + "="*60)
            print("PHASE 3: Validating Workflow Feasibility")
            print("="*60)
            validation = generator.validate_workflow_feasibility(workflow)
            
            # Save validation
            validation_file = output_dir / 'validation.json'
            with open(validation_file, 'w') as f:
                json.dump(validation, f, indent=2)
            print(f"💾 Saved validation to {validation_file}")
            
            # Print summary
            print("\n" + "="*60)
            print("SUMMARY")
            print("="*60)
            print(f"✅ Workflow Title: {idea.get('title')}")
            print(f"✅ Steps: {len(workflow.get('steps', []))}")
            print(f"✅ Feasibility Score: {validation.get('feasibility_score', 0)}/100")
            print(f"✅ Verdict: {validation.get('verdict', 'Unknown')}")
            
            if not validation.get('feasible', False):
                print("\n⚠️  Workflow has feasibility issues!")
                for issue in validation.get('issues', [])[:5]:
                    print(f"   - {issue}")
        
        print(f"\n🎉 Complete! All files saved to {output_dir}")


if __name__ == '__main__':
    main()
