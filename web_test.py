#!/usr/bin/env python3
"""
Test script for SkyQuest Tracker Web Application
Tests all endpoints and functionality
"""

import requests
import json
import time
import sys
from datetime import datetime

class WebAppTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': timestamp,
            'response': response
        }
        self.test_results.append(result)
        print(f"[{timestamp}] {status} - {test_name}: {message}")
        
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
    
    def test_main_page(self):
        """Test main page loads"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("Main Page", True, "Page loaded successfully")
            else:
                self.log_test("Main Page", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Main Page", False, f"Error: {str(e)}")
    
    def test_api_events(self):
        """Test API events endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/events")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    events_count = len(data.get('data', {}).get('events', []))
                    self.log_test("API Events", True, f"Found {events_count} events")
                else:
                    self.log_test("API Events", False, f"API error: {data.get('message')}")
            else:
                self.log_test("API Events", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Events", False, f"Error: {str(e)}")
    
    def test_api_event_types(self):
        """Test API event types endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/event-types")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    types_count = len(data.get('data', {}).get('event_types', []))
                    self.log_test("API Event Types", True, f"Found {types_count} event types")
                else:
                    self.log_test("API Event Types", False, f"API error: {data.get('message')}")
            else:
                self.log_test("API Event Types", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Event Types", False, f"Error: {str(e)}")
    
    def test_api_locations(self):
        """Test API locations endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/locations")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    locations_count = len(data.get('data', {}).get('locations', []))
                    self.log_test("API Locations", True, f"Found {locations_count} locations")
                else:
                    self.log_test("API Locations", False, f"API error: {data.get('message')}")
            else:
                self.log_test("API Locations", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Locations", False, f"Error: {str(e)}")
    
    def test_api_recommendations(self):
        """Test API recommendations endpoint"""
        test_data = {
            "event_type": "meteor shower",
            "location": "USA",
            "time_of_day": "night"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/recommend",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    recommendations_count = len(data.get('data', {}).get('recommendations', []))
                    self.log_test("API Recommendations", True, f"Got {recommendations_count} recommendations")
                else:
                    self.log_test("API Recommendations", False, f"API error: {data.get('message')}")
            else:
                self.log_test("API Recommendations", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Recommendations", False, f"Error: {str(e)}")
    
    def test_api_feedback(self):
        """Test API feedback endpoint"""
        test_data = {
            "user_preferences": {
                "event_type": "meteor shower",
                "location": "USA",
                "time_of_day": "night"
            },
            "selected_event": {
                "event_type": "meteor shower",
                "location": "USA"
            },
            "feedback": "positive",
            "recommendations_shown": 3
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/feedback",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_test("API Feedback", True, "Feedback submitted successfully")
                else:
                    self.log_test("API Feedback", False, f"API error: {data.get('message')}")
            else:
                self.log_test("API Feedback", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Feedback", False, f"Error: {str(e)}")
    
    def test_api_stats(self):
        """Test API stats endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/stats")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_test("API Stats", True, "Stats retrieved successfully")
                else:
                    self.log_test("API Stats", False, f"API error: {data.get('message')}")
            else:
                self.log_test("API Stats", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Stats", False, f"Error: {str(e)}")
    
    def test_error_pages(self):
        """Test error pages"""
        # Test 404 page
        try:
            response = self.session.get(f"{self.base_url}/nonexistent-page")
            if response.status_code == 404:
                self.log_test("404 Error Page", True, "404 page served correctly")
            else:
                self.log_test("404 Error Page", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("404 Error Page", False, f"Error: {str(e)}")
    
    def test_static_files(self):
        """Test static files are served"""
        try:
            response = self.session.get(f"{self.base_url}/static/css/style.css")
            if response.status_code == 200:
                self.log_test("Static CSS", True, "CSS file served correctly")
            else:
                self.log_test("Static CSS", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Static CSS", False, f"Error: {str(e)}")
        
        try:
            response = self.session.get(f"{self.base_url}/static/js/app.js")
            if response.status_code == 200:
                self.log_test("Static JS", True, "JS file served correctly")
            else:
                self.log_test("Static JS", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Static JS", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("SkyQuest Tracker Web Application Test Suite")
        print("=" * 60)
        print(f"Testing web application at: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all tests
        self.test_health_check()
        self.test_main_page()
        self.test_api_events()
        self.test_api_event_types()
        self.test_api_locations()
        self.test_api_recommendations()
        self.test_api_feedback()
        self.test_api_stats()
        self.test_error_pages()
        self.test_static_files()
        
        # Print summary
        print()
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print()
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print()
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return failed_tests == 0

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test SkyQuest Tracker Web Application')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL of the web application (default: http://localhost:8000)')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Request timeout in seconds (default: 10)')
    
    args = parser.parse_args()
    
    # Set timeout for requests
    requests.adapters.DEFAULT_RETRIES = 1
    
    # Create tester and run tests
    tester = WebAppTester(args.url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 