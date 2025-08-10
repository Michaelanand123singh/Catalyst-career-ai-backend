import os
import google.generativeai as genai
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from app.config import settings
import logging
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        # Configure Google Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Initialize embeddings - updated for newer LangChain
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY
            )
        except Exception as e:
            logger.warning(f"Failed to initialize with {settings.EMBEDDING_MODEL}, trying fallback: {e}")
            # Fallback to basic model
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=settings.GOOGLE_API_KEY
            )
        
        self.vector_store = None
        self.initialize_vector_store()
    
    def initialize_vector_store(self):
        """Initialize or load existing vector store"""
        try:
            # Check if vector store exists
            if os.path.exists(settings.CHROMA_DB_PATH) and os.listdir(settings.CHROMA_DB_PATH):
                try:
                    self.vector_store = Chroma(
                        persist_directory=settings.CHROMA_DB_PATH,
                        embedding_function=self.embeddings
                    )
                    logger.info("Loaded existing vector store")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load existing vector store: {e}, creating new one")
            
            logger.info("Creating new vector store...")
            self.load_documents()
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            # Create empty vector store as fallback
            self.create_empty_vector_store()
    
    def create_empty_vector_store(self):
        """Create an empty vector store with sample document"""
        try:
            # Create a sample document to initialize the vector store
            sample_doc = Document(
                page_content="Welcome to Catalyst Career AI. This is a sample document to initialize the system.",
                metadata={"source": "system_init"}
            )
            
            self.vector_store = Chroma.from_documents(
                documents=[sample_doc],
                embedding=self.embeddings,
                persist_directory=settings.CHROMA_DB_PATH
            )
            logger.info("Created empty vector store with sample document")
        except Exception as e:
            logger.error(f"Failed to create empty vector store: {e}")
    
    def load_documents_from_directory(self, directory_path: str):
        """Load documents from directory using safe file loading"""
        documents = []
        
        # Find text files
        txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
        
        for file_path in txt_files:
            try:
                # Use TextLoader for better compatibility
                loader = TextLoader(file_path, encoding='utf-8')
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = os.path.basename(file_path)
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} chunks from {file_path}")
            except Exception as e:
                logger.warning(f"Could not load {file_path}: {e}")
                # Try manual loading as fallback
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        doc = Document(
                            page_content=content,
                            metadata={"source": os.path.basename(file_path)}
                        )
                        documents.append(doc)
                except Exception as e2:
                    logger.error(f"Manual loading also failed for {file_path}: {e2}")
        
        return documents
    
    def load_documents(self):
        """Load career documents into vector store"""
        if not os.path.exists(settings.DOCUMENTS_PATH):
            os.makedirs(settings.DOCUMENTS_PATH)
            logger.info(f"Created directory: {settings.DOCUMENTS_PATH}")
        
        # Create sample data if no documents exist
        if not os.listdir(settings.DOCUMENTS_PATH):
            logger.info("No documents found. Creating sample career data...")
            self.create_sample_data()
        
        try:
            # Load documents
            documents = self.load_documents_from_directory(settings.DOCUMENTS_PATH)
            
            if not documents:
                logger.warning("No documents loaded, creating sample data")
                self.create_sample_data()
                documents = self.load_documents_from_directory(settings.DOCUMENTS_PATH)
            
            if not documents:
                logger.error("Still no documents after creating samples")
                self.create_empty_vector_store()
                return
            
            # Split documents - compatible with newer LangChain
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len
            )
            splits = text_splitter.split_documents(documents)
            
            # Create vector store directory if it doesn't exist
            os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
            
            # Create vector store - compatible with newer ChromaDB
            self.vector_store = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=settings.CHROMA_DB_PATH
            )
            logger.info(f"Created vector store with {len(splits)} chunks from {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            self.create_empty_vector_store()
    
    def create_sample_data(self):
        """Create sample career guidance documents"""
        sample_docs = {
            "career_transition_guide.txt": """
Career Transition Guide

Switching careers can be challenging but rewarding. Here are key steps for a successful career transition:

1. Self Assessment
   - Identify your transferable skills
   - Understand your interests and passions
   - Clarify your values and priorities
   - Assess your financial situation

2. Research Your Target Field
   - Study industry trends and growth prospects
   - Understand required skills and qualifications
   - Research salary ranges and job availability
   - Identify key companies and roles

3. Skill Development
   - Bridge skill gaps through online courses
   - Obtain relevant certifications
   - Build a portfolio or projects
   - Practice new skills through volunteering

4. Networking Strategy
   - Connect with professionals in your target field
   - Attend industry events and meetups
   - Join professional associations
   - Leverage LinkedIn for networking

5. Resume and Application Materials
   - Highlight transferable skills
   - Create a compelling career change narrative
   - Tailor your resume for each application
   - Write targeted cover letters

Timeline Expectations:
A career transition typically takes 6-18 months depending on how different your target field is.
            """,
            
            "interview_preparation.txt": """
Interview Preparation Guide

Mastering job interviews requires preparation, practice, and confidence.

Common Interview Questions:

1. "Tell me about yourself"
   - Keep it professional and relevant
   - Follow the Present-Past-Future format
   - Highlight key achievements

2. "Why do you want this role?"
   - Show you've researched the company
   - Connect your skills to their needs
   - Demonstrate genuine interest

3. "What are your strengths?"
   - Choose strengths relevant to the job
   - Provide specific examples
   - Show impact on previous employers

4. "Describe a challenging situation"
   - Use the STAR method (Situation, Task, Action, Result)
   - Choose a relevant example
   - Focus on problem-solving

Interview Preparation Checklist:
- Research the company thoroughly
- Practice common questions out loud
- Prepare 5-10 questions to ask them
- Plan your outfit and route
- Arrive 10-15 minutes early
            """,
            
            "resume_optimization.txt": """
Resume Optimization Guide

Your resume is your first impression with potential employers.

Essential Resume Sections:

1. Contact Information
   - Full name and professional email
   - Phone number and LinkedIn profile
   - City, State (no full address needed)

2. Professional Summary (2-3 lines)
   - Highlight key qualifications
   - Include years of experience
   - Mention your specialization

3. Work Experience
   - Use reverse chronological order
   - Start with strong action verbs
   - Quantify achievements with numbers
   - Focus on accomplishments, not duties

4. Skills Section
   - Technical skills relevant to the job
   - Software proficiencies
   - Relevant certifications

Best Practices:
- Keep it to 1-2 pages maximum
- Use clean, professional formatting
- Include keywords from job descriptions
- Tailor for each application
- Proofread carefully
            """,
            
            "salary_negotiation.txt": """
Salary Negotiation Guide

Negotiating your salary effectively can significantly impact your career earnings.

Preparation Phase:

1. Research Market Rates
   - Use Glassdoor, PayScale, Salary.com
   - Consider location and experience
   - Network with industry professionals

2. Know Your Worth
   - List accomplishments and contributions
   - Quantify your impact with metrics
   - Consider unique skills and experience

Negotiation Strategies:

When to Negotiate:
- After receiving a job offer
- During performance reviews
- When taking on new responsibilities

How to Negotiate:
- Express enthusiasm first
- Present research and justification
- Be confident but respectful
- Consider total compensation package

What to Say:
"I'm excited about this opportunity. Based on my research and experience, I was hoping for a salary in the range of $X to $Y."

Remember: The worst they can say is no, but they're likely to respect you for advocating professionally.
            """
        }
        
        for filename, content in sample_docs.items():
            filepath = os.path.join(settings.DOCUMENTS_PATH, filename)
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Created sample document: {filename}")
            except Exception as e:
                logger.error(f"Failed to create {filename}: {e}")
        
        logger.info("Sample career documents creation completed")
    
    def search(self, query: str, k: int = None):
        """Search for relevant documents"""
        if k is None:
            k = settings.VECTOR_SEARCH_K
            
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in results]
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def search_with_scores(self, query: str, k: int = None, score_threshold: float = None):
        """Search for relevant documents with similarity scores"""
        if k is None:
            k = settings.VECTOR_SEARCH_K
        if score_threshold is None:
            score_threshold = settings.SCORE_THRESHOLD
            
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []
        
        try:
            # Updated method for newer ChromaDB
            if hasattr(self.vector_store, 'similarity_search_with_relevance_scores'):
                results = self.vector_store.similarity_search_with_relevance_scores(query, k=k)
                # Higher score = more relevant
                filtered_results = [doc.page_content for doc, score in results if score >= score_threshold]
                if filtered_results:
                    return filtered_results
                # Fallback to top-2 contents
                return [doc.page_content for doc, _ in results[:2]]
            elif hasattr(self.vector_store, 'similarity_search_with_score'):
                results = self.vector_store.similarity_search_with_score(query, k=k)
                # Older API returns distance where LOWER is better; take top-k by ascending score
                results_sorted = sorted(results, key=lambda x: x[1])
                return [doc.page_content for doc, _ in results_sorted[:k]]
            else:
                # Final fallback to regular search
                return self.search(query, k)
        except Exception as e:
            logger.error(f"Error searching vector store with scores: {e}")
            return self.search(query, k)
    
    def add_document(self, content: str, filename: str):
        """Add a new document to the vector store"""
        try:
            # Save document to file
            filepath = os.path.join(settings.DOCUMENTS_PATH, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Add to vector store
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len
            )
            
            # Create Document object with metadata
            doc = Document(page_content=content, metadata={"source": filename})
            splits = text_splitter.split_documents([doc])
            
            if self.vector_store:
                self.vector_store.add_documents(splits)
                logger.info(f"Added document {filename} to vector store with {len(splits)} chunks")
            else:
                logger.error("Vector store not initialized, cannot add document")
                raise Exception("Vector store not available")
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise
    
    def get_document_count(self):
        """Get the number of documents in the vector store"""
        try:
            if self.vector_store and hasattr(self.vector_store, '_collection'):
                return self.vector_store._collection.count()
            elif self.vector_store:
                # Try alternative method for newer versions
                test_results = self.vector_store.similarity_search("test", k=1000)
                return len(test_results)
            return 0
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def delete_documents_by_source(self, source_filename: str):
        """Delete documents by source filename"""
        try:
            if self.vector_store and hasattr(self.vector_store, 'delete'):
                # This might work in newer versions
                self.vector_store.delete(where={"source": source_filename})
                logger.info(f"Attempted to delete documents with source: {source_filename}")
            else:
                logger.warning("Delete functionality not available in this ChromaDB version")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            # Don't raise, as this is not critical functionality