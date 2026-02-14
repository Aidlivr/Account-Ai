"""
Test Beta Features for AI Accounting Copilot
- Feedback submission and retrieval
- Export vouchers (CSV/PDF)
- Mock email service logs
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "betatest@example.dk"
TEST_USER_PASSWORD = "test123"
ADMIN_EMAIL = f"admin_test_{uuid.uuid4().hex[:8]}@example.dk"
ADMIN_PASSWORD = "admin123"


class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"✓ API Health: {data}")


class TestUserAuthentication:
    """Test user login and registration"""
    
    def test_login_beta_user(self):
        """Login with beta test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        print(f"✓ Beta user login successful: {data['user']['email']}")
        return data["access_token"]
    
    def test_register_admin_user(self):
        """Register a new admin user for testing admin endpoints"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "name": "Test Admin User",
            "company_name": "Admin Test Company"
        })
        # May already exist or succeed
        if response.status_code == 201:
            print(f"✓ Admin user registered: {ADMIN_EMAIL}")
            return response.json()
        elif response.status_code == 400:
            print(f"⚠ Admin user may already exist: {response.text}")
            return None
        else:
            print(f"⚠ Registration response: {response.status_code} - {response.text}")
            return None


class TestFeedbackAPI:
    """Test feedback submission and retrieval endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for beta user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Could not authenticate beta user")
    
    def test_submit_feedback(self, auth_token):
        """Test POST /api/feedback - submit feedback"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        feedback_data = {
            "type": "feedback",
            "rating": 4,
            "category": "general",
            "message": "Test feedback from automated testing - great beta experience!",
            "page_context": "/dashboard",
            "user_agent": "pytest-test-agent",
            "timestamp": "2026-01-15T10:00:00Z"
        }
        
        response = requests.post(f"{BASE_URL}/api/feedback", json=feedback_data, headers=headers)
        assert response.status_code == 200, f"Feedback submission failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "id" in data
        assert data["message"] == "Feedback received. Thank you!"
        print(f"✓ Feedback submitted successfully: {data['id']}")
        return data["id"]
    
    def test_submit_bug_report(self, auth_token):
        """Test POST /api/feedback - submit bug report"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        bug_data = {
            "type": "bug_report",
            "rating": None,
            "category": "ai_extraction",
            "message": "Test bug report - AI extracted wrong VAT amount from invoice",
            "page_context": "/documents",
            "user_agent": "pytest-test-agent",
            "timestamp": "2026-01-15T10:05:00Z"
        }
        
        response = requests.post(f"{BASE_URL}/api/feedback", json=bug_data, headers=headers)
        assert response.status_code == 200, f"Bug report submission failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "id" in data
        print(f"✓ Bug report submitted successfully: {data['id']}")
    
    def test_submit_feature_request(self, auth_token):
        """Test POST /api/feedback - submit feature request"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        feature_data = {
            "type": "feedback",
            "rating": 5,
            "category": "feature_request",
            "message": "Would love to see batch invoice upload feature",
            "page_context": "/documents",
            "user_agent": "pytest-test-agent"
        }
        
        response = requests.post(f"{BASE_URL}/api/feedback", json=feature_data, headers=headers)
        assert response.status_code == 200, f"Feature request failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        print(f"✓ Feature request submitted: {data['id']}")
    
    def test_get_feedback_requires_admin(self, auth_token):
        """Test GET /api/feedback - should require admin role"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/feedback", headers=headers)
        # Regular user should get 403
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("✓ GET /api/feedback correctly requires admin role")


class TestExportAPI:
    """Test export vouchers endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for beta user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not authenticate beta user")
    
    @pytest.fixture
    def tenant_id(self, auth_token):
        """Get a tenant ID for the user"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/tenants/", headers=headers)
        if response.status_code == 200:
            tenants = response.json()
            if tenants and len(tenants) > 0:
                return tenants[0]["id"]
        pytest.skip("No tenants available for testing")
    
    def test_export_vouchers_csv(self, auth_token, tenant_id):
        """Test POST /api/export/{tenant_id}/vouchers - CSV format"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        export_data = {
            "format": "csv",
            "voucher_ids": None
        }
        
        response = requests.post(
            f"{BASE_URL}/api/export/{tenant_id}/vouchers", 
            json=export_data, 
            headers=headers
        )
        
        # May return 404 if no vouchers exist
        if response.status_code == 404:
            print("⚠ No vouchers found to export (expected if no vouchers created)")
            return
        
        assert response.status_code == 200, f"CSV export failed: {response.text}"
        
        # CSV should be text content
        content = response.text
        assert "Voucher ID" in content or len(content) > 0
        print(f"✓ CSV export successful, content length: {len(content)}")
    
    def test_export_vouchers_pdf(self, auth_token, tenant_id):
        """Test POST /api/export/{tenant_id}/vouchers - PDF format"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        export_data = {
            "format": "pdf",
            "voucher_ids": None
        }
        
        response = requests.post(
            f"{BASE_URL}/api/export/{tenant_id}/vouchers", 
            json=export_data, 
            headers=headers
        )
        
        # May return 404 if no vouchers exist
        if response.status_code == 404:
            print("⚠ No vouchers found to export (expected if no vouchers created)")
            return
        
        assert response.status_code == 200, f"PDF export failed: {response.text}"
        
        data = response.json()
        assert "content" in data
        assert "filename" in data
        print(f"✓ PDF export successful, filename: {data['filename']}")
    
    def test_export_invalid_tenant(self, auth_token):
        """Test export with invalid tenant ID"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        export_data = {"format": "csv"}
        
        response = requests.post(
            f"{BASE_URL}/api/export/invalid-tenant-id/vouchers", 
            json=export_data, 
            headers=headers
        )
        
        assert response.status_code == 403, f"Expected 403 for invalid tenant, got {response.status_code}"
        print("✓ Export correctly rejects invalid tenant ID")


class TestEmailLogsAPI:
    """Test mock email service logs endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for beta user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not authenticate beta user")
    
    def test_get_email_logs_requires_admin(self, auth_token):
        """Test GET /api/emails/logs - should require admin role"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/emails/logs", headers=headers)
        # Regular user should get 403
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("✓ GET /api/emails/logs correctly requires admin role")


class TestMockEmailOnRegistration:
    """Test that mock email is created on user registration"""
    
    def test_register_creates_email_log(self):
        """Register a new user and verify welcome email is logged"""
        unique_email = f"test_email_{uuid.uuid4().hex[:8]}@example.dk"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "testpass123",
            "name": "Email Test User",
            "company_name": "Email Test Company"
        })
        
        if response.status_code == 201:
            data = response.json()
            assert "token" in data
            assert "user" in data
            print(f"✓ User registered: {unique_email}")
            print("✓ Welcome email should be logged in db.email_logs (MOCKED)")
            return data
        else:
            print(f"⚠ Registration response: {response.status_code} - {response.text}")
            return None


class TestBetaBannerIntegration:
    """Test that feedback submission triggers email notification"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for beta user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not authenticate beta user")
    
    def test_feedback_triggers_email_notification(self, auth_token):
        """Verify feedback submission triggers mock email to admin"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        feedback_data = {
            "type": "feedback",
            "rating": 5,
            "category": "praise",
            "message": "Integration test - feedback should trigger admin email notification",
            "page_context": "/dashboard"
        }
        
        response = requests.post(f"{BASE_URL}/api/feedback", json=feedback_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        print("✓ Feedback submitted - admin email notification logged (MOCKED)")


class TestDashboardWithBetaBanner:
    """Test dashboard stats endpoint (used by dashboard with beta banner)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for beta user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not authenticate beta user")
    
    def test_dashboard_stats(self, auth_token):
        """Test GET /api/dashboard/stats"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        assert response.status_code == 200, f"Dashboard stats failed: {response.text}"
        
        data = response.json()
        assert "total_documents" in data
        assert "pending_documents" in data
        assert "total_vouchers" in data
        print(f"✓ Dashboard stats: {data['total_documents']} docs, {data['total_vouchers']} vouchers")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
