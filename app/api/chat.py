from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.schemas import ChatMessage, ChatResponse, HealthCheck
from app.services.chat_service import ChatService
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Global chat service instance and async init lock to prevent race conditions
chat_service = None
_init_lock = asyncio.Lock()

async def get_chat_service():
    """Get or initialize chat service in a thread-safe manner"""
    global chat_service
    if chat_service is None:
        async with _init_lock:
            if chat_service is None:
                try:
                    logger.info("Initializing chat service (once)...")
                    chat_service = ChatService()
                    logger.info("Chat service initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize chat service: {e}")
                    chat_service = None
    return chat_service

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint to verify service status"""
    try:
        # Initialize once here under lock
        service = await get_chat_service()
        if not service or not service.initialized:
            return HealthCheck(
                status="unhealthy", 
                message="Chat service failed to initialize"
            )
        
        health_status = service.health_check()
        return HealthCheck(
            status=health_status["status"],
            message=health_status["message"],
            services=health_status.get("services")
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheck(
            status="unhealthy",
            message=f"Health check failed: {str(e)}"
        )

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Main chat endpoint for career guidance"""
    try:
        service = await get_chat_service()
        if not service:
            raise HTTPException(
                status_code=503, 
                detail="Chat service is not available. Please try again later."
            )
        
        if not message.message or not message.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        logger.info(f"Received chat message from user: {message.user_id}")
        
        # Process the message
        result = service.process_message(message.message, message.user_id)
        
        # Ensure response matches schema
        response = ChatResponse(
            response=result.get("response", "I apologize, but I couldn't process your request."),
            sources=result.get("sources", []),
            agent_used=result.get("agent_used"),
            status=result.get("status", "success"),
            context_used=result.get("context_used", False)
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail="I'm experiencing some technical difficulties. Please try again or rephrase your question."
        )

@router.post("/chat/comprehensive", response_model=ChatResponse)
async def comprehensive_chat(message: ChatMessage):
    """Comprehensive chat endpoint using multiple agents"""
    try:
        service = await get_chat_service()
        if not service:
            raise HTTPException(
                status_code=503,
                detail="Chat service is not available"
            )
        
        if not message.message or not message.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        logger.info(f"Received comprehensive chat request from user: {message.user_id}")
        
        # Process with multiple agents (fallback to single agent for now)
        result = service.get_multi_agent_response(message.message, message.user_id)
        
        response = ChatResponse(
            response=result.get("response", "Unable to process comprehensive analysis."),
            sources=result.get("sources", []),
            agent_used=result.get("agent_used"),
            status=result.get("status", "success"),
            context_used=result.get("context_used", False)
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in comprehensive chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process comprehensive analysis right now. Please try the regular chat endpoint."
        )

@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """Upload a career-related document to enhance the knowledge base"""
    try:
        service = await get_chat_service()
        if not service:
            raise HTTPException(
                status_code=503,
                detail="Chat service is not available"
            )
        
        # Check file type
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )
            
        allowed_extensions = ['.txt', '.pdf', '.docx']
        file_extension = '.' + file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Please upload {', '.join(allowed_extensions)} files."
            )
        
        # Read file content
        if file_extension == '.txt':
            content = await file.read()
            content = content.decode('utf-8')
        else:
            # For now, we'll only support .txt files
            raise HTTPException(
                status_code=400,
                detail="Currently only .txt files are supported. PDF and DOCX support coming soon!"
            )
        
        # Add to knowledge base
        result = service.add_knowledge(content, file.filename)
        
        if result["status"] == "success":
            return {"message": result["message"], "filename": file.filename}
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upload document. Please try again."
        )

@router.get("/conversation-starters")
async def get_conversation_starters():
    """Get suggested conversation starters for users"""
    try:
        # Do not force initialization for starters; return static if service not ready
        global chat_service
        service = chat_service
        if not service:
            # Return static starters if service is down
            return {
                "starters": [
                    "How do I transition to a new career?",
                    "Help me improve my resume",
                    "Prepare me for an upcoming interview",
                    "What skills should I develop?",
                    "How do I negotiate salary?"
                ]
            }
        
        starters = service.get_conversation_starters()
        return {"starters": starters}
        
    except Exception as e:
        logger.error(f"Error getting conversation starters: {e}")
        return {
            "starters": [
                "How can I improve my career prospects?",
                "What are some interview tips?",
                "Help me with career planning"
            ]
        }

@router.get("/agent-info")
async def get_agent_info():
    """Get information about available career guidance agents"""
    return {
        "agents": [
            {
                "name": "Career Analyst",
                "role": "Market trends and career insights",
                "expertise": ["Job market analysis", "Salary trends", "Industry insights", "Career transitions"]
            },
            {
                "name": "Resume Expert", 
                "role": "Resume and application optimization",
                "expertise": ["Resume writing", "ATS optimization", "Cover letters", "LinkedIn profiles"]
            },
            {
                "name": "Interview Coach",
                "role": "Interview preparation and coaching", 
                "expertise": ["Interview practice", "Behavioral questions", "Presentation skills", "Confidence building"]
            },
            {
                "name": "Skill Advisor",
                "role": "Learning and development guidance",
                "expertise": ["Skill assessment", "Learning paths", "Certifications", "Professional development"]
            },
            {
                "name": "Networking Specialist",
                "role": "Professional networking strategies",
                "expertise": ["LinkedIn optimization", "Industry events", "Relationship building", "Personal branding"]
            }
        ],
        "description": "Our AI agents are specialized career experts that work together to provide comprehensive guidance tailored to your specific needs."
    }

@router.get("/system-status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        # Do not force initialization for status; report unavailable if not ready
        global chat_service
        service = chat_service
        if not service:
            return {
                "status": "unavailable",
                "message": "Chat service not initialized"
            }
        
        return service.get_system_status()
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }