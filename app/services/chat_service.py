from app.services.rag_service import RAGService
from app.services.crew_service import CrewService
from app.config import settings
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        """Initialize chat service with RAG and CrewAI services"""
        try:
            # Initialize RAG service first
            logger.info("Initializing RAG service...")
            self.rag_service = RAGService()
            
            # Initialize CrewAI service with RAG service
            logger.info("Initializing CrewAI service...")
            self.crew_service = CrewService(rag_service=self.rag_service)
            
            self.initialized = True
            logger.info("Chat service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize chat service: {e}")
            self.initialized = False
            self.rag_service = None
            self.crew_service = None
    
    def health_check(self) -> Dict[str, str]:
        """Check the health status of the chat service"""
        if not self.initialized:
            return {
                "status": "unhealthy",
                "message": "Chat service failed to initialize"
            }
        
        try:
            # Test RAG service
            rag_status = "healthy" if self.rag_service and self.rag_service.vector_store else "unhealthy"
            
            # Test CrewAI service
            crew_status = "healthy" if self.crew_service else "unhealthy"
            
            overall_status = "healthy" if rag_status == "healthy" and crew_status == "healthy" else "degraded"
            
            return {
                "status": overall_status,
                "message": f"RAG: {rag_status}, CrewAI: {crew_status}",
                "services": {
                    "rag_service": rag_status,
                    "crew_service": crew_status
                }
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Health check error: {str(e)}"
            }
    
    def process_message(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        """Process a user message and return AI response"""
        if not self.initialized:
            return {
                "response": "I'm sorry, but I'm experiencing technical difficulties. Please try again later.",
                "agent_used": "System Error",
                "status": "error",
                "sources": []
            }
        
        try:
            logger.info(f"Processing message from user {user_id}: {message[:50]}...")
            
            # Get RAG context
            rag_context = []
            if self.rag_service:
                try:
                    rag_context = self.rag_service.search_with_scores(message, k=4, score_threshold=0.6)
                except Exception as e:
                    logger.warning(f"RAG search failed: {e}")
                    rag_context = []
            
            # Get CrewAI response
            if self.crew_service:
                result = self.crew_service.get_career_advice(message, rag_context)
            else:
                result = self._fallback_response(message)
            
            # Add sources from RAG context
            sources = []
            if rag_context:
                sources = [f"Knowledge base ({len(rag_context)} relevant documents)"]
            
            # Ensure all required fields are present
            response = {
                "response": result.get("response", "I apologize, but I couldn't generate a proper response."),
                "agent_used": result.get("agent_used", "Unknown"),
                "status": result.get("status", "success"),
                "sources": sources,
                "context_used": result.get("context_used", bool(rag_context))
            }
            
            logger.info(f"Successfully processed message using {response['agent_used']}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._error_response(str(e))
    
    def get_multi_agent_response(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        """Get response using multiple agents for comprehensive analysis"""
        if not self.initialized or not self.crew_service:
            return self.process_message(message, user_id)
        
        try:
            logger.info(f"Processing multi-agent request from user {user_id}")
            
            # For now, use single agent (multi-agent collaboration was complex in old CrewAI)
            # You can extend this later
            result = self.process_message(message, user_id)
            result["collaboration"] = False
            
            return result
            
        except Exception as e:
            logger.error(f"Error in multi-agent processing: {e}")
            return self.process_message(message, user_id)
    
    def add_knowledge(self, content: str, filename: str) -> Dict[str, str]:
        """Add new knowledge to the system"""
        if not self.initialized or not self.rag_service:
            return {
                "status": "error",
                "message": "Knowledge service is not available"
            }
        
        try:
            self.rag_service.add_document(content, filename)
            return {
                "status": "success",
                "message": f"Successfully added {filename} to the knowledge base"
            }
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            return {
                "status": "error",
                "message": f"Failed to add document: {str(e)}"
            }
    
    def get_conversation_starters(self) -> List[str]:
        """Get suggested conversation starters"""
        return [
            "How do I transition to a new career field?",
            "Help me optimize my resume for tech jobs",
            "What should I expect in a behavioral interview?",
            "How do I negotiate salary effectively?",
            "What skills should I develop to advance my career?",
            "How do I build a professional network?",
            "What are the current trends in my industry?",
            "How do I prepare for a leadership role?",
            "What certifications would boost my career?",
            "How do I handle a career gap in my resume?"
        ]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        if not self.initialized:
            return {
                "status": "error",
                "message": "System not initialized",
                "services": {},
                "capabilities": []
            }
        
        try:
            if self.crew_service:
                return self.crew_service.get_system_status()
            else:
                return {
                    "status": "degraded",
                    "message": "CrewAI service unavailable",
                    "services": {
                        "rag_service": "active" if self.rag_service else "inactive"
                    },
                    "capabilities": ["Basic chat responses"]
                }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "status": "error",
                "message": str(e),
                "services": {},
                "capabilities": []
            }
    
    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Generate a fallback response when CrewAI is unavailable"""
        query_lower = message.lower()
        
        if any(keyword in query_lower for keyword in ['resume', 'cv']):
            response = """Here are some key resume tips:

• Use action verbs and quantify achievements
• Tailor your resume to each job application
• Keep it clean and ATS-friendly
• Focus on accomplishments, not just duties
• Include relevant keywords from job postings

For more detailed guidance, please try asking a more specific resume question."""
            
        elif any(keyword in query_lower for keyword in ['interview', 'preparation']):
            response = """For interview success:

• Research the company thoroughly
• Practice the STAR method for behavioral questions
• Prepare thoughtful questions to ask them
• Practice your "tell me about yourself" pitch
• Plan your logistics in advance

What specific aspect of interview preparation would you like to focus on?"""
            
        elif any(keyword in query_lower for keyword in ['salary', 'negotiation']):
            response = """For salary negotiation:

• Research market rates using salary websites
• Know your value and be ready to articulate it
• Wait for the offer before negotiating
• Consider the total compensation package
• Be professional and respectful

Would you like specific negotiation scripts or strategies?"""
            
        else:
            response = """I'm here to help with your career questions! I can assist with:

• Resume and CV optimization
• Interview preparation
• Salary negotiation
• Career transition planning
• Skill development guidance
• Professional networking

Please feel free to ask a more specific question about any of these areas."""
        
        return {
            "response": response,
            "agent_used": "Fallback Assistant",
            "status": "fallback"
        }
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Generate an error response"""
        return {
            "response": "I'm experiencing some technical difficulties right now. Please try rephrasing your question or try again in a moment.",
            "agent_used": "Error Handler",
            "status": "error",
            "sources": [],
            "error": error_msg
        }