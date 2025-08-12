#!/usr/bin/env python3
"""
Fix admin privileges for existing user
"""
import os
import sys
from datetime import datetime, timezone

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import get_users_collection
from app.config import settings

# Admin user details
ADMIN_EMAIL = "theanandsingh76@gmail.com"

async def fix_admin_privileges():
    """Fix admin privileges for existing user"""
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
        print(f"   Is Admin: {existing_user.get('is_admin', False)}")
        
        # Update admin privileges
        result = await collection.update_one(
            {"email": ADMIN_EMAIL.lower()},
            {
                "$set": {
                    "is_admin": True,
                    "last_login_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"\n✅ Admin privileges updated successfully!")
            print(f"   Email: {ADMIN_EMAIL}")
            print(f"   Is Admin: True")
            
            # Verify the update
            updated_user = await collection.find_one({"email": ADMIN_EMAIL.lower()})
            print(f"\n🧪 Verification:")
            print(f"   Is Admin: {updated_user.get('is_admin', False)}")
            
            if updated_user.get('is_admin'):
                print(f"✅ Admin privileges confirmed!")
            else:
                print(f"❌ Admin privileges not set!")
                
        else:
            print(f"⚠️  No changes made - user may already have admin privileges")
        
    except Exception as e:
        print(f"❌ Error fixing admin privileges: {e}")

if __name__ == "__main__":
    import asyncio
    
    print("🔧 Fixing Admin Privileges")
    print("=" * 50)
    
    if not settings.MONGODB_URI:
        print("❌ MongoDB URI not configured in .env file")
        sys.exit(1)
    
    print(f"📊 MongoDB URI: {settings.MONGODB_URI}")
    print(f"📊 Collection: users")
    
    # Run the async function
    asyncio.run(fix_admin_privileges())
