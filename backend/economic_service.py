# E-conomic API Integration Service for Accountrix
# Handles all communication with the e-conomic REST API

import os
import logging
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

ECONOMIC_BASE_URL = os.environ.get("ECONOMIC_BASE_URL", "https://restapi.e-conomic.com")
ECONOMIC_APP_SECRET_TOKEN = os.environ.get("ECONOMIC_APP_SECRET_TOKEN", "")
ECONOMIC_AGREEMENT_GRANT_TOKEN = os.environ.get("ECONOMIC_AGREEMENT_GRANT_TOKEN", "")

# ── E-conomic Service ──────────────────────────────────────────────────────────

class EconomicService:
    """
    Centralized service for all e-conomic API interactions.
    Uses X-AppSecretToken + X-AgreementGrantToken authentication.
    """

    def __init__(
        self,
        app_secret_token: str = None,
        agreement_grant_token: str = None,
    ):
        self.app_secret_token = app_secret_token or ECONOMIC_APP_SECRET_TOKEN
        self.agreement_grant_token = agreement_grant_token or ECONOMIC_AGREEMENT_GRANT_TOKEN
        self.base_url = ECONOMIC_BASE_URL

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _headers(self) -> Dict[str, str]:
        return {
            "X-AppSecretToken": self.app_secret_token,
            "X-AgreementGrantToken": self.agreement_grant_token,
            "Content-Type": "application/json",
        }

    async def _get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        logger.info(f"E-conomic GET {endpoint}")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self._headers(), params=params)
            return self._handle_response(response, endpoint)

    async def _post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        logger.info(f"E-conomic POST {endpoint}")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=self._headers(), json=data)
            return self._handle_response(response, endpoint)

    def _handle_response(self, response: httpx.Response, endpoint: str) -> Dict[str, Any]:
        logger.info(f"E-conomic response {endpoint}: {response.status_code}")

        if response.status_code == 401:
            raise EconomicAuthError("Invalid tokens — check ECONOMIC_APP_SECRET_TOKEN and ECONOMIC_AGREEMENT_GRANT_TOKEN")
        elif response.status_code == 403:
            raise EconomicAuthError("Access forbidden — check app permissions in e-conomic developer portal")
        elif response.status_code == 429:
            raise EconomicRateLimitError("E-conomic rate limit exceeded — try again later")
        elif response.status_code >= 500:
            raise EconomicServerError(f"E-conomic server error: {response.status_code}")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", response.text)
            except Exception:
                message = response.text
            raise EconomicAPIError(f"E-conomic API error {response.status_code}: {message}")

        try:
            return response.json()
        except Exception:
            return {"raw": response.text}

    def _is_configured(self) -> bool:
        return bool(self.app_secret_token and self.agreement_grant_token)

    # ── 1. Test Connection ─────────────────────────────────────────────────────

    async def test_connection(self) -> Dict[str, Any]:
        """Test that API credentials work by fetching accounts."""
        if not self._is_configured():
            return {
                "success": False,
                "error": "E-conomic tokens not configured. Set ECONOMIC_APP_SECRET_TOKEN and ECONOMIC_AGREEMENT_GRANT_TOKEN in .env"
            }
        try:
            result = await self._get("/accounts", params={"pagesize": 1})
            return {
                "success": True,
                "message": "E-conomic connection successful",
                "accounts_count": result.get("pagination", {}).get("results", 0),
            }
        except EconomicAuthError as e:
            return {"success": False, "error": str(e), "type": "auth_error"}
        except Exception as e:
            logger.error(f"E-conomic connection test failed: {e}")
            return {"success": False, "error": str(e)}

    # ── 2. Chart of Accounts ───────────────────────────────────────────────────

    async def get_accounts(self) -> List[Dict[str, Any]]:
        """Get full chart of accounts from e-conomic."""
        accounts = []
        page = 0
        pagesize = 100

        while True:
            result = await self._get("/accounts", params={"skippages": page, "pagesize": pagesize})
            items = result.get("collection", [])
            accounts.extend(items)

            pagination = result.get("pagination", {})
            if len(accounts) >= pagination.get("results", 0):
                break
            page += 1

        logger.info(f"E-conomic: fetched {len(accounts)} accounts")
        return accounts

    # ── 3. Customers ───────────────────────────────────────────────────────────

    async def get_customers(self) -> List[Dict[str, Any]]:
        """Get all customers from e-conomic."""
        customers = []
        page = 0
        pagesize = 100

        while True:
            result = await self._get("/customers", params={"skippages": page, "pagesize": pagesize})
            items = result.get("collection", [])
            customers.extend(items)

            pagination = result.get("pagination", {})
            if len(customers) >= pagination.get("results", 0):
                break
            page += 1

        logger.info(f"E-conomic: fetched {len(customers)} customers")
        return customers

    # ── 4. Suppliers ───────────────────────────────────────────────────────────

    async def get_suppliers(self) -> List[Dict[str, Any]]:
        """Get all suppliers (creditors) from e-conomic."""
        suppliers = []
        page = 0
        pagesize = 100

        while True:
            result = await self._get("/suppliers", params={"skippages": page, "pagesize": pagesize})
            items = result.get("collection", [])
            suppliers.extend(items)

            pagination = result.get("pagination", {})
            if len(suppliers) >= pagination.get("results", 0):
                break
            page += 1

        logger.info(f"E-conomic: fetched {len(suppliers)} suppliers")
        return suppliers

    # ── 5. Create Voucher ──────────────────────────────────────────────────────

    async def create_voucher(
        self,
        journal_number: int,
        account_number: int,
        amount: float,
        vat_code: str,
        date: str,
        description: str,
        supplier_name: str = None,
        invoice_number: str = None,
    ) -> Dict[str, Any]:
        """
        Create a voucher entry in e-conomic journal.

        Args:
            journal_number: e-conomic journal number (e.g. 1 for KØB)
            account_number: Chart of accounts code (e.g. 4000)
            amount: Transaction amount
            vat_code: Danish VAT code (e.g. "25" for 25% VAT)
            date: Date in YYYY-MM-DD format
            description: Transaction description
            supplier_name: Optional supplier name
            invoice_number: Optional invoice reference
        """
        entry = {
            "date": date,
            "account": {"accountNumber": account_number},
            "amount": amount,
            "vatCode": vat_code,
            "text": description,
        }

        if supplier_name:
            entry["supplier"] = {"name": supplier_name}
        if invoice_number:
            entry["voucherNumber"] = invoice_number

        result = await self._post(f"/journals/{journal_number}/entries", entry)
        logger.info(f"E-conomic: created voucher in journal {journal_number}")
        return result

    # ── 6. Upload Document ─────────────────────────────────────────────────────

    async def upload_document(
        self,
        file_name: str,
        file_content_base64: str,
        document_type: str = "supplierInvoice",
    ) -> Dict[str, Any]:
        """Upload a document/invoice PDF to e-conomic."""
        data = {
            "name": file_name,
            "content": file_content_base64,
            "type": document_type,
        }
        result = await self._post("/documents", data)
        logger.info(f"E-conomic: uploaded document {file_name}")
        return result

    # ── 7. Get Journals ────────────────────────────────────────────────────────

    async def get_journals(self) -> List[Dict[str, Any]]:
        """Get available journals from e-conomic."""
        result = await self._get("/journals")
        return result.get("collection", [])

    # ── 8. Get VAT Accounts ────────────────────────────────────────────────────

    async def get_vat_accounts(self) -> List[Dict[str, Any]]:
        """Get VAT account settings from e-conomic."""
        result = await self._get("/vat-accounts")
        return result.get("collection", [])

    # ── 9. Get Invoices (Supplier) ─────────────────────────────────────────────

    async def get_supplier_invoices(self, from_date: str = None, to_date: str = None) -> List[Dict[str, Any]]:
        """Get supplier invoices from e-conomic."""
        params = {"pagesize": 100}
        if from_date:
            params["filter"] = f"date$gte:{from_date}"

        result = await self._get("/supplier-invoices", params=params)
        return result.get("collection", [])


# ── Custom Exceptions ──────────────────────────────────────────────────────────

class EconomicAPIError(Exception):
    pass

class EconomicAuthError(EconomicAPIError):
    pass

class EconomicRateLimitError(EconomicAPIError):
    pass

class EconomicServerError(EconomicAPIError):
    pass


# ── Singleton instance ─────────────────────────────────────────────────────────

economic_service = EconomicService()
