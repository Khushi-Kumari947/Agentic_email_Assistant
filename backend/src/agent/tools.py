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
            return "No relevant policy documents found in the company database. Please contact HR directly for assistance with your policy question."
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            # Safely extract document data
            doc = result.get("document", {})
            metadata = doc.get("metadata", {})
            text = doc.get("text", "")
            score = result.get("similarity_score", 0)
            
            # Get source with fallback
            source = metadata.get("source", f"Document {i}")
            document_name = metadata.get("document_name", source)
            
            if text:
                formatted_results.append(
                    f"[Document: {document_name}, Relevance: {score:.2f}]\n"
                    f"Content: {text[:500]}..."
                )
            else:
                formatted_results.append(
                    f"[Document: {document_name}, Relevance: {score:.2f}]\n"
                    f"Content: [No text content available]"
                )
        
        if formatted_results:
            return "\n\n---\n\n".join(formatted_results)
        else:
            return "No relevant policy information found. Please contact HR directly for assistance."
    
    except Exception as e:
        print(f"❌ PolicySearch error: {e}")
        return f"I encountered an error while searching policy documents. Please contact HR directly for assistance with your question."

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