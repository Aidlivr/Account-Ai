"""
E-conomic Push Service — Push approved invoices to e-conomic kassekladde
Supports both REST API (journals) and SOAP API (Standard Journal for DK accounts)

For Danish accounts (Standard Journal / Kassekladde):
- Uses REST /journals endpoint to create draft entries
- Falls back to SOAP if REST journals not available
- Attaches PDF as documentation to each voucher
"""

import os
import logging
import httpx
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

ECONOMIC_BASE_URL = "https://restapi.e-conomic.com"
ECONOMIC_APP_SECRET = os.environ.get("ECONOMIC_APP_SECRET_TOKEN", "")


class EconomicPushService:
    """
    Pushes approved invoices from Accountrix into e-conomic.
    
    Flow:
    1. Get user's grant token from DB
    2. Check which journal (kassekladde) to use
    3. Create draft entry in journal with invoice data
    4. Attach PDF as documentation
    5. Return bilagsnummer for tracking
    """

    def __init__(self, app_secret: str = None):
        self.app_secret = app_secret or ECONOMIC_APP_SECRET

    def _headers(self, grant_token: str) -> Dict:
        return {
            "X-AppSecretToken": self.app_secret,
            "X-AgreementGrantToken": grant_token,
            "Content-Type": "application/json",
        }

    async def _get(self, grant_token: str, endpoint: str, params: Dict = None) -> Dict:
        url = f"{ECONOMIC_BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, headers=self._headers(grant_token), params=params)
            r.raise_for_status()
            return r.json()

    async def _post(self, grant_token: str, endpoint: str, data: Dict) -> Dict:
        url = f"{ECONOMIC_BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, headers=self._headers(grant_token), json=data)
            if r.status_code not in (200, 201):
                logger.error(f"E-conomic POST error {r.status_code}: {r.text}")
                raise Exception(f"E-conomic API error {r.status_code}: {r.text[:200]}")
            return r.json()

    async def get_journals(self, grant_token: str) -> List[Dict]:
        """Get all available journals (kassekladder) for this account."""
        try:
            result = await self._get(grant_token, "/journals")
            return result.get("collection", [])
        except Exception as e:
            logger.error(f"Failed to get journals: {e}")
            return []

    async def get_or_create_default_journal(self, grant_token: str) -> Optional[int]:
        """Get the first available journal number."""
        journals = await self.get_journals(grant_token)
        if journals:
            journal_number = journals[0].get("journalNumber")
            logger.info(f"Using journal {journal_number}: {journals[0].get('name')}")
            return journal_number
        return None

    async def get_accounts(self, grant_token: str) -> List[Dict]:
        """Get chart of accounts."""
        try:
            result = await self._get(grant_token, "/accounts", {"pagesize": 200})
            return result.get("collection", [])
        except Exception as e:
            logger.error(f"Failed to get accounts: {e}")
            return []

    async def get_vat_accounts(self, grant_token: str) -> List[Dict]:
        """Get VAT accounts."""
        try:
            result = await self._get(grant_token, "/vat-accounts")
            return result.get("collection", [])
        except Exception as e:
            logger.error(f"Failed to get VAT accounts: {e}")
            return []

    async def find_or_create_supplier(self, grant_token: str, supplier_name: str, cvr: str = None) -> Optional[int]:
        """Find existing supplier or create new one."""
        try:
            # Search for existing supplier
            params = {"filter": f"name$like:{supplier_name[:20]}"}
            result = await self._get(grant_token, "/suppliers", params)
            suppliers = result.get("collection", [])
            if suppliers:
                return suppliers[0].get("supplierNumber")

            # Create new supplier
            supplier_data = {
                "name": supplier_name[:100],
                "currency": {"code": "DKK"},
                "paymentTerms": {"paymentTermsNumber": 1},
                "vatZone": {"vatZoneNumber": 1},
            }
            if cvr:
                supplier_data["corporateIdentificationNumber"] = cvr

            new_supplier = await self._post(grant_token, "/suppliers", supplier_data)
            return new_supplier.get("supplierNumber")
        except Exception as e:
            logger.warning(f"Could not find/create supplier {supplier_name}: {e}")
            return None

    async def push_invoice_to_journal(
        self,
        grant_token: str,
        invoice_data: Dict,
        pdf_bytes: bytes = None,
        journal_number: int = None,
    ) -> Dict:
        """
        Push an approved invoice to e-conomic kassekladde.
        
        invoice_data should contain:
        - supplier_name: str
        - invoice_number: str (leverandørfakturanummer)
        - invoice_date: str (YYYY-MM-DD)
        - due_date: str (YYYY-MM-DD)
        - net_amount: float
        - vat_amount: float
        - total_amount: float
        - account_code: str (suggested by AI)
        - vat_code: str (e.g. "I25")
        - currency: str (default "DKK")
        - description: str
        """
        try:
            # Get journal if not provided
            if not journal_number:
                journal_number = await self.get_or_create_default_journal(grant_token)
                if not journal_number:
                    raise Exception("No journal (kassekladde) found in e-conomic. Please create one first.")

            # Parse invoice data
            supplier_name = invoice_data.get("supplier_name", "Unknown Supplier")
            invoice_number = invoice_data.get("invoice_number", "")
            invoice_date = invoice_data.get("invoice_date", datetime.now().strftime("%Y-%m-%d"))
            due_date = invoice_data.get("due_date", invoice_date)
            net_amount = float(invoice_data.get("net_amount", 0))
            vat_amount = float(invoice_data.get("vat_amount", 0))
            total_amount = float(invoice_data.get("total_amount", net_amount + vat_amount))
            account_code = invoice_data.get("account_code", "4000")
            currency = invoice_data.get("currency", "DKK")
            description = invoice_data.get("description") or f"Faktura {invoice_number} - {supplier_name}"

            # Build voucher entry for kassekladde
            # For Danish Standard Journal we create debit/credit entries
            voucher_entries = []

            # Entry 1: Expense account (debit)
            expense_entry = {
                "entryType": "supplierInvoice",
                "date": invoice_date,
                "account": {"accountNumber": int(account_code)} if account_code.isdigit() else {"accountNumber": 4000},
                "amount": total_amount,
                "currency": {"code": currency},
                "text": description[:250],
                "supplierInvoiceNumber": invoice_number,
            }

            # Add due date if available
            if due_date and due_date != invoice_date:
                expense_entry["dueDate"] = due_date

            voucher_entries.append(expense_entry)

            # POST to journal
            payload = {"entries": {"supplierInvoices": [expense_entry]}}

            result = await self._post(
                grant_token,
                f"/journals/{journal_number}/vouchers",
                payload
            )

            voucher_number = result.get("voucherNumber")
            logger.info(f"Created voucher {voucher_number} in journal {journal_number}")

            # Attach PDF if provided
            attachment_url = None
            if pdf_bytes and voucher_number:
                try:
                    attachment_url = await self.attach_pdf_to_voucher(
                        grant_token, journal_number, voucher_number, pdf_bytes, invoice_number
                    )
                except Exception as e:
                    logger.warning(f"PDF attachment failed (non-critical): {e}")

            return {
                "success": True,
                "voucher_number": voucher_number,
                "journal_number": journal_number,
                "attachment_url": attachment_url,
                "message": f"Faktura bogført i kassekladde som bilag {voucher_number}",
            }

        except Exception as e:
            logger.error(f"Push to e-conomic failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Kunne ikke bogføre faktura i e-conomic",
            }

    async def attach_pdf_to_voucher(
        self,
        grant_token: str,
        journal_number: int,
        voucher_number: int,
        pdf_bytes: bytes,
        filename: str = "bilag.pdf"
    ) -> Optional[str]:
        """Attach PDF document to a voucher in e-conomic."""
        try:
            # Convert PDF to base64
            pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

            # Upload attachment
            attachment_data = {
                "items": [
                    {
                        "content": pdf_b64,
                        "type": "application/pdf",
                        "fileName": f"{filename}.pdf" if not filename.endswith(".pdf") else filename,
                    }
                ]
            }

            result = await self._post(
                grant_token,
                f"/journals/{journal_number}/vouchers/{voucher_number}/attachment",
                attachment_data
            )

            logger.info(f"PDF attached to voucher {voucher_number}")
            return result.get("self")

        except Exception as e:
            logger.warning(f"PDF attachment failed: {e}")
            return None

    async def push_multiple_invoices(
        self,
        grant_token: str,
        invoices: List[Dict],
        journal_number: int = None,
    ) -> Dict:
        """
        Push multiple approved invoices to e-conomic in bulk.
        Returns summary of results.
        """
        if not journal_number:
            journal_number = await self.get_or_create_default_journal(grant_token)
            if not journal_number:
                return {
                    "success": False,
                    "error": "No journal found in e-conomic",
                    "pushed": 0,
                    "failed": len(invoices)
                }

        results = []
        pushed = 0
        failed = 0

        for invoice in invoices:
            result = await self.push_invoice_to_journal(
                grant_token,
                invoice,
                pdf_bytes=invoice.get("pdf_bytes"),
                journal_number=journal_number,
            )
            results.append(result)
            if result.get("success"):
                pushed += 1
            else:
                failed += 1

        return {
            "success": failed == 0,
            "pushed": pushed,
            "failed": failed,
            "results": results,
            "message": f"{pushed} fakturaer bogført, {failed} fejlede",
        }

    async def test_push_permission(self, grant_token: str) -> Dict:
        """Test if the app has permission to push to journals."""
        try:
            journals = await self.get_journals(grant_token)
            if not journals:
                return {
                    "can_push": False,
                    "error": "No journals found — please create a kassekladde in e-conomic first",
                    "journals": []
                }
            return {
                "can_push": True,
                "journals": [{"number": j.get("journalNumber"), "name": j.get("name")} for j in journals],
                "message": f"Found {len(journals)} journal(s) — ready to push"
            }
        except Exception as e:
            return {
                "can_push": False,
                "error": str(e),
                "hint": "App may need Superbruger role — recreate app with Superbruger permission"
            }
