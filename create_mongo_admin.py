#!/usr/bin/env python3
"""
Create admin user directly in MongoDB
"""
import os
import sys
import hashlib
from datetime import datetime, timezone

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import get_users_collection
from app.config import settings

# Admin user details
ADMIN_EMAIL = "theanandsingh76@gmail.com"
ADMIN_PASSWORD = "Password@#123"
ADMIN_NAME = "Anand Singh"

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

async def create_mongo_admin():
    """Create admin user in MongoDB"""
    try:
        collection = get_users_collection()
        
        # Check if user already exists
        existing_user = await collection.find_one({"email": ADMIN_EMAIL.lower()})
        if existing_user:
            print(f"⚠️  User {ADMIN_EMAIL} already exists in MongoDB")
            print(f"   User ID: {existing_user['_id']}")
            print(f"   Name: {existing_user.get('name', 'N/A')}")
            print(f"   Created: {existing_user.get('created_at', 'N/A')}")
            return
        
        # Create new admin user
        user_doc = {
            "name": ADMIN_NAME,
            "email": ADMIN_EMAIL.lower(),
            "password": hash_password(ADMIN_PASSWORD),
            "created_at": datetime.now(timezone.utc),
            "last_login_at": datetime.now(timezone.utc),
            "is_admin": True
        }
        
        result = await collection.insert_one(user_doc)
        print(f"✅ Admin user created successfully in MongoDB!")
        print(f"   User ID: {result.inserted_id}")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Name: {ADMIN_NAME}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"\n🎉 You can now login to your admin dashboard!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        print(f"   MongoDB URI: {settings.MONGODB_URI}")

if __name__ == "__main__":
    import asyncio
    
    print("🚀 Creating Admin User in MongoDB")
    print("=" * 50)
    
    if not settings.MONGODB_URI:
        print("❌ MongoDB URI not configured in .env file")
        print("   Please set MONGODB_URI in your .env file")
        sys.exit(1)
    
    print(f"📊 MongoDB URI: {settings.MONGODB_URI}")
    print(f"📊 Collection: users")
    
    # Run the async function
    asyncio.run(create_mongo_admin())
