#!/usr/bin/env python3
"""
Deep Diagnosis Script for Catalyst Career AI Backend
Identifies the exact root cause of configuration and initialization issues
"""

import os
import sys
import traceback
from pathlib import Path

def check_environment_variables():
    """Check all required environment variables"""
    print("🔍 Checking Environment Variables...")
    print("=" * 50)
    
    required_vars = {
        'ENVIRONMENT': 'Application environment',
        'GOOGLE_API_KEY': 'Google AI API key',
        'MONGODB_URI': 'MongoDB connection string',
        'ADMIN_API_TOKEN': 'Admin authentication token',
        'ADMIN_EMAILS': 'Admin email addresses'
    }
    
    optional_vars = {
        'CLOUDINARY_CLOUD_NAME': 'Cloudinary cloud name',
        'CLOUDINARY_API_KEY': 'Cloudinary API key',
        'CLOUDINARY_API_SECRET': 'Cloudinary API secret',
        'FRONTEND_URL': 'Frontend URL for CORS'
    }
    
    missing_required = []
    missing_optional = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {description} - CONFIGURED")
            if var == 'GOOGLE_API_KEY':
                print(f"   Value: {value[:10]}...{value[-4:] if len(value) > 14 else '***'}")
            elif var == 'MONGODB_URI':
                print(f"   Value: {value[:30]}...{value[-20:] if len(value) > 50 else '***'}")
            else:
                print(f"   Value: {value[:20]}...{value[-10:] if len(value) > 30 else '***'}")
        else:
            print(f"❌ {var}: {description} - MISSING")
            missing_required.append(var)
    
    print("\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {description} - CONFIGURED")
        else:
            print(f"⚠️  {var}: {description} - NOT SET")
            missing_optional.append(var)
    
    return missing_required, missing_optional

def check_configuration_files():
    """Check configuration files and imports"""
    print("\n🔍 Checking Configuration Files...")
    print("=" * 50)
    
    # Check if we can import the config
    try:
        sys.path.append(str(Path(__file__).parent))
        from app.config import settings
        print("✅ Configuration module imported successfully")
        
        # Check specific settings
        print(f"   Environment: {settings.ENVIRONMENT}")
        print(f"   Port: {settings.PORT}")
        print(f"   Host: {settings.HOST}")
        print(f"   Google API Key: {'✅ Set' if settings.GOOGLE_API_KEY else '❌ Missing'}")
        print(f"   MongoDB URI: {'✅ Set' if settings.MONGODB_URI else '❌ Missing'}")
        print(f"   Admin Token: {'✅ Set' if settings.ADMIN_API_TOKEN else '❌ Missing'}")
        print(f"   Admin Emails: {'✅ Set' if settings.ADMIN_EMAILS else '❌ Missing'}")
        
        return True, settings
    except Exception as e:
        print(f"❌ Failed to import configuration: {e}")
        traceback.print_exc()
        return False, None

def check_database_connection():
    """Test database connection"""
    print("\n🔍 Testing Database Connection...")
    print("=" * 50)
    
    try:
        from app.db import get_client, get_db
        
        # Test connection
        client = get_client()
        db = get_db()
        
        # Test a simple operation
        result = db.command("ping")
        print("✅ MongoDB connection successful")
        print(f"   Database: {db.name}")
        print(f"   Collections: Available (connection test successful)")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        if "MONGODB_URI is not configured" in str(e):
            print("   Root Cause: MONGODB_URI environment variable is missing")
        elif "authentication failed" in str(e).lower():
            print("   Root Cause: MongoDB authentication failed - check username/password")
        elif "connection refused" in str(e).lower():
            print("   Root Cause: MongoDB connection refused - check network/firewall")
        else:
            print(f"   Root Cause: {e}")
        return False

def check_service_initialization():
    """Test service initialization"""
    print("\n🔍 Testing Service Initialization...")
    print("=" * 50)
    
    try:
        from app.services.rag_service import RAGService
        print("✅ RAG Service imported successfully")
        
        # Try to initialize RAG service
        try:
            rag_service = RAGService()
            print("✅ RAG Service initialized successfully")
            print(f"   Vector Store: {'✅ Available' if rag_service.vector_store else '❌ Not Available'}")
        except Exception as e:
            print(f"❌ RAG Service initialization failed: {e}")
            if "GOOGLE_API_KEY" in str(e):
                print("   Root Cause: Google API Key is missing or invalid")
            else:
                print(f"   Root Cause: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to import RAG Service: {e}")
        return False

def check_crew_service():
    """Test CrewAI service"""
    print("\n🔍 Testing CrewAI Service...")
    print("=" * 50)
    
    try:
        from app.services.crew_service import CrewService
        print("✅ CrewAI Service imported successfully")
        
        # Try to initialize CrewAI service
        try:
            crew_service = CrewService()
            print("✅ CrewAI Service initialized successfully")
            print(f"   LLM: {'✅ Available' if crew_service.llm else '❌ Not Available'}")
            print(f"   Agents: {'✅ Available' if hasattr(crew_service, 'career_analyst') else '❌ Not Available'}")
        except Exception as e:
            print(f"❌ CrewAI Service initialization failed: {e}")
            if "GOOGLE_API_KEY" in str(e):
                print("   Root Cause: Google API Key is missing or invalid")
            else:
                print(f"   Root Cause: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to import CrewAI Service: {e}")
        return False

