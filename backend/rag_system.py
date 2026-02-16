import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import json
from typing import List, Dict, Any
import os

# Initialize ChromaDB
chroma_client = chromadb.Client()

# Use sentence transformers for FREE embeddings (no API needed)
model = SentenceTransformer('all-MiniLM-L6-v2')  # small and fast

class RAGSystem:
    def __init__(self):
        # Create collections
        self.resources_collection = chroma_client.create_collection(
            name="financial_resources",
            metadata={"description": "Financial assistance resources"}
        )
        
        self.cases_collection = chroma_client.create_collection(
            name="past_cases",
            metadata={"description": "Historical case outcomes"}
        )
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings using sentence transformers"""
        return model.encode(text).tolist()
    
    def add_resource(self, resource: Dict[str, Any]):
        """Add a resource to vector DB"""
        # Create rich description for better matching
        text = f"""
        {resource['name']}. {resource['description']}
        Eligibility: {resource['eligibility_criteria']}
        Category: {resource['category']}
        Location: {resource.get('location', 'National')}
        Max amount: ${resource.get('max_amount', 'varies')}
        Approval time: {resource['typical_approval_time']}
        """
        
        embedding = self.embed_text(text)
        
        self.resources_collection.add(
            ids=[resource['id']],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "name": resource['name'],
                "category": resource['category'],
                "max_amount": resource.get('max_amount', 0) or 0,
                "success_rate": resource['success_rate'],
                "approval_time": resource['typical_approval_time']
            }]
        )
    
    def search_resources(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Semantic search for resources"""
        query_embedding = self.embed_text(query)
        
        results = self.resources_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results
    
    def add_case(self, case: Dict[str, Any], outcome: Dict[str, Any]):
        """Store a case with its outcome for future reference"""
        # Create searchable description
        text = f"""
        Employee: {case['employee_name']} at {case['employer']}
        Income: ${case['financial_snapshot']['annual_income']}
        Credit: {case['financial_snapshot']['credit_score']}
        Issue: {', '.join(case['categories'])}
        Urgency: {case['urgency']}
        Outcome: {outcome.get('resolution', 'unknown')}
        Resources used: {', '.join(outcome.get('resources_used', []))}
        Success: {outcome.get('success', False)}
        """
        
        embedding = self.embed_text(text)
        
        self.cases_collection.add(
            ids=[f"case_{case['id']}"],
            embeddings=[embedding],
            documents=[text],
            metadatas={
                "employee_name": case['employee_name'],
                "employer": case['employer'],
                "urgency": case['urgency'],
                "success": outcome.get('success', False)
            }
        )
    
    def find_similar_cases(self, current_case: Dict[str, Any], n_results: int = 3) -> List[Dict[str, Any]]:
        """Find similar past cases to learn from"""
        query = f"""
        Income: ${current_case['financial_snapshot']['annual_income']}
        Credit: {current_case['financial_snapshot']['credit_score']}
        Issue: {', '.join(current_case['categories'])}
        Urgency: {current_case['urgency']}
        """
        
        query_embedding = self.embed_text(query)
        
        results = self.cases_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results

# Global instance
rag = RAGSystem()
