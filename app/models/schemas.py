# app/models/schemas.py - Updated for Pydantic v2

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict

class ChatMessage(BaseModel):
    # Pydantic v2: Use model_config instead of Config class
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "How do I optimize my resume for tech jobs?",
                "user_id": "user_123"
            }
        }
    )
    
    message: str = Field(..., description="The user's chat message")
    user_id: Optional[str] = Field(default="default_user", description="User identifier")

class ChatResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "Here are some tips for optimizing your resume...",
                "sources": ["resume_guide.pdf", "tech_hiring_trends.txt"],
                "agent_used": "Resume Expert",
                "status": "success",
                "context_used": True
            }
        }
    )
    
    response: str = Field(..., description="AI agent's response")
    sources: Optional[List[str]] = Field(default=[], description="RAG sources used")
    agent_used: Optional[str] = Field(default=None, description="Which agent handled the query")
    status: Optional[str] = Field(default="success", description="Response status")
    context_used: Optional[bool] = Field(default=False, description="Whether RAG context was used")

class HealthCheck(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "message": "All systems operational",
                "services": {
                    "rag_system": "operational",
                    "crew_ai": "operational"
                }
            }
        }
    )
    
    status: str = Field(..., description="Service health status")
    message: str = Field(..., description="Health check message")
    services: Optional[Dict[str, str]] = Field(default=None, description="Individual service statuses")
    
class DocumentUpload(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "career_guide.pdf",
                "content": "This is the content of the career guide..."
            }
        }
    )
    
    filename: str = Field(..., description="Name of the document file")
    content: str = Field(..., description="Document content as text")

class AgentInfo(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Resume Expert",
                "role": "Senior Resume Optimization Specialist",
                "specialization": ["Resume writing", "ATS optimization", "Cover letters"],
                "status": "active"
            }
        }
    )
    
    name: str = Field(..., description="Agent name")
    role: str = Field(..., description="Agent's role")
    specialization: List[str] = Field(..., description="Agent's areas of expertise")
    status: str = Field(default="active", description="Agent status")

class SystemStatus(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "operational",
                "agents": {
                    "career_analyst": "active",
                    "resume_expert": "active"
                },
                "rag_service": {
                    "status": "active",
                    "document_count": 15
                },
                "capabilities": ["Career guidance", "Resume optimization"]
            }
        }
    )
    
    status: str = Field(..., description="Overall system status")
    agents: Dict[str, str] = Field(..., description="Agent statuses")
    rag_service: Dict[str, Any] = Field(..., description="RAG service info")
    capabilities: List[str] = Field(..., description="System capabilities")

class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Failed to process request",
                "type": "processing_error",
                "details": "Agent service temporarily unavailable"
            }
        }
    )
    
    error: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")
    details: Optional[str] = Field(default=None, description="Additional error details")