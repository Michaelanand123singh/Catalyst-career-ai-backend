#!/usr/bin/env python3
"""
Script to create admin user for Catalyst Career AI
"""

import os
import sys
import hashlib
import json
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

# Admin user details
ADMIN_EMAIL = "theanandsingh76@gmail.com"
ADMIN_PASSWORD = "Password@#123"
ADMIN_NAME = "Anand Singh"

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_admin_user():
    """Create admin user in the appropriate storage"""
    
    print("🔐 Creating admin user...")
    print(f"Email: {ADMIN_EMAIL}")
    print(f"Name: {ADMIN_NAME}")
    
    # Check if MongoDB is configured
    if settings.MONGODB_URI:
        print("📊 Using MongoDB for user storage")
        try:
            from app.db import get_users_collection
            import asyncio
            from datetime import datetime, timezone
            
            async def create_mongo_user():
                collection = get_users_collection()
                
                # Check if user already exists
                existing_user = await collection.find_one({"email": ADMIN_EMAIL.lower()})
                if existing_user:
                    print("⚠️  User already exists in MongoDB")
                    return
                
                # Create new user
                user_doc = {
                    "name": ADMIN_NAME,
                    "email": ADMIN_EMAIL.lower(),
                    "password": hash_password(ADMIN_PASSWORD),
                    "created_at": datetime.now(timezone.utc),
                    "last_login_at": datetime.now(timezone.utc),
                    "is_admin": True
                }
                
                result = await collection.insert_one(user_doc)
                print(f"✅ Admin user created in MongoDB with ID: {result.inserted_id}")
                
            # Run the async function
            asyncio.run(create_mongo_user())
            
        except Exception as e:
            print(f"❌ Failed to create user in MongoDB: {e}")
            print("🔄 Falling back to file storage...")
            create_file_user()
    else:
        print("📁 Using file storage for user storage")
        create_file_user()

def create_file_user():
    """Create admin user in file storage"""
    users_file = Path("data/users.json")
    
    # Ensure data directory exists
    users_file.parent.mkdir(exist_ok=True)
    
    # Read existing users or create new file
    if users_file.exists():
        with open(users_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"users": []}
    
    # Check if user already exists
    existing_user = next((u for u in data["users"] if u["email"].lower() == ADMIN_EMAIL.lower()), None)
    if existing_user:
        print("⚠️  User already exists in file storage")
        return
    
    # Create new user
    user = {
        "id": hashlib.md5(ADMIN_EMAIL.lower().encode('utf-8')).hexdigest(),
        "name": ADMIN_NAME,
        "email": ADMIN_EMAIL,
        "password": hash_password(ADMIN_PASSWORD),
        "is_admin": True
    }
    
    data["users"].append(user)
    
    # Write back to file
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Admin user created in file storage")

def update_env_file():
    """Update .env file to include admin email"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = f"""# Admin Configuration
ADMIN_EMAILS={ADMIN_EMAIL}

# Other configurations can be added here
GOOGLE_API_KEY=your_google_api_key_here
ENVIRONMENT=development
"""
    else:
        print("📝 Updating .env file...")
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        # Check if ADMIN_EMAILS is already set
        if "ADMIN_EMAILS=" not in env_content:
            env_content += f"\n# Admin Configuration\nADMIN_EMAILS={ADMIN_EMAIL}\n"
        else:
            # Update existing ADMIN_EMAILS
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('ADMIN_EMAILS='):
                    lines[i] = f"ADMIN_EMAILS={ADMIN_EMAIL}"
                    break
            env_content = '\n'.join(lines)
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ Updated .env file with ADMIN_EMAILS={ADMIN_EMAIL}")

def main():
    """Main function"""
    print("🚀 Catalyst Career AI - Admin User Creation")
    print("=" * 50)
    
    try:
        # Create admin user
        create_admin_user()
        
        # Update environment file
        update_env_file()
        
        print("\n🎉 Admin user setup completed!")
        print(f"\n📋 Login Details:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"\n🔗 Admin endpoints:")
        print(f"   - List users: GET /api/admin/users")
        print(f"   - User details: GET /api/admin/users/{{user_id}}")
        print(f"   - Activity logs: GET /api/admin/activity")
        print(f"   - User summary: GET /api/admin/users/{{user_id}}/summary")
        print(f"\n⚠️  Remember to restart the backend after updating .env")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
