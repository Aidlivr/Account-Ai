"""
Test AI Dashboard and Accounting Data Endpoints for AI Accounting Copilot
Production AI Architecture Upgrade - Version 2.1.0-beta

Tests:
- GET /api/accounting-data/chart-of-accounts (73 Danish accounts)
- GET /api/accounting-data/vat-codes (10 VAT codes)
- GET /api/accounting-data/journals (8 journals)
- GET /api/accounting-data/available-countries (DK active)
- GET /api/ai-dashboard/stats (admin/accountant only)
- GET /api/ai-dashboard/corrections (admin only)
- GET /api/ai-dashboard/vendor-accuracy/{tenant_id}
- GET /api/ai-dashboard/active-companies/{year}/{month} (admin only)
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@aiaccounting.dk"
ADMIN_PASSWORD = "admin123"
SME_USER_EMAIL = "betatest@example.dk"
SME_USER_PASSWORD = "test123"


class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"✓ API Health: {data}")


class TestAuthentication:
    """Test authentication for admin and SME users"""
    
    def test_admin_login(self):
        """Login with admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin", f"Expected admin role, got {data['user']['role']}"
        print(f"✓ Admin login successful: {data['user']['email']} (role: {data['user']['role']})")
        return data["access_token"]
    
    def test_sme_user_login(self):
        """Login with SME test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": SME_USER_EMAIL,
            "password": SME_USER_PASSWORD
        })
        assert response.status_code == 200, f"SME user login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        print(f"✓ SME user login successful: {data['user']['email']} (role: {data['user']['role']})")
        return data["access_token"]


class TestAccountingDataEndpoints:
    """Test Danish accounting data endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for SME user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": SME_USER_EMAIL,
            "password": SME_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Could not authenticate SME user")
    
    def test_get_chart_of_accounts(self, auth_token):
        """Test GET /api/accounting-data/chart-of-accounts - should return 73 Danish accounts"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/accounting-data/chart-of-accounts", headers=headers)
        assert response.status_code == 200, f"Chart of accounts failed: {response.text}"
        
        data = response.json()
        assert "accounts" in data
        assert "total" in data
        assert "country" in data
        
        # Verify 73 accounts
        assert data["total"] == 73, f"Expected 73 accounts, got {data['total']}"
        assert data["country"] == "DK"
        
        # Verify account structure
        accounts = data["accounts"]
        assert len(accounts) == 73
        
        # Check first account structure
        first_account = accounts[0]
        assert "code" in first_account
        assert "name" in first_account
        assert "type" in first_account
        assert "category" in first_account
        
        # Verify some key accounts exist
        account_codes = [a["code"] for a in accounts]
        assert "1000" in account_codes  # Kasse
        assert "1010" in account_codes  # Bank
        assert "4000" in account_codes  # Varekøb
        assert "9000" in account_codes  # Indgående moms
        
        print(f"✓ Chart of Accounts: {data['total']} accounts for {data['country']}")
        print(f"  Sample accounts: {accounts[0]['code']} - {accounts[0]['name']}")
    
    def test_get_vat_codes(self, auth_token):
        """Test GET /api/accounting-data/vat-codes - should return 10 VAT codes"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/accounting-data/vat-codes", headers=headers)
        assert response.status_code == 200, f"VAT codes failed: {response.text}"
        
        data = response.json()
        assert "vat_codes" in data
        assert "total" in data
        assert "country" in data
        
        # Verify 10 VAT codes
        assert data["total"] == 10, f"Expected 10 VAT codes, got {data['total']}"
        assert data["country"] == "DK"
        
        vat_codes = data["vat_codes"]
        assert len(vat_codes) == 10
        
        # Check VAT code structure
        first_vat = vat_codes[0]
        assert "code" in first_vat
        assert "name" in first_vat
        assert "rate" in first_vat
        assert "type" in first_vat
        
        # Verify key VAT codes exist
        vat_code_list = [v["code"] for v in vat_codes]
        assert "I25" in vat_code_list  # Indgående moms 25%
        assert "U25" in vat_code_list  # Udgående moms 25%
        assert "IEU" in vat_code_list  # EU-erhvervelser
        assert "IREV" in vat_code_list  # Reverse charge
        assert "MOMSFRI" in vat_code_list  # Momsfritaget
        
        print(f"✓ VAT Codes: {data['total']} codes for {data['country']}")
        print(f"  Sample: {vat_codes[0]['code']} - {vat_codes[0]['name']} ({vat_codes[0]['rate']}%)")
    
    def test_get_journals(self, auth_token):
        """Test GET /api/accounting-data/journals - should return 8 journals"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/accounting-data/journals", headers=headers)
        assert response.status_code == 200, f"Journals failed: {response.text}"
        
        data = response.json()
        assert "journals" in data
        assert "total" in data
        assert "country" in data
        
        # Verify 8 journals
        assert data["total"] == 8, f"Expected 8 journals, got {data['total']}"
        assert data["country"] == "DK"
        
        journals = data["journals"]
        assert len(journals) == 8
        
        # Check journal structure
        first_journal = journals[0]
        assert "code" in first_journal
        assert "name" in first_journal
        assert "type" in first_journal
        
        # Verify key journals exist
        journal_codes = [j["code"] for j in journals]
        assert "KOB" in journal_codes  # Købsjournal
        assert "SALG" in journal_codes  # Salgsjournal
        assert "BANK" in journal_codes  # Bankjournal
        assert "LON" in journal_codes  # Lønjournal
        
        print(f"✓ Journals: {data['total']} journals for {data['country']}")
        print(f"  Sample: {journals[0]['code']} - {journals[0]['name']}")
    
    def test_get_available_countries(self, auth_token):
        """Test GET /api/accounting-data/available-countries - DK should be active"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/accounting-data/available-countries", headers=headers)
        assert response.status_code == 200, f"Available countries failed: {response.text}"
        
        data = response.json()
        assert "countries" in data
        assert "active" in data
        
        # Verify DK is active
        assert data["active"] == "DK", f"Expected DK as active, got {data['active']}"
        
        # Verify available countries include DK, SE, NO
        countries = data["countries"]
        assert "DK" in countries
        assert "SE" in countries  # Prepared
        assert "NO" in countries  # Prepared
        
        print(f"✓ Available Countries: {countries}")
        print(f"  Active: {data['active']}")


class TestAIDashboardEndpoints:
    """Test AI Dashboard endpoints with role-based access"""
    
    @pytest.fixture
    def admin_token(self):
        """Get auth token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Could not authenticate admin user")
    
    @pytest.fixture
    def sme_token(self):
        """Get auth token for SME user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": SME_USER_EMAIL,
            "password": SME_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Could not authenticate SME user")
    
    def test_ai_dashboard_stats_admin(self, admin_token):
        """Test GET /api/ai-dashboard/stats - admin should have access"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/ai-dashboard/stats", headers=headers)
        assert response.status_code == 200, f"AI Dashboard stats failed: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "ai_accuracy_percent" in data
        assert "account_accuracy_percent" in data
        assert "vat_accuracy_percent" in data
        assert "average_confidence_score" in data
        assert "total_extractions" in data
        assert "time_saved_hours" in data
        assert "error_rate_percent" in data
        
        # Verify data types
        assert isinstance(data["ai_accuracy_percent"], (int, float))
        assert isinstance(data["total_extractions"], int)
        
        print(f"✓ AI Dashboard Stats (Admin):")
        print(f"  AI Accuracy: {data['ai_accuracy_percent']}%")
        print(f"  Account Accuracy: {data['account_accuracy_percent']}%")
        print(f"  VAT Accuracy: {data['vat_accuracy_percent']}%")
        print(f"  Total Extractions: {data['total_extractions']}")
        print(f"  Time Saved: {data['time_saved_hours']} hours")
    
    def test_ai_dashboard_stats_sme_denied(self, sme_token):
        """Test GET /api/ai-dashboard/stats - SME user should be denied"""
        headers = {"Authorization": f"Bearer {sme_token}"}
        
        response = requests.get(f"{BASE_URL}/api/ai-dashboard/stats", headers=headers)
        # SME user should get 403 (requires admin or accountant role)
        assert response.status_code == 403, f"Expected 403 for SME user, got {response.status_code}"
        print("✓ AI Dashboard Stats correctly denies SME user access")
    
    def test_ai_corrections_admin(self, admin_token):
        """Test GET /api/ai-dashboard/corrections - admin only"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/ai-dashboard/corrections", headers=headers)
        assert response.status_code == 200, f"AI corrections failed: {response.text}"
        
        data = response.json()
        assert "corrections" in data
        assert "total" in data
        
        print(f"✓ AI Corrections (Admin): {data['total']} corrections")
        
        # If there are corrections, verify structure
        if data["corrections"]:
            correction = data["corrections"][0]
            print(f"  Sample correction: vendor={correction.get('vendor_name')}, was_correct={correction.get('was_correct')}")
    
    def test_ai_corrections_sme_denied(self, sme_token):
        """Test GET /api/ai-dashboard/corrections - SME user should be denied"""
        headers = {"Authorization": f"Bearer {sme_token}"}
        
        response = requests.get(f"{BASE_URL}/api/ai-dashboard/corrections", headers=headers)
        assert response.status_code == 403, f"Expected 403 for SME user, got {response.status_code}"
        print("✓ AI Corrections correctly denies SME user access")
    
    def test_active_companies_admin(self, admin_token):
        """Test GET /api/ai-dashboard/active-companies/{year}/{month} - admin only"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test with current month
        now = datetime.now()
        year = now.year
        month = now.month
        
        response = requests.get(f"{BASE_URL}/api/ai-dashboard/active-companies/{year}/{month}", headers=headers)
        assert response.status_code == 200, f"Active companies failed: {response.text}"
        
        data = response.json()
        assert "period" in data
        assert "active_count" in data
        assert "companies" in data
        
        assert data["period"] == f"{year}-{month:02d}"
        
        print(f"✓ Active Companies (Admin) for {data['period']}:")
        print(f"  Active Count: {data['active_count']}")
        
        if data["companies"]:
            company = data["companies"][0]
            print(f"  Sample: {company.get('tenant_name')} - {company.get('invoices_processed')} invoices")
    
    def test_active_companies_sme_denied(self, sme_token):
        """Test GET /api/ai-dashboard/active-companies - SME user should be denied"""
        headers = {"Authorization": f"Bearer {sme_token}"}
        
        now = datetime.now()
        response = requests.get(f"{BASE_URL}/api/ai-dashboard/active-companies/{now.year}/{now.month}", headers=headers)
        assert response.status_code == 403, f"Expected 403 for SME user, got {response.status_code}"
        print("✓ Active Companies correctly denies SME user access")


class TestVendorAccuracyEndpoint:
    """Test vendor accuracy endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get auth token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Could not authenticate admin user")
    
    @pytest.fixture
    def tenant_id(self, admin_token):
        """Get a tenant ID"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/tenants/", headers=headers)
        if response.status_code == 200:
            tenants = response.json()
            if tenants and len(tenants) > 0:
                return tenants[0]["id"]
        pytest.skip("No tenants available for testing")
    
    def test_vendor_accuracy(self, admin_token, tenant_id):
        """Test GET /api/ai-dashboard/vendor-accuracy"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/ai-dashboard/vendor-accuracy?tenant_id={tenant_id}", headers=headers)
        assert response.status_code == 200, f"Vendor accuracy failed: {response.text}"
        
        data = response.json()
        assert "vendors" in data
        
        print(f"✓ Vendor Accuracy for tenant {tenant_id}:")
        print(f"  Total vendors: {len(data['vendors'])}")
        
        if data["vendors"]:
            vendor = data["vendors"][0]
            print(f"  Sample: {vendor.get('vendor_name')} - {vendor.get('accuracy_percent', 0):.1f}% accuracy")


class TestAccountingDataRequiresAuth:
    """Test that accounting data endpoints require authentication"""
    
    def test_chart_of_accounts_requires_auth(self):
        """Chart of accounts should require authentication"""
        response = requests.get(f"{BASE_URL}/api/accounting-data/chart-of-accounts")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Chart of accounts correctly requires authentication")
    
    def test_vat_codes_requires_auth(self):
        """VAT codes should require authentication"""
        response = requests.get(f"{BASE_URL}/api/accounting-data/vat-codes")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ VAT codes correctly requires authentication")
    
    def test_journals_requires_auth(self):
        """Journals should require authentication"""
        response = requests.get(f"{BASE_URL}/api/accounting-data/journals")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Journals correctly requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
