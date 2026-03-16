# E-conomic API Routes for Accountrix
# Exposes e-conomic integration endpoints

import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, Optional
from pydantic import BaseModel
from economic_service import (
    EconomicService, economic_service,
    EconomicAuthError, EconomicRateLimitError, EconomicAPIError
)

logger = logging.getLogger(__name__)

economic_router = APIRouter(prefix="/api/economic", tags=["E-conomic"])


# ── Request Models ─────────────────────────────────────────────────────────────

class VoucherRequest(BaseModel):
    journal_number: int = 1
    account_number: int
    amount: float
    vat_code: str = "25"
    date: str
    description: str
    supplier_name: Optional[str] = None
    invoice_number: Optional[str] = None


class ConnectRequest(BaseModel):
    app_secret_token: str
    agreement_grant_token: str


# ── Helper ─────────────────────────────────────────────────────────────────────

def handle_economic_error(e: Exception):
    if isinstance(e, EconomicAuthError):
        raise HTTPException(status_code=401, detail=str(e))
    elif isinstance(e, EconomicRateLimitError):
        raise HTTPException(status_code=429, detail=str(e))
    elif isinstance(e, EconomicAPIError):
        raise HTTPException(status_code=400, detail=str(e))
    else:
        logger.error(f"E-conomic unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"E-conomic error: {str(e)}")


# ── OAuth2 Callback ────────────────────────────────────────────────────────────
# Path: GET /api/economic/callback
# e-conomic redirects here after user grants access
# Query param: agreementGrantToken

@economic_router.get("/callback")
async def economic_callback(request: Request):
    """
    Callback from e-conomic after user grants access.
    e-conomic sends agreementGrantToken as a query parameter.
    Token is NOT logged for security.
    """
    grant_token = request.query_params.get("token") or request.query_params.get("agreementGrantToken")

    if not grant_token:
        logger.warning("E-conomic callback received with no agreementGrantToken")
        return {
            "status": "error",
            "message": "No agreementGrantToken received",
            "received_params": list(request.query_params.keys())
        }

    # Log only that we received it — never log the value
    logger.info("E-conomic callback: agreementGrantToken received successfully")

    return {
        "status": "success",
        "message": "Agreement grant token received. Add it to your server .env as ECONOMIC_AGREEMENT_GRANT_TOKEN",
        "agreementGrantToken": grant_token
    }


# ── Test Route ─────────────────────────────────────────────────────────────────
# Path: GET /api/test/economic
# Uses ECONOMIC_APP_SECRET_TOKEN + ECONOMIC_AGREEMENT_GRANT_TOKEN from env
# Calls GET https://restapi.e-conomic.com/accounts

@economic_router.get("/test-connection")
@economic_router.get("/test")
async def test_economic_route():
    """
    Test route — verifies e-conomic credentials work.
    Uses ECONOMIC_APP_SECRET_TOKEN and ECONOMIC_AGREEMENT_GRANT_TOKEN from .env
    Calls GET https://restapi.e-conomic.com/accounts
    """
    result = await economic_service.test_connection()
    return result


# ── Test Connection ────────────────────────────────────────────────────────────

@economic_router.get("/test")
async def test_economic_connection():
    """Test e-conomic API connection."""
    result = await economic_service.test_connection()
    return result


# ── Connect with custom tokens ─────────────────────────────────────────────────

@economic_router.post("/connect")
async def connect_economic(request: ConnectRequest):
    """Test connection with provided tokens."""
    service = EconomicService(
        app_secret_token=request.app_secret_token,
        agreement_grant_token=request.agreement_grant_token,
    )
    result = await service.test_connection()
    return result


# ── Chart of Accounts ──────────────────────────────────────────────────────────

@economic_router.get("/accounts")
async def get_accounts():
    """Get chart of accounts from e-conomic."""
    try:
        accounts = await economic_service.get_accounts()
        return {"success": True, "count": len(accounts), "accounts": accounts}
    except Exception as e:
        handle_economic_error(e)


# ── Customers ──────────────────────────────────────────────────────────────────

@economic_router.get("/customers")
async def get_customers():
    """Get all customers from e-conomic."""
    try:
        customers = await economic_service.get_customers()
        return {"success": True, "count": len(customers), "customers": customers}
    except Exception as e:
        handle_economic_error(e)


# ── Suppliers ──────────────────────────────────────────────────────────────────

@economic_router.get("/suppliers")
async def get_suppliers():
    """Get all suppliers from e-conomic."""
    try:
        suppliers = await economic_service.get_suppliers()
        return {"success": True, "count": len(suppliers), "suppliers": suppliers}
    except Exception as e:
        handle_economic_error(e)


# ── Journals ───────────────────────────────────────────────────────────────────

@economic_router.get("/journals")
async def get_journals():
    """Get available journals from e-conomic."""
    try:
        journals = await economic_service.get_journals()
        return {"success": True, "count": len(journals), "journals": journals}
    except Exception as e:
        handle_economic_error(e)


# ── Create Voucher ─────────────────────────────────────────────────────────────

@economic_router.post("/vouchers")
async def create_voucher(voucher: VoucherRequest):
    """Create a voucher entry in e-conomic."""
    try:
        result = await economic_service.create_voucher(
            journal_number=voucher.journal_number,
            account_number=voucher.account_number,
            amount=voucher.amount,
            vat_code=voucher.vat_code,
            date=voucher.date,
            description=voucher.description,
            supplier_name=voucher.supplier_name,
            invoice_number=voucher.invoice_number,
        )
        return {"success": True, "voucher": result}
    except Exception as e:
        handle_economic_error(e)


# ── VAT Accounts ───────────────────────────────────────────────────────────────

@economic_router.get("/vat-accounts")
async def get_vat_accounts():
    """Get VAT account configuration from e-conomic."""
    try:
        vat_accounts = await economic_service.get_vat_accounts()
        return {"success": True, "count": len(vat_accounts), "vat_accounts": vat_accounts}
    except Exception as e:
        handle_economic_error(e)


# ── Status ─────────────────────────────────────────────────────────────────────

@economic_router.get("/status")
async def economic_status():
    """Get e-conomic integration status."""
    import os
    has_secret = bool(os.environ.get("ECONOMIC_APP_SECRET_TOKEN"))
    has_grant = bool(os.environ.get("ECONOMIC_AGREEMENT_GRANT_TOKEN"))

    return {
        "configured": has_secret and has_grant,
        "app_secret_token": "✅ Set" if has_secret else "❌ Missing",
        "agreement_grant_token": "✅ Set" if has_grant else "❌ Missing",
        "base_url": os.environ.get("ECONOMIC_BASE_URL", "https://restapi.e-conomic.com"),
    }


# ── Standalone test router at /api/test/economic ───────────────────────────────
# Separate router so the path is exactly /api/test/economic

test_economic_router = APIRouter(tags=["E-conomic Test"])

@test_economic_router.get("/api/test/economic")
async def test_economic_standalone():
    """
    Exact path: GET /api/test/economic
    Uses ECONOMIC_APP_SECRET_TOKEN + ECONOMIC_AGREEMENT_GRANT_TOKEN from env.
    Calls GET https://restapi.e-conomic.com/accounts and returns result.
    """
    result = await economic_service.test_connection()
    return result


# ── Per-User E-conomic Connection Routes ──────────────────────────────────────
# Each accountant connects their OWN e-conomic account

from fastapi import Header
import jwt as pyjwt

def get_user_from_token(authorization: str = Header(None)):
    """Extract user_id from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    try:
        import os
        secret = os.environ.get("JWT_SECRET", "ai-accounting-copilot-secret-key-2024")
        payload = pyjwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

user_economic_router = APIRouter(prefix="/api/user/economic", tags=["User E-conomic"])

@user_economic_router.get("/callback")
async def user_economic_callback(request: Request, authorization: str = Header(None)):
    """
    Per-user OAuth2 callback.
    After accountant grants access, saves their grant token to database.
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from user_economic_service import UserEconomicService
    from email_service import send_economic_connected_email

    grant_token = request.query_params.get("token") or request.query_params.get("agreementGrantToken")

    if not grant_token:
        return {"status": "error", "message": "No grant token received"}

    # Get user from token if provided
    user_id = None
    user_email = ""
    user_name = ""
    if authorization and authorization.startswith("Bearer "):
        try:
            secret = os.environ.get("JWT_SECRET", "ai-accounting-copilot-secret-key-2024")
            payload = pyjwt.decode(authorization.split(" ")[1], secret, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user_email = payload.get("email", "")
        except Exception:
            pass

    # If no auth header, try to get user_id from query param
    if not user_id:
        user_id = request.query_params.get("user_id")

    if not user_id:
        # Store token temporarily with a session key
        return {
            "status": "success",
            "message": "Grant token received! Please log in and go to Settings to complete the connection.",
            "grant_token": grant_token,
        }

    # Save the connection
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    service = UserEconomicService(db)

    await service.save_connection(user_id, grant_token, user_email)

    # Sync clients
    try:
        sync_result = await service.sync_clients_to_portfolio(user_id, user_email)
        synced_count = sync_result.get("synced", 0)

        # Send confirmation email
        if user_email:
            import asyncio
            asyncio.create_task(send_economic_connected_email(user_email, user_name or user_email, synced_count))

        logger.info(f"E-conomic connected and synced {synced_count} clients for user {user_id}")

        return {
            "status": "success",
            "message": f"E-conomic connected! {synced_count} clients synced to your dashboard.",
            "synced_clients": synced_count,
            "redirect": "https://accountrix.norabot.ai/app/portfolio"
        }
    except Exception as e:
        logger.error(f"Sync failed for user {user_id}: {e}")
        return {"status": "partial", "message": "Connected but sync failed. Try syncing from Settings."}


@user_economic_router.get("/status")
async def user_economic_status(authorization: str = Header(None)):
    """Check if current user has connected their e-conomic."""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from user_economic_service import UserEconomicService

    user = get_user_from_token(authorization)
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    service = UserEconomicService(db)

    conn = await service.get_connection(user["user_id"])
    return {
        "connected": bool(conn and conn.get("status") == "active"),
        "connected_at": conn.get("connected_at") if conn else None,
    }


@user_economic_router.post("/sync")
async def user_sync_clients(authorization: str = Header(None)):
    """Manually sync clients from user's e-conomic account."""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from user_economic_service import UserEconomicService

    user = get_user_from_token(authorization)
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    service = UserEconomicService(db)

    try:
        result = await service.sync_clients_to_portfolio(user["user_id"], user.get("email", ""))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_economic_router.get("/test")
async def user_test_economic(authorization: str = Header(None)):
    """Test current user's e-conomic connection."""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from user_economic_service import UserEconomicService

    user = get_user_from_token(authorization)
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    service = UserEconomicService(db)
    return await service.test_connection(user["user_id"])


@user_economic_router.delete("/disconnect")
async def user_disconnect_economic(authorization: str = Header(None)):
    """Disconnect user's e-conomic account."""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from user_economic_service import UserEconomicService

    user = get_user_from_token(authorization)
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    service = UserEconomicService(db)
    return await service.disconnect(user["user_id"])
