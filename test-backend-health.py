#!/usr/bin/env python3
"""
Backend Health Test Script
Tests the GCP Cloud Run backend endpoints to verify configuration
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL
BACKEND_URL = "https://catalyst-career-ai-backend-147549542423.asia-southeast1.run.app"

def test_endpoint(endpoint, description):
    """Test a specific endpoint and return results"""
    url = f"{BACKEND_URL}{endpoint}"
    print(f"\n🔍 Testing {description}...")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                return True, data
            except json.JSONDecodeError:
                print(f"   Response: {response.text}")
                return True, response.text
        else:
            print(f"   Error: {response.text}")
            return False, response.text
            
    except requests.exceptions.Timeout:
        print("   ❌ Timeout error")
        return False, "timeout"
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error")
        return False, "connection_error"
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, str(e)

def main():
    print("🚀 Catalyst Career AI Backend Health Check")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test endpoints
    endpoints = [
        ("/ping", "Basic Ping"),
        ("/api/status", "API Status"),
        ("/api/health", "Health Check"),
        ("/api/blog-posts", "Blog Posts"),
        ("/api/system-status", "System Status"),
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        success, data = test_endpoint(endpoint, description)
        results.append({
            "endpoint": endpoint,
            "description": description,
            "success": success,
            "data": data
        })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    if successful == total:
        print("\n🎉 All endpoints are working correctly!")
        print("   Your backend is properly configured.")
    else:
        print("\n⚠️  Some endpoints are failing.")
        print("   Please check the environment variables in GCP Cloud Run.")
        print("   See setup-gcp-env.md for configuration instructions.")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS")
    print("=" * 50)
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['description']}: {result['endpoint']}")
        if not result["success"]:
            print(f"   Error: {result['data']}")

if __name__ == "__main__":
    main()
