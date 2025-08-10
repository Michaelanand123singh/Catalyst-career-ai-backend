#!/usr/bin/env python3
"""
Script to run the Catalyst Career AI backend server
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all required environment variables are set"""
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file")
        return False
    
    return True

def main():
    """Main function to start the server"""
    print("🚀 Starting Catalyst Career AI Backend...")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    environment = os.getenv("ENVIRONMENT", "development")
    
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🌍 Environment: {environment}")
    print(f"📚 API Documentation: http://localhost:{port}/docs")
    print("-" * 50)
    
    # Run the server
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=True if environment == "development" else False,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Catalyst Career AI Backend...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()