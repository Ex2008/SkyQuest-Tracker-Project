import requests
import json
import time
import sys

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
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

def test_events_endpoint():
    """Test the events endpoint"""
    print("\nTesting events endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/events")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Events endpoint passed: {data['total_events']} events found")
            return True
        else:
            print(f"❌ Events endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Events endpoint error: {e}")
        return False

def test_recommend_endpoint():
    """Test the recommend endpoint with various inputs"""
    print("\nTesting recommend endpoint...")
    
    test_cases = [
        {
            "name": "Meteor shower in USA at night",
            "data": {
                "event_type": "meteor shower",
                "location": "USA",
                "time_of_day": "night"
            }
        },
        {
            "name": "Solar eclipse in Europe during day",
            "data": {
                "event_type": "solar eclipse",
                "location": "Europe",
                "time_of_day": "day"
            }
        },
        {
            "name": "Aurora borealis in Norway at night",
            "data": {
                "event_type": "aurora borealis",
                "location": "Norway",
                "time_of_day": "night"
            }
        },
        {
            "name": "Rocket launch in Asia during day",
            "data": {
                "event_type": "rocket launch",
                "location": "Asia",
                "time_of_day": "day"
            }
        }
    ]
    
    success_count = 0
    for test_case in test_cases:
        try:
            print(f"\n  Testing: {test_case['name']}")
            response = requests.post(
                f"{BASE_URL}/recommend",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get('recommendations', [])
                print(f"    ✅ Success: {len(recommendations)} recommendations")
                for i, rec in enumerate(recommendations[:2], 1):  # Show first 2
                    print(f"      {i}. {rec['event_type']} in {rec['location']} "
                          f"(prob: {rec.get('like_probability', 0):.2f})")
                success_count += 1
            else:
                print(f"    ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    print(f"\n✅ Recommend endpoint: {success_count}/{len(test_cases)} tests passed")
    return success_count == len(test_cases)

def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\nTesting error handling...")
    
    error_cases = [
        {
            "name": "Missing event_type",
            "data": {
                "location": "USA",
                "time_of_day": "night"
            }
        },
        {
            "name": "Invalid event_type",
            "data": {
                "event_type": "invalid_event",
                "location": "USA",
                "time_of_day": "night"
            }
        },
        {
            "name": "Empty request",
            "data": {}
        }
    ]
    
    success_count = 0
    for test_case in error_cases:
        try:
            print(f"\n  Testing: {test_case['name']}")
            response = requests.post(
                f"{BASE_URL}/recommend",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [400, 500]:  # Expected error codes
                print(f"    ✅ Correctly handled error: {response.status_code}")
                success_count += 1
            else:
                print(f"    ❌ Unexpected response: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    print(f"\n✅ Error handling: {success_count}/{len(error_cases)} tests passed")
    return success_count == len(error_cases)

def test_performance():
    """Test API performance with multiple requests"""
    print("\nTesting performance...")
    
    test_data = {
        "event_type": "meteor shower",
        "location": "USA",
        "time_of_day": "night"
    }
    
    start_time = time.time()
    response_times = []
    
    for i in range(10):
        request_start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/recommend",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            request_time = time.time() - request_start
            response_times.append(request_time)
            
            if response.status_code == 200:
                print(f"  Request {i+1}: {request_time:.3f}s ✅")
            else:
                print(f"  Request {i+1}: {request_time:.3f}s ❌")
                
        except Exception as e:
            print(f"  Request {i+1}: Error - {e}")
    
    total_time = time.time() - start_time
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    print(f"\n📊 Performance Results:")
    print(f"  Total time: {total_time:.3f}s")
    print(f"  Average response time: {avg_response_time:.3f}s")
    print(f"  Requests per second: {10/total_time:.1f}")
    
    return avg_response_time < 1.0  # Should be under 1 second

def main():
    """Run all tests"""
    print("🚀 Starting API Tests...")
    print("=" * 50)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Events Endpoint", test_events_endpoint),
        ("Recommend Endpoint", test_recommend_endpoint),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the API implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main() 