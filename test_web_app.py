#!/usr/bin/env python3
"""
Test script for SkyQuest Tracker Web Application
"""

import requests
import time
import sys
import os

def test_web_app():
    """Test the web application endpoints"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing SkyQuest Tracker Web Application...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Landing Page
    print("\n2. Testing Landing Page...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Landing page loads successfully")
        else:
            print(f"❌ Landing page failed: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Landing page failed: {e}")
        return False
    
    # Test 3: Recommendations Page
    print("\n3. Testing Recommendations Page...")
    try:
        response = requests.get(f"{base_url}/recommendations", timeout=5)
        if response.status_code == 200:
            print("✅ Recommendations page loads successfully")
        else:
            print(f"❌ Recommendations page failed: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Recommendations page failed: {e}")
        return False
    
    # Test 4: Events Page
    print("\n4. Testing Events Page...")
    try:
        response = requests.get(f"{base_url}/events", timeout=5)
        if response.status_code == 200:
            print("✅ Events page loads successfully")
        else:
            print(f"❌ Events page failed: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Events page failed: {e}")
        return False
    
    # Test 5: About Page
    print("\n5. Testing About Page...")
    try:
        response = requests.get(f"{base_url}/about", timeout=5)
        if response.status_code == 200:
            print("✅ About page loads successfully")
        else:
            print(f"❌ About page failed: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ About page failed: {e}")
        return False
    
    # Test 6: API Endpoints (with fallback data)
    print("\n6. Testing API Endpoints...")
    try:
        response = requests.get(f"{base_url}/api/events", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Events API works: {len(data.get('events', []))} events returned")
        else:
            print(f"❌ Events API failed: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Events API failed: {e}")
        return False
    
    # Test 7: Recommendations API
    print("\n7. Testing Recommendations API...")
    try:
        test_data = {
            "event_type": "meteor_shower",
            "location": "USA",
            "time_of_day": "night"
        }
        response = requests.post(f"{base_url}/api/recommend", json=test_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recommendations API works: {len(data.get('recommendations', []))} recommendations returned")
        else:
            print(f"❌ Recommendations API failed: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Recommendations API failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The web application is working correctly.")
    print("\n📱 You can now access the application at:")
    print(f"   Landing Page: {base_url}")
    print(f"   Recommendations: {base_url}/recommendations")
    print(f"   Events: {base_url}/events")
    print(f"   About: {base_url}/about")
    print(f"   Health Check: {base_url}/health")
    
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Flask is not installed")
        print("   Run: pip install -r web_requirements.txt")
        return False
    
    try:
        import requests
        print("✅ Requests is installed")
    except ImportError:
        print("❌ Requests is not installed")
        print("   Run: pip install -r web_requirements.txt")
        return False
    
    return True

def main():
    """Main test function"""
    print("SkyQuest Tracker - Web Application Test")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install required packages.")
        sys.exit(1)
    
    # Check if web app is running
    print("\n🔍 Checking if web app is running...")
    try:
        response = requests.get("http://localhost:5001/health", timeout=3)
        if response.status_code == 200:
            print("✅ Web app is running")
        else:
            print("❌ Web app is not responding correctly")
            print("   Please start the web app first:")
            print("   Windows: start_web_only.bat")
            print("   Linux/Mac: ./start_web_only.sh")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Web app is not running")
        print("   Please start the web app first:")
        print("   Windows: start_web_only.bat")
        print("   Linux/Mac: ./start_web_only.sh")
        sys.exit(1)
    
    # Run tests
    if test_web_app():
        print("\n🎯 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 