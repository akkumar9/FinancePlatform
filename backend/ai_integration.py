from groq import Groq
import os
from typing import Dict, Any, List
import json
from rag_system import rag

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    return Groq(api_key=api_key)

async def analyze_message(message: str, case_context: Dict[str, Any]) -> Dict[str, Any]:
    # Find similar past cases for context
    similar_cases = rag.find_similar_cases({
        'financial_snapshot': case_context,
        'categories': ['rent'],  # would come from case
        'urgency': 'critical'
    }, n_results=2)
    
    past_cases_context = ""
    if similar_cases and similar_cases['documents']:
        past_cases_context = f"\n\nSimilar past cases:\n" + "\n".join(similar_cases['documents'][0][:2])
    
    prompt = f"""Analyze this employee message:

MESSAGE: "{message}"
CONTEXT: Income ${case_context.get('annual_income')}, Credit {case_context.get('credit_score')}, Dependents {case_context.get('dependents')}
{past_cases_context}

Return ONLY valid JSON:
{{
  "urgency": "critical/high/medium/low",
  "categories": ["rent", "utilities", "medical"],
  "sentiment": "desperate/anxious/calm",
  "priority_score": 10,
  "reasoning": "explanation",
  "suggested_response": "empathetic response",
  "red_flags": ["flag1"]
}}"""

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error: {e}")
        return {"urgency": "medium", "categories": ["other"], "sentiment": "anxious", "priority_score": 5, "reasoning": "Error", "suggested_response": "Let me help.", "red_flags": []}

async def recommend_resources(case_context: Dict[str, Any], resources: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    # Build search query from case context
    search_query = f"""
    Need financial help. Income ${case_context.get('annual_income')}, credit score {case_context.get('credit_score')}.
    Crisis: {', '.join(case_context.get('categories', []))}
    Urgency: {case_context.get('urgency')}
    Employer: {case_context.get('employer')}
    """
    
    # RAG SEMANTIC SEARCH - finds resources even if exact keywords don't match
    vector_results = rag.search_resources(search_query, n_results=8)
    
    # Get the actual resource IDs from vector search
    top_resource_ids = vector_results['ids'][0] if vector_results['ids'] else []
    
    # Filter resources to only those found by RAG
    relevant_resources = [r for r in resources if r['id'] in top_resource_ids]
    
    if not relevant_resources:
        relevant_resources = resources[:5]  # fallback
    
    resources_str = "\n".join([
        f"ID: {r['id']} | {r['name']}: {r['description']} | Similarity: {vector_results['distances'][0][vector_results['ids'][0].index(r['id'])] if r['id'] in top_resource_ids else 'N/A'}"
        for r in relevant_resources[:8]
    ])
    
    prompt = f"""Employee: ${case_context.get('annual_income')} income, {case_context.get('credit_score')} credit
Crisis: {', '.join(case_context.get('categories', []))}
Employer: {case_context.get('employer')}

RAG found these relevant resources (ranked by semantic similarity):
{resources_str}

Rank top {limit} as JSON array. Use the similarity scores to guide your ranking:
[{{"resource_id": "res_1", "relevance_score": 0.9, "reasoning": "specific reason with timing/amount/eligibility", "estimated_success": 0.8}}]"""

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        content = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error: {e}")
        return []

async def suggest_response(case_context: Dict[str, Any], partial_message: str) -> Dict[str, Any]:
    if len(partial_message) < 10:
        return {}
    
    prompt = f"""FA typing: "{partial_message}"
Case: {case_context.get('urgency')}

Suggest as JSON: {{"empathy_check": "", "questions_to_ask": [], "red_flags": [], "next_steps": []}}"""

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        content = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error: {e}")
        return {}

async def detect_patterns(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    prompt = f"""Analyze {len(cases)} cases for patterns. Return JSON with insights and trends."""
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        content = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error: {e}")
        return {"insights": [], "trends": {}}
