# Portfolio Risk Platform API Routes
# Handles client portfolio, exceptions, and pre-VAT review functionality

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Router will be initialized with db in server.py
portfolio_router = APIRouter(prefix="/portfolio", tags=["Portfolio Risk"])


class ExceptionAction(BaseModel):
    action: str  # "approve", "investigate", "assign", "dismiss"
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class PortfolioService:
    """Service class for portfolio risk operations"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_firm_clients(self, firm_id: str, sort_by: str = "risk_score", sort_order: str = "desc") -> List[dict]:
        """Get all clients for a firm with risk metrics"""
        sort_direction = -1 if sort_order == "desc" else 1
        
        clients = await self.db.portfolio_clients.find(
            {"firm_id": firm_id},
            {"_id": 0}
        ).sort(sort_by, sort_direction).to_list(500)
        
        return clients
    
    async def get_client_detail(self, firm_id: str, client_id: str) -> dict:
        """Get detailed client information"""
        client = await self.db.portfolio_clients.find_one(
            {"firm_id": firm_id, "id": client_id},
            {"_id": 0}
        )
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get recent transactions
        transactions = await self.db.portfolio_transactions.find(
            {"firm_id": firm_id, "client_id": client_id},
            {"_id": 0}
        ).sort("date", -1).limit(50).to_list(50)
        
        # Get exceptions
        exceptions = await self.db.portfolio_exceptions.find(
            {"firm_id": firm_id, "client_id": client_id},
            {"_id": 0}
        ).sort("detected_at", -1).to_list(100)
        
        client["recent_transactions"] = transactions
        client["exceptions"] = exceptions
        
        return client
    
    async def get_portfolio_summary(self, firm_id: str) -> dict:
        """Get portfolio-wide summary statistics"""
        clients = await self.db.portfolio_clients.find(
            {"firm_id": firm_id},
            {"_id": 0}
        ).to_list(500)
        
        if not clients:
            return {
                "total_clients": 0,
                "high_risk": 0,
                "elevated_risk": 0,
                "normal_risk": 0,
                "total_exceptions": 0,
                "open_exceptions": 0,
                "clients_near_vat_deadline": 0
            }
        
        # Calculate summary
        high_risk = len([c for c in clients if c.get("risk_level") == "high"])
        elevated_risk = len([c for c in clients if c.get("risk_level") == "elevated"])
        normal_risk = len([c for c in clients if c.get("risk_level") == "normal"])
        
        total_exceptions = sum(c.get("exception_count", 0) for c in clients)
        open_exceptions = sum(c.get("open_exceptions", 0) for c in clients)
        
        # Clients with VAT deadline within 14 days
        near_deadline = len([c for c in clients if c.get("days_to_vat_deadline", 999) <= 14])
        
        return {
            "total_clients": len(clients),
            "high_risk": high_risk,
            "elevated_risk": elevated_risk,
            "normal_risk": normal_risk,
            "total_exceptions": total_exceptions,
            "open_exceptions": open_exceptions,
            "clients_near_vat_deadline": near_deadline
        }
    
    async def get_exceptions(
        self, 
        firm_id: str, 
        status: Optional[str] = None,
        severity: Optional[str] = None,
        client_id: Optional[str] = None,
        exception_type: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """Get exceptions with optional filters"""
        query = {"firm_id": firm_id}
        
        if status:
            query["status"] = status
        if severity:
            query["severity"] = severity
        if client_id:
            query["client_id"] = client_id
        if exception_type:
            query["type"] = exception_type
        
        exceptions = await self.db.portfolio_exceptions.find(
            query,
            {"_id": 0}
        ).sort("detected_at", -1).limit(limit).to_list(limit)
        
        return exceptions
    
    async def update_exception(self, firm_id: str, exception_id: str, action: ExceptionAction, user_name: str) -> dict:
        """Update exception status based on action"""
        
        exception = await self.db.portfolio_exceptions.find_one(
            {"firm_id": firm_id, "id": exception_id}
        )
        
        if not exception:
            raise HTTPException(status_code=404, detail="Exception not found")
        
        update_data = {
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if action.action == "approve":
            update_data["status"] = "resolved"
            update_data["resolution"] = "approved"
            update_data["reviewed_by"] = user_name
            update_data["reviewed_at"] = datetime.now(timezone.utc).isoformat()
        
        elif action.action == "investigate":
            update_data["status"] = "investigating"
            update_data["assigned_to"] = action.assigned_to or user_name
        
        elif action.action == "assign":
            update_data["status"] = "assigned"
            update_data["assigned_to"] = action.assigned_to
        
        elif action.action == "dismiss":
            update_data["status"] = "dismissed"
            update_data["resolution"] = "dismissed"
            update_data["reviewed_by"] = user_name
            update_data["reviewed_at"] = datetime.now(timezone.utc).isoformat()
        
        if action.notes:
            update_data["notes"] = action.notes
        
        await self.db.portfolio_exceptions.update_one(
            {"firm_id": firm_id, "id": exception_id},
            {"$set": update_data}
        )
        
        # Update client exception counts
        await self._recalculate_client_exceptions(firm_id, exception["client_id"])
        
        return {"success": True, "action": action.action, "exception_id": exception_id}
    
    async def _recalculate_client_exceptions(self, firm_id: str, client_id: str):
        """Recalculate exception counts for a client"""
        exceptions = await self.db.portfolio_exceptions.find(
            {"firm_id": firm_id, "client_id": client_id},
            {"_id": 0}
        ).to_list(500)
        
        total = len(exceptions)
        open_count = len([e for e in exceptions if e.get("status") == "open"])
        
        # Recalculate risk score
        high_count = len([e for e in exceptions if e.get("severity") == "high" and e.get("status") == "open"])
        medium_count = len([e for e in exceptions if e.get("severity") == "medium" and e.get("status") == "open"])
        low_count = len([e for e in exceptions if e.get("severity") == "low" and e.get("status") == "open"])
        
        risk_score = min(100, (high_count * 30) + (medium_count * 15) + (low_count * 5))
        
        if risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "elevated"
        else:
            risk_level = "normal"
        
        await self.db.portfolio_clients.update_one(
            {"firm_id": firm_id, "id": client_id},
            {"$set": {
                "exception_count": total,
                "open_exceptions": open_count,
                "risk_score": risk_score,
                "risk_level": risk_level
            }}
        )
    
    async def get_pre_vat_review(self, firm_id: str, days_threshold: int = 30) -> dict:
        """Get clients approaching VAT deadline with review status"""
        
        clients = await self.db.portfolio_clients.find(
            {
                "firm_id": firm_id,
                "days_to_vat_deadline": {"$lte": days_threshold}
            },
            {"_id": 0}
        ).sort("days_to_vat_deadline", 1).to_list(100)
        
        # Get exceptions for these clients
        client_ids = [c["id"] for c in clients]
        
        for client in clients:
            exceptions = await self.db.portfolio_exceptions.find(
                {
                    "firm_id": firm_id,
                    "client_id": client["id"],
                    "status": "open"
                },
                {"_id": 0}
            ).to_list(50)
            
            client["open_exceptions_list"] = exceptions
            
            # Calculate VAT review checklist
            client["vat_checklist"] = {
                "exceptions_reviewed": client.get("open_exceptions", 0) == 0,
                "recent_review": self._is_recently_reviewed(client.get("last_review_date")),
                "no_high_risk_items": not any(e.get("severity") == "high" for e in exceptions),
                "vat_trends_checked": random.choice([True, False]),  # Mock for demo
            }
            
            # Overall ready status
            checklist = client["vat_checklist"]
            client["vat_ready"] = all([
                checklist["exceptions_reviewed"],
                checklist["recent_review"],
                checklist["no_high_risk_items"]
            ])
        
        # Summary
        ready_count = len([c for c in clients if c.get("vat_ready")])
        
        return {
            "threshold_days": days_threshold,
            "total_clients": len(clients),
            "ready_count": ready_count,
            "needs_attention": len(clients) - ready_count,
            "clients": clients
        }
    
    def _is_recently_reviewed(self, last_review_date: Optional[str]) -> bool:
        """Check if client was reviewed in last 7 days"""
        if not last_review_date:
            return False
        try:
            review_date = datetime.fromisoformat(last_review_date.replace('Z', '+00:00'))
            return (datetime.now(timezone.utc) - review_date).days <= 7
        except:
            return False
    
    async def get_transaction_history(
        self,
        firm_id: str,
        client_id: str,
        account_code: Optional[str] = None,
        vendor: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """Get transaction history with filters"""
        query = {"firm_id": firm_id, "client_id": client_id}
        
        if account_code:
            query["account_code"] = account_code
        if vendor:
            query["vendor_name"] = {"$regex": vendor, "$options": "i"}
        if start_date:
            query["date"] = {"$gte": start_date}
        if end_date:
            if "date" in query:
                query["date"]["$lte"] = end_date
            else:
                query["date"] = {"$lte": end_date}
        
        transactions = await self.db.portfolio_transactions.find(
            query,
            {"_id": 0}
        ).sort("date", -1).limit(limit).to_list(limit)
        
        return transactions


# Need to import random for mock checklist
import random


def setup_portfolio_routes(router: APIRouter, db, get_current_user):
    """Setup portfolio routes with database and auth dependencies"""
    
    service = PortfolioService(db)
    
    @router.get("/summary")
    async def get_portfolio_summary(user: dict = Depends(get_current_user)):
        """Get portfolio-wide summary for the current firm"""
        firm_id = user.get("tenant_id") or user.get("id")
        return await service.get_portfolio_summary(firm_id)
    
    @router.get("/clients")
    async def get_clients(
        sort_by: str = Query("risk_score", enum=["risk_score", "name", "days_to_vat_deadline", "exception_count"]),
        sort_order: str = Query("desc", enum=["asc", "desc"]),
        user: dict = Depends(get_current_user)
    ):
        """Get all clients with risk metrics"""
        firm_id = user.get("tenant_id") or user.get("id")
        clients = await service.get_firm_clients(firm_id, sort_by, sort_order)
        return {"clients": clients, "total": len(clients)}
    
    @router.get("/clients/{client_id}")
    async def get_client_detail(client_id: str, user: dict = Depends(get_current_user)):
        """Get detailed client information"""
        firm_id = user.get("tenant_id") or user.get("id")
        return await service.get_client_detail(firm_id, client_id)
    
    @router.get("/exceptions")
    async def get_exceptions(
        status: Optional[str] = Query(None, enum=["open", "investigating", "assigned", "resolved", "dismissed"]),
        severity: Optional[str] = Query(None, enum=["high", "medium", "low"]),
        client_id: Optional[str] = None,
        exception_type: Optional[str] = Query(None, enum=["expense_spike", "duplicate_invoice", "unusual_vendor", "vat_variance", "pattern_deviation", "vat_trend"]),
        limit: int = Query(100, le=500),
        user: dict = Depends(get_current_user)
    ):
        """Get exceptions with optional filters"""
        firm_id = user.get("tenant_id") or user.get("id")
        exceptions = await service.get_exceptions(firm_id, status, severity, client_id, exception_type, limit)
        return {"exceptions": exceptions, "total": len(exceptions)}
    
    @router.post("/exceptions/{exception_id}/action")
    async def handle_exception_action(
        exception_id: str,
        action: ExceptionAction,
        user: dict = Depends(get_current_user)
    ):
        """Handle exception action (approve, investigate, assign, dismiss)"""
        firm_id = user.get("tenant_id") or user.get("id")
        user_name = user.get("name", user.get("email", "Unknown"))
        return await service.update_exception(firm_id, exception_id, action, user_name)
    
    @router.get("/pre-vat-review")
    async def get_pre_vat_review(
        days: int = Query(30, description="Days until VAT deadline threshold"),
        user: dict = Depends(get_current_user)
    ):
        """Get pre-VAT review status for clients approaching deadline"""
        firm_id = user.get("tenant_id") or user.get("id")
        return await service.get_pre_vat_review(firm_id, days)
    
    @router.get("/clients/{client_id}/transactions")
    async def get_client_transactions(
        client_id: str,
        account_code: Optional[str] = None,
        vendor: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = Query(100, le=500),
        user: dict = Depends(get_current_user)
    ):
        """Get transaction history for a client"""
        firm_id = user.get("tenant_id") or user.get("id")
        transactions = await service.get_transaction_history(
            firm_id, client_id, account_code, vendor, start_date, end_date, limit
        )
        return {"transactions": transactions, "total": len(transactions)}
    
    @router.post("/generate-demo-data")
    async def generate_demo_data(user: dict = Depends(get_current_user)):
        """Generate demo portfolio data for the current firm"""
        from portfolio_data_generator import generate_demo_portfolio
        
        firm_id = user.get("tenant_id") or user.get("id")
        
        # Check if data already exists
        existing = await db.portfolio_clients.find_one({"firm_id": firm_id})
        if existing:
            return {"success": False, "message": "Demo data already exists for this firm", "action": "none"}
        
        # Generate data
        portfolio = generate_demo_portfolio(firm_id, num_clients=25)
        
        # Insert into database
        if portfolio["clients"]:
            await db.portfolio_clients.insert_many(portfolio["clients"])
        if portfolio["transactions"]:
            await db.portfolio_transactions.insert_many(portfolio["transactions"])
        if portfolio["exceptions"]:
            await db.portfolio_exceptions.insert_many(portfolio["exceptions"])
        
        return {
            "success": True,
            "message": "Demo data generated successfully",
            "stats": {
                "clients": len(portfolio["clients"]),
                "transactions": len(portfolio["transactions"]),
                "exceptions": len(portfolio["exceptions"])
            }
        }
    
    @router.delete("/demo-data")
    async def clear_demo_data(user: dict = Depends(get_current_user)):
        """Clear demo portfolio data for the current firm"""
        firm_id = user.get("tenant_id") or user.get("id")
        
        result_clients = await db.portfolio_clients.delete_many({"firm_id": firm_id})
        result_transactions = await db.portfolio_transactions.delete_many({"firm_id": firm_id})
        result_exceptions = await db.portfolio_exceptions.delete_many({"firm_id": firm_id})
        
        return {
            "success": True,
            "deleted": {
                "clients": result_clients.deleted_count,
                "transactions": result_transactions.deleted_count,
                "exceptions": result_exceptions.deleted_count
            }
        }
    
    return router
