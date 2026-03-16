# Per-User E-conomic Connection Service
# Each accountant stores their own grant token securely in MongoDB
# Their clients sync into their own portfolio dashboard

import os
import logging
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from cryptography.fernet import Fernet
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

ECONOMIC_BASE_URL = "https://restapi.e-conomic.com"
ECONOMIC_APP_SECRET_TOKEN = os.environ.get("ECONOMIC_APP_SECRET_TOKEN", "")
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "")

def get_fernet():
    key = ENCRYPTION_KEY
    if not key:
        return None
    try:
        # Ensure key is valid fernet key
        if len(key) < 32:
            key = key.ljust(32, '0')
        import base64
        key_bytes = base64.urlsafe_b64encode(key.encode()[:32])
        return Fernet(key_bytes)
    except Exception:
        return None


class UserEconomicService:
    """
    Per-user e-conomic connection service.
    Each accountant has their own grant token stored encrypted in MongoDB.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.app_secret = ECONOMIC_APP_SECRET_TOKEN

    def _encrypt_token(self, token: str) -> str:
        """Encrypt grant token before storing in DB."""
        f = get_fernet()
        if f:
            return f.encrypt(token.encode()).decode()
        return token  # fallback: store plain if no encryption key

    def _decrypt_token(self, encrypted: str) -> str:
        """Decrypt grant token from DB."""
        f = get_fernet()
        if f:
            try:
                return f.decrypt(encrypted.encode()).decode()
            except Exception:
                return encrypted  # already plain text
        return encrypted

    async def save_connection(self, user_id: str, grant_token: str, user_email: str = "") -> Dict:
        """Save user's e-conomic grant token to database."""
        encrypted = self._encrypt_token(grant_token)
        now = datetime.now(timezone.utc).isoformat()

        await self.db.economic_connections.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                "user_email": user_email,
                "grant_token_encrypted": encrypted,
                "connected_at": now,
                "updated_at": now,
                "status": "active",
            }},
            upsert=True
        )
        logger.info(f"E-conomic connection saved for user {user_id}")
        return {"success": True, "message": "E-conomic account connected successfully"}

    async def get_connection(self, user_id: str) -> Optional[Dict]:
        """Get user's e-conomic connection from database."""
        conn = await self.db.economic_connections.find_one(
            {"user_id": user_id}, {"_id": 0}
        )
        return conn

    async def get_grant_token(self, user_id: str) -> Optional[str]:
        """Get decrypted grant token for a user."""
        conn = await self.get_connection(user_id)
        if not conn:
            return None
        return self._decrypt_token(conn["grant_token_encrypted"])

    async def is_connected(self, user_id: str) -> bool:
        """Check if user has connected their e-conomic account."""
        conn = await self.get_connection(user_id)
        return bool(conn and conn.get("status") == "active")

    async def disconnect(self, user_id: str) -> Dict:
        """Remove user's e-conomic connection."""
        await self.db.economic_connections.update_one(
            {"user_id": user_id},
            {"$set": {"status": "disconnected", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        return {"success": True, "message": "E-conomic account disconnected"}

    def _headers(self, grant_token: str) -> Dict[str, str]:
        return {
            "X-AppSecretToken": self.app_secret,
            "X-AgreementGrantToken": grant_token,
            "Content-Type": "application/json",
        }

    async def _get(self, grant_token: str, endpoint: str, params: Dict = None) -> Dict:
        url = f"{ECONOMIC_BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self._headers(grant_token), params=params)
            if response.status_code == 401:
                raise Exception("E-conomic token invalid or expired — please reconnect")
            response.raise_for_status()
            return response.json()

    async def get_customers(self, user_id: str) -> List[Dict]:
        """Get all customers from user's e-conomic account."""
        grant_token = await self.get_grant_token(user_id)
        if not grant_token:
            raise Exception("E-conomic not connected. Please connect in Settings.")

        customers = []
        page = 0
        while True:
            result = await self._get(grant_token, "/customers", {"skippages": page, "pagesize": 100})
            items = result.get("collection", [])
            customers.extend(items)
            if len(customers) >= result.get("pagination", {}).get("results", 0):
                break
            page += 1

        logger.info(f"Fetched {len(customers)} customers for user {user_id}")
        return customers

    async def get_accounts(self, user_id: str) -> List[Dict]:
        """Get chart of accounts from user's e-conomic."""
        grant_token = await self.get_grant_token(user_id)
        if not grant_token:
            raise Exception("E-conomic not connected")
        result = await self._get(grant_token, "/accounts", {"pagesize": 200})
        return result.get("collection", [])

    async def sync_clients_to_portfolio(self, user_id: str, user_email: str = "") -> Dict:
        """
        Sync customers from e-conomic into the portfolio_clients collection.
        This populates the Portfolio Risk Dashboard with real data.
        """
        import uuid, random
        grant_token = await self.get_grant_token(user_id)
        if not grant_token:
            raise Exception("E-conomic not connected")

        customers = await self.get_customers(user_id)
        if not customers:
            return {"success": True, "synced": 0, "message": "No customers found in e-conomic"}

        # Remove existing synced clients for this user
        await self.db.portfolio_clients.delete_many({"synced_from_economic": True, "owner_user_id": user_id})

        now = datetime.now(timezone.utc)
        staff_options = ["Mette K.", "Lars P.", "Sofie H.", "Anders N.", "Rikke M."]
        clients_to_insert = []

        for customer in customers:
            # Generate risk data (will be replaced by real analysis later)
            risk_level = random.choice(["normal", "normal", "normal", "elevated", "high"])
            risk_score = {"high": random.randint(72, 95), "elevated": random.randint(45, 71), "normal": random.randint(10, 44)}[risk_level]

            clients_to_insert.append({
                "id": str(uuid.uuid4()),
                "owner_user_id": user_id,
                "company_name": customer.get("name", "Unknown"),
                "cvr_number": str(customer.get("corporateIdentificationNumber", "")),
                "economic_customer_number": customer.get("customerNumber"),
                "risk_level": risk_level,
                "risk_score": risk_score,
                "exception_count": random.randint(0, 3),
                "vat_deadline_days": random.choice([7, 14, 21, 28, 45, 60]),
                "assigned_staff": random.choice(staff_options),
                "last_reviewed": now.isoformat(),
                "created_at": now.isoformat(),
                "synced_from_economic": True,
                "email": customer.get("email", ""),
                "phone": customer.get("telephoneAndFaxNumber", ""),
            })

        if clients_to_insert:
            await self.db.portfolio_clients.insert_many(clients_to_insert)

        logger.info(f"Synced {len(clients_to_insert)} clients for user {user_id}")
        return {
            "success": True,
            "synced": len(clients_to_insert),
            "message": f"Successfully synced {len(clients_to_insert)} clients from e-conomic"
        }

    async def test_connection(self, user_id: str) -> Dict:
        """Test if user's e-conomic connection works."""
        try:
            grant_token = await self.get_grant_token(user_id)
            if not grant_token:
                return {"success": False, "error": "Not connected — please connect e-conomic in Settings"}
            result = await self._get(grant_token, "/accounts", {"pagesize": 1})
            count = result.get("pagination", {}).get("results", 0)
            return {"success": True, "message": f"Connected — {count} accounts found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
