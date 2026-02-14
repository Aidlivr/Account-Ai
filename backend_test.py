import requests
import sys
import json
import io
from datetime import datetime

class AIAccountingAPITester:
    def __init__(self, base_url="https://fintech-ocr-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tenant_id = None
        self.document_id = None
        self.voucher_id = None
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

    def test_provider_config(self):
        """Test provider configuration endpoints"""
        if not self.token or not self.tenant_id:
            self.log_test("Provider Config - GET", False, "No auth token or tenant available")
            return False
            
        # Test GET provider config
        success, response = self.run_test("Provider Config - GET", "GET", f"/tenants/{self.tenant_id}/provider", 200)
        
        if not success:
            return False
            
        # Test PUT provider config
        config_data = {
            "provider_type": "e-conomic",
            "agreement_number": "123456",
            "user_token": "test_token_123",
            "is_active": True
        }
        
        success, response = self.run_test("Provider Config - PUT", "PUT", f"/tenants/{self.tenant_id}/provider", 200, config_data)
        return success

    def test_document_upload(self):
        """Test document upload with mock PDF"""
        if not self.token or not self.tenant_id:
            self.log_test("Document Upload", False, "No auth token or tenant available")
            return False
            
        # Create a simple mock PDF content
        mock_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        
        files = {
            'file': ('test_invoice.pdf', mock_pdf_content, 'application/pdf'),
            'tenant_id': (None, self.tenant_id)
        }
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            url = f"{self.api_base}/documents/upload"
            response = requests.post(url, files=files, headers=headers, timeout=30)
            
            success = response.status_code == 200
            
            if success:
                response_data = response.json()
                if 'id' in response_data:
                    self.document_id = response_data['id']
                self.log_test("Document Upload", True, f"Status: {response.status_code}, Document ID: {self.document_id}")
                return True
            else:
                try:
                    error_data = response.json()
                    self.log_test("Document Upload", False, f"Expected 200, got {response.status_code}. Error: {error_data}")
                except:
                    self.log_test("Document Upload", False, f"Expected 200, got {response.status_code}. Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Document Upload", False, f"Request failed: {str(e)}")
            return False

    def test_get_documents(self):
        """Test getting documents list"""
        if not self.token or not self.tenant_id:
            self.log_test("Get Documents", False, "No auth token or tenant available")
            return False
            
        success, response = self.run_test("Get Documents", "GET", f"/documents/?tenant_id={self.tenant_id}", 200)
        return success

    def test_document_edit_fields(self):
        """Test editing document fields"""
        if not self.token or not self.document_id:
            self.log_test("Document Edit Fields", False, "No auth token or document available")
            return False
            
        # Wait a bit for document processing
        import time
        time.sleep(3)
            
        edit_data = {
            "field_updates": {
                "supplier_name": "Test Supplier Updated",
                "total_amount": 1500.00
            }
        }
        
        success, response = self.run_test("Document Edit Fields", "PUT", f"/documents/{self.document_id}/edit", 200, edit_data)
        return success

    def test_document_approval(self):
        """Test document approval and voucher creation"""
        if not self.token or not self.document_id:
            self.log_test("Document Approval", False, "No auth token or document available")
            return False
            
        approval_data = {
            "approved": True,
            "final_data": {
                "supplier_name": "Test Supplier Final",
                "total_amount": 1500.00,
                "vat_amount": 300.00,
                "net_amount": 1200.00
            },
            "account_mapping": {
                "account_code": "4000",
                "account_name": "Varekøb",
                "vat_code": "25"
            }
        }
        
        success, response = self.run_test("Document Approval", "PUT", f"/documents/{self.document_id}/approve", 200, approval_data)
        
        if success and response.get('voucher_id'):
            self.voucher_id = response['voucher_id']
            
        return success

    def test_get_vouchers(self):
        """Test getting vouchers list"""
        if not self.token or not self.tenant_id:
            self.log_test("Get Vouchers", False, "No auth token or tenant available")
            return False
            
        success, response = self.run_test("Get Vouchers", "GET", f"/vouchers/{self.tenant_id}", 200)
        return success

    def test_activity_logs(self):
        """Test getting activity logs"""
        if not self.token or not self.tenant_id:
            self.log_test("Get Activity Logs", False, "No auth token or tenant available")
            return False
            
        success, response = self.run_test("Get Activity Logs", "GET", f"/activity/{self.tenant_id}", 200)
        return success

    def test_time_saved_calculation(self):
        """Test time saved calculation"""
        if not self.token or not self.tenant_id:
            self.log_test("Time Saved Calculation", False, "No auth token or tenant available")
            return False
            
        success, response = self.run_test("Time Saved Calculation", "GET", f"/activity/{self.tenant_id}/time-saved", 200)
        return success

    def test_vendor_patterns(self):
        """Test vendor patterns"""
        if not self.token or not self.tenant_id:
            self.log_test("Get Vendor Patterns", False, "No auth token or tenant available")
            return False
            
        success, response = self.run_test("Get Vendor Patterns", "GET", f"/vendors/{self.tenant_id}", 200)
        return success

    def test_admin_subscription_activation(self):
        """Test admin subscription activation"""
        if not self.token or not self.user_id:
            self.log_test("Admin Subscription Activation", False, "No auth token or user available")
            return False
            
        activation_data = {
            "user_id": self.user_id,
            "plan_id": "starter",
            "notes": "Test activation"
        }
        
        success, response = self.run_test("Admin Subscription Activation", "POST", "/admin/subscriptions/activate", 200, activation_data)
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting AI Accounting Copilot Beta-Ready MVP API Tests")
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
        
        # Provider configuration tests
        self.test_provider_config()
        
        # Document workflow tests
        self.test_document_upload()
        self.test_get_documents()
        self.test_document_edit_fields()
        self.test_document_approval()
        
        # Voucher tests
        self.test_get_vouchers()
        
        # Activity and analytics tests
        self.test_activity_logs()
        self.test_time_saved_calculation()
        self.test_vendor_patterns()
        
        # Dashboard tests
        self.test_dashboard_stats()
        
        # Billing tests
        self.test_billing_plans()
        self.test_get_current_subscription()
        
        # Admin tests
        self.test_admin_subscription_activation()
        
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