#!/usr/bin/env python3
"""
Test script for the enhanced Space Events Recommendation API
Tests the /recommend endpoint with NASA API integration
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_model_info():
    """Test the model info endpoint"""
    print("\n🔍 Testing model info...")
    try:
        response = requests.get(f"{API_BASE_URL}/model/info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model info: {data}")
            return True
        else:
            print(f"❌ Model info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model info error: {e}")
        return False

def test_nasa_events():
    """Test the NASA events endpoint"""
    print("\n🔍 Testing NASA events...")
    try:
        response = requests.get(f"{API_BASE_URL}/nasa/events")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ NASA events: {data['total_events']} events found")
            for event in data['events']:
                print(f"  - {event.get('title', event['event_type'])} ({event['source']})")
            return True
        else:
            print(f"❌ NASA events failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ NASA events error: {e}")
        return False

def test_recommendation(user_prefs, description):
    """Test the recommendation endpoint with given preferences"""
    print(f"\n🔍 Testing recommendation: {description}")
    print(f"   Preferences: {user_prefs}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/recommend",
            json=user_prefs,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recommendation successful!")
            print(f"   Total recommendations: {data['total_recommendations']}")
            print(f"   NASA events included: {data['nasa_events_included']}")
            print(f"   Timestamp: {data['timestamp']}")
            
            print("\n   Recommendations:")
            for i, rec in enumerate(data['recommendations'], 1):
                print(f"   {i}. {rec['event_type']} in {rec['location']}")
                print(f"      Time: {rec['time_of_day']}, Duration: {rec['duration']} min")
                print(f"      Popularity: {rec['popularity_score']}, Like Probability: {rec['like_probability']:.2f}")
                print(f"      Source: {rec['source']}, Reason: {rec['reason']}")
                if 'title' in rec:
                    print(f"      Title: {rec['title']}")
                if 'description' in rec:
                    print(f"      Description: {rec['description']}")
                print()
            return True
        else:
            print(f"❌ Recommendation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Recommendation error: {e}")
        return False

def test_all_recommendations():
    """Test various recommendation scenarios"""
    test_cases = [
        {
            "prefs": {
                "event_type": "meteor shower",
                "location": "USA",
                "time_of_day": "night",
                "include_nasa": True
            },
            "description": "Meteor shower in USA at night with NASA events"
        },
        {
            "prefs": {
                "event_type": "solar eclipse",
                "location": "Europe",
                "time_of_day": "day",
                "include_nasa": True
            },
            "description": "Solar eclipse in Europe during day with NASA events"
        },
        {
            "prefs": {
                "event_type": "rocket launch",
                "location": "Asia",
                "time_of_day": "day",
                "include_nasa": False
            },
            "description": "Rocket launch in Asia during day without NASA events"
        },
        {
            "prefs": {
                "event_type": "aurora borealis",
                "location": "Canada",
                "time_of_day": "night",
                "include_nasa": True
            },
            "description": "Aurora borealis in Canada at night with NASA events"
        }
    ]
    
    results = []
    for test_case in test_cases:
        success = test_recommendation(test_case["prefs"], test_case["description"])
        results.append(success)
        time.sleep(1)  # Small delay between requests
    
    return results

def test_error_cases():
    """Test error handling"""
    print("\n🔍 Testing error cases...")
    
    # Test missing required field
    print("   Testing missing required field...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/recommend",
            json={"event_type": "meteor shower"},  # Missing location and time_of_day
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 400:
            print("✅ Correctly handled missing required field")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error case test failed: {e}")
    
    # Test empty request
    print("   Testing empty request...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/recommend",
            json={},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 400:
            print("✅ Correctly handled empty request")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error case test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Space Events Recommendation API Test Suite")
    print("=" * 50)
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test basic endpoints
    health_ok = test_health_check()
    if not health_ok:
        print("❌ API is not running or not healthy. Please start the API first.")
        return
    
    model_ok = test_model_info()
    nasa_ok = test_nasa_events()
    
    # Test recommendations
    print("\n" + "=" * 50)
    print("Testing Recommendation Endpoint")
    print("=" * 50)
    
    recommendation_results = test_all_recommendations()
    
    # Test error cases
    print("\n" + "=" * 50)
    print("Testing Error Handling")
    print("=" * 50)
    
    test_error_cases()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    total_tests = 1 + 1 + 1 + len(recommendation_results)  # health + model + nasa + recommendations
    passed_tests = sum([health_ok, model_ok, nasa_ok] + recommendation_results)
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! The API is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the API configuration.")

if __name__ == "__main__":
    main() 