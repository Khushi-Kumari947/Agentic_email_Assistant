from langchain.tools import tool
from typing import Optional
from src.ingestion import vector_store
from src.models import EmailCategory

@tool
def PolicySearch(query: str) -> str:
    """
    Search company policies, SOPs, and internal documents.
    Use this for any policy-related, rule-based, or procedure questions.
    Input should be a specific question or search query.
    """
    try:
        results = vector_store.similarity_search(query, k=3)
        
        if not results:
            return "No relevant policy documents found in the company database."
        
        formatted_results = []
        for result in results:
            doc = result["document"]
            formatted_results.append(
                f"[Document: {doc['metadata']['source']}, "
                f"Relevance: {result['similarity_score']:.2f}]\n"
                f"Content: {doc['text'][:500]}..."  # Truncate for token limits
            )
        
        return "\n\n---\n\n".join(formatted_results)
    
    except Exception as e:
        return f"Error searching policies: {str(e)}"

@tool
def HumanEscalation(reason: str) -> str:
    """
    Escalate sensitive, confidential, or complex matters to human review.
    Use this for HR issues, legal matters, complaints, or unclear requests.
    Input should be the reason for escalation.
    """
    return f"ESCALATION REQUIRED - Human Review Needed: {reason}"

@tool
def DraftEmail(context: str, tone: str = "professional") -> str:
    """
    Draft a professional email based on context and tone.
    Use this to generate the actual email response.
    Input should include the key points to address in the reply.
    """
    return f"DRAFT EMAIL based on: {context} (Tone: {tone})"

@tool
def CheckSensitivity(content: str) -> str:
    """
    Check if email content contains sensitive information that requires escalation.
    Returns 'sensitive' if HR/legal issues detected, 'safe' otherwise.
    """
    sensitive_keywords = [
        "harassment", "discrimination", "complaint", "legal", "lawsuit",
        "hr issue", "termination", "fire", "fired", "sexual", "harass",
        "bullying", "unfair", "lawsuit", "attorney", "lawyer", "court"
    ]
    
    content_lower = content.lower()
    for keyword in sensitive_keywords:
        if keyword in content_lower:
            return f"sensitive - contains keyword: {keyword}"
    
    return "safe"

tools = [PolicySearch, HumanEscalation, DraftEmail, CheckSensitivity]