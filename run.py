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
    """Warn about missing optional environment variables without failing startup.

    The application is designed to run auth/admin endpoints without AI keys.
    Missing keys (e.g., GOOGLE_API_KEY) should degrade chat features only,
    not prevent the server from starting.
    """
    optional_vars = ["GOOGLE_API_KEY"]
    missing_optionals = []

    for var in optional_vars:
        if not os.getenv(var):
            missing_optionals.append(var)

    if missing_optionals:
        print("⚠️  Missing optional environment variables (chat features may be limited):")
        for var in missing_optionals:
            print(f"   - {var}")
        print("Proceeding to start the server without these.")

    return True

def main():
    """Main function to start the server"""
    print("🚀 Starting Catalyst Career AI Backend...")
    
    # Check requirements (non-fatal warnings only)
    check_requirements()
    
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