#!/usr/bin/env python3
"""
Reset admin user password in MongoDB
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
NEW_PASSWORD = "Password@#123"

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

async def reset_admin_password():
    """Reset admin user password in MongoDB"""
    try:
        collection = get_users_collection()
        
        # Find the existing user
        existing_user = await collection.find_one({"email": ADMIN_EMAIL.lower()})
        if not existing_user:
            print(f"❌ User {ADMIN_EMAIL} not found in MongoDB")
            return
        
        print(f"🔍 Found existing user:")
        print(f"   User ID: {existing_user['_id']}")
        print(f"   Name: {existing_user.get('name', 'N/A')}")
        print(f"   Email: {existing_user.get('email', 'N/A')}")
        print(f"   Created: {existing_user.get('created_at', 'N/A')}")
        
        # Update the password
        new_password_hash = hash_password(NEW_PASSWORD)
        
        result = await collection.update_one(
            {"email": ADMIN_EMAIL.lower()},
            {
                "$set": {
                    "password": new_password_hash,
                    "last_login_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"\n✅ Password updated successfully!")
            print(f"   Email: {ADMIN_EMAIL}")
            print(f"   New Password: {NEW_PASSWORD}")
            print(f"\n🎉 You can now login to your admin dashboard!")
            
            # Test the login
            print(f"\n🧪 Testing login with new password...")
            test_user = await collection.find_one({"email": ADMIN_EMAIL.lower()})
            if test_user and test_user.get("password") == new_password_hash:
                print(f"✅ Password hash verification successful!")
            else:
                print(f"❌ Password hash verification failed!")
                
        else:
            print(f"❌ Password update failed - no changes made")
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")

if __name__ == "__main__":
    import asyncio
    
    print("🔧 Resetting Admin User Password")
    print("=" * 50)
    
    if not settings.MONGODB_URI:
        print("❌ MongoDB URI not configured in .env file")
        sys.exit(1)
    
    print(f"📊 MongoDB URI: {settings.MONGODB_URI}")
    print(f"📊 Collection: users")
    
    # Run the async function
    asyncio.run(reset_admin_password())
