# app/models/schemas.py - Updated for Pydantic v2

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime

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

# New models for blog and contact features
class BlogPost(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "How to Ace Your Job Interview",
                "content": "This is the blog content...",
                "excerpt": "Learn the best practices for job interviews",
                "author": "Career Expert",
                "tags": ["interview", "career", "tips"],
                "featured_image": "https://example.com/image.jpg",
                "status": "published"
            }
        }
    )
    
    title: str = Field(..., description="Blog post title")
    content: str = Field(..., description="Blog post content")
    excerpt: Optional[str] = Field(default=None, description="Blog post excerpt")
    author: str = Field(..., description="Author name")
    tags: List[str] = Field(default=[], description="Blog post tags")
    featured_image: Optional[str] = Field(default=None, description="Featured image URL")
    status: str = Field(default="draft", description="Post status: draft, published, archived")
    published_at: Optional[datetime] = Field(default=None, description="Publication date")

class BlogPostResponse(BaseModel):
    id: str = Field(..., description="Blog post ID")
    title: str = Field(..., description="Blog post title")
    content: str = Field(..., description="Blog post content")
    excerpt: Optional[str] = Field(default=None, description="Blog post excerpt")
    author: str = Field(..., description="Author name")
    tags: List[str] = Field(default=[], description="Blog post tags")
    featured_image: Optional[str] = Field(default=None, description="Featured image URL")
    status: str = Field(default="draft", description="Post status")
    created_at: datetime = Field(..., description="Creation date")
    updated_at: datetime = Field(..., description="Last update date")
    published_at: Optional[datetime] = Field(default=None, description="Publication date")

class ContactSubmission(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "subject": "Career Guidance Inquiry",
                "message": "I need help with career planning..."
            }
        }
    )
    
    name: str = Field(..., description="Contact person name")
    email: str = Field(..., description="Contact email")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    subject: str = Field(..., description="Message subject")
    message: str = Field(..., description="Message content")

class ContactSubmissionResponse(BaseModel):
    id: str = Field(..., description="Contact submission ID")
    name: str = Field(..., description="Contact person name")
    email: str = Field(..., description="Contact email")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    subject: str = Field(..., description="Message subject")
    message: str = Field(..., description="Message content")
    status: str = Field(default="new", description="Status: new, read, replied, archived")
    created_at: datetime = Field(..., description="Submission date")
    read_at: Optional[datetime] = Field(default=None, description="When message was read")
    replied_at: Optional[datetime] = Field(default=None, description="When reply was sent")