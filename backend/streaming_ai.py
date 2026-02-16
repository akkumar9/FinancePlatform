from groq import Groq
import os
import json
from typing import AsyncGenerator

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    return Groq(api_key=api_key)

async def stream_analyze_message(message: str, case_context: dict) -> AsyncGenerator[str, None]:
    """Stream AI analysis in real-time"""
    prompt = f"""Analyze this employee message:

MESSAGE: "{message}"
CONTEXT: Income ${case_context.get('annual_income')}, Credit {case_context.get('credit_score')}

Return ONLY valid JSON:
{{
  "urgency": "critical/high/medium/low",
  "categories": ["rent"],
  "sentiment": "desperate/anxious/calm",
  "priority_score": 10,
  "reasoning": "explanation",
  "suggested_response": "response",
  "red_flags": ["flag"]
}}"""

    client = get_client()
    
    try:
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800,
            stream=True
        )
        
        accumulated = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                accumulated += content
                yield f"data: {json.dumps({'token': content})}\n\n"
        
        # Send final result
        try:
            clean = accumulated.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)
            yield f"data: {json.dumps({'done': True, 'result': result})}\n\n"
        except:
            yield f"data: {json.dumps({'done': True, 'result': accumulated})}\n\n"
            
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

async def stream_resource_recommendations(case_context: dict, resources: list) -> AsyncGenerator[str, None]:
    """Stream resource recommendations"""
    resources_str = "\n".join([f"ID: {r['id']} | {r['name']}" for r in resources[:8]])
    
    prompt = f"""Employee: ${case_context.get('annual_income')} income
Crisis: {', '.join(case_context.get('categories', []))}

Resources:
{resources_str}

Rank top 3 as JSON array:
[{{"resource_id": "res_1", "relevance_score": 0.9, "reasoning": "why", "estimated_success": 0.8}}]"""

    client = get_client()
    
    try:
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            stream=True
        )
        
        accumulated = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                accumulated += content
                yield f"data: {json.dumps({'token': content})}\n\n"
        
        try:
            clean = accumulated.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)
            yield f"data: {json.dumps({'done': True, 'result': result})}\n\n"
        except:
            yield f"data: {json.dumps({'done': True, 'result': []})}\n\n"
            
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
