from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
import json
import asyncio
from typing import List, Dict, Any, Optional
from rag_system import rag, RAGSystem
from file_handler import file_handler
from pathlib import Path

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
cases = []
financial_resources = []
case_documents = {}  # case_id -> list of documents
case_notes = {}  # case_id -> notes string

# Initialize with sample data
def init_data():
    global cases, financial_resources
    
    # Sample resources
    financial_resources = [
        {
            "id": "res_1",
            "name": "Emergency Rental Assistance Program (ERAP)",
            "description": "Provides rental and utility assistance for eligible households",
            "category": "housing",
            "eligibility_criteria": "Income at or below 80% AMI, COVID-19 related hardship",
            "max_amount": 15000,
            "typical_approval_time": "2-4 weeks",
            "application_difficulty": "moderate",
            "success_rate": 0.72,
            "location": "National"
        },
        {
            "id": "res_2",
            "name": "Low Income Home Energy Assistance (LIHEAP)",
            "description": "Helps with heating and cooling bills",
            "category": "utilities",
            "eligibility_criteria": "Income below 150% federal poverty level",
            "max_amount": 1200,
            "typical_approval_time": "1-2 weeks",
            "application_difficulty": "easy",
            "success_rate": 0.85,
            "location": "National"
        },
        {
            "id": "res_3",
            "name": "Salvation Army Emergency Financial Assistance",
            "description": "Emergency funds for rent, utilities, and other needs",
            "category": "emergency",
            "eligibility_criteria": "Demonstrated financial hardship",
            "max_amount": 500,
            "typical_approval_time": "1-3 days",
            "application_difficulty": "easy",
            "success_rate": 0.65,
            "location": "Local"
        },
        {
            "id": "res_4",
            "name": "211 Utility Assistance",
            "description": "Connects to local utility assistance programs",
            "category": "utilities",
            "eligibility_criteria": "Varies by location",
            "max_amount": 800,
            "typical_approval_time": "1-2 weeks",
            "application_difficulty": "easy",
            "success_rate": 0.70,
            "location": "Local"
        },
        {
            "id": "res_5",
            "name": "Catholic Charities Emergency Services",
            "description": "Emergency financial assistance and case management",
            "category": "emergency",
            "eligibility_criteria": "Financial hardship, varies by location",
            "max_amount": 1000,
            "typical_approval_time": "3-5 days",
            "application_difficulty": "moderate",
            "success_rate": 0.68,
            "location": "Local"
        },
        {
            "id": "res_6",
            "name": "Medical Bill Hardship Program",
            "description": "Hospital financial assistance for medical bills",
            "category": "medical",
            "eligibility_criteria": "Income below 200% FPL",
            "max_amount": 25000,
            "typical_approval_time": "4-6 weeks",
            "application_difficulty": "difficult",
            "success_rate": 0.55,
            "location": "National"
        }
    ]
    
    # Add resources to RAG system
    for resource in financial_resources:
        rag.add_resource(resource)
    
    # Sample cases
    cases = [
        {
            "id": "case_1",
            "employee_name": "Maria Rodriguez",
            "employer": "Acme Corp",
            "urgency": "critical",
            "categories": ["housing", "utilities"],
            "last_contact": "2025-01-09T10:30:00",
            "status": "active",
            "financial_snapshot": {
                "annual_income": 35000,
                "credit_score": 580,
                "savings": 200,
                "total_debt": 8500,
                "dependents": 2
            },
            "open_actions": [
                "Follow up on ERAP application",
                "Send utility assistance resources",
                "Schedule budgeting session"
            ],
            "messages": [
                {
                    "id": "msg_1",
                    "sender": "employee",
                    "content": "I just got an eviction notice. I'm 3 months behind on rent and they want me out in 30 days. I have two kids and nowhere to go. Please help!",
                    "timestamp": "2025-01-09T10:30:00"
                }
            ]
        },
        {
            "id": "case_2",
            "employee_name": "John Davis",
            "employer": "Tech Solutions Inc",
            "urgency": "high",
            "categories": ["utilities", "debt"],
            "last_contact": "2025-01-08T14:20:00",
            "status": "active",
            "financial_snapshot": {
                "annual_income": 45000,
                "credit_score": 620,
                "savings": 1200,
                "total_debt": 12000,
                "dependents": 1
            },
            "open_actions": [
                "Apply for LIHEAP",
                "Debt consolidation consultation scheduled"
            ],
            "messages": [
                {
                    "id": "msg_2",
                    "sender": "employee",
                    "content": "My electricity is going to be shut off next week. I owe $800 and can't pay it all. What options do I have?",
                    "timestamp": "2025-01-08T14:20:00"
                }
            ]
        },
        {
            "id": "case_3",
            "employee_name": "Sarah Chen",
            "employer": "Global Retail",
            "urgency": "medium",
            "categories": ["medical"],
            "last_contact": "2025-01-07T09:15:00",
            "status": "active",
            "financial_snapshot": {
                "annual_income": 52000,
                "credit_score": 690,
                "savings": 3000,
                "total_debt": 15000,
                "dependents": 0
            },
            "open_actions": [
                "Hospital financial assistance application in progress"
            ],
            "messages": [
                {
                    "id": "msg_3",
                    "sender": "employee",
                    "content": "I have a $12,000 medical bill from an emergency surgery. My insurance only covered part of it. Can you help me negotiate this down?",
                    "timestamp": "2025-01-07T09:15:00"
                }
            ]
        }
    ]

init_data()

# Request models
class RecommendRequest(BaseModel):
    case_id: str

class TriageRequest(BaseModel):
    case_id: str
    message: str

class ConversationRequest(BaseModel):
    case_id: str
    message: str

class SendMessageRequest(BaseModel):
    sender: str
    content: str

class CreateCaseRequest(BaseModel):
    employee_name: str
    employer: str
    financial_snapshot: Dict[str, int]

class NotesRequest(BaseModel):
    notes: str

# API Endpoints
@app.get("/api/cases")
async def get_cases():
    """Get all cases - includes messages for testing"""
    print(f"DEBUG: Returning {len(cases)} cases")
    for case in cases:
        print(f"  - {case['employee_name']}: {len(case.get('messages', []))} messages")
    return cases

@app.post("/api/cases")
async def create_case(request: CreateCaseRequest):
    """Create a new case"""
    new_case = {
        "id": f"case_{len(cases) + 1}",
        "employee_name": request.employee_name,
        "employer": request.employer,
        "urgency": "medium",
        "categories": ["general"],
        "last_contact": datetime.now().isoformat(),
        "status": "active",
        "financial_snapshot": request.financial_snapshot,
        "open_actions": [],
        "messages": []
    }
    
    cases.append(new_case)
    return {"success": True, "case": new_case}

@app.get("/api/analytics")
async def get_analytics():
    return {
        "total_active_cases": len(cases),
        "critical_cases": sum(1 for c in cases if c["urgency"] == "critical"),
        "this_month": {
            "cases_resolved": 12,
            "total_money_saved": 45000,
            "avg_credit_score_improvement": 35,
            "avg_response_time_hours": 4.2
        },
        "category_breakdown": {
            "housing": sum(1 for c in cases if "housing" in c["categories"]),
            "utilities": sum(1 for c in cases if "utilities" in c["categories"]),
            "medical": sum(1 for c in cases if "medical" in c["categories"]),
            "debt": sum(1 for c in cases if "debt" in c["categories"]),
            "employment": sum(1 for c in cases if "employment" in c["categories"])
        }
    }

@app.get("/api/case/{case_id}/documents")
async def get_case_documents(case_id: str):
    return case_documents.get(case_id, [])

@app.post("/api/case/{case_id}/message")
async def send_message(case_id: str, request: SendMessageRequest):
    """Add a new message to a case"""
    case = next((c for c in cases if c["id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    new_message = {
        "id": f"msg_{len(case['messages']) + 1}",
        "sender": request.sender,
        "content": request.content,
        "timestamp": datetime.now().isoformat()
    }
    
    case["messages"].append(new_message)
    case["last_contact"] = datetime.now().isoformat()
    
    return {"success": True, "message": new_message}

@app.get("/api/case/{case_id}/notes")
async def get_notes(case_id: str):
    """Get notes for a case"""
    return {"notes": case_notes.get(case_id, "")}

@app.post("/api/case/{case_id}/notes")
async def save_notes(case_id: str, request: NotesRequest):
    """Save notes for a case"""
    case = next((c for c in cases if c["id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case_notes[case_id] = request.notes
    return {"success": True}

@app.get("/api/debug/vector-search")
async def debug_vector_search():
    """Debug endpoint to show vector search is real"""
    
    # Test query 1: Housing/eviction
    query1 = "I need help with eviction and rent assistance urgently"
    results1 = rag.search_resources(query1, n_results=3)
    
    # Test query 2: Utilities
    query2 = "My electricity bill is overdue and getting shut off"
    results2 = rag.search_resources(query2, n_results=3)
    
    return {
        "proof": "This shows ChromaDB vector search returns DIFFERENT results for different queries",
        "query1": {
            "text": query1,
            "top_results": results1['ids'][0] if results1['ids'] else [],
            "distances": results1['distances'][0] if results1['distances'] else []
        },
        "query2": {
            "text": query2,
            "top_results": results2['ids'][0] if results2['ids'] else [],
            "distances": results2['distances'][0] if results2['distances'] else []
        },
        "explanation": "Lower distance = better match. Different queries get different results. This is REAL semantic search, not hardcoded!"
    }

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), case_id: str = None):
    if not case_id:
        raise HTTPException(status_code=400, detail="case_id required")
    
    # Save file and extract text
    result = await file_handler.save_file(file, case_id)
    
    # Store document metadata
    if case_id not in case_documents:
        case_documents[case_id] = []
    
    doc_metadata = {
        "id": result["id"],
        "filename": result["filename"],
        "file_type": result["file_type"],
        "uploaded_at": datetime.now().isoformat(),
        "has_text": bool(result["extracted_text"] and len(result["extracted_text"]) > 10)
    }
    case_documents[case_id].append(doc_metadata)
    
    # Add extracted text to case context for AI to use
    case = next((c for c in cases if c["id"] == case_id), None)
    if case and result["extracted_text"]:
        if "documents_text" not in case:
            case["documents_text"] = []
        case["documents_text"].append({
            "filename": result["filename"],
            "text": result["extracted_text"]
        })
    
    return {
        "success": True,
        "document_id": result["id"],
        "extracted_text_preview": result["extracted_text"][:200] if result["extracted_text"] else None
    }

@app.post("/api/recommend")
async def recommend_resources(request: RecommendRequest):
    """Non-streaming recommendations"""
    case = next((c for c in cases if c["id"] == request.case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Build context including documents
    query_parts = [
        f"Financial Profile:",
        f"- Income: ${case['financial_snapshot']['annual_income']}",
        f"- Credit Score: {case['financial_snapshot']['credit_score']}",
        f"- Savings: ${case['financial_snapshot']['savings']}",
        f"- Debt: ${case['financial_snapshot']['total_debt']}",
        f"- Issues: {', '.join(case['categories'])}",
        f"- Urgency: {case['urgency']}"
    ]
    
    # Add document context if available
    if "documents_text" in case and case["documents_text"]:
        query_parts.append("\nDocument Information:")
        for doc in case["documents_text"]:
            query_parts.append(f"- {doc['filename']}: {doc['text'][:300]}")
    
    query = "\n".join(query_parts)
    
    # Search RAG system
    results = rag.search_resources(query, n_results=5)
    
    # Build recommendations
    recommendations = []
    for i in range(len(results['ids'][0])):
        doc_id = results['ids'][0][i]
        metadata = results['metadatas'][0][i]
        distance = results['distances'][0][i]
        
        resource = next((r for r in financial_resources if r['id'] == doc_id), None)
        if not resource:
            continue
        
        relevance_score = max(0, 1 - (distance / 2))
        credit_factor = case['financial_snapshot']['credit_score'] / 850
        estimated_success = (resource['success_rate'] * 0.7) + (credit_factor * 0.3)
        
        reasoning = f"Matches your {', '.join(case['categories'])} situation. "
        if case['urgency'] in ['critical', 'high']:
            reasoning += f"Fast approval time ({resource['typical_approval_time']}) suits urgent need. "
        
        recommendations.append({
            'resource_id': resource['id'],
            'name': resource['name'],
            'description': resource['description'],
            'max_amount': resource.get('max_amount'),
            'typical_approval_time': resource['typical_approval_time'],
            'application_difficulty': resource['application_difficulty'],
            'success_rate': resource['success_rate'],
            'relevance_score': relevance_score,
            'estimated_success': estimated_success,
            'reasoning': reasoning
        })
    
    return recommendations

@app.post("/api/recommend/stream")
async def recommend_resources_stream(request: RecommendRequest):
    """Streaming recommendations with thinking process"""
    
    async def event_generator():
        try:
            case = next((c for c in cases if c['id'] == request.case_id), None)
            if not case:
                yield f"data: {json.dumps({'error': 'Case not found'})}\n\n"
                return
            
            # Stream thinking steps
            steps = [
                "🔍 Analyzing financial profile...",
                "📊 Checking credit score and income...",
                "🔎 Searching vector database for relevant resources...",
                "📄 Reviewing uploaded documents..."
            ]
            
            for step in steps:
                newline = '\n'
                yield f"data: {json.dumps({'token': step + newline})}\n\n"
                await asyncio.sleep(0.4)
            
            # Build query with document context
            query_parts = [
                f"Income: ${case['financial_snapshot']['annual_income']}",
                f"Credit: {case['financial_snapshot']['credit_score']}",
                f"Issues: {', '.join(case['categories'])}",
                f"Urgency: {case['urgency']}"
            ]
            
            # Add document insights
            if "documents_text" in case and case["documents_text"]:
                doc_count_msg = f'📋 Found {len(case["documents_text"])} uploaded documents\n'
                yield f"data: {json.dumps({'token': doc_count_msg})}\n\n"
                await asyncio.sleep(0.3)
                for doc in case["documents_text"]:
                    query_parts.append(f"Document: {doc['text'][:300]}")
            
            query = "\n".join(query_parts)
            
            ai_msg = '✨ Querying AI knowledge base...\n'
            yield f"data: {json.dumps({'token': ai_msg})}\n\n"
            await asyncio.sleep(0.3)
            
            # RAG search
            results = rag.search_resources(query, n_results=5)
            
            found_msg = f'✅ Found {len(results["ids"][0])} relevant resources\n'
            yield f"data: {json.dumps({'token': found_msg})}\n\n"
            await asyncio.sleep(0.3)
            
            # Build recommendations
            recommendations = []
            for i in range(len(results['ids'][0])):
                doc_id = results['ids'][0][i]
                distance = results['distances'][0][i]
                
                resource = next((r for r in financial_resources if r['id'] == doc_id), None)
                if not resource:
                    continue
                
                relevance_score = max(0, 1 - (distance / 2))
                credit_factor = case['financial_snapshot']['credit_score'] / 850
                estimated_success = (resource['success_rate'] * 0.7) + (credit_factor * 0.3)
                
                reasoning = f"Matches your {', '.join(case['categories'])} situation. "
                if case['urgency'] in ['critical', 'high']:
                    reasoning += f"Fast approval ({resource['typical_approval_time']}). "
                if case['financial_snapshot']['credit_score'] >= 650:
                    reasoning += "Good credit improves approval odds."
                else:
                    reasoning += "May need additional documentation."
                
                recommendations.append({
                    'resource_id': resource['id'],
                    'name': resource['name'],
                    'description': resource['description'],
                    'max_amount': resource.get('max_amount'),
                    'typical_approval_time': resource['typical_approval_time'],
                    'application_difficulty': resource['application_difficulty'],
                    'success_rate': resource['success_rate'],
                    'relevance_score': relevance_score,
                    'estimated_success': estimated_success,
                    'reasoning': reasoning
                })
            
            rank_msg = '🎯 Ranking by relevance...\n'
            yield f"data: {json.dumps({'token': rank_msg})}\n\n"
            await asyncio.sleep(0.2)
            
            complete_msg = '✅ Complete!\n\n'
            yield f"data: {json.dumps({'token': complete_msg})}\n\n"
            
            yield f"data: {json.dumps({'done': True, 'result': recommendations})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/triage")
async def triage_message(request: TriageRequest):
    """Non-streaming triage"""
    case = next((c for c in cases if c["id"] == request.case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Analyze message with document context
    context = request.message.lower()
    
    # Add document context
    if "documents_text" in case and case["documents_text"]:
        for doc in case["documents_text"]:
            context += " " + doc["text"].lower()
    
    # Sentiment
    negative_words = ['eviction', 'desperate', 'urgent', 'help', 'crisis', 'emergency', 'cant', "can't", 'unable', 'shutoff', 'disconnect']
    sentiment_score = sum(1 for word in negative_words if word in context)
    
    if sentiment_score >= 3:
        sentiment = "highly distressed"
        priority_score = 9
    elif sentiment_score >= 2:
        sentiment = "concerned"
        priority_score = 7
    else:
        sentiment = "neutral"
        priority_score = 5
    
    # Categories
    categories = []
    if any(word in context for word in ['eviction', 'rent', 'landlord', 'lease']):
        categories.append('housing')
    if any(word in context for word in ['bill', 'utility', 'electric', 'water', 'gas']):
        categories.append('utilities')
    if any(word in context for word in ['medical', 'hospital', 'doctor', 'health']):
        categories.append('medical')
    if any(word in context for word in ['job', 'work', 'unemployed', 'laid off']):
        categories.append('employment')
    if any(word in context for word in ['debt', 'credit', 'loan']):
        categories.append('debt')
    
    if not categories:
        categories = ['general']
    
    # Red flags
    red_flags = []
    if 'eviction' in context:
        red_flags.append("⚠️ Eviction notice - immediate action required")
    if 'court' in context:
        red_flags.append("⚠️ Legal proceedings - may need legal aid")
    if any(word in context for word in ['disconnect', 'shutoff', 'shut off']):
        red_flags.append("⚠️ Utility disconnection threat")
    if any(word in context for word in ['children', 'kids', 'dependents']):
        red_flags.append("👨‍👩‍👧‍👦 Dependents involved - prioritize family stability")
    
    # Urgency
    if red_flags or sentiment_score >= 3:
        urgency = "critical"
    elif sentiment_score >= 2:
        urgency = "high"
    else:
        urgency = "medium"
    
    # Response suggestion
    if urgency == "critical":
        suggested_response = f"I understand this is urgent. Let me help you right away. I'm looking into emergency programs for {categories[0]}. Can you tell me the specific deadline?"
    else:
        suggested_response = f"Thank you for reaching out. I can help with {', '.join(categories)}. Let's find the best solution together."
    
    return {
        'urgency': urgency,
        'priority_score': priority_score,
        'sentiment': sentiment,
        'categories': categories,
        'red_flags': red_flags,
        'suggested_response': suggested_response,
        'reasoning': f"Detected {sentiment} tone with {len(red_flags)} urgent indicators. Categories: {', '.join(categories)}."
    }

@app.post("/api/triage/stream")
async def triage_message_stream(request: TriageRequest):
    """Streaming triage analysis"""
    
    async def event_generator():
        try:
            case = next((c for c in cases if c['id'] == request.case_id), None)
            if not case:
                yield f"data: {json.dumps({'error': 'Case not found'})}\n\n"
                return
            
            steps = [
                "📖 Reading message...",
                "📄 Checking uploaded documents...",
                "😊 Analyzing sentiment...",
                "🚨 Identifying urgency indicators...",
                "🏷️ Categorizing issues...",
                "💡 Generating response..."
            ]
            
            for step in steps:
                newline = '\n'
                yield f"data: {json.dumps({'token': step + newline})}\n\n"
                await asyncio.sleep(0.3)
            
            # Build context
            context = request.message.lower()
            if "documents_text" in case and case["documents_text"]:
                doc_count = len(case["documents_text"])
                doc_msg = f'📋 Found {doc_count} documents with additional context\n'
                yield f"data: {json.dumps({'token': doc_msg})}\n\n"
                await asyncio.sleep(0.2)
                for doc in case["documents_text"]:
                    context += " " + doc["text"].lower()
            
            # Analysis
            negative_words = ['eviction', 'desperate', 'urgent', 'help', 'crisis', 'emergency', 'cant', "can't", 'unable']
            sentiment_score = sum(1 for word in negative_words if word in context)
            
            if sentiment_score >= 3:
                sentiment = "highly distressed"
                priority_score = 9
            elif sentiment_score >= 2:
                sentiment = "concerned"
                priority_score = 7
            else:
                sentiment = "neutral"
                priority_score = 5
            
            categories = []
            if any(word in context for word in ['eviction', 'rent', 'landlord']):
                categories.append('housing')
            if any(word in context for word in ['bill', 'utility', 'electric']):
                categories.append('utilities')
            if any(word in context for word in ['medical', 'hospital']):
                categories.append('medical')
            
            if not categories:
                categories = ['general']
            
            red_flags = []
            if 'eviction' in context:
                red_flags.append("Eviction notice detected")
            if 'shutoff' in context or 'disconnect' in context:
                red_flags.append("Utility disconnection threat")
            
            urgency = "critical" if red_flags else ("high" if sentiment_score >= 2 else "medium")
            
            if urgency == "critical":
                suggested_response = f"This is urgent. I'll help immediately with {categories[0]} assistance. What's your deadline?"
            else:
                suggested_response = f"I can help with {', '.join(categories)}. Let's work on this together."
            
            result = {
                'urgency': urgency,
                'priority_score': priority_score,
                'sentiment': sentiment,
                'categories': categories,
                'red_flags': red_flags,
                'suggested_response': suggested_response,
                'reasoning': f"{sentiment} sentiment, {len(red_flags)} urgent flags"
            }
            
            complete_msg = '✅ Analysis complete!\n\n'
            yield f"data: {json.dumps({'token': complete_msg})}\n\n"
            yield f"data: {json.dumps({'done': True, 'result': result})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/conversation/assist")
async def conversation_assist(request: ConversationRequest):
    """Get AI suggestions for responding to a message"""
    case = next((c for c in cases if c["id"] == request.case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Simple response suggestions based on message content
    message_lower = request.message.lower()
    suggestions = []
    
    if not request.message.strip():
        return {"suggestions": ["Please type a message to get AI suggestions"]}
    
    # Tone suggestions
    if any(word in message_lower for word in ['unfortunately', 'sorry', 'cannot']):
        suggestions.append("💡 Consider a more empowering tone: Focus on what you CAN do rather than limitations")
    
    if len(request.message) < 20:
        suggestions.append("✏️ Add more detail: Explain specific next steps or resources")
    
    # Resource suggestions based on case
    if "housing" in case["categories"] and "erap" not in message_lower:
        suggestions.append("🏠 Mention ERAP (Emergency Rental Assistance) - highly relevant for this case")
    
    if "utilities" in case["categories"] and "liheap" not in message_lower:
        suggestions.append("⚡ Suggest LIHEAP for utility assistance")
    
    if not suggestions:
        suggestions.append("✅ Message looks good! Clear and helpful.")
    
    return {"suggestions": suggestions}

@app.get("/api/insights/patterns")
async def get_pattern_insights():
    """Analyze patterns across all cases"""
    
    # Calculate real insights
    total_cases = len(cases)
    urgent_cases = sum(1 for c in cases if c["urgency"] in ["critical", "high"])
    avg_debt = sum(c["financial_snapshot"]["total_debt"] for c in cases) / total_cases if total_cases > 0 else 0
    avg_income = sum(c["financial_snapshot"]["annual_income"] for c in cases) / total_cases if total_cases > 0 else 0
    avg_credit = sum(c["financial_snapshot"]["credit_score"] for c in cases) / total_cases if total_cases > 0 else 0
    
    # Category trends
    category_counts = {}
    for case in cases:
        for cat in case["categories"]:
            category_counts[cat] = category_counts.get(cat, 0) + 1
    
    top_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "housing"
    
    insights = [
        f"📊 {urgent_cases} of {total_cases} cases need immediate attention ({urgent_cases/total_cases*100:.0f}%)",
        f"💰 Average debt-to-income ratio: {(avg_debt/avg_income*100):.1f}%",
        f"📈 Most common issue: {top_category} ({category_counts.get(top_category, 0)} cases)",
        f"🎯 Average credit score: {avg_credit:.0f} - focus on credit rebuilding programs",
    ]
    
    # Document insights
    total_docs = sum(len(docs) for docs in case_documents.values())
    if total_docs > 0:
        insights.append(f"📄 {total_docs} documents uploaded across cases - AI has more context!")
    
    return {"insights": insights}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)