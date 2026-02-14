from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form, status, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Literal
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import re
import json
import stripe
import base64
from io import BytesIO
from cryptography.fernet import Fernet
import hashlib

# Import AI integration
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Import production AI modules
from ai_production import ProductionAIService, AIAnalyticsService, ActiveCompanyService
from danish_accounting import (
    DANISH_CHART_OF_ACCOUNTS,
    DANISH_VAT_CODES, 
    DANISH_STANDARD_JOURNALS,
    validate_account_code,
    validate_vat_code,
    format_chart_for_prompt,
    format_vat_codes_for_prompt,
    get_account_by_code,
)
from vat_rules import get_vat_rules, apply_vat_rules, VATRuleFactory

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'ai-accounting-copilot-secret-key-2024')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Stripe Configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')

# Emergent LLM Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Encryption key for sensitive data
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key().decode())

# Initialize Production AI Services
production_ai_service = None  # Will be initialized after app startup
ai_analytics_service = None
active_company_service = None

# Create the main app
app = FastAPI(title="AI Accounting Copilot", version="2.1.0-beta")

# Create routers
api_router = APIRouter(prefix="/api")
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
tenant_router = APIRouter(prefix="/tenants", tags=["Tenants"])
document_router = APIRouter(prefix="/documents", tags=["Documents"])
voucher_router = APIRouter(prefix="/vouchers", tags=["Vouchers"])
reconciliation_router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])
vat_router = APIRouter(prefix="/vat", tags=["VAT"])
billing_router = APIRouter(prefix="/billing", tags=["Billing"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"])
activity_router = APIRouter(prefix="/activity", tags=["Activity"])
vendor_router = APIRouter(prefix="/vendors", tags=["Vendors"])
ai_dashboard_router = APIRouter(prefix="/ai-dashboard", tags=["AI Dashboard"])
accounting_data_router = APIRouter(prefix="/accounting-data", tags=["Accounting Data"])

security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== CONSTANTS ====================

class UserRole:
    SME_USER = "sme_user"
    ACCOUNTANT = "accountant"
    ADMIN = "admin"

class ActivityType:
    INVOICE_UPLOADED = "invoice_uploaded"
    AI_EXTRACTION_COMPLETED = "ai_extraction_completed"
    USER_EDITED_FIELDS = "user_edited_fields"
    INVOICE_APPROVED = "invoice_approved"
    INVOICE_REJECTED = "invoice_rejected"
    VOUCHER_CREATED = "voucher_created"
    VOUCHER_PUSHED = "voucher_pushed"
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    COMPANY_CREATED = "company_created"
    SUBSCRIPTION_ACTIVATED = "subscription_activated"
    PROVIDER_CONFIGURED = "provider_configured"

class VoucherStatus:
    DRAFT = "draft"
    READY_TO_PUSH = "ready_to_push"
    PUSHED = "pushed"
    FAILED = "failed"

class ProviderType:
    ECONOMIC = "e-conomic"
    DINERO = "dinero"
    BILLY = "billy"
    NONE = "none"

# Time saved estimates (in minutes)
TIME_ESTIMATES = {
    "ocr_extraction": 3,
    "data_entry": 5,
    "account_mapping": 2,
    "vat_calculation": 1,
    "voucher_creation": 4
}

# ==================== MODELS ====================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = UserRole.SME_USER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class TenantCreate(BaseModel):
    name: str
    cvr_number: Optional[str] = None
    address: Optional[str] = None
    settings: Optional[Dict[str, Any]] = {}

class TenantResponse(BaseModel):
    id: str
    name: str
    cvr_number: Optional[str]
    address: Optional[str]
    owner_id: str
    settings: Dict[str, Any]
    provider_configured: bool = False
    created_at: str

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    cvr_number: Optional[str] = None
    address: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

# Provider Configuration Models
class ProviderConfig(BaseModel):
    provider_type: str = ProviderType.ECONOMIC
    agreement_number: Optional[str] = None
    user_token: Optional[str] = None
    api_url: Optional[str] = None
    is_active: bool = False

class ProviderConfigUpdate(BaseModel):
    provider_type: Optional[str] = None
    agreement_number: Optional[str] = None
    user_token: Optional[str] = None
    api_url: Optional[str] = None
    is_active: Optional[bool] = None

# Enhanced Document Models with Field Confidence
class FieldConfidence(BaseModel):
    value: Any
    confidence: float  # 0.0 to 1.0
    source: str  # "ai", "ocr", "user_edited", "vendor_learned"
    uncertain: bool = False

class ExtractedInvoiceData(BaseModel):
    supplier_name: Optional[FieldConfidence] = None
    cvr_number: Optional[FieldConfidence] = None
    invoice_number: Optional[FieldConfidence] = None
    invoice_date: Optional[FieldConfidence] = None
    due_date: Optional[FieldConfidence] = None
    net_amount: Optional[FieldConfidence] = None
    vat_amount: Optional[FieldConfidence] = None
    total_amount: Optional[FieldConfidence] = None
    vat_percentage: Optional[FieldConfidence] = None
    currency: Optional[FieldConfidence] = None
    account_code: Optional[FieldConfidence] = None
    account_name: Optional[FieldConfidence] = None
    line_items: Optional[List[Dict[str, Any]]] = None

class DocumentResponse(BaseModel):
    id: str
    tenant_id: str
    filename: str
    file_type: str
    status: str
    extracted_data: Optional[Dict[str, Any]]
    field_confidence: Optional[Dict[str, Any]]
    ai_suggestions: Optional[Dict[str, Any]]
    overall_confidence: Optional[float]
    uncertain_fields: Optional[List[str]]
    created_at: str
    updated_at: str

class DocumentEditRequest(BaseModel):
    field_updates: Dict[str, Any]

class DocumentApproval(BaseModel):
    approved: bool
    final_data: Optional[Dict[str, Any]] = None
    account_mapping: Optional[Dict[str, str]] = None

# Voucher Models
class VoucherResponse(BaseModel):
    id: str
    tenant_id: str
    document_id: str
    status: str
    voucher_data: Dict[str, Any]
    account_mapping: Dict[str, Any]
    preview: Dict[str, Any]
    created_at: str
    updated_at: str

class VoucherPushRequest(BaseModel):
    voucher_id: str

# Activity Models
class ActivityLog(BaseModel):
    id: str
    tenant_id: Optional[str]
    user_id: str
    activity_type: str
    entity_type: str
    entity_id: Optional[str]
    details: Dict[str, Any]
    time_saved_minutes: Optional[float]
    timestamp: str

# Vendor Learning Models
class VendorPattern(BaseModel):
    id: str
    tenant_id: str
    vendor_identifier: str  # CVR or name hash
    vendor_name: str
    learned_account_code: Optional[str]
    learned_account_name: Optional[str]
    learned_vat_code: Optional[str]
    learned_description_pattern: Optional[str]
    usage_count: int
    last_used: str
    created_at: str

class VendorPatternUpdate(BaseModel):
    account_code: Optional[str] = None
    account_name: Optional[str] = None
    vat_code: Optional[str] = None
    description_pattern: Optional[str] = None

# Subscription Models
class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price: float
    currency: str = "dkk"
    features: List[str]
    limits: Dict[str, int]
    is_active: bool = True

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    plan_name: str
    status: str
    activated_by: Optional[str]
    activated_at: Optional[str]
    current_period_start: str
    current_period_end: str
    usage: Dict[str, int]
    limits: Dict[str, int]

class AdminSubscriptionActivate(BaseModel):
    user_id: str
    plan_id: str
    notes: Optional[str] = None

class TransactionMatch(BaseModel):
    transaction_id: str
    invoice_id: str
    confidence: float

class DashboardStats(BaseModel):
    total_documents: int
    pending_documents: int
    processed_documents: int
    total_vouchers: int
    ready_to_push_vouchers: int
    total_transactions: int
    unmatched_transactions: int
    vat_risk_score: float
    time_saved_hours: float
    time_saved_breakdown: Dict[str, float]

# ==================== ENCRYPTION HELPERS ====================

def get_fernet():
    key = ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY
    # Ensure key is valid Fernet key (32 url-safe base64-encoded bytes)
    if len(key) != 44:
        key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
    return Fernet(key)

def encrypt_sensitive(data: str) -> str:
    if not data:
        return data
    try:
        f = get_fernet()
        return f.encrypt(data.encode()).decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return data

def decrypt_sensitive(data: str) -> str:
    if not data:
        return data
    try:
        f = get_fernet()
        return f.decrypt(data.encode()).decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        return data

# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(allowed_roles: List[str]):
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker

# ==================== ACTIVITY LOGGING SERVICE ====================

class ActivityService:
    """Centralized activity logging service"""
    
    @staticmethod
    async def log(
        user_id: str,
        activity_type: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        details: Dict[str, Any] = None,
        time_saved_minutes: Optional[float] = None
    ):
        """Log an activity"""
        activity = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "activity_type": activity_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details or {},
            "time_saved_minutes": time_saved_minutes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.activity_logs.insert_one(activity)
        return activity
    
    @staticmethod
    async def get_activities(
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get activities with filters"""
        query = {}
        if tenant_id:
            query["tenant_id"] = tenant_id
        if user_id:
            query["user_id"] = user_id
        if activity_type:
            query["activity_type"] = activity_type
        
        activities = await db.activity_logs.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
        return activities
    
    @staticmethod
    async def calculate_time_saved(tenant_id: str, period_days: int = 30) -> Dict[str, float]:
        """Calculate total time saved in different categories"""
        since = (datetime.now(timezone.utc) - timedelta(days=period_days)).isoformat()
        
        pipeline = [
            {"$match": {"tenant_id": tenant_id, "timestamp": {"$gte": since}, "time_saved_minutes": {"$exists": True}}},
            {"$group": {
                "_id": "$activity_type",
                "total_minutes": {"$sum": "$time_saved_minutes"},
                "count": {"$sum": 1}
            }}
        ]
        
        results = await db.activity_logs.aggregate(pipeline).to_list(100)
        
        breakdown = {}
        total = 0
        for r in results:
            breakdown[r["_id"]] = r["total_minutes"]
            total += r["total_minutes"]
        
        return {
            "total_minutes": total,
            "total_hours": round(total / 60, 2),
            "breakdown": breakdown
        }

# ==================== VENDOR LEARNING SERVICE ====================

class VendorLearningService:
    """Service for learning vendor patterns"""
    
    @staticmethod
    def get_vendor_identifier(cvr_number: Optional[str], supplier_name: Optional[str]) -> str:
        """Generate unique vendor identifier"""
        if cvr_number:
            return f"cvr_{cvr_number}"
        if supplier_name:
            return f"name_{hashlib.md5(supplier_name.lower().strip().encode()).hexdigest()[:12]}"
        return None
    
    @staticmethod
    async def learn_from_approval(
        tenant_id: str,
        extracted_data: Dict[str, Any],
        final_data: Dict[str, Any],
        account_mapping: Dict[str, str]
    ):
        """Learn vendor pattern from approved invoice"""
        cvr = final_data.get("cvr_number") or extracted_data.get("cvr_number")
        supplier = final_data.get("supplier_name") or extracted_data.get("supplier_name")
        
        identifier = VendorLearningService.get_vendor_identifier(cvr, supplier)
        if not identifier:
            return
        
        existing = await db.vendor_patterns.find_one({
            "tenant_id": tenant_id,
            "vendor_identifier": identifier
        })
        
        pattern_data = {
            "tenant_id": tenant_id,
            "vendor_identifier": identifier,
            "vendor_name": supplier or "Unknown",
            "learned_account_code": account_mapping.get("account_code"),
            "learned_account_name": account_mapping.get("account_name"),
            "learned_vat_code": account_mapping.get("vat_code") or str(final_data.get("vat_percentage", "25")),
            "last_used": datetime.now(timezone.utc).isoformat()
        }
        
        if existing:
            await db.vendor_patterns.update_one(
                {"id": existing["id"]},
                {"$set": pattern_data, "$inc": {"usage_count": 1}}
            )
        else:
            pattern_data["id"] = str(uuid.uuid4())
            pattern_data["usage_count"] = 1
            pattern_data["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.vendor_patterns.insert_one(pattern_data)
    
    @staticmethod
    async def get_vendor_suggestion(tenant_id: str, cvr_number: Optional[str], supplier_name: Optional[str]) -> Optional[Dict]:
        """Get learned pattern for vendor"""
        identifier = VendorLearningService.get_vendor_identifier(cvr_number, supplier_name)
        if not identifier:
            return None
        
        pattern = await db.vendor_patterns.find_one({
            "tenant_id": tenant_id,
            "vendor_identifier": identifier
        }, {"_id": 0})
        
        return pattern

# ==================== AI SERVICE (ENHANCED) ====================

class AIService:
    """Centralized AI service with confidence scoring"""
    
    @staticmethod
    async def extract_invoice_data_with_confidence(text: str, tenant_id: str = None) -> Dict[str, Any]:
        """Extract invoice data with field-level confidence scores"""
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"invoice-{uuid.uuid4()}",
                system_message="""You are an expert invoice data extractor. Extract structured data from invoice text.
                For each field, provide a confidence score (0.0-1.0) based on how clearly the information was found.
                
                Return ONLY valid JSON with this structure:
                {
                    "supplier_name": {"value": "string", "confidence": 0.0-1.0},
                    "cvr_number": {"value": "string (8 digits)", "confidence": 0.0-1.0},
                    "invoice_number": {"value": "string", "confidence": 0.0-1.0},
                    "invoice_date": {"value": "YYYY-MM-DD", "confidence": 0.0-1.0},
                    "due_date": {"value": "YYYY-MM-DD", "confidence": 0.0-1.0},
                    "net_amount": {"value": number, "confidence": 0.0-1.0},
                    "vat_amount": {"value": number, "confidence": 0.0-1.0},
                    "total_amount": {"value": number, "confidence": 0.0-1.0},
                    "vat_percentage": {"value": number, "confidence": 0.0-1.0},
                    "currency": {"value": "DKK/EUR/etc", "confidence": 0.0-1.0},
                    "line_items": [{"description": "string", "quantity": number, "unit_price": number, "amount": number}]
                }
                
                Set confidence < 0.7 if the field is unclear, partially visible, or inferred.
                Set confidence > 0.9 only if clearly visible and unambiguous."""
            ).with_model("openai", "gpt-5.2")
            
            response = await chat.send_message(UserMessage(text=f"Extract invoice data from this text:\n\n{text}"))
            
            # Parse JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                extracted = json.loads(json_match.group())
                
                # Process and normalize the response
                processed = {}
                uncertain_fields = []
                total_confidence = 0
                field_count = 0
                
                for field in ["supplier_name", "cvr_number", "invoice_number", "invoice_date", 
                             "due_date", "net_amount", "vat_amount", "total_amount", 
                             "vat_percentage", "currency"]:
                    if field in extracted and isinstance(extracted[field], dict):
                        value = extracted[field].get("value")
                        confidence = extracted[field].get("confidence", 0.5)
                        
                        processed[field] = {
                            "value": value,
                            "confidence": confidence,
                            "source": "ai",
                            "uncertain": confidence < 0.7
                        }
                        
                        if confidence < 0.7:
                            uncertain_fields.append(field)
                        
                        total_confidence += confidence
                        field_count += 1
                    elif field in extracted:
                        # Handle non-dict values (backward compatibility)
                        processed[field] = {
                            "value": extracted[field],
                            "confidence": 0.6,
                            "source": "ai",
                            "uncertain": True
                        }
                        uncertain_fields.append(field)
                        total_confidence += 0.6
                        field_count += 1
                
                # Keep line items as-is
                if "line_items" in extracted:
                    processed["line_items"] = extracted["line_items"]
                
                # Calculate overall confidence
                overall_confidence = total_confidence / field_count if field_count > 0 else 0
                
                return {
                    "fields": processed,
                    "overall_confidence": round(overall_confidence, 2),
                    "uncertain_fields": uncertain_fields,
                    "extraction_complete": True
                }
            
            return {
                "fields": {},
                "overall_confidence": 0,
                "uncertain_fields": [],
                "extraction_complete": False
            }
            
        except Exception as e:
            logger.error(f"AI extraction error: {e}")
            return {
                "fields": {},
                "overall_confidence": 0,
                "uncertain_fields": [],
                "extraction_complete": False,
                "error": str(e)
            }
    
    @staticmethod
    async def suggest_account_mapping(
        supplier_name: str, 
        description: str, 
        amount: float,
        vendor_pattern: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Suggest account mapping, incorporating vendor learning"""
        
        # If we have learned pattern, use it with high confidence
        if vendor_pattern and vendor_pattern.get("learned_account_code"):
            return {
                "account_code": vendor_pattern["learned_account_code"],
                "account_name": vendor_pattern.get("learned_account_name", "Learned Account"),
                "vat_code": vendor_pattern.get("learned_vat_code", "25"),
                "confidence": 0.95,
                "source": "vendor_learned",
                "usage_count": vendor_pattern.get("usage_count", 0)
            }
        
        # Otherwise, use AI
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"account-{uuid.uuid4()}",
                system_message="""You are a Danish accounting expert. Suggest the appropriate chart of accounts category.
                Use standard Danish kontoplan codes.
                Return JSON: {
                    "account_code": "4-digit code",
                    "account_name": "Account name in Danish",
                    "vat_code": "25 or 0",
                    "confidence": 0.0-1.0
                }"""
            ).with_model("openai", "gpt-5.2")
            
            response = await chat.send_message(UserMessage(
                text=f"Supplier: {supplier_name}\nDescription: {description}\nAmount: {amount} DKK\nSuggest Danish accounting category."
            ))
            
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                result["source"] = "ai"
                return result
            
            return {"account_code": "4000", "account_name": "Varekøb", "vat_code": "25", "confidence": 0.5, "source": "default"}
        except Exception as e:
            logger.error(f"AI account mapping error: {e}")
            return {"account_code": "4000", "account_name": "Varekøb", "vat_code": "25", "confidence": 0.3, "source": "fallback"}
    
    @staticmethod
    async def generate_vat_risk_summary(vat_data: Dict[str, Any]) -> str:
        """Generate VAT risk analysis summary"""
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"vat-{uuid.uuid4()}",
                system_message="You are a Danish VAT compliance expert. Analyze VAT data and provide risk assessment in Danish."
            ).with_model("openai", "gpt-5.2")
            
            response = await chat.send_message(UserMessage(
                text=f"Analyze this VAT data for compliance risks:\n{json.dumps(vat_data, indent=2)}"
            ))
            return response
        except Exception as e:
            logger.error(f"AI VAT analysis error: {e}")
            return "Unable to generate risk summary"

# ==================== ACCOUNTING PROVIDER ABSTRACTION (INTEGRATION-READY) ====================

class AccountingProviderInterface:
    """Abstract accounting provider interface - Integration Ready"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.is_configured = False
        self.is_connected = False
    
    async def connect(self) -> Dict[str, Any]:
        """Connect to accounting system"""
        raise NotImplementedError
    
    async def refresh_token(self) -> bool:
        """Refresh authentication token"""
        raise NotImplementedError
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test if connection is working"""
        raise NotImplementedError
    
    async def fetch_chart_of_accounts(self) -> List[Dict]:
        """Fetch chart of accounts"""
        raise NotImplementedError
    
    async def create_draft_voucher(self, voucher_data: Dict) -> Dict[str, Any]:
        """Create a draft voucher in accounting system"""
        raise NotImplementedError
    
    async def push_voucher(self, voucher_id: str) -> Dict[str, Any]:
        """Push voucher to accounting system"""
        raise NotImplementedError
    
    async def validate_vat(self, vat_data: Dict) -> Dict[str, Any]:
        """Validate VAT data"""
        raise NotImplementedError
    
    async def attach_document(self, voucher_id: str, document_data: bytes, filename: str) -> bool:
        """Attach document to voucher"""
        raise NotImplementedError

class EconomicProvider(AccountingProviderInterface):
    """e-conomic provider - Integration Ready Structure"""
    
    PROVIDER_TYPE = ProviderType.ECONOMIC
    API_BASE_URL = "https://restapi.e-conomic.com"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.agreement_number = config.get("agreement_number") if config else None
        self.user_token = config.get("user_token") if config else None
        self.api_url = config.get("api_url", self.API_BASE_URL) if config else self.API_BASE_URL
        self.is_configured = bool(self.agreement_number and self.user_token)
    
    async def connect(self) -> Dict[str, Any]:
        """Connect to e-conomic API"""
        if not self.is_configured:
            return {
                "success": False,
                "error": "Provider not configured. Please set agreement number and user token.",
                "requires_configuration": True
            }
        
        # TODO: Implement actual e-conomic OAuth/API connection
        # For now, return integration-ready response
        return {
            "success": False,
            "error": "e-conomic integration pending. System is ready to connect once credentials are activated.",
            "integration_ready": True,
            "provider": self.PROVIDER_TYPE
        }
    
    async def refresh_token(self) -> bool:
        if not self.is_configured:
            return False
        # TODO: Implement token refresh
        return False
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection status"""
        return {
            "connected": False,
            "configured": self.is_configured,
            "provider": self.PROVIDER_TYPE,
            "message": "Integration ready - awaiting live credentials"
        }
    
    async def fetch_chart_of_accounts(self) -> List[Dict]:
        """Return standard Danish chart of accounts structure"""
        # Return default Danish kontoplan structure
        return [
            {"code": "1000", "name": "Likvider", "type": "asset"},
            {"code": "2000", "name": "Tilgodehavender", "type": "asset"},
            {"code": "3000", "name": "Varelager", "type": "asset"},
            {"code": "4000", "name": "Varekøb", "type": "expense"},
            {"code": "4500", "name": "Omkostninger", "type": "expense"},
            {"code": "5000", "name": "Lønninger", "type": "expense"},
            {"code": "6000", "name": "Andre omkostninger", "type": "expense"},
            {"code": "7000", "name": "Af- og nedskrivninger", "type": "expense"},
            {"code": "8000", "name": "Finansielle poster", "type": "expense"},
        ]
    
    async def create_draft_voucher(self, voucher_data: Dict) -> Dict[str, Any]:
        """Create internal draft voucher (ready for push when connected)"""
        return {
            "success": True,
            "voucher_id": str(uuid.uuid4()),
            "status": VoucherStatus.READY_TO_PUSH,
            "message": "Draft voucher created. Ready to push to e-conomic when connected.",
            "integration_ready": True
        }
    
    async def push_voucher(self, voucher_id: str) -> Dict[str, Any]:
        """Push voucher to e-conomic"""
        if not self.is_configured:
            return {
                "success": False,
                "error": "Cannot push: e-conomic not configured",
                "requires_configuration": True
            }
        
        # TODO: Implement actual push to e-conomic API
        return {
            "success": False,
            "error": "Push pending: awaiting live e-conomic integration",
            "integration_ready": True
        }
    
    async def validate_vat(self, vat_data: Dict) -> Dict[str, Any]:
        """Validate VAT according to Danish rules"""
        net = vat_data.get("net_amount", 0)
        vat = vat_data.get("vat_amount", 0)
        rate = vat_data.get("vat_percentage", 25)
        
        expected_vat = net * (rate / 100)
        is_valid = abs(vat - expected_vat) < 1  # Allow 1 DKK tolerance
        
        return {
            "valid": is_valid,
            "expected_vat": round(expected_vat, 2),
            "actual_vat": vat,
            "difference": round(vat - expected_vat, 2),
            "rate": rate
        }
    
    async def attach_document(self, voucher_id: str, document_data: bytes, filename: str) -> bool:
        # TODO: Implement document attachment
        return True

# Provider factory
def get_accounting_provider(provider_type: str, config: Dict[str, Any] = None) -> AccountingProviderInterface:
    """Factory to get appropriate accounting provider"""
    providers = {
        ProviderType.ECONOMIC: EconomicProvider,
        # Future: ProviderType.DINERO: DineroProvider,
        # Future: ProviderType.BILLY: BillyProvider,
    }
    
    provider_class = providers.get(provider_type, EconomicProvider)
    return provider_class(config)

# ==================== VOUCHER SERVICE ====================

class VoucherService:
    """Service for managing draft vouchers"""
    
    @staticmethod
    async def create_draft_voucher(
        tenant_id: str,
        document_id: str,
        extracted_data: Dict[str, Any],
        account_mapping: Dict[str, str],
        user_id: str
    ) -> Dict[str, Any]:
        """Create a draft voucher from approved document"""
        
        voucher_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        # Build voucher data
        voucher_data = {
            "supplier_name": extracted_data.get("supplier_name"),
            "cvr_number": extracted_data.get("cvr_number"),
            "invoice_number": extracted_data.get("invoice_number"),
            "invoice_date": extracted_data.get("invoice_date"),
            "due_date": extracted_data.get("due_date"),
            "net_amount": extracted_data.get("net_amount"),
            "vat_amount": extracted_data.get("vat_amount"),
            "total_amount": extracted_data.get("total_amount"),
            "vat_percentage": extracted_data.get("vat_percentage", 25),
            "currency": extracted_data.get("currency", "DKK"),
        }
        
        # Build voucher preview
        preview = {
            "debit_entries": [
                {
                    "account_code": account_mapping.get("account_code", "4000"),
                    "account_name": account_mapping.get("account_name", "Varekøb"),
                    "amount": voucher_data["net_amount"],
                    "vat_code": account_mapping.get("vat_code", "25")
                }
            ],
            "credit_entries": [
                {
                    "account_code": "6900",
                    "account_name": "Leverandørgæld",
                    "amount": voucher_data["total_amount"]
                }
            ],
            "vat_entry": {
                "account_code": "6510",
                "account_name": "Indgående moms",
                "amount": voucher_data["vat_amount"]
            },
            "total_debit": voucher_data["total_amount"],
            "total_credit": voucher_data["total_amount"],
            "balanced": True
        }
        
        voucher = {
            "id": voucher_id,
            "tenant_id": tenant_id,
            "document_id": document_id,
            "status": VoucherStatus.READY_TO_PUSH,
            "voucher_data": voucher_data,
            "account_mapping": account_mapping,
            "preview": preview,
            "created_by": user_id,
            "created_at": now,
            "updated_at": now
        }
        
        await db.vouchers.insert_one(voucher)
        
        # Log activity
        time_saved = TIME_ESTIMATES["voucher_creation"]
        await ActivityService.log(
            user_id=user_id,
            activity_type=ActivityType.VOUCHER_CREATED,
            entity_type="voucher",
            entity_id=voucher_id,
            tenant_id=tenant_id,
            details={
                "document_id": document_id,
                "total_amount": voucher_data["total_amount"],
                "account_code": account_mapping.get("account_code")
            },
            time_saved_minutes=time_saved
        )
        
        return voucher
    
    @staticmethod
    async def get_voucher(voucher_id: str) -> Optional[Dict]:
        """Get voucher by ID"""
        return await db.vouchers.find_one({"id": voucher_id}, {"_id": 0})
    
    @staticmethod
    async def get_tenant_vouchers(tenant_id: str, status: Optional[str] = None) -> List[Dict]:
        """Get all vouchers for a tenant"""
        query = {"tenant_id": tenant_id}
        if status:
            query["status"] = status
        return await db.vouchers.find(query, {"_id": 0}).to_list(1000)

# ==================== OCR PROVIDER ====================

class TesseractProvider:
    """Tesseract OCR provider implementation"""
    
    @staticmethod
    async def extract_text(document_bytes: bytes, file_type: str) -> str:
        try:
            import pytesseract
            from PIL import Image
            from pdf2image import convert_from_bytes
            
            if file_type == "pdf":
                images = convert_from_bytes(document_bytes)
                text_parts = []
                for img in images:
                    text_parts.append(pytesseract.image_to_string(img))
                return "\n".join(text_parts)
            else:
                image = Image.open(BytesIO(document_bytes))
                return pytesseract.image_to_string(image)
        except Exception as e:
            logger.error(f"Tesseract OCR error: {e}")
            return ""

# ==================== AUTH ROUTES ====================

@auth_router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, background_tasks: BackgroundTasks):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "name": user_data.name,
        "role": user_data.role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id, user_data.email, user_data.role)
    
    await ActivityService.log(
        user_id=user_id,
        activity_type=ActivityType.USER_REGISTERED,
        entity_type="user",
        entity_id=user_id,
        details={"email": user_data.email, "role": user_data.role}
    )
    
    # Send welcome email (mocked)
    background_tasks.add_task(MockEmailService.send_welcome_email, user_data.email, user_data.name)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            role=user_data.role,
            created_at=user_doc["created_at"]
        )
    )

@auth_router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"], user["email"], user["role"])
    
    await ActivityService.log(
        user_id=user["id"],
        activity_type=ActivityType.USER_LOGIN,
        entity_type="user",
        entity_id=user["id"],
        details={}
    )
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            role=user["role"],
            created_at=user["created_at"]
        )
    )

@auth_router.post("/password-reset/request")
async def request_password_reset(data: PasswordResetRequest):
    user = await db.users.find_one({"email": data.email})
    if user:
        reset_token = str(uuid.uuid4())
        await db.password_resets.insert_one({
            "token": reset_token,
            "user_id": user["id"],
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "used": False
        })
        logger.info(f"Password reset token for {data.email}: {reset_token}")
    
    return {"message": "If email exists, reset instructions have been sent"}

@auth_router.post("/password-reset/confirm")
async def confirm_password_reset(data: PasswordResetConfirm):
    reset = await db.password_resets.find_one({"token": data.token, "used": False})
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    if datetime.fromisoformat(reset["expires_at"]) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired")
    
    await db.users.update_one(
        {"id": reset["user_id"]},
        {"$set": {"password": hash_password(data.new_password), "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    await db.password_resets.update_one({"token": data.token}, {"$set": {"used": True}})
    
    return {"message": "Password updated successfully"}

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        created_at=user["created_at"]
    )

@auth_router.post("/refresh")
async def refresh_token(user: dict = Depends(get_current_user)):
    token = create_token(user["id"], user["email"], user["role"])
    return {"access_token": token, "token_type": "bearer"}

# ==================== TENANT ROUTES ====================

@tenant_router.post("/", response_model=TenantResponse)
async def create_tenant(tenant_data: TenantCreate, user: dict = Depends(get_current_user)):
    tenant_id = str(uuid.uuid4())
    tenant_doc = {
        "id": tenant_id,
        "name": tenant_data.name,
        "cvr_number": tenant_data.cvr_number,
        "address": tenant_data.address,
        "owner_id": user["id"],
        "settings": tenant_data.settings or {},
        "users": [user["id"]],
        "provider_config": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.tenants.insert_one(tenant_doc)
    
    await ActivityService.log(
        user_id=user["id"],
        activity_type=ActivityType.COMPANY_CREATED,
        entity_type="tenant",
        entity_id=tenant_id,
        tenant_id=tenant_id,
        details={"name": tenant_data.name}
    )
    
    return TenantResponse(
        id=tenant_id,
        name=tenant_data.name,
        cvr_number=tenant_data.cvr_number,
        address=tenant_data.address,
        owner_id=user["id"],
        settings=tenant_doc["settings"],
        provider_configured=False,
        created_at=tenant_doc["created_at"]
    )

@tenant_router.get("/", response_model=List[TenantResponse])
async def get_user_tenants(user: dict = Depends(get_current_user)):
    if user["role"] == UserRole.ADMIN:
        tenants = await db.tenants.find({}, {"_id": 0}).to_list(1000)
    else:
        tenants = await db.tenants.find({"users": user["id"]}, {"_id": 0}).to_list(100)
    
    return [TenantResponse(
        id=t["id"],
        name=t["name"],
        cvr_number=t.get("cvr_number"),
        address=t.get("address"),
        owner_id=t["owner_id"],
        settings=t.get("settings", {}),
        provider_configured=bool(t.get("provider_config")),
        created_at=t["created_at"]
    ) for t in tenants]

@tenant_router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str, user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if user["role"] != UserRole.ADMIN and user["id"] not in tenant.get("users", []):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return TenantResponse(
        id=tenant["id"],
        name=tenant["name"],
        cvr_number=tenant.get("cvr_number"),
        address=tenant.get("address"),
        owner_id=tenant["owner_id"],
        settings=tenant.get("settings", {}),
        provider_configured=bool(tenant.get("provider_config")),
        created_at=tenant["created_at"]
    )

@tenant_router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: str, update_data: TenantUpdate, user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if tenant["owner_id"] != user["id"] and user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only owner can update tenant")
    
    updates = {k: v for k, v in update_data.model_dump().items() if v is not None}
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.tenants.update_one({"id": tenant_id}, {"$set": updates})
    
    updated = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    return TenantResponse(
        id=updated["id"],
        name=updated["name"],
        cvr_number=updated.get("cvr_number"),
        address=updated.get("address"),
        owner_id=updated["owner_id"],
        settings=updated.get("settings", {}),
        provider_configured=bool(updated.get("provider_config")),
        created_at=updated["created_at"]
    )

@tenant_router.post("/{tenant_id}/users/{user_email}")
async def add_user_to_tenant(tenant_id: str, user_email: str, user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if tenant["owner_id"] != user["id"] and user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only owner can add users")
    
    target_user = await db.users.find_one({"email": user_email}, {"_id": 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.tenants.update_one({"id": tenant_id}, {"$addToSet": {"users": target_user["id"]}})
    return {"message": "User added to tenant"}

# Provider Configuration Routes
@tenant_router.get("/{tenant_id}/provider")
async def get_provider_config(tenant_id: str, user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if user["role"] != UserRole.ADMIN and user["id"] not in tenant.get("users", []):
        raise HTTPException(status_code=403, detail="Access denied")
    
    config = tenant.get("provider_config") or {}
    
    # Mask sensitive data
    if config.get("user_token"):
        config["user_token"] = "***configured***"
    
    return {
        "configured": bool(tenant.get("provider_config")),
        "config": config,
        "available_providers": [ProviderType.ECONOMIC]
    }

@tenant_router.put("/{tenant_id}/provider")
async def update_provider_config(
    tenant_id: str, 
    config: ProviderConfigUpdate, 
    user: dict = Depends(get_current_user)
):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if tenant["owner_id"] != user["id"] and user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only owner can configure provider")
    
    # Build config update
    current_config = tenant.get("provider_config") or {}
    updates = {k: v for k, v in config.model_dump().items() if v is not None}
    
    # Encrypt sensitive data
    if "user_token" in updates and updates["user_token"]:
        updates["user_token"] = encrypt_sensitive(updates["user_token"])
    
    new_config = {**current_config, **updates}
    
    await db.tenants.update_one(
        {"id": tenant_id},
        {"$set": {"provider_config": new_config, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await ActivityService.log(
        user_id=user["id"],
        activity_type=ActivityType.PROVIDER_CONFIGURED,
        entity_type="tenant",
        entity_id=tenant_id,
        tenant_id=tenant_id,
        details={"provider_type": new_config.get("provider_type")}
    )
    
    return {"message": "Provider configuration updated", "configured": bool(new_config.get("user_token"))}

@tenant_router.post("/{tenant_id}/provider/test")
async def test_provider_connection(tenant_id: str, user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if user["role"] != UserRole.ADMIN and user["id"] not in tenant.get("users", []):
        raise HTTPException(status_code=403, detail="Access denied")
    
    config = tenant.get("provider_config") or {}
    provider = get_accounting_provider(config.get("provider_type", ProviderType.ECONOMIC), config)
    
    result = await provider.test_connection()
    return result

# ==================== DOCUMENT ROUTES (ENHANCED) ====================

@document_router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tenant_id: str = Form(...),
    user: dict = Depends(get_current_user)
):
    # Validate tenant access
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: jpg, png, pdf")
    
    file_content = await file.read()
    file_type = "pdf" if file.content_type == "application/pdf" else "image"
    
    doc_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    doc = {
        "id": doc_id,
        "tenant_id": tenant_id,
        "user_id": user["id"],
        "filename": file.filename,
        "file_type": file_type,
        "file_content": base64.b64encode(file_content).decode(),
        "status": "processing",
        "extracted_data": None,
        "field_confidence": None,
        "ai_suggestions": None,
        "overall_confidence": None,
        "uncertain_fields": [],
        "user_edits": [],
        "created_at": now,
        "updated_at": now
    }
    await db.documents.insert_one(doc)
    
    # Log upload activity
    await ActivityService.log(
        user_id=user["id"],
        activity_type=ActivityType.INVOICE_UPLOADED,
        entity_type="document",
        entity_id=doc_id,
        tenant_id=tenant_id,
        details={"filename": file.filename, "file_type": file_type}
    )
    
    # Process in background
    background_tasks.add_task(process_document_enhanced, doc_id, file_content, file_type, tenant_id, user["id"])
    
    return DocumentResponse(
        id=doc_id,
        tenant_id=tenant_id,
        filename=file.filename,
        file_type=file_type,
        status="processing",
        extracted_data=None,
        field_confidence=None,
        ai_suggestions=None,
        overall_confidence=None,
        uncertain_fields=None,
        created_at=now,
        updated_at=now
    )

async def process_document_enhanced(doc_id: str, file_content: bytes, file_type: str, tenant_id: str, user_id: str):
    """Enhanced document processing with production AI, validation, and vendor learning"""
    global production_ai_service
    
    try:
        # OCR extraction
        ocr_text = await TesseractProvider.extract_text(file_content, file_type)
        
        time_saved = TIME_ESTIMATES["ocr_extraction"]
        
        # Initialize production AI service if needed
        if not production_ai_service:
            production_ai_service = ProductionAIService(db, EMERGENT_LLM_KEY)
        
        # Get tenant context
        tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
        company_context = {
            "industry": tenant.get("settings", {}).get("industry", "general"),
            "currency": tenant.get("settings", {}).get("currency", "DKK")
        }
        
        # Use production AI service for extraction
        ai_result = await production_ai_service.extract_invoice_data(
            ocr_text, 
            tenant_id, 
            company_context
        )
        
        time_saved += TIME_ESTIMATES["data_entry"]
        
        if not ai_result.get("success"):
            # AI failed - mark document with error status
            await db.documents.update_one(
                {"id": doc_id},
                {"$set": {
                    "status": "ai_processing_failed",
                    "error_message": ai_result.get("error", "AI extraction failed"),
                    "ocr_text": ocr_text,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            logger.error(f"Document {doc_id} AI processing failed: {ai_result.get('error')}")
            return
        
        # Extract data from production AI result
        ai_data = ai_result.get("data", {})
        overall_confidence = ai_data.get("confidence_score", 0)
        vendor_override_applied = ai_result.get("vendor_override_applied", False)
        
        # Build fields with confidence
        fields = {}
        uncertain_fields = []
        
        field_mapping = [
            ("supplier_name", "vendor_name"),
            ("cvr_number", "cvr_number"),
            ("invoice_number", "invoice_number"),
            ("invoice_date", "invoice_date"),
            ("due_date", "due_date"),
            ("net_amount", "net_amount"),
            ("vat_amount", "vat_amount"),
            ("total_amount", "total_amount"),
            ("currency", "currency"),
        ]
        
        for field_key, ai_key in field_mapping:
            value = ai_data.get(ai_key)
            confidence = overall_confidence if value else 0.3
            uncertain = confidence < 0.7
            
            fields[field_key] = {
                "value": value,
                "confidence": confidence,
                "source": "ai_production" if not vendor_override_applied else "vendor_learned",
                "uncertain": uncertain
            }
            
            if uncertain and value:
                uncertain_fields.append(field_key)
        
        # Add account mapping from production AI
        account_code = ai_data.get("suggested_account")
        account_name = ai_data.get("suggested_account_name")
        vat_code = ai_data.get("vat_code", "I25")
        
        fields["account_code"] = {
            "value": account_code,
            "confidence": overall_confidence,
            "source": "vendor_learned" if vendor_override_applied else "ai_production",
            "uncertain": not vendor_override_applied and overall_confidence < 0.7
        }
        fields["account_name"] = {
            "value": account_name,
            "confidence": overall_confidence,
            "source": "vendor_learned" if vendor_override_applied else "ai_production",
            "uncertain": not vendor_override_applied and overall_confidence < 0.7
        }
        
        time_saved += TIME_ESTIMATES["account_mapping"]
        
        # Validate CVR format
        cvr_val = ai_data.get("cvr_number")
        cvr_valid = bool(re.match(r"^\d{8}$", str(cvr_val))) if cvr_val else None
        
        # Validate VAT consistency
        vat_amount = float(ai_data.get("vat_amount", 0) or 0)
        net_amount = float(ai_data.get("net_amount", 0) or 0)
        expected_vat = net_amount * 0.25
        vat_consistent = abs(vat_amount - expected_vat) < 1 if net_amount > 0 else None
        
        time_saved += TIME_ESTIMATES["vat_calculation"]
        
        # Check duplicates
        supplier_name = ai_data.get("vendor_name")
        existing = await db.documents.find_one({
            "id": {"$ne": doc_id},
            "tenant_id": tenant_id,
            "extracted_data.invoice_number": ai_data.get("invoice_number"),
            "extracted_data.supplier_name": supplier_name
        })
        is_duplicate = existing is not None
        
        # Build extracted_data for backward compatibility
        extracted_data = {k: v.get("value") if isinstance(v, dict) else v for k, v in fields.items()}
        extracted_data["supplier_name"] = supplier_name  # Ensure supplier name is set
        
        # Build AI suggestions
        ai_suggestions = {
            "account_code": account_code,
            "account_name": account_name,
            "vat_code": vat_code,
            "journal": ai_data.get("journal", "KOB"),
            "account_confidence": overall_confidence,
            "account_source": "vendor_learned" if vendor_override_applied else "ai_production",
            "cvr_valid": cvr_valid,
            "vat_consistent": vat_consistent,
            "vat_rule_applied": ai_data.get("_vat_rule"),
            "is_duplicate": is_duplicate,
            "vendor_override_applied": vendor_override_applied,
            "validation_passed": ai_result.get("validation_passed", True)
        }
        
        # Update document
        await db.documents.update_one(
            {"id": doc_id},
            {"$set": {
                "status": "review",
                "ocr_text": ocr_text,
                "extracted_data": extracted_data,
                "field_confidence": fields,
                "ai_suggestions": ai_suggestions,
                "ai_raw_response": ai_data,  # Store raw AI response for learning
                "overall_confidence": overall_confidence,
                "uncertain_fields": uncertain_fields,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Log AI extraction activity
        await ActivityService.log(
            user_id=user_id,
            activity_type=ActivityType.AI_EXTRACTION_COMPLETED,
            entity_type="document",
            entity_id=doc_id,
            tenant_id=tenant_id,
            details={
                "overall_confidence": overall_confidence,
                "uncertain_fields_count": len(uncertain_fields),
                "vendor_override_applied": vendor_override_applied,
                "vat_rule_applied": ai_data.get("_vat_rule"),
                "ai_version": "production_v2"
            },
            time_saved_minutes=time_saved
        )
        
        logger.info(f"Document {doc_id} processed with confidence {overall_confidence} (vendor_override={vendor_override_applied})")
        
    except Exception as e:
        logger.error(f"Document processing error for {doc_id}: {e}")
        await db.documents.update_one(
            {"id": doc_id},
            {"$set": {
                "status": "ai_processing_failed",
                "error_message": str(e),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )

@document_router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    query = {}
    
    if tenant_id:
        tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
        if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
            raise HTTPException(status_code=403, detail="Access denied")
        query["tenant_id"] = tenant_id
    else:
        if user["role"] != UserRole.ADMIN:
            user_tenants = await db.tenants.find({"users": user["id"]}, {"id": 1, "_id": 0}).to_list(100)
            tenant_ids = [t["id"] for t in user_tenants]
            query["tenant_id"] = {"$in": tenant_ids}
    
    if status:
        query["status"] = status
    
    docs = await db.documents.find(query, {"_id": 0, "file_content": 0, "ocr_text": 0}).to_list(1000)
    
    return [DocumentResponse(
        id=d["id"],
        tenant_id=d["tenant_id"],
        filename=d["filename"],
        file_type=d["file_type"],
        status=d["status"],
        extracted_data=d.get("extracted_data"),
        field_confidence=d.get("field_confidence"),
        ai_suggestions=d.get("ai_suggestions"),
        overall_confidence=d.get("overall_confidence"),
        uncertain_fields=d.get("uncertain_fields"),
        created_at=d["created_at"],
        updated_at=d["updated_at"]
    ) for d in docs]

@document_router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, user: dict = Depends(get_current_user)):
    doc = await db.documents.find_one({"id": doc_id}, {"_id": 0, "file_content": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    tenant = await db.tenants.find_one({"id": doc["tenant_id"]}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return DocumentResponse(
        id=doc["id"],
        tenant_id=doc["tenant_id"],
        filename=doc["filename"],
        file_type=doc["file_type"],
        status=doc["status"],
        extracted_data=doc.get("extracted_data"),
        field_confidence=doc.get("field_confidence"),
        ai_suggestions=doc.get("ai_suggestions"),
        overall_confidence=doc.get("overall_confidence"),
        uncertain_fields=doc.get("uncertain_fields"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"]
    )

@document_router.put("/{doc_id}/edit")
async def edit_document_fields(doc_id: str, edit_request: DocumentEditRequest, user: dict = Depends(get_current_user)):
    """Allow user to edit extracted fields before approval"""
    doc = await db.documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    tenant = await db.tenants.find_one({"id": doc["tenant_id"]}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if doc["status"] != "review":
        raise HTTPException(status_code=400, detail="Can only edit documents in review status")
    
    # Track user edits
    edits = doc.get("user_edits", [])
    edits.append({
        "user_id": user["id"],
        "fields": list(edit_request.field_updates.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Update extracted data and field confidence
    extracted_data = doc.get("extracted_data", {})
    field_confidence = doc.get("field_confidence", {})
    
    for field, value in edit_request.field_updates.items():
        extracted_data[field] = value
        field_confidence[field] = {
            "value": value,
            "confidence": 1.0,  # User edited = 100% confidence
            "source": "user_edited",
            "uncertain": False
        }
    
    # Recalculate uncertain fields
    uncertain_fields = [k for k, v in field_confidence.items() if isinstance(v, dict) and v.get("uncertain")]
    
    await db.documents.update_one(
        {"id": doc_id},
        {"$set": {
            "extracted_data": extracted_data,
            "field_confidence": field_confidence,
            "uncertain_fields": uncertain_fields,
            "user_edits": edits,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Log edit activity
    await ActivityService.log(
        user_id=user["id"],
        activity_type=ActivityType.USER_EDITED_FIELDS,
        entity_type="document",
        entity_id=doc_id,
        tenant_id=doc["tenant_id"],
        details={"fields_edited": list(edit_request.field_updates.keys())}
    )
    
    return {"message": "Fields updated", "fields_edited": list(edit_request.field_updates.keys())}

@document_router.put("/{doc_id}/approve")
async def approve_document(doc_id: str, approval: DocumentApproval, user: dict = Depends(get_current_user)):
    """Approve document and create draft voucher"""
    doc = await db.documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    tenant = await db.tenants.find_one({"id": doc["tenant_id"]}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if approval.approved:
        # Build final data
        extracted_data = doc.get("extracted_data", {})
        final_data = {**extracted_data, **(approval.final_data or {})}
        
        # Build account mapping
        ai_suggestions = doc.get("ai_suggestions", {})
        account_mapping = approval.account_mapping or {
            "account_code": ai_suggestions.get("account_code", "4000"),
            "account_name": ai_suggestions.get("account_name", "Varekøb"),
            "vat_code": ai_suggestions.get("vat_code", "25")
        }
        
        # Create draft voucher
        voucher = await VoucherService.create_draft_voucher(
            tenant_id=doc["tenant_id"],
            document_id=doc_id,
            extracted_data=final_data,
            account_mapping=account_mapping,
            user_id=user["id"]
        )
        
        # Learn vendor pattern
        await VendorLearningService.learn_from_approval(
            tenant_id=doc["tenant_id"],
            extracted_data=extracted_data,
            final_data=final_data,
            account_mapping=account_mapping
        )
        
        # Update document
        await db.documents.update_one(
            {"id": doc_id},
            {"$set": {
                "status": "approved",
                "final_data": final_data,
                "account_mapping": account_mapping,
                "voucher_id": voucher["id"],
                "approved_by": user["id"],
                "approved_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Log approval
        await ActivityService.log(
            user_id=user["id"],
            activity_type=ActivityType.INVOICE_APPROVED,
            entity_type="document",
            entity_id=doc_id,
            tenant_id=doc["tenant_id"],
            details={
                "voucher_id": voucher["id"],
                "total_amount": final_data.get("total_amount")
            }
        )
        
        return {
            "message": "Document approved",
            "voucher_id": voucher["id"],
            "voucher_status": voucher["status"],
            "voucher_preview": voucher["preview"]
        }
    else:
        await db.documents.update_one(
            {"id": doc_id},
            {"$set": {
                "status": "rejected",
                "rejected_by": user["id"],
                "rejected_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        await ActivityService.log(
            user_id=user["id"],
            activity_type=ActivityType.INVOICE_REJECTED,
            entity_type="document",
            entity_id=doc_id,
            tenant_id=doc["tenant_id"],
            details={}
        )
        
        return {"message": "Document rejected"}

# ==================== VOUCHER ROUTES ====================

@voucher_router.get("/{tenant_id}")
async def get_vouchers(
    tenant_id: str,
    status: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    vouchers = await VoucherService.get_tenant_vouchers(tenant_id, status)
    return vouchers

@voucher_router.get("/{tenant_id}/{voucher_id}")
async def get_voucher_detail(tenant_id: str, voucher_id: str, user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    voucher = await VoucherService.get_voucher(voucher_id)
    if not voucher or voucher["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    return voucher

@voucher_router.post("/{tenant_id}/push")
async def push_voucher_to_accounting(
    tenant_id: str,
    push_request: VoucherPushRequest,
    user: dict = Depends(get_current_user)
):
    """Push voucher to accounting system (when connected)"""
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    voucher = await VoucherService.get_voucher(push_request.voucher_id)
    if not voucher or voucher["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    if voucher["status"] != VoucherStatus.READY_TO_PUSH:
        raise HTTPException(status_code=400, detail=f"Voucher status is {voucher['status']}, cannot push")
    
    # Get provider
    config = tenant.get("provider_config") or {}
    provider = get_accounting_provider(config.get("provider_type", ProviderType.ECONOMIC), config)
    
    # Attempt to push
    result = await provider.push_voucher(voucher["id"])
    
    if result.get("success"):
        await db.vouchers.update_one(
            {"id": voucher["id"]},
            {"$set": {
                "status": VoucherStatus.PUSHED,
                "pushed_at": datetime.now(timezone.utc).isoformat(),
                "external_id": result.get("external_id"),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        await ActivityService.log(
            user_id=user["id"],
            activity_type=ActivityType.VOUCHER_PUSHED,
            entity_type="voucher",
            entity_id=voucher["id"],
            tenant_id=tenant_id,
            details={"external_id": result.get("external_id")}
        )
    
    return result

# ==================== VENDOR ROUTES ====================

@vendor_router.get("/{tenant_id}")
async def get_vendor_patterns(tenant_id: str, user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    patterns = await db.vendor_patterns.find({"tenant_id": tenant_id}, {"_id": 0}).to_list(1000)
    return patterns

@vendor_router.put("/{tenant_id}/{pattern_id}")
async def update_vendor_pattern(
    tenant_id: str,
    pattern_id: str,
    update: VendorPatternUpdate,
    user: dict = Depends(get_current_user)
):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    updates = {f"learned_{k}": v for k, v in update.model_dump().items() if v is not None}
    updates["last_used"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.vendor_patterns.update_one(
        {"id": pattern_id, "tenant_id": tenant_id},
        {"$set": updates}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Pattern not found")
    
    return {"message": "Pattern updated"}

# ==================== ACTIVITY ROUTES ====================

@activity_router.get("/{tenant_id}")
async def get_activity_logs(
    tenant_id: str,
    activity_type: Optional[str] = None,
    limit: int = 100,
    user: dict = Depends(get_current_user)
):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    activities = await ActivityService.get_activities(
        tenant_id=tenant_id,
        activity_type=activity_type,
        limit=limit
    )
    return activities

@activity_router.get("/{tenant_id}/time-saved")
async def get_time_saved(tenant_id: str, days: int = 30, user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    time_saved = await ActivityService.calculate_time_saved(tenant_id, days)
    return time_saved

# ==================== RECONCILIATION ROUTES ====================

@reconciliation_router.get("/{tenant_id}/unmatched")
async def get_unmatched_transactions(tenant_id: str, user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    transactions = await db.transactions.find(
        {"tenant_id": tenant_id, "matched": False},
        {"_id": 0}
    ).to_list(1000)
    
    invoices = await db.documents.find(
        {"tenant_id": tenant_id, "status": "approved"},
        {"_id": 0, "id": 1, "extracted_data": 1, "filename": 1}
    ).to_list(1000)
    
    suggestions = []
    for tx in transactions:
        tx_amount = tx.get("amount", 0)
        tx_desc = tx.get("description", "").lower()
        
        for inv in invoices:
            inv_data = inv.get("extracted_data") or {}
            inv_amount = inv_data.get("total_amount", 0) or 0
            inv_supplier = (inv_data.get("supplier_name") or "").lower()
            
            amount_match = abs(tx_amount - inv_amount) / max(inv_amount, 1) < 0.01 if inv_amount > 0 else False
            text_match = inv_supplier in tx_desc or any(word in tx_desc for word in inv_supplier.split())
            
            if amount_match or text_match:
                confidence = 0.5 * amount_match + 0.5 * text_match
                suggestions.append({
                    "transaction_id": tx["id"],
                    "transaction_amount": tx_amount,
                    "transaction_description": tx.get("description"),
                    "invoice_id": inv["id"],
                    "invoice_amount": inv_amount,
                    "invoice_supplier": inv_data.get("supplier_name"),
                    "confidence": confidence
                })
    
    return {"transactions": transactions, "suggestions": sorted(suggestions, key=lambda x: -x["confidence"])}

@reconciliation_router.post("/{tenant_id}/match")
async def match_transaction(tenant_id: str, match: TransactionMatch, user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.transactions.update_one(
        {"id": match.transaction_id, "tenant_id": tenant_id},
        {"$set": {
            "matched": True,
            "matched_invoice_id": match.invoice_id,
            "match_confidence": match.confidence,
            "matched_by": user["id"],
            "matched_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    recon_id = str(uuid.uuid4())
    await db.reconciliations.insert_one({
        "id": recon_id,
        "tenant_id": tenant_id,
        "transaction_id": match.transaction_id,
        "invoice_id": match.invoice_id,
        "status": "matched",
        "match_confidence": match.confidence,
        "created_by": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Transaction matched", "reconciliation_id": recon_id}

@reconciliation_router.post("/{tenant_id}/bulk-approve")
async def bulk_approve_matches(tenant_id: str, matches: List[TransactionMatch], user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    results = []
    for match in matches:
        await db.transactions.update_one(
            {"id": match.transaction_id, "tenant_id": tenant_id},
            {"$set": {
                "matched": True,
                "matched_invoice_id": match.invoice_id,
                "match_confidence": match.confidence,
                "matched_by": user["id"],
                "matched_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        results.append({"transaction_id": match.transaction_id, "status": "matched"})
    
    return {"message": f"{len(results)} transactions matched", "results": results}

# ==================== VAT ROUTES ====================

@vat_router.get("/{tenant_id}/analysis")
async def get_vat_analysis(
    tenant_id: str,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not period_start:
        now = datetime.now(timezone.utc)
        quarter_start = datetime(now.year, ((now.month - 1) // 3) * 3 + 1, 1, tzinfo=timezone.utc)
        period_start = quarter_start.isoformat()
    if not period_end:
        period_end = datetime.now(timezone.utc).isoformat()
    
    pipeline = [
        {"$match": {
            "tenant_id": tenant_id,
            "status": "approved",
            "created_at": {"$gte": period_start, "$lte": period_end}
        }},
        {"$group": {
            "_id": None,
            "total_net": {"$sum": {"$ifNull": ["$extracted_data.net_amount", 0]}},
            "total_vat": {"$sum": {"$ifNull": ["$extracted_data.vat_amount", 0]}},
            "total_amount": {"$sum": {"$ifNull": ["$extracted_data.total_amount", 0]}},
            "doc_count": {"$sum": 1}
        }}
    ]
    
    result = await db.documents.aggregate(pipeline).to_list(1)
    stats = result[0] if result else {"total_net": 0, "total_vat": 0, "total_amount": 0, "doc_count": 0}
    
    anomalies = []
    
    docs_with_issues = await db.documents.find({
        "tenant_id": tenant_id,
        "status": "approved",
        "ai_suggestions.vat_consistent": False
    }, {"_id": 0, "id": 1, "filename": 1, "extracted_data": 1}).to_list(100)
    
    for doc in docs_with_issues:
        anomalies.append({
            "type": "vat_inconsistency",
            "severity": "medium",
            "document_id": doc["id"],
            "filename": doc["filename"],
            "details": "VAT amount doesn't match expected 25% rate"
        })
    
    duplicate_docs = await db.documents.find({
        "tenant_id": tenant_id,
        "ai_suggestions.is_duplicate": True
    }, {"_id": 0, "id": 1, "filename": 1}).to_list(100)
    
    for doc in duplicate_docs:
        anomalies.append({
            "type": "potential_duplicate",
            "severity": "high",
            "document_id": doc["id"],
            "filename": doc["filename"],
            "details": "Potential duplicate invoice detected"
        })
    
    risk_score = min(100, len(anomalies) * 15)
    
    vat_data = {
        "period": f"{period_start} to {period_end}",
        "total_purchases": stats["total_net"],
        "total_vat_paid": stats["total_vat"],
        "document_count": stats["doc_count"],
        "anomalies_count": len(anomalies),
        "anomaly_types": [a["type"] for a in anomalies]
    }
    
    risk_summary = await AIService.generate_vat_risk_summary(vat_data)
    
    return {
        "tenant_id": tenant_id,
        "period_start": period_start,
        "period_end": period_end,
        "summary": {
            "total_purchases": stats["total_net"],
            "total_vat_paid": stats["total_vat"],
            "total_amount": stats["total_amount"],
            "document_count": stats["doc_count"]
        },
        "anomalies": anomalies,
        "risk_score": risk_score,
        "ai_risk_summary": risk_summary
    }

@vat_router.get("/{tenant_id}/report")
async def generate_vat_report(
    tenant_id: str,
    period_start: str,
    period_end: str,
    user: dict = Depends(get_current_user)
):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    analysis = await get_vat_analysis(tenant_id, period_start, period_end, user)
    
    report_id = str(uuid.uuid4())
    report = {
        "id": report_id,
        "tenant_id": tenant_id,
        "period_start": period_start,
        "period_end": period_end,
        "data": analysis,
        "generated_by": user["id"],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.vat_reports.insert_one(report)
    
    return {"report_id": report_id, "data": analysis}

# ==================== BILLING ROUTES (ADMIN-ACTIVATED) ====================

SUBSCRIPTION_PLANS = [
    {
        "id": "starter",
        "name": "Starter",
        "price": 299,
        "currency": "dkk",
        "features": ["Up to 50 documents/month", "1 company", "Email support"],
        "limits": {"documents_per_month": 50, "companies": 1}
    },
    {
        "id": "professional",
        "name": "Professional",
        "price": 799,
        "currency": "dkk",
        "features": ["Up to 200 documents/month", "5 companies", "Priority support", "VAT analysis"],
        "limits": {"documents_per_month": 200, "companies": 5}
    },
    {
        "id": "accountant",
        "name": "Accountant",
        "price": 1499,
        "currency": "dkk",
        "features": ["Unlimited documents", "Unlimited companies", "Multi-client dashboard", "Full suite"],
        "limits": {"documents_per_month": 999999, "companies": 999999}
    }
]

@billing_router.get("/plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans():
    return [SubscriptionPlan(**plan) for plan in SUBSCRIPTION_PLANS]

@billing_router.get("/subscription")
async def get_current_subscription(user: dict = Depends(get_current_user)):
    subscription = await db.subscriptions.find_one({"user_id": user["id"], "status": "active"}, {"_id": 0})
    if not subscription:
        return {"subscription": None, "plan": None}
    
    plan = next((p for p in SUBSCRIPTION_PLANS if p["id"] == subscription["plan_id"]), None)
    
    # Calculate usage
    tenant_count = await db.tenants.count_documents({"users": user["id"]})
    
    now = datetime.now(timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc).isoformat()
    
    user_tenants = await db.tenants.find({"users": user["id"]}, {"id": 1, "_id": 0}).to_list(100)
    tenant_ids = [t["id"] for t in user_tenants]
    
    doc_count = await db.documents.count_documents({
        "tenant_id": {"$in": tenant_ids},
        "created_at": {"$gte": month_start}
    })
    
    return {
        "subscription": {
            "id": subscription["id"],
            "user_id": subscription["user_id"],
            "plan_id": subscription["plan_id"],
            "plan_name": plan["name"] if plan else "Unknown",
            "status": subscription["status"],
            "activated_by": subscription.get("activated_by"),
            "activated_at": subscription.get("activated_at"),
            "current_period_start": subscription["current_period_start"],
            "current_period_end": subscription["current_period_end"],
            "usage": {
                "documents_this_month": doc_count,
                "companies": tenant_count
            },
            "limits": plan["limits"] if plan else {}
        },
        "plan": plan
    }

@billing_router.post("/request")
async def request_subscription(plan_id: str, user: dict = Depends(get_current_user)):
    """Request subscription - admin will activate"""
    plan = next((p for p in SUBSCRIPTION_PLANS if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    existing = await db.subscriptions.find_one({"user_id": user["id"], "status": {"$in": ["active", "pending"]}})
    if existing:
        raise HTTPException(status_code=400, detail="Already have an active or pending subscription")
    
    request_id = str(uuid.uuid4())
    await db.subscription_requests.insert_one({
        "id": request_id,
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "plan_id": plan_id,
        "status": "pending",
        "requested_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Subscription request submitted", "request_id": request_id, "status": "pending"}

@billing_router.delete("/subscription")
async def cancel_subscription(user: dict = Depends(get_current_user)):
    subscription = await db.subscriptions.find_one({"user_id": user["id"], "status": "active"})
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription")
    
    await db.subscriptions.update_one(
        {"id": subscription["id"]},
        {"$set": {"status": "cancelled", "cancelled_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Subscription cancelled"}

# ==================== ADMIN ROUTES ====================

@admin_router.get("/users", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def get_all_users():
    users = await db.users.find({}, {"_id": 0, "password": 0}).to_list(1000)
    return users

@admin_router.get("/stats", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def get_admin_stats():
    user_count = await db.users.count_documents({})
    tenant_count = await db.tenants.count_documents({})
    doc_count = await db.documents.count_documents({})
    voucher_count = await db.vouchers.count_documents({})
    subscription_count = await db.subscriptions.count_documents({"status": "active"})
    pending_requests = await db.subscription_requests.count_documents({"status": "pending"})
    
    return {
        "total_users": user_count,
        "total_tenants": tenant_count,
        "total_documents": doc_count,
        "total_vouchers": voucher_count,
        "active_subscriptions": subscription_count,
        "pending_subscription_requests": pending_requests
    }

@admin_router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, admin: dict = Depends(require_role([UserRole.ADMIN]))):
    if role not in [UserRole.SME_USER, UserRole.ACCOUNTANT, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    result = await db.users.update_one({"id": user_id}, {"$set": {"role": role}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Role updated"}

@admin_router.get("/subscription-requests", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def get_subscription_requests():
    requests = await db.subscription_requests.find({}, {"_id": 0}).sort("requested_at", -1).to_list(100)
    return requests

@admin_router.post("/subscriptions/activate", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def admin_activate_subscription(data: AdminSubscriptionActivate, admin: dict = Depends(require_role([UserRole.ADMIN]))):
    """Admin manually activates a subscription"""
    plan = next((p for p in SUBSCRIPTION_PLANS if p["id"] == data.plan_id), None)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    target_user = await db.users.find_one({"id": data.user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Deactivate existing subscription
    await db.subscriptions.update_many(
        {"user_id": data.user_id, "status": "active"},
        {"$set": {"status": "superseded"}}
    )
    
    # Create new subscription
    subscription_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    await db.subscriptions.insert_one({
        "id": subscription_id,
        "user_id": data.user_id,
        "plan_id": data.plan_id,
        "status": "active",
        "activated_by": admin["id"],
        "activated_at": now.isoformat(),
        "activation_notes": data.notes,
        "current_period_start": now.isoformat(),
        "current_period_end": (now + timedelta(days=30)).isoformat(),
        "created_at": now.isoformat()
    })
    
    # Update any pending requests
    await db.subscription_requests.update_many(
        {"user_id": data.user_id, "status": "pending"},
        {"$set": {"status": "approved", "approved_at": now.isoformat(), "approved_by": admin["id"]}}
    )
    
    await ActivityService.log(
        user_id=data.user_id,
        activity_type=ActivityType.SUBSCRIPTION_ACTIVATED,
        entity_type="subscription",
        entity_id=subscription_id,
        details={"plan_id": data.plan_id, "activated_by": admin["email"]}
    )
    
    return {
        "message": "Subscription activated",
        "subscription_id": subscription_id,
        "plan": plan["name"],
        "user_email": target_user["email"]
    }

# ==================== DASHBOARD ROUTES ====================

@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    if user["role"] == UserRole.ADMIN:
        tenant_ids = [t["id"] for t in await db.tenants.find({}, {"id": 1, "_id": 0}).to_list(1000)]
    else:
        tenant_ids = [t["id"] for t in await db.tenants.find({"users": user["id"]}, {"id": 1, "_id": 0}).to_list(100)]
    
    total_docs = await db.documents.count_documents({"tenant_id": {"$in": tenant_ids}})
    pending_docs = await db.documents.count_documents({"tenant_id": {"$in": tenant_ids}, "status": "review"})
    processed_docs = await db.documents.count_documents({"tenant_id": {"$in": tenant_ids}, "status": "approved"})
    
    total_vouchers = await db.vouchers.count_documents({"tenant_id": {"$in": tenant_ids}})
    ready_vouchers = await db.vouchers.count_documents({"tenant_id": {"$in": tenant_ids}, "status": VoucherStatus.READY_TO_PUSH})
    
    total_tx = await db.transactions.count_documents({"tenant_id": {"$in": tenant_ids}})
    unmatched_tx = await db.transactions.count_documents({"tenant_id": {"$in": tenant_ids}, "matched": False})
    
    risk_scores = []
    for tid in tenant_ids[:5]:
        analysis = await db.vat_reports.find_one({"tenant_id": tid}, {"_id": 0, "data.risk_score": 1}, sort=[("generated_at", -1)])
        if analysis and "data" in analysis:
            risk_scores.append(analysis["data"].get("risk_score", 0))
    
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    
    # Calculate time saved from activity logs
    time_saved_data = {"total_hours": 0, "breakdown": {}}
    if tenant_ids:
        for tid in tenant_ids[:5]:
            ts = await ActivityService.calculate_time_saved(tid, 30)
            time_saved_data["total_hours"] += ts.get("total_hours", 0)
            for k, v in ts.get("breakdown", {}).items():
                time_saved_data["breakdown"][k] = time_saved_data["breakdown"].get(k, 0) + v
    
    return DashboardStats(
        total_documents=total_docs,
        pending_documents=pending_docs,
        processed_documents=processed_docs,
        total_vouchers=total_vouchers,
        ready_to_push_vouchers=ready_vouchers,
        total_transactions=total_tx,
        unmatched_transactions=unmatched_tx,
        vat_risk_score=avg_risk,
        time_saved_hours=round(time_saved_data["total_hours"], 1),
        time_saved_breakdown=time_saved_data["breakdown"]
    )

@api_router.get("/accountant/overview")
async def get_accountant_overview(user: dict = Depends(require_role([UserRole.ACCOUNTANT, UserRole.ADMIN]))):
    tenants = await db.tenants.find({"users": user["id"]}, {"_id": 0}).to_list(100)
    
    overview = []
    for tenant in tenants:
        pending = await db.documents.count_documents({"tenant_id": tenant["id"], "status": "review"})
        ready_vouchers = await db.vouchers.count_documents({"tenant_id": tenant["id"], "status": VoucherStatus.READY_TO_PUSH})
        
        risk_report = await db.vat_reports.find_one(
            {"tenant_id": tenant["id"]},
            {"_id": 0, "data.risk_score": 1, "data.anomalies": 1},
            sort=[("generated_at", -1)]
        )
        
        overview.append({
            "tenant_id": tenant["id"],
            "tenant_name": tenant["name"],
            "pending_documents": pending,
            "ready_vouchers": ready_vouchers,
            "provider_configured": bool(tenant.get("provider_config")),
            "risk_score": risk_report["data"]["risk_score"] if risk_report else 0,
            "anomalies_count": len(risk_report["data"].get("anomalies", [])) if risk_report else 0
        })
    
    overview.sort(key=lambda x: (-x["pending_documents"], -x["risk_score"]))
    
    return {"clients": overview, "total_clients": len(tenants)}

# ==================== HEALTH CHECK ====================

@api_router.get("/")
async def root():
    return {"message": "AI Accounting Copilot API", "version": "2.0.0-beta"}

@api_router.get("/health")
async def health_check():
    try:
        await db.command("ping")
        return {"status": "healthy", "database": "connected", "version": "2.0.0-beta"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

# ==================== BETA FEATURES ====================

# Feedback Router
feedback_router = APIRouter(prefix="/feedback", tags=["Feedback"])

class FeedbackSubmission(BaseModel):
    type: str  # feedback, bug_report
    rating: Optional[int] = None
    category: str
    message: str
    page_context: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: Optional[str] = None

@feedback_router.post("")
async def submit_feedback(feedback: FeedbackSubmission, user: dict = Depends(get_current_user)):
    """Submit beta feedback or bug report"""
    feedback_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "user_email": user["email"],
        "type": feedback.type,
        "rating": feedback.rating,
        "category": feedback.category,
        "message": feedback.message,
        "page_context": feedback.page_context,
        "user_agent": feedback.user_agent,
        "status": "new",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.feedback.insert_one(feedback_doc)
    
    # Log for monitoring
    logger.info(f"[FEEDBACK] User {user['email']} submitted {feedback.type}: {feedback.category}")
    
    # Mock email notification to admin
    await MockEmailService.send_email(
        to="admin@ai-accounting-copilot.com",
        subject=f"New {feedback.type.replace('_', ' ').title()} from {user['email']}",
        body=f"""
New feedback received:
- Type: {feedback.type}
- Category: {feedback.category}
- Rating: {feedback.rating or 'N/A'}
- Message: {feedback.message}
- Page: {feedback.page_context}
- User: {user['email']}
"""
    )
    
    return {"success": True, "id": feedback_doc["id"], "message": "Feedback received. Thank you!"}

@feedback_router.get("")
async def get_all_feedback(user: dict = Depends(require_role([UserRole.ADMIN]))):
    """Admin endpoint to view all feedback"""
    feedback_list = await db.feedback.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return {"feedback": feedback_list, "total": len(feedback_list)}

# Export Router
export_router = APIRouter(prefix="/export", tags=["Export"])

class ExportRequest(BaseModel):
    format: str = "csv"  # csv or pdf
    voucher_ids: Optional[List[str]] = None

@export_router.post("/{tenant_id}/vouchers")
async def export_vouchers(tenant_id: str, request: ExportRequest, user: dict = Depends(get_current_user)):
    """Export vouchers as CSV or PDF"""
    # Verify tenant access
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get vouchers
    query = {"tenant_id": tenant_id}
    if request.voucher_ids:
        query["id"] = {"$in": request.voucher_ids}
    
    vouchers = await db.vouchers.find(query, {"_id": 0}).to_list(1000)
    
    if not vouchers:
        raise HTTPException(status_code=404, detail="No vouchers found to export")
    
    if request.format == "csv":
        return export_vouchers_csv(vouchers, tenant["name"])
    else:
        return export_vouchers_pdf(vouchers, tenant["name"])

def export_vouchers_csv(vouchers: List[Dict], tenant_name: str) -> str:
    """Generate CSV export of vouchers"""
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Voucher ID", "Supplier", "CVR", "Invoice #", "Invoice Date", 
        "Due Date", "Net Amount", "VAT Amount", "Total Amount", "Currency",
        "Account Code", "Account Name", "Status", "Created At"
    ])
    
    # Data rows
    for v in vouchers:
        data = v.get("voucher_data", {})
        mapping = v.get("account_mapping", {})
        writer.writerow([
            v.get("id", ""),
            data.get("supplier_name", ""),
            data.get("cvr_number", ""),
            data.get("invoice_number", ""),
            data.get("invoice_date", ""),
            data.get("due_date", ""),
            data.get("net_amount", 0),
            data.get("vat_amount", 0),
            data.get("total_amount", 0),
            data.get("currency", "DKK"),
            mapping.get("account_code", ""),
            mapping.get("account_name", ""),
            v.get("status", ""),
            v.get("created_at", "")
        ])
    
    return output.getvalue()

def export_vouchers_pdf(vouchers: List[Dict], tenant_name: str) -> Dict[str, Any]:
    """Generate simple PDF export of vouchers (base64 encoded)"""
    # Simple text-based PDF generation
    pdf_content = f"""AI Accounting Copilot - Voucher Export
Company: {tenant_name}
Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC
Total Vouchers: {len(vouchers)}
{'='*60}

"""
    
    for i, v in enumerate(vouchers, 1):
        data = v.get("voucher_data", {})
        mapping = v.get("account_mapping", {})
        preview = v.get("preview", {})
        
        pdf_content += f"""
VOUCHER #{i}
-----------
ID: {v.get('id', '')}
Status: {v.get('status', '').upper()}

INVOICE DETAILS:
  Supplier: {data.get('supplier_name', 'N/A')}
  CVR: {data.get('cvr_number', 'N/A')}
  Invoice #: {data.get('invoice_number', 'N/A')}
  Invoice Date: {data.get('invoice_date', 'N/A')}
  Due Date: {data.get('due_date', 'N/A')}

AMOUNTS:
  Net Amount: {data.get('net_amount', 0):,.2f} {data.get('currency', 'DKK')}
  VAT Amount: {data.get('vat_amount', 0):,.2f} {data.get('currency', 'DKK')}
  Total: {data.get('total_amount', 0):,.2f} {data.get('currency', 'DKK')}

ACCOUNTING:
  Account: {mapping.get('account_code', '')} - {mapping.get('account_name', '')}
  Balance: {'BALANCED' if preview.get('balanced') else 'UNBALANCED'}

Created: {v.get('created_at', '')}
{'='*60}
"""
    
    # Encode as base64 for simple transfer
    import base64
    encoded = base64.b64encode(pdf_content.encode()).decode()
    
    return {"content": encoded, "filename": f"vouchers-{tenant_name}-{datetime.now().strftime('%Y%m%d')}.txt"}

# ==================== MOCK EMAIL SERVICE ====================

class MockEmailService:
    """Mock email service that logs emails instead of sending them"""
    
    @staticmethod
    async def send_email(to: str, subject: str, body: str, from_email: str = "noreply@ai-accounting-copilot.com"):
        """Log email instead of sending"""
        email_log = {
            "id": str(uuid.uuid4()),
            "to": to,
            "from": from_email,
            "subject": subject,
            "body": body,
            "status": "logged",  # In production this would be "sent"
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.email_logs.insert_one(email_log)
        
        logger.info(f"[MOCK EMAIL] To: {to}, Subject: {subject}")
        logger.debug(f"[MOCK EMAIL BODY] {body[:200]}...")
        
        return {"success": True, "id": email_log["id"], "status": "logged"}
    
    @staticmethod
    async def send_invoice_processed_notification(user_email: str, document_id: str, confidence: float):
        """Send notification when invoice is processed"""
        await MockEmailService.send_email(
            to=user_email,
            subject="Invoice Processed - AI Accounting Copilot",
            body=f"""
Your invoice has been processed successfully!

Document ID: {document_id}
AI Confidence: {confidence*100:.0f}%

Please review and approve the extracted data in your dashboard.

Best regards,
AI Accounting Copilot Team
"""
        )
    
    @staticmethod
    async def send_voucher_ready_notification(user_email: str, voucher_id: str, amount: float):
        """Send notification when voucher is ready"""
        await MockEmailService.send_email(
            to=user_email,
            subject="Voucher Ready to Push - AI Accounting Copilot",
            body=f"""
A new voucher is ready for your accounting system!

Voucher ID: {voucher_id}
Amount: {amount:,.2f} DKK

Log in to review and push to your accounting system.

Best regards,
AI Accounting Copilot Team
"""
        )
    
    @staticmethod
    async def send_welcome_email(user_email: str, user_name: str):
        """Send welcome email to new users"""
        await MockEmailService.send_email(
            to=user_email,
            subject="Welcome to AI Accounting Copilot (Beta)",
            body=f"""
Hi {user_name},

Welcome to AI Accounting Copilot! 🎉

You're now part of our exclusive beta program. Here's what you can do:

1. Upload invoices (PDF or images)
2. Review AI-extracted data with confidence scores
3. Approve and create accounting vouchers
4. Track your time savings

As a beta user, your feedback is invaluable. Use the feedback button in the app to share your thoughts!

Need help? Contact support@ai-accounting-copilot.com

Best regards,
The AI Accounting Copilot Team
"""
        )

# Email Admin Router
email_router = APIRouter(prefix="/emails", tags=["Emails"])

@email_router.get("/logs")
async def get_email_logs(user: dict = Depends(require_role([UserRole.ADMIN])), limit: int = 100):
    """Admin endpoint to view email logs"""
    logs = await db.email_logs.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"logs": logs, "total": len(logs)}

# ==================== AI DASHBOARD ROUTES ====================

@ai_dashboard_router.get("/stats")
async def get_ai_dashboard_stats(
    tenant_id: Optional[str] = None,
    user: dict = Depends(require_role([UserRole.ADMIN, UserRole.ACCOUNTANT]))
):
    """Get AI accuracy and performance statistics"""
    global ai_analytics_service
    if not ai_analytics_service:
        ai_analytics_service = AIAnalyticsService(db)
    
    # For non-admin, limit to their tenants
    if user["role"] != UserRole.ADMIN and tenant_id:
        tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
        if not tenant or user["id"] not in tenant.get("users", []):
            raise HTTPException(status_code=403, detail="Access denied")
    
    stats = await ai_analytics_service.get_dashboard_stats(tenant_id)
    return stats

@ai_dashboard_router.get("/corrections")
async def get_ai_corrections(
    tenant_id: Optional[str] = None,
    limit: int = 100,
    user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """Get AI correction history"""
    query = {}
    if tenant_id:
        query["tenant_id"] = tenant_id
    
    corrections = await db.ai_corrections.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"corrections": corrections, "total": len(corrections)}

@ai_dashboard_router.get("/vendor-accuracy")
async def get_vendor_accuracy(
    tenant_id: str,
    user: dict = Depends(get_current_user)
):
    """Get vendor-specific accuracy stats"""
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    pipeline = [
        {"$match": {"tenant_id": tenant_id}},
        {"$group": {
            "_id": "$vendor_name",
            "total": {"$sum": 1},
            "correct": {"$sum": {"$cond": ["$was_correct", 1, 0]}},
            "avg_confidence": {"$avg": "$ai_confidence"}
        }},
        {"$project": {
            "vendor_name": "$_id",
            "total_extractions": "$total",
            "correct_extractions": "$correct",
            "accuracy_percent": {"$multiply": [{"$divide": ["$correct", "$total"]}, 100]},
            "avg_confidence": 1
        }},
        {"$sort": {"total_extractions": -1}}
    ]
    
    vendors = await db.ai_corrections.aggregate(pipeline).to_list(100)
    return {"vendors": vendors}

@ai_dashboard_router.get("/active-companies/{year}/{month}")
async def get_active_companies(
    year: int,
    month: int,
    user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """Get active companies for a given month (for billing)"""
    global active_company_service
    if not active_company_service:
        active_company_service = ActiveCompanyService(db)
    
    companies = await active_company_service.calculate_monthly_activity(year, month)
    return {
        "period": f"{year}-{month:02d}",
        "active_count": len(companies),
        "companies": companies
    }

# ==================== ACCOUNTING DATA ROUTES ====================

@accounting_data_router.get("/chart-of-accounts")
async def get_chart_of_accounts(user: dict = Depends(get_current_user)):
    """Get standard Danish chart of accounts"""
    return {
        "accounts": DANISH_CHART_OF_ACCOUNTS,
        "total": len(DANISH_CHART_OF_ACCOUNTS),
        "country": "DK"
    }

@accounting_data_router.get("/vat-codes")
async def get_vat_codes(user: dict = Depends(get_current_user)):
    """Get Danish VAT codes"""
    return {
        "vat_codes": DANISH_VAT_CODES,
        "total": len(DANISH_VAT_CODES),
        "country": "DK"
    }

@accounting_data_router.get("/journals")
async def get_journals(user: dict = Depends(get_current_user)):
    """Get standard Danish journals"""
    return {
        "journals": DANISH_STANDARD_JOURNALS,
        "total": len(DANISH_STANDARD_JOURNALS),
        "country": "DK"
    }

@accounting_data_router.get("/available-countries")
async def get_available_countries(user: dict = Depends(get_current_user)):
    """Get list of available country VAT rules"""
    return {
        "countries": VATRuleFactory.get_available_countries(),
        "active": "DK"
    }

@accounting_data_router.post("/company/{tenant_id}/custom-accounts")
async def add_company_custom_account(
    tenant_id: str,
    account: Dict[str, Any],
    user: dict = Depends(get_current_user)
):
    """Add a custom account for a company"""
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (tenant["owner_id"] != user["id"] and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Only owner can add custom accounts")
    
    custom_account = {
        "id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "code": account.get("code"),
        "name": account.get("name"),
        "type": account.get("type", "expense"),
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.company_accounts.insert_one(custom_account)
    
    # Clear cache
    global production_ai_service
    if production_ai_service:
        production_ai_service.clear_cache(tenant_id)
    
    return {"success": True, "account": custom_account}

@accounting_data_router.post("/company/{tenant_id}/custom-journals")
async def add_company_custom_journal(
    tenant_id: str,
    journal: Dict[str, Any],
    user: dict = Depends(get_current_user)
):
    """Add a custom journal for a company"""
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (tenant["owner_id"] != user["id"] and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Only owner can add custom journals")
    
    custom_journal = {
        "id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "code": journal.get("code"),
        "name": journal.get("name"),
        "type": journal.get("type", "general"),
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.company_journals.insert_one(custom_journal)
    
    return {"success": True, "journal": custom_journal}

# ==================== INCLUDE ROUTERS ====================

api_router.include_router(auth_router)
api_router.include_router(tenant_router)
api_router.include_router(document_router)
api_router.include_router(voucher_router)
api_router.include_router(vendor_router)
api_router.include_router(activity_router)
api_router.include_router(reconciliation_router)
api_router.include_router(vat_router)
api_router.include_router(billing_router)
api_router.include_router(admin_router)
api_router.include_router(feedback_router)
api_router.include_router(export_router)
api_router.include_router(email_router)
api_router.include_router(ai_dashboard_router)
api_router.include_router(accounting_data_router)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global production_ai_service, ai_analytics_service, active_company_service
    
    # Initialize production AI service
    production_ai_service = ProductionAIService(db, EMERGENT_LLM_KEY)
    ai_analytics_service = AIAnalyticsService(db)
    active_company_service = ActiveCompanyService(db)
    
    logger.info("Production AI services initialized")
    logger.info(f"Active VAT country: {VATRuleFactory._active_country}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