def check_chat_service():
    """Test chat service"""
    print("\n🔍 Testing Chat Service...")
    print("=" * 50)
    
    try:
        from app.services.chat_service import ChatService
        print("✅ Chat Service imported successfully")
        
        # Try to initialize chat service
        try:
            chat_service = ChatService()
            print(f"✅ Chat Service initialized: {chat_service.initialized}")
            if chat_service.initialized:
                print("   RAG Service: ✅ Available")
                print("   CrewAI Service: ✅ Available")
            else:
                print("   RAG Service: ❌ Failed")
                print("   CrewAI Service: ❌ Failed")
        except Exception as e:
            print(f"❌ Chat Service initialization failed: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to import Chat Service: {e}")
        return False

def check_api_endpoints():
    """Test API endpoints"""
    print("\n🔍 Testing API Endpoints...")
    print("=" * 50)
    
    try:
        import requests
        
        base_url = "https://catalyst-career-ai-backend-147549542423.asia-southeast1.run.app"
        
        # Test basic endpoints
        endpoints = [
            ("/ping", "Basic Ping"),
            ("/api/status", "API Status"),
            ("/api/health", "Health Check"),
            ("/api/blog-posts", "Blog Posts"),
            ("/api/system-status", "System Status")
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {description}: {endpoint} - Status: {response.status_code}")
                else:
                    print(f"❌ {description}: {endpoint} - Status: {response.status_code}")
                    print(f"   Response: {response.text[:100]}...")
            except Exception as e:
                print(f"❌ {description}: {endpoint} - Error: {e}")
        
        return True
    except Exception as e:
        print(f"❌ API endpoint testing failed: {e}")
        return False

def generate_fix_instructions(missing_required, missing_optional):
    """Generate fix instructions based on findings"""
    print("\n🔧 FIX INSTRUCTIONS")
    print("=" * 50)
    
    if missing_required:
        print("🚨 CRITICAL ISSUES - Must fix immediately:")
        for var in missing_required:
            if var == 'GOOGLE_API_KEY':
                print(f"   1. Set {var}: Get API key from https://makersuite.google.com/app/apikey")
            elif var == 'MONGODB_URI':
                print(f"   2. Set {var}: Create MongoDB Atlas cluster or use existing MongoDB")
            elif var == 'ADMIN_API_TOKEN':
                print(f"   3. Set {var}: Generate a secure random token")
            elif var == 'ADMIN_EMAILS':
                print(f"   4. Set {var}: Add admin email addresses (comma-separated)")
            elif var == 'ENVIRONMENT':
                print(f"   5. Set {var}: Set to 'production' for production deployment")
        
        print("\n📋 Quick Fix Commands:")
        print("   # Option 1: Google Cloud Console")
        print("   # Go to: https://console.cloud.google.com/run")
        print("   # Select your service and add environment variables")
        
        print("\n   # Option 2: gcloud CLI")
        print("   gcloud run services update catalyst-career-ai-backend \\")
        print("       --region asia-southeast1 \\")
        print("       --set-env-vars \"ENVIRONMENT=production,GOOGLE_API_KEY=your_key,MONGODB_URI=your_uri,ADMIN_API_TOKEN=your_token,ADMIN_EMAILS=admin@catalystcareers.in\"")
    
    if missing_optional:
        print("\n⚠️  OPTIONAL IMPROVEMENTS:")
        for var in missing_optional:
            if var.startswith('CLOUDINARY'):
                print(f"   - Set {var}: For image upload functionality")
            elif var == 'FRONTEND_URL':
                print(f"   - Set {var}: For proper CORS configuration")
    
    print("\n🔄 After fixing environment variables:")
    print("   1. Deploy new revision in GCP Cloud Run")
    print("   2. Wait for deployment to complete")
    print("   3. Run: python test-backend-health.py")
    print("   4. Verify all endpoints return 200 status")

def main():
    """Main diagnostic function"""
    print("🚀 Catalyst Career AI - Deep Diagnosis")
    print("=" * 60)
    print("This script will identify the exact root cause of your backend issues")
    print("=" * 60)
    
    # Check environment variables
    missing_required, missing_optional = check_environment_variables()
    
    # Check configuration
    config_ok, settings = check_configuration_files()
    
    # Check database if config is ok
    db_ok = False
    if config_ok:
        db_ok = check_database_connection()
    
    # Check services if database is ok
    services_ok = False
    if db_ok:
        services_ok = check_service_initialization()
        if services_ok:
            services_ok = check_crew_service()
            if services_ok:
                services_ok = check_chat_service()
    
    # Test API endpoints
    api_ok = check_api_endpoints()
    
    # Summary
    print("\n📊 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    if not missing_required:
        print("✅ All required environment variables are configured")
    else:
        print(f"❌ Missing {len(missing_required)} required environment variables")
    
    print(f"Configuration: {'✅ OK' if config_ok else '❌ Failed'}")
    print(f"Database: {'✅ OK' if db_ok else '❌ Failed'}")
    print(f"Services: {'✅ OK' if services_ok else '❌ Failed'}")
    print(f"API Endpoints: {'✅ OK' if api_ok else '❌ Failed'}")
    
    # Generate fix instructions
    generate_fix_instructions(missing_required, missing_optional)
    
    print("\n🎯 ROOT CAUSE IDENTIFIED:")
    if missing_required:
        print("   The backend is failing because essential environment variables are missing.")
        print("   This prevents proper initialization of services and database connections.")
    else:
        print("   Environment variables are configured, but there may be other issues.")
        print("   Check the detailed logs above for specific error messages.")

if __name__ == "__main__":
    main()
