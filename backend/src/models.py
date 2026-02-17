from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class EmailCategory(str, Enum):
    POLICY_QUERY = "policy_query"
    GENERAL_INQUIRY = "general_inquiry"
    SENSITIVE_MATTER = "sensitive_matter"
    CLARIFICATION_NEEDED = "clarification_needed"
    HUMAN_ESCALATION = "human_escalation"

class EmailInput(BaseModel):
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    sender: str = Field(..., description="Sender email address")
    recipient: Optional[str] = Field(None, description="Recipient email address")

class EmailResponse(BaseModel):
    draft_reply: str = Field(..., description="Generated email reply")
    category: EmailCategory = Field(..., description="Categorized intent of email")
    retrieved_docs: List[Dict[str, Any]] = Field(default=[], description="Retrieved documents used")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the response")
    requires_human_review: bool = Field(False, description="Whether human review is needed")
    clarification_needed: bool = Field(False, description="Whether clarification is needed")
    clarification_question: Optional[str] = Field(None, description="Question to ask sender")

class IngestResponse(BaseModel):
    status: str
    documents_processed: int
    chunks_created: int
    message: str