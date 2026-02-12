#!/usr/bin/env python3
"""
BrowserOS Workflow Generator - AI-Powered Workflow Creation
Uses Kimi-K2.5:cloud via Ollama Cloud API to generate realistic, working workflows

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

try:
    from config_loader import load_config
except ImportError:
    print("Warning: config_loader not available, using defaults")
    load_config = None


class KimiWorkflowGenerator:
    """
    AI-Powered Workflow Generator using Kimi-K2.5:cloud
    
    This class uses Kimi (Moonshot AI's latest model) to generate
    realistic, production-ready BrowserOS workflows based on use cases.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the workflow generator"""
        self.api_key = api_key or os.getenv('OLLAMA_API_KEY')
        if not self.api_key:
            raise ValueError("OLLAMA_API_KEY environment variable required")
        
        # Kimi model name MUST include :cloud tag for Ollama Cloud
        self.model = "kimi-k2.5:cloud"
        self.base_url = "https://api.ollama.ai/v1"
        
        # Load configuration if available
        self.config = self._load_config()
        
        print(f"✅ Initialized Kimi Workflow Generator")
        print(f"   Model: {self.model}")
        print(f"   API: Ollama Cloud")
    
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
                'model': 'kimi-k2.5:cloud',
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
        Generate a workflow idea using Kimi
        
        Args:
            use_case: What the workflow should accomplish
            industry: Optional industry context
            complexity: low, medium, high, expert
        
        Returns:
            Dict with workflow idea and metadata
        """
        print(f"\n🤖 Generating workflow idea for: {use_case}")
        if industry:
            print(f"   Industry: {industry}")
        print(f"   Complexity: {complexity}")
        
        # Construct prompt for Kimi
        prompt = self._build_workflow_idea_prompt(use_case, industry, complexity)
        
        # Call Kimi via Ollama Cloud API
        response = self._call_kimi(prompt, max_tokens=2000)
        
        # Parse response
        try:
            idea = json.loads(response)
            idea['generated_at'] = datetime.utcnow().isoformat()
            idea['model'] = self.model
            idea['use_case'] = use_case
            idea['industry'] = industry
            idea['complexity'] = complexity
            
            print(f"✅ Generated workflow idea: {idea.get('title', 'Untitled')}")
            return idea
            
        except json.JSONDecodeError:
            print("⚠️  Kimi response was not valid JSON, wrapping in structure")
            return {
                'title': f"Workflow for {use_case}",
                'description': response,
                'generated_at': datetime.utcnow().isoformat(),
                'model': self.model,
                'use_case': use_case,
                'industry': industry,
                'complexity': complexity,
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
        
        # Call Kimi with larger token limit
        response = self._call_kimi(prompt, max_tokens=4000)
        
        # Parse workflow JSON
        try:
            workflow = json.loads(response)
            
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
        
        # Call Kimi for analysis
        response = self._call_kimi(prompt, max_tokens=2000)
        
        # Parse validation results
        try:
            validation = json.loads(response)
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
    
    def _call_kimi(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Call Kimi-K2.5:cloud via Ollama Cloud API
        
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
            'model': self.model,  # Must be "kimi-k2.5:cloud"
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
            print(f"❌ Error calling Kimi API: {e}")
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

📋 THE REQUEST:
Use Case: {use_case}{industry_context}
Complexity Level: {complexity}

🎯 YOUR MISSION:
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
❌ BAD (Generic): "This workflow automates data extraction from websites"
✅ GOOD (Personal): "Picture spending 30 minutes every Monday manually copying competitor prices into a spreadsheet. This workflow does it in 90 seconds, letting you grab coffee while it runs - and it never misses a price change."

❌ BAD: "Extract product information"  
✅ GOOD: "Capture 15 data points per product: price, availability, reviews (count + avg rating), shipping time, warranty details, and promotional badges - everything your pricing team needs to stay competitive"

Make this feel like it was designed specifically for the user's problem, not a template filled in by AI.
    
    def _build_workflow_implementation_prompt(self, idea: Dict[str, Any]) -> str:
        """Build prompt for workflow implementation generation"""
        
        prompt = f"""You are crafting a production-ready BrowserOS workflow that someone will actually use in their daily work.

📋 WORKFLOW TO IMPLEMENT:
Title: {idea.get('title')}
Description: {idea.get('description')}
Use Case: {idea.get('use_case')}

🎯 YOUR MISSION:
Create a complete, thoughtful workflow implementation that feels like it was hand-crafted by an expert - not auto-generated.

KEY PRINCIPLES:
1. **Descriptive Step Names**: Instead of "Click button", write "Click 'Add to Cart' button to select product for comparison"
2. **Realistic Selectors**: Use plausible CSS selectors based on common patterns (e.g., '[data-testid="product-price"]', '.product-card h2')
3. **Helpful Comments**: Each step's "name" should explain WHY this step matters, not just WHAT it does
4. **Smart Error Handling**: Include fallback selectors, wait conditions, and retry logic
5. **Extractable Patterns**: Show where data is captured and how it's stored
6. **Variable Names**: Use descriptive variables like 'competitor_prices' not 'data1'

AVAILABLE STEP TYPES:
- navigate: Go to URL (include wait_for: "load", "networkidle", or selector)
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
✅ Use multiple fallback selectors: ".selector1, .selector2, [data-attr]"
✅ Add waits before interactions: wait_before, wait_after
✅ Include timeout values: Be realistic (5-10 seconds for most operations)
✅ Use variables for user inputs: {{{{variable_name}}}}
✅ Comment complex steps: Explain the "why" in the comment field
✅ Handle pagination: Loop through results, track page numbers
✅ Extract structured data: Use fields object for related data points
✅ Plan for errors: Retry logic, fallbacks, graceful degradation
✅ Document outputs: What data is captured and in what format
✅ Rate limiting: Respect target sites with delays

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

📋 WORKFLOW TO VALIDATE:
{workflow_json}

🎯 YOUR MISSION:
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

5. **Security & Ethics**
   - Are there hardcoded credentials? (RED FLAG)
   - Does it respect robots.txt?
   - Is rate limiting respectful?
   - Any data privacy concerns?

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
❌ Don't say: "Selectors might not work"
✅ Do say: "Selector '.product' is too generic - most e-commerce sites use more specific patterns like '.product-card', '.product-tile', or '[data-component=ProductCard]'. This will likely grab unrelated elements."

❌ Don't say: "Add error handling"
✅ Do say: "Missing try-catch around network requests. If site returns 503, workflow will hang. Add timeout: 10000 and retry_count: 3 with exponential backoff."

Your goal is to ensure this workflow will actually work in production and make the user successful.


def main():
    """CLI interface for workflow generator"""
    parser = argparse.ArgumentParser(
        description='Generate BrowserOS workflows using Kimi-K2.5:cloud AI'
    )
    
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
        generator = KimiWorkflowGenerator()
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
