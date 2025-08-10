from crewai import Agent, Task, Crew, LLM
from app.config import settings
from app.services.rag_service import RAGService
import logging
from typing import Dict, List, Optional, Any
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrewService:
    def __init__(self, rag_service: Optional[RAGService] = None):
        # Configure Google Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Normalize model for CrewAI which expects 'gemini/<model>' or '<provider>/<model>'
        raw_model = settings.GEMINI_MODEL.strip()
        if raw_model.startswith('gemini/'):
            crew_model = raw_model
        elif raw_model.startswith('gemini-'):
            crew_model = f"gemini/{raw_model}"
        elif raw_model.replace(' ', '') in {"1.5-flash", "1.5-pro"}:
            crew_model = f"gemini/gemini-{raw_model}"
        else:
            crew_model = f"gemini/{raw_model}"

        # Initialize Google Gemini LLM - Updated for newer CrewAI
        self.llm = LLM(
            model=crew_model,
            api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
        logger.info(f"Initialized CrewAI LLM with model: {crew_model}")
        
        # Initialize RAG service
        self.rag_service = rag_service or RAGService()
        
        self.setup_agents()
    
    def setup_agents(self):
        """Initialize career guidance agents - Updated for newer CrewAI"""
        
        # Career Analyst Agent
        self.career_analyst = Agent(
            role='Senior Career Market Analyst',
            goal='Analyze job market trends, salary insights, and provide strategic career guidance',
            backstory='''You are a seasoned career counselor with 15+ years of experience 
            in analyzing job markets, industry trends, and career opportunities across various sectors. 
            You have worked with Fortune 500 companies and helped thousands of professionals 
            navigate their career paths. You stay updated with the latest market data, 
            emerging roles, and industry disruptions.''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False  # Updated parameter
        )
        
        # Resume Expert Agent  
        self.resume_expert = Agent(
            role='Senior Resume Optimization Specialist',
            goal='Create compelling resumes, optimize ATS compatibility, and improve job application materials',
            backstory='''You are a certified professional resume writer (CPRW) with over 12 years 
            of experience in crafting winning resumes, cover letters, and LinkedIn profiles. 
            You have helped professionals at all levels - from recent graduates to C-suite 
            executives - land their dream jobs. You understand what recruiters and hiring 
            managers look for and how ATS systems work.''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Interview Coach Agent
        self.interview_coach = Agent(
            role='Executive Interview Preparation Coach', 
            goal='Prepare candidates for successful interviews and improve their presentation skills',
            backstory='''You are a former HR Director turned interview coach with 18 years 
            of experience in recruitment, candidate evaluation, and interview processes. 
            You have conducted over 5,000 interviews across various industries and levels. 
            You understand both sides of the interview table and know exactly what 
            makes candidates stand out.''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Skill Development Advisor
        self.skill_advisor = Agent(
            role='Learning & Development Specialist',
            goal='Identify skill gaps, recommend learning paths, and create development plans',
            backstory='''You are a Learning & Development expert with 10+ years of experience 
            in corporate training, skill assessment, and career development planning. 
            You have designed curriculum for major tech companies and understand the 
            skills needed for various roles across industries.''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Networking Specialist Agent
        self.networking_specialist = Agent(
            role='Professional Networking Strategist',
            goal='Help professionals build meaningful connections and leverage networking for career growth',
            backstory='''You are a networking expert with 12+ years of experience in 
            relationship building, personal branding, and professional development. 
            You have helped thousands of professionals expand their networks, both 
            online and offline.''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        logger.info("Career guidance agents initialized successfully")
    
    def determine_agent(self, user_query: str) -> tuple:
        """Determine which agent should handle the query"""
        query_lower = user_query.lower()
        
        # Keywords for different agents
        resume_keywords = ['resume', 'cv', 'application', 'ats', 'optimize', 'format', 'cover letter']
        interview_keywords = ['interview', 'preparation', 'questions', 'behavioral', 'practice', 'mock']
        skill_keywords = ['skills', 'learning', 'course', 'certification', 'training', 'development']
        market_keywords = ['salary', 'market', 'trends', 'industry', 'compensation', 'career path']
        networking_keywords = ['networking', 'connections', 'linkedin', 'events', 'professional network']
        
        # Count matches
        resume_score = sum(1 for keyword in resume_keywords if keyword in query_lower)
        interview_score = sum(1 for keyword in interview_keywords if keyword in query_lower)
        skill_score = sum(1 for keyword in skill_keywords if keyword in query_lower)
        market_score = sum(1 for keyword in market_keywords if keyword in query_lower)
        networking_score = sum(1 for keyword in networking_keywords if keyword in query_lower)
        
        # Determine the best agent
        scores = {
            'Resume Expert': resume_score,
            'Interview Coach': interview_score,
            'Skill Advisor': skill_score,
            'Career Analyst': market_score,
            'Networking Specialist': networking_score
        }
        
        best_agent_name = max(scores.items(), key=lambda x: x[1])[0]
        
        # If no clear winner, default to Career Analyst
        if max(scores.values()) == 0:
            best_agent_name = 'Career Analyst'
        
        agent_mapping = {
            'Career Analyst': self.career_analyst,
            'Resume Expert': self.resume_expert,
            'Interview Coach': self.interview_coach,
            'Skill Advisor': self.skill_advisor,
            'Networking Specialist': self.networking_specialist
        }
        
        return agent_mapping[best_agent_name], best_agent_name
    
    def get_career_advice(self, user_query: str, rag_context: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get career advice using the most appropriate agent"""
        
        try:
            # Get RAG context if not provided
            if rag_context is None:
                try:
                    rag_context = self.rag_service.search_with_scores(user_query, k=4, score_threshold=0.6)
                except:
                    rag_context = []
            
            # Combine RAG context
            if rag_context:
                context = "\n\n--- Document Context ---\n" + "\n\n".join(rag_context)
            else:
                context = "No specific context available from knowledge base."
            
            # Determine the best agent for this query
            selected_agent, agent_name = self.determine_agent(user_query)
            
            # Create task description - Updated for newer CrewAI
            task_description = f"""
            You are helping a professional with their career question. Please provide expert advice 
            based on your role as a {selected_agent.role}.
            
            USER QUESTION: {user_query}
            
            CONTEXT: {context}
            
            Please provide specific, actionable advice with:
            1. Clear recommendations based on your expertise
            2. Concrete next steps the user can take
            3. Relevant tools, resources, or timeframes
            4. Professional, encouraging tone
            
            Keep your response comprehensive but focused (under 500 words).
            """
            
            # Create task - Updated for newer CrewAI
            task = Task(
                description=task_description,
                agent=selected_agent,
                expected_output="A comprehensive career advice response with actionable recommendations"
            )
            
            # Execute task with crew - Updated method
            crew = Crew(
                agents=[selected_agent],
                tasks=[task],
                verbose=False
            )
            
            # Execute the crew - Updated method for newer CrewAI
            result = crew.kickoff()
            
            # Handle different result types from newer CrewAI
            if hasattr(result, 'raw'):
                response_text = result.raw
            elif hasattr(result, 'output'):
                response_text = result.output
            else:
                response_text = str(result)
            
            logger.info(f"Successfully processed query using {agent_name}")
            
            return {
                "response": response_text,
                "agent_used": agent_name,
                "status": "success",
                "context_used": bool(rag_context)
            }
            
        except Exception as e:
            logger.error(f"Error in crew processing: {e}")
            fallback_response = self._generate_fallback_response(user_query)
            return {
                "response": fallback_response,
                "agent_used": "System Fallback",
                "status": "fallback",
                "error": str(e)
            }
    
    def _generate_fallback_response(self, user_query: str) -> str:
        """Generate a helpful fallback response when the main system fails"""
        
        query_lower = user_query.lower()
        
        if any(keyword in query_lower for keyword in ['resume', 'cv', 'application']):
            return """I understand you're asking about resume/CV optimization. Here are some quick tips:
            
            • Use action verbs and quantify achievements (e.g., "Increased sales by 25%")
            • Tailor your resume to each job application
            • Include relevant keywords from the job posting
            • Keep formatting clean and ATS-friendly
            • Focus on accomplishments, not just job duties
            
            For more detailed guidance, please try asking a more specific question about resume writing."""
            
        elif any(keyword in query_lower for keyword in ['interview', 'preparation']):
            return """I see you're asking about interview preparation. Here are key strategies:
            
            • Research the company and role thoroughly
            • Practice the STAR method for behavioral questions
            • Prepare 5-7 thoughtful questions to ask them
            • Practice your "tell me about yourself" pitch
            • Plan your outfit and logistics in advance
            
            Feel free to ask me about specific interview scenarios or question types!"""
            
        elif any(keyword in query_lower for keyword in ['salary', 'negotiation']):
            return """For salary negotiation, consider these fundamentals:
            
            • Research market rates using Glassdoor, PayScale, etc.
            • Know your value and be ready to articulate it
            • Wait for the offer before negotiating
            • Consider the total compensation package
            • Be professional and respectful in your approach
            
            Remember: negotiation shows you value yourself professionally!"""
            
        else:
            return """I'm here to help with your career questions! I can assist with:
            
            • Resume and CV optimization
            • Interview preparation and practice
            • Salary negotiation strategies
            • Skill development planning
            • Professional networking
            • Career transition guidance
            
            Please feel free to ask me a more specific question about any of these areas!"""
    
    def add_custom_knowledge(self, content: str, filename: str) -> Dict[str, Any]:
        """Add custom knowledge to the RAG system"""
        try:
            self.rag_service.add_document(content, filename)
            return {
                "status": "success",
                "message": f"Successfully added {filename} to knowledge base"
            }
        except Exception as e:
            logger.error(f"Error adding custom knowledge: {e}")
            return {
                "status": "error",
                "message": f"Failed to add document: {str(e)}"
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and capabilities"""
        try:
            doc_count = self.rag_service.get_document_count() if hasattr(self.rag_service, 'get_document_count') else 0
        except:
            doc_count = 0
            
        return {
            "status": "active",
            "agents": {
                "career_analyst": "Available",
                "resume_expert": "Available", 
                "interview_coach": "Available",
                "skill_advisor": "Available",
                "networking_specialist": "Available"
            },
            "rag_service": {
                "status": "active",
                "document_count": doc_count
            },
            "capabilities": [
                "Career guidance and planning",
                "Resume and CV optimization", 
                "Interview preparation",
                "Skill development planning",
                "Professional networking advice",
                "Salary negotiation strategies",
                "Career transition support"
            ]
        }