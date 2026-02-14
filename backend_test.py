import requests
import sys
import json
from datetime import datetime

class AIAccountingAPITester:
    def __init__(self, base_url="https://ai-accounting-12.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tenant_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_base}{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    self.log_test(name, True, f"Status: {response.status_code}")
                    return True, response_data
                except:
                    self.log_test(name, True, f"Status: {response.status_code} (No JSON response)")
                    return True, {}
            else:
                try:
                    error_data = response.json()
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Error: {error_data}")
                except:
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Request failed: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health check"""
        success, _ = self.run_test("Health Check", "GET", "/health", 200)
        return success

    def test_register_user(self):
        """Test user registration"""
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.dk"
        user_data = {
            "email": test_email,
            "password": "testpass123",
            "name": "Test User",
            "role": "sme_user"
        }
        
        success, response = self.run_test("User Registration", "POST", "/auth/register", 200, user_data)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            return True
        return False

    def test_login_existing_user(self):
        """Test login with existing test user"""
        login_data = {
            "email": "test@example.dk",
            "password": "test123"
        }
        
        success, response = self.run_test("User Login (Existing)", "POST", "/auth/login", 200, login_data)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            return True
        return False

    def test_get_current_user(self):
        """Test get current user info"""
        if not self.token:
            self.log_test("Get Current User", False, "No auth token available")
            return False
            
        success, response = self.run_test("Get Current User", "GET", "/auth/me", 200)
        return success

    def test_create_tenant(self):
        """Test creating a company/tenant"""
        if not self.token:
            self.log_test("Create Tenant", False, "No auth token available")
            return False
            
        tenant_data = {
            "name": f"Test Company {datetime.now().strftime('%H%M%S')}",
            "cvr_number": "12345678",
            "address": "Test Street 123, Copenhagen",
            "settings": {"currency": "DKK"}
        }
        
        success, response = self.run_test("Create Tenant", "POST", "/tenants/", 200, tenant_data)
        
        if success and 'id' in response:
            self.tenant_id = response['id']
            return True
        return False

    def test_get_user_tenants(self):
        """Test getting user's tenants"""
        if not self.token:
            self.log_test("Get User Tenants", False, "No auth token available")
            return False
            
        success, response = self.run_test("Get User Tenants", "GET", "/tenants/", 200)
        return success

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        if not self.token:
            self.log_test("Dashboard Stats", False, "No auth token available")
            return False
            
        success, response = self.run_test("Dashboard Stats", "GET", "/dashboard/stats", 200)
        return success

    def test_billing_plans(self):
        """Test getting billing plans"""
        success, response = self.run_test("Get Billing Plans", "GET", "/billing/plans", 200)
        return success

    def test_create_subscription(self):
        """Test creating a subscription"""
        if not self.token:
            self.log_test("Create Subscription", False, "No auth token available")
            return False
            
        subscription_data = {
            "plan_id": "starter"
        }
        
        success, response = self.run_test("Create Subscription", "POST", "/billing/subscribe", 200, subscription_data)
        return success

    def test_get_current_subscription(self):
        """Test getting current subscription"""
        if not self.token:
            self.log_test("Get Current Subscription", False, "No auth token available")
            return False
            
        success, response = self.run_test("Get Current Subscription", "GET", "/billing/subscription", 200)
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting AI Accounting Copilot API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Health check
        self.test_health_check()
        
        # Try login with existing user first
        if not self.test_login_existing_user():
            # If login fails, try registration
            self.test_register_user()
        
        # Auth tests
        self.test_get_current_user()
        
        # Tenant tests
        self.test_create_tenant()
        self.test_get_user_tenants()
        
        # Dashboard tests
        self.test_dashboard_stats()
        
        # Billing tests
        self.test_billing_plans()
        self.test_create_subscription()
        self.test_get_current_subscription()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = AIAccountingAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())