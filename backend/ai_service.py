"""
AI Service - handles all LLM interactions
Supports mock mode and real Anthropic API
"""

import os
import json
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

USE_REAL_AI = os.getenv("USE_REAL_AI", "false").lower() == "true"

if USE_REAL_AI:
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    MODEL = "claude-sonnet-4-20250514"

class AIService:
    
    @staticmethod
    async def triage_message(message: str, employee_context: dict) -> dict:
        """Analyze message for urgency, categories, sentiment"""
        
        if not USE_REAL_AI:
            return AIService._mock_triage(message)
        
        prompt = f"""You are analyzing a message from an employee seeking financial assistance.

Employee Context:
- Income: ${employee_context.get('annual_income', 'unknown')}
- Credit Score: {employee_context.get('credit_score', 'unknown')}
- Savings: ${employee_context.get('savings', 'unknown')}
- Dependents: {employee_context.get('dependents', 0)}

Employee Message:
"{message}"

Analyze this and respond with ONLY a JSON object (no markdown, no explanation):
{{
  "urgency": "critical|high|medium|low",
  "categories": ["rent", "utilities", "medical", "debt", "transportation", "food"],
  "key_facts": {{
    "amounts": ["$800 rent"],
    "deadlines": ["Friday"],
    "people_affected": 2
  }},
  "sentiment": "desperate|anxious|calm|hopeful",
  "priority_score": 8,
  "reasoning": "Brief explanation of urgency level",
  "suggested_response": "Empathetic opening for Financial Assistant",
  "red_flags": ["eviction with children", "tight deadline"]
}}"""

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
    
    @staticmethod
    async def recommend_resources(case_data: dict, resources: List[dict]) -> List[dict]:
        """Rank resources using LLM"""
        
        if not USE_REAL_AI:
            return AIService._mock_recommendations()
        
        prompt = f"""You are helping a Financial Assistant find resources for this employee:

Employee Situation:
{json.dumps(case_data, indent=2)}

Available Resources:
{json.dumps(resources, indent=2)}

Rank the top 5 resources. Respond with ONLY a JSON array:
[
  {{
    "resource_id": "res_1",
    "relevance_score": 0.95,
    "reasoning": "Specific explanation of why this fits - mention eligibility, timing, amount",
    "estimated_success": 0.85,
    "action_items": ["step 1", "step 2"]
  }}
]"""

        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
    
    @staticmethod
    async def suggest_response(case_context: dict, partial_message: str) -> dict:
        """Real-time conversation suggestions"""
        
        if not USE_REAL_AI:
            return AIService._mock_suggestions()
        
        prompt = f"""You're helping a Financial Assistant respond to an employee.

Case Context:
{json.dumps(case_context, indent=2)}

Financial Assistant is typing: "{partial_message}"

Provide suggestions as JSON:
{{
  "empathy_check": "Suggest empathetic opening if missing, or null",
  "questions_to_ask": ["clarifying questions"],
  "red_flags": ["safety concerns, legal issues"],
  "next_steps": ["concrete actions to suggest"],
  "tone_suggestion": "Brief note on tone if needed"
}}"""

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
    
    @staticmethod
    async def detect_patterns(cases: List[dict]) -> dict:
        """Analyze all cases for systemic patterns"""
        
        if not USE_REAL_AI:
            return AIService._mock_patterns()
        
        prompt = f"""Analyze these financial assistance cases for patterns:

{json.dumps(cases, indent=2)}

Find patterns and respond with JSON:
{{
  "insights": [
    {{
      "type": "employer_issue|geographic|demographic|systemic",
      "severity": "critical|high|medium|low",
      "description": "Clear pattern description",
      "affected_cases": 3,
      "recommendation": "Actionable step",
      "examples": ["case_1", "case_2"]
    }}
  ],
  "trends": {{
    "increasing": ["category names"],
    "stable": ["category names"]
  }}
}}"""

        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
    
    # Mock responses for development
    @staticmethod
    def _mock_triage(message: str) -> dict:
        return {
            "urgency": "critical",
            "categories": ["rent"],
            "key_facts": {
                "amounts": ["$800"],
                "deadlines": ["Friday"],
                "people_affected": 3
            },
            "sentiment": "desperate",
            "priority_score": 10,
            "reasoning": "Immediate eviction threat with children involved",
            "suggested_response": "I understand how stressful this must be with your children. Let's work through this together right away.",
            "red_flags": ["eviction with children", "very tight deadline"]
        }
    
    @staticmethod
    def _mock_recommendations() -> List[dict]:
        return [
            {
                "resource_id": "res_1",
                "relevance_score": 0.95,
                "reasoning": "Amazon employee - hardship fund offers up to $2000 with 2-3 day approval",
                "estimated_success": 0.85,
                "action_items": ["Apply through AtoZ app", "Prepare pay stubs"]
            }
        ]
    
    @staticmethod
    def _mock_suggestions() -> dict:
        return {
            "empathy_check": "Consider starting with acknowledgment of stress",
            "questions_to_ask": [
                "When did you fall behind on rent?",
                "Have you spoken with your landlord?"
            ],
            "red_flags": ["Children involved - may need childcare support"],
            "next_steps": ["Check employer hardship fund", "Draft email to landlord"],
            "tone_suggestion": None
        }
    
    @staticmethod
    def _mock_patterns() -> dict:
        return {
            "insights": [
                {
                    "type": "systemic",
                    "severity": "high",
                    "description": "15% of caseload struggling with medical debt",
                    "affected_cases": 3,
                    "recommendation": "Consider employer health benefits review",
                    "examples": ["case_2", "case_4"]
                }
            ],
            "trends": {
                "increasing": ["medical_debt", "food_insecurity"],
                "stable": ["rent", "utilities"]
            }
        }