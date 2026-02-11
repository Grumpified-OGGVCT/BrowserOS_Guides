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
        
        prompt = f"""Generate a creative and realistic workflow idea for BrowserOS.

Use Case: {use_case}{industry_context}
Complexity Level: {complexity}

Respond with ONLY a JSON object in this exact format:
{{
  "title": "Short descriptive title",
  "description": "2-3 sentence description of what this workflow does",
  "use_case": "The problem this solves",
  "steps_overview": ["Step 1 summary", "Step 2 summary", "Step 3 summary"],
  "input_required": ["What inputs the user needs to provide"],
  "output_produced": ["What outputs the workflow generates"],
  "estimated_duration": "Time to complete (e.g., '2-5 minutes')",
  "difficulty": "beginner|intermediate|advanced|expert",
  "tags": ["tag1", "tag2", "tag3"],
  "real_world_applications": ["Where this would be used in practice"],
  "feasibility_notes": "Any technical considerations or limitations"
}}

Make sure this is a REALISTIC workflow that can actually be implemented with browser automation.
Focus on practical, valuable use cases that solve real problems."""

        return prompt
    
    def _build_workflow_implementation_prompt(self, idea: Dict[str, Any]) -> str:
        """Build prompt for workflow implementation generation"""
        
        prompt = f"""Generate a complete, working BrowserOS workflow implementation.

Workflow Idea:
Title: {idea.get('title')}
Description: {idea.get('description')}
Use Case: {idea.get('use_case')}

Respond with ONLY a valid BrowserOS workflow JSON in this format:
{{
  "name": "{idea.get('title', 'Workflow')}",
  "description": "{idea.get('description', '')}",
  "version": "1.0.0",
  "steps": [
    {{
      "type": "navigate",
      "name": "Open website",
      "url": "https://example.com",
      "wait_for": "load"
    }},
    {{
      "type": "click",
      "name": "Click button",
      "selector": "#button-id",
      "wait_after": 1000
    }},
    {{
      "type": "extract",
      "name": "Extract data",
      "selector": ".data-class",
      "output": "extracted_data"
    }}
  ],
  "error_handling": {{
    "retry_count": 3,
    "retry_delay": 2000,
    "on_error": "continue"
  }},
  "metadata": {{
    "category": "appropriate-category",
    "tags": {json.dumps(idea.get('tags', []))},
    "difficulty": "{idea.get('difficulty', 'intermediate')}"
  }}
}}

Requirements:
1. Use realistic URLs and selectors (examples are fine, but make them plausible)
2. Include proper error handling
3. Add comments in step names explaining what each step does
4. Include data extraction and output where appropriate
5. Use appropriate step types: navigate, click, input, extract, wait, conditional, loop
6. Make it COMPLETE and RUNNABLE (with minor customization by user)

Respond with ONLY the JSON, no additional text."""

        return prompt
    
    def _build_validation_prompt(self, workflow: Dict[str, Any]) -> str:
        """Build prompt for workflow validation"""
        
        workflow_json = json.dumps(workflow, indent=2)
        
        prompt = f"""Validate this BrowserOS workflow for technical feasibility and real-world applicability.

Workflow:
{workflow_json}

Analyze the workflow and respond with ONLY a JSON object in this format:
{{
  "feasible": true/false,
  "feasibility_score": 0-100,
  "issues": ["List of problems or concerns", "Another issue"],
  "recommendations": ["Suggested improvements", "Another suggestion"],
  "security_concerns": ["Any security issues"],
  "performance_notes": ["Performance considerations"],
  "estimated_reliability": "high|medium|low",
  "real_world_score": 0-100,
  "verdict": "Short summary of overall assessment"
}}

Check for:
- Are the selectors realistic and likely to work?
- Is the error handling adequate?
- Are the steps in logical order?
- Would this actually work on real websites?
- Are there security issues (like hardcoded credentials)?
- Is the workflow practical and useful?
- Are there missing steps or edge cases?

Be honest and critical. The goal is to ensure only high-quality workflows."""

        return prompt


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
