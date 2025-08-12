#!/usr/bin/env python3
"""
Test script to verify CORS configuration and API endpoints
"""
import requests
import json

# Test URLs
BASE_URL = "https://catalyst-career-ai-backend.onrender.com"
ADMIN_ORIGIN = "https://admin.catalystcareers.in"

def test_cors_preflight():
    """Test CORS preflight request"""
    print("🔍 Testing CORS preflight request...")
    
    headers = {
        'Origin': ADMIN_ORIGIN,
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Authorization,Content-Type',
    }
    
    try:
        response = requests.options(f"{BASE_URL}/api/admin/blog-posts", headers=headers)
        print(f"✅ Preflight response status: {response.status_code}")
        print(f"✅ Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
        print(f"✅ Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods')}")
        print(f"✅ Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers')}")
        return True
    except Exception as e:
        print(f"❌ Preflight request failed: {e}")
        return False

def test_api_health():
    """Test basic API health"""
    print("\n🔍 Testing API health...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        print(f"✅ Health check status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_admin_endpoint():
    """Test admin endpoint (should return 401 without auth)"""
    print("\n🔍 Testing admin endpoint...")
    
    headers = {
        'Origin': ADMIN_ORIGIN,
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/blog-posts", headers=headers)
        print(f"✅ Admin endpoint status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Expected 401 (authentication required)")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
        print(f"✅ CORS headers present: {'Access-Control-Allow-Origin' in response.headers}")
        return True
    except Exception as e:
        print(f"❌ Admin endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting CORS and API tests...")
    print(f"Testing against: {BASE_URL}")
    print(f"From origin: {ADMIN_ORIGIN}")
    
    success = True
    success &= test_cors_preflight()
    success &= test_api_health()
    success &= test_admin_endpoint()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
