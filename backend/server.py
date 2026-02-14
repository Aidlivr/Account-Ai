from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import re
import json
import stripe
import base64
from io import BytesIO

# Import AI integration
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

# Create the main app
app = FastAPI(title="AI Accounting Copilot", version="1.0.0")

# Create routers
api_router = APIRouter(prefix="/api")
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
tenant_router = APIRouter(prefix="/tenants", tags=["Tenants"])
document_router = APIRouter(prefix="/documents", tags=["Documents"])
reconciliation_router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])
vat_router = APIRouter(prefix="/vat", tags=["VAT"])
billing_router = APIRouter(prefix="/billing", tags=["Billing"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"])

security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class UserRole:
    SME_USER = "sme_user"
    ACCOUNTANT = "accountant"
    ADMIN = "admin"

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
    created_at: str

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    cvr_number: Optional[str] = None
    address: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class DocumentCreate(BaseModel):
    tenant_id: str

class DocumentResponse(BaseModel):
    id: str
    tenant_id: str
    filename: str
    file_type: str
    status: str
    extracted_data: Optional[Dict[str, Any]]
    ai_suggestions: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    created_at: str
    updated_at: str

class DocumentApproval(BaseModel):
    approved: bool
    modifications: Optional[Dict[str, Any]] = None

class TransactionMatch(BaseModel):
    transaction_id: str
    invoice_id: str
    confidence: float

class ReconciliationResponse(BaseModel):
    id: str
    tenant_id: str
    transaction_id: str
    invoice_id: Optional[str]
    status: str
    match_confidence: Optional[float]
    created_at: str

class VATReportResponse(BaseModel):
    id: str
    tenant_id: str
    period_start: str
    period_end: str
    total_sales: float
    total_purchases: float
    vat_collected: float
    vat_paid: float
    net_vat: float
    anomalies: List[Dict[str, Any]]
    risk_score: float
    created_at: str

class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price: float
    currency: str = "dkk"
    features: List[str]
    limits: Dict[str, int]

class SubscriptionCreate(BaseModel):
    plan_id: str
    payment_method_id: Optional[str] = None

class DashboardStats(BaseModel):
    total_documents: int
    pending_documents: int
    processed_documents: int
    total_transactions: int
    unmatched_transactions: int
    vat_risk_score: float
    time_saved_hours: float

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

# ==================== AI SERVICE ====================

class AIService:
    """Centralized AI service for all AI operations"""
    
    @staticmethod
    async def extract_invoice_data(text: str) -> Dict[str, Any]:
        """Extract structured invoice data from OCR text"""
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"invoice-{uuid.uuid4()}",
                system_message="""You are an expert invoice data extractor. Extract structured data from invoice text.
                Return ONLY valid JSON with these fields:
                {
                    "supplier_name": "string",
                    "cvr_number": "string (8 digits for Danish companies)",
                    "invoice_number": "string",
                    "invoice_date": "YYYY-MM-DD",
                    "due_date": "YYYY-MM-DD",
                    "net_amount": number,
                    "vat_amount": number,
                    "total_amount": number,
                    "vat_percentage": number,
                    "currency": "string (DKK, EUR, etc.)",
                    "line_items": [{"description": "string", "quantity": number, "unit_price": number, "amount": number}]
                }
                If a field cannot be found, use null."""
            ).with_model("openai", "gpt-5.2")
            
            response = await chat.send_message(UserMessage(text=f"Extract invoice data from this text:\n\n{text}"))
            
            # Parse JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            logger.error(f"AI extraction error: {e}")
            return {}
    
    @staticmethod
    async def suggest_account_category(supplier_name: str, description: str, amount: float) -> Dict[str, Any]:
        """Suggest chart of accounts category"""
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"category-{uuid.uuid4()}",
                system_message="""You are an accounting expert. Suggest the appropriate chart of accounts category.
                Return JSON: {"account_code": "string", "account_name": "string", "vat_code": "string", "confidence": 0.0-1.0}"""
            ).with_model("openai", "gpt-5.2")
            
            response = await chat.send_message(UserMessage(
                text=f"Supplier: {supplier_name}\nDescription: {description}\nAmount: {amount}\nSuggest accounting category."
            ))
            
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            return {"account_code": "unknown", "account_name": "Unknown", "vat_code": "25", "confidence": 0.5}
        except Exception as e:
            logger.error(f"AI categorization error: {e}")
            return {"account_code": "unknown", "account_name": "Unknown", "vat_code": "25", "confidence": 0.5}
    
    @staticmethod
    async def generate_vat_risk_summary(vat_data: Dict[str, Any]) -> str:
        """Generate VAT risk analysis summary"""
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"vat-{uuid.uuid4()}",
                system_message="You are a Danish VAT compliance expert. Analyze VAT data and provide risk assessment."
            ).with_model("openai", "gpt-5.2")
            
            response = await chat.send_message(UserMessage(
                text=f"Analyze this VAT data for compliance risks:\n{json.dumps(vat_data, indent=2)}"
            ))
            return response
        except Exception as e:
            logger.error(f"AI VAT analysis error: {e}")
            return "Unable to generate risk summary"

# ==================== PAYMENT PROVIDER ABSTRACTION ====================

class PaymentProvider:
    """Abstract payment provider interface"""
    async def create_customer(self, email: str, name: str) -> str:
        raise NotImplementedError
    
    async def create_subscription(self, customer_id: str, plan_id: str) -> Dict[str, Any]:
        raise NotImplementedError
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        raise NotImplementedError
    
    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        raise NotImplementedError

class StripeProvider(PaymentProvider):
    """Stripe payment provider implementation"""
    
    async def create_customer(self, email: str, name: str) -> str:
        try:
            customer = stripe.Customer.create(email=email, name=name)
            return customer.id
        except Exception as e:
            logger.error(f"Stripe customer creation error: {e}")
            raise HTTPException(status_code=500, detail="Payment provider error")
    
    async def create_subscription(self, customer_id: str, price_id: str) -> Dict[str, Any]:
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice else None
            }
        except Exception as e:
            logger.error(f"Stripe subscription error: {e}")
            raise HTTPException(status_code=500, detail="Payment provider error")
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except Exception as e:
            logger.error(f"Stripe cancellation error: {e}")
            return False
    
    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        try:
            event = stripe.Webhook.construct_event(payload, signature, endpoint_secret)
            return {"event_type": event.type, "data": event.data.object}
        except Exception as e:
            logger.error(f"Stripe webhook error: {e}")
            raise HTTPException(status_code=400, detail="Webhook error")

# Initialize payment provider
payment_provider = StripeProvider()

# ==================== ACCOUNTING PROVIDER ABSTRACTION ====================

class AccountingProvider:
    """Abstract accounting provider interface"""
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        raise NotImplementedError
    
    async def fetch_invoices(self, tenant_id: str, from_date: str, to_date: str) -> List[Dict]:
        raise NotImplementedError
    
    async def fetch_bank_transactions(self, tenant_id: str, from_date: str, to_date: str) -> List[Dict]:
        raise NotImplementedError
    
    async def fetch_chart_of_accounts(self, tenant_id: str) -> List[Dict]:
        raise NotImplementedError
    
    async def create_draft_voucher(self, tenant_id: str, voucher_data: Dict) -> str:
        raise NotImplementedError
    
    async def attach_document(self, tenant_id: str, voucher_id: str, document_url: str) -> bool:
        raise NotImplementedError
    
    async def fetch_vat_report_data(self, tenant_id: str, period: str) -> Dict:
        raise NotImplementedError

class EconomicProvider(AccountingProvider):
    """e-conomic accounting provider implementation (placeholder)"""
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        # Implement e-conomic OAuth flow
        return True
    
    async def fetch_invoices(self, tenant_id: str, from_date: str, to_date: str) -> List[Dict]:
        # Fetch from e-conomic API
        return []
    
    async def fetch_bank_transactions(self, tenant_id: str, from_date: str, to_date: str) -> List[Dict]:
        return []
    
    async def fetch_chart_of_accounts(self, tenant_id: str) -> List[Dict]:
        return []
    
    async def create_draft_voucher(self, tenant_id: str, voucher_data: Dict) -> str:
        return str(uuid.uuid4())
    
    async def attach_document(self, tenant_id: str, voucher_id: str, document_url: str) -> bool:
        return True
    
    async def fetch_vat_report_data(self, tenant_id: str, period: str) -> Dict:
        return {}

# ==================== OCR PROVIDER ABSTRACTION ====================

class OCRProvider:
    """Abstract OCR provider interface"""
    async def extract_text(self, document_bytes: bytes, file_type: str) -> str:
        raise NotImplementedError

class TesseractProvider(OCRProvider):
    """Tesseract OCR provider implementation"""
    
    async def extract_text(self, document_bytes: bytes, file_type: str) -> str:
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

# Initialize providers
ocr_provider = TesseractProvider()
accounting_provider = EconomicProvider()

# ==================== AUTH ROUTES ====================

@auth_router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
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
    
    # Create token
    token = create_token(user_id, user_data.email, user_data.role)
    
    # Log audit
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": "user_registered",
        "details": {"email": user_data.email, "role": user_data.role},
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
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
    
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "action": "user_login",
        "details": {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
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
        # In production, send email with reset link
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
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.tenants.insert_one(tenant_doc)
    
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "tenant_id": tenant_id,
        "action": "tenant_created",
        "details": {"name": tenant_data.name},
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return TenantResponse(
        id=tenant_id,
        name=tenant_data.name,
        cvr_number=tenant_data.cvr_number,
        address=tenant_data.address,
        owner_id=user["id"],
        settings=tenant_doc["settings"],
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

# ==================== DOCUMENT ROUTES ====================

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
    
    # Read file
    file_content = await file.read()
    file_type = "pdf" if file.content_type == "application/pdf" else "image"
    
    # Create document record
    doc_id = str(uuid.uuid4())
    doc = {
        "id": doc_id,
        "tenant_id": tenant_id,
        "user_id": user["id"],
        "filename": file.filename,
        "file_type": file_type,
        "file_content": base64.b64encode(file_content).decode(),
        "status": "processing",
        "extracted_data": None,
        "ai_suggestions": None,
        "confidence_score": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.documents.insert_one(doc)
    
    # Process document in background
    background_tasks.add_task(process_document, doc_id, file_content, file_type)
    
    return DocumentResponse(
        id=doc_id,
        tenant_id=tenant_id,
        filename=file.filename,
        file_type=file_type,
        status="processing",
        extracted_data=None,
        ai_suggestions=None,
        confidence_score=None,
        created_at=doc["created_at"],
        updated_at=doc["updated_at"]
    )

async def process_document(doc_id: str, file_content: bytes, file_type: str):
    """Background task to process document with OCR and AI"""
    try:
        # OCR extraction
        ocr_text = await ocr_provider.extract_text(file_content, file_type)
        
        # AI data extraction
        extracted_data = await AIService.extract_invoice_data(ocr_text)
        
        # Validate CVR format (Danish: 8 digits)
        cvr = extracted_data.get("cvr_number", "")
        cvr_valid = bool(re.match(r"^\d{8}$", str(cvr))) if cvr else None
        
        # Validate VAT consistency (Danish standard: 25%)
        vat_amount = extracted_data.get("vat_amount", 0) or 0
        net_amount = extracted_data.get("net_amount", 0) or 0
        expected_vat = net_amount * 0.25
        vat_consistent = abs(vat_amount - expected_vat) < 1 if net_amount > 0 else None
        
        # Check for duplicate invoice
        existing = await db.documents.find_one({
            "id": {"$ne": doc_id},
            "extracted_data.invoice_number": extracted_data.get("invoice_number"),
            "extracted_data.supplier_name": extracted_data.get("supplier_name")
        })
        is_duplicate = existing is not None
        
        # Get AI categorization suggestions
        ai_suggestions = await AIService.suggest_account_category(
            extracted_data.get("supplier_name", ""),
            str(extracted_data.get("line_items", [])),
            extracted_data.get("total_amount", 0) or 0
        )
        
        # Calculate confidence score
        confidence_factors = [
            0.3 if extracted_data.get("supplier_name") else 0,
            0.2 if extracted_data.get("invoice_number") else 0,
            0.2 if extracted_data.get("total_amount") else 0,
            0.15 if cvr_valid else 0,
            0.15 if vat_consistent else 0
        ]
        confidence_score = sum(confidence_factors)
        
        # Update document
        await db.documents.update_one(
            {"id": doc_id},
            {"$set": {
                "status": "review",
                "ocr_text": ocr_text,
                "extracted_data": extracted_data,
                "ai_suggestions": {
                    **ai_suggestions,
                    "cvr_valid": cvr_valid,
                    "vat_consistent": vat_consistent,
                    "is_duplicate": is_duplicate
                },
                "confidence_score": confidence_score,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        logger.info(f"Document {doc_id} processed successfully")
    except Exception as e:
        logger.error(f"Document processing error for {doc_id}: {e}")
        await db.documents.update_one(
            {"id": doc_id},
            {"$set": {"status": "error", "error_message": str(e), "updated_at": datetime.now(timezone.utc).isoformat()}}
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
        # Get all tenants user has access to
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
        ai_suggestions=d.get("ai_suggestions"),
        confidence_score=d.get("confidence_score"),
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
        ai_suggestions=doc.get("ai_suggestions"),
        confidence_score=doc.get("confidence_score"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"]
    )

@document_router.put("/{doc_id}/approve")
async def approve_document(doc_id: str, approval: DocumentApproval, user: dict = Depends(get_current_user)):
    doc = await db.documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    tenant = await db.tenants.find_one({"id": doc["tenant_id"]}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if approval.approved:
        # Merge modifications with extracted data
        final_data = {**(doc.get("extracted_data") or {}), **(approval.modifications or {})}
        
        # Create voucher in accounting system
        voucher_id = await accounting_provider.create_draft_voucher(doc["tenant_id"], final_data)
        
        await db.documents.update_one(
            {"id": doc_id},
            {"$set": {
                "status": "approved",
                "final_data": final_data,
                "voucher_id": voucher_id,
                "approved_by": user["id"],
                "approved_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Log audit
        await db.audit_logs.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "tenant_id": doc["tenant_id"],
            "action": "document_approved",
            "details": {"doc_id": doc_id, "voucher_id": voucher_id, "modifications": approval.modifications},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {"message": "Document approved", "voucher_id": voucher_id}
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
        return {"message": "Document rejected"}

# ==================== RECONCILIATION ROUTES ====================

@reconciliation_router.get("/{tenant_id}/unmatched")
async def get_unmatched_transactions(tenant_id: str, user: dict = Depends(get_current_user)):
    tenant = await db.tenants.find_one({"id": tenant_id}, {"_id": 0})
    if not tenant or (user["id"] not in tenant.get("users", []) and user["role"] != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get unmatched bank transactions
    transactions = await db.transactions.find(
        {"tenant_id": tenant_id, "matched": False},
        {"_id": 0}
    ).to_list(1000)
    
    # Get approved invoices for matching suggestions
    invoices = await db.documents.find(
        {"tenant_id": tenant_id, "status": "approved"},
        {"_id": 0, "id": 1, "extracted_data": 1, "filename": 1}
    ).to_list(1000)
    
    # Generate match suggestions using fuzzy matching
    suggestions = []
    for tx in transactions:
        tx_amount = tx.get("amount", 0)
        tx_desc = tx.get("description", "").lower()
        
        for inv in invoices:
            inv_data = inv.get("extracted_data") or {}
            inv_amount = inv_data.get("total_amount", 0) or 0
            inv_supplier = (inv_data.get("supplier_name") or "").lower()
            
            # Amount tolerance (within 1%)
            amount_match = abs(tx_amount - inv_amount) / max(inv_amount, 1) < 0.01 if inv_amount > 0 else False
            
            # Text similarity (simple containment check)
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
    
    # Update transaction as matched
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
    
    # Create reconciliation record
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
    
    # Default to current quarter
    if not period_start:
        now = datetime.now(timezone.utc)
        quarter_start = datetime(now.year, ((now.month - 1) // 3) * 3 + 1, 1, tzinfo=timezone.utc)
        period_start = quarter_start.isoformat()
    if not period_end:
        period_end = datetime.now(timezone.utc).isoformat()
    
    # Aggregate VAT data from approved documents
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
    
    # Detect anomalies
    anomalies = []
    
    # Check for unusual VAT rates
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
    
    # Check for duplicates
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
    
    # Calculate risk score (0-100)
    risk_score = min(100, len(anomalies) * 15)
    
    # Generate AI risk summary
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
    
    # Get VAT analysis
    analysis = await get_vat_analysis(tenant_id, period_start, period_end, user)
    
    # Store report
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

# ==================== BILLING ROUTES ====================

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
        "id": "enterprise",
        "name": "Enterprise",
        "price": 1999,
        "currency": "dkk",
        "features": ["Unlimited documents", "Unlimited companies", "Dedicated support", "Full suite"],
        "limits": {"documents_per_month": 999999, "companies": 999999}
    }
]

@billing_router.get("/plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans():
    return [SubscriptionPlan(**plan) for plan in SUBSCRIPTION_PLANS]

@billing_router.post("/subscribe")
async def create_subscription(data: SubscriptionCreate, user: dict = Depends(get_current_user)):
    plan = next((p for p in SUBSCRIPTION_PLANS if p["id"] == data.plan_id), None)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Check if user already has subscription
    existing = await db.subscriptions.find_one({"user_id": user["id"], "status": "active"})
    if existing:
        raise HTTPException(status_code=400, detail="Already subscribed")
    
    # Create Stripe customer if not exists
    user_billing = await db.billing.find_one({"user_id": user["id"]})
    if not user_billing:
        customer_id = await payment_provider.create_customer(user["email"], user["name"])
        await db.billing.insert_one({
            "user_id": user["id"],
            "stripe_customer_id": customer_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    else:
        customer_id = user_billing["stripe_customer_id"]
    
    # For demo purposes, create subscription directly
    subscription_id = str(uuid.uuid4())
    await db.subscriptions.insert_one({
        "id": subscription_id,
        "user_id": user["id"],
        "plan_id": data.plan_id,
        "status": "active",
        "current_period_start": datetime.now(timezone.utc).isoformat(),
        "current_period_end": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"subscription_id": subscription_id, "status": "active", "plan": plan}

@billing_router.get("/subscription")
async def get_current_subscription(user: dict = Depends(get_current_user)):
    subscription = await db.subscriptions.find_one({"user_id": user["id"], "status": "active"}, {"_id": 0})
    if not subscription:
        return {"subscription": None}
    
    plan = next((p for p in SUBSCRIPTION_PLANS if p["id"] == subscription["plan_id"]), None)
    return {"subscription": subscription, "plan": plan}

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
    subscription_count = await db.subscriptions.count_documents({"status": "active"})
    
    return {
        "total_users": user_count,
        "total_tenants": tenant_count,
        "total_documents": doc_count,
        "active_subscriptions": subscription_count
    }

@admin_router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, admin: dict = Depends(require_role([UserRole.ADMIN]))):
    if role not in [UserRole.SME_USER, UserRole.ACCOUNTANT, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    result = await db.users.update_one({"id": user_id}, {"$set": {"role": role}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Role updated"}

# ==================== DASHBOARD ROUTES ====================

@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    # Get user's tenants
    if user["role"] == UserRole.ADMIN:
        tenant_ids = [t["id"] for t in await db.tenants.find({}, {"id": 1, "_id": 0}).to_list(1000)]
    else:
        tenant_ids = [t["id"] for t in await db.tenants.find({"users": user["id"]}, {"id": 1, "_id": 0}).to_list(100)]
    
    # Document stats
    total_docs = await db.documents.count_documents({"tenant_id": {"$in": tenant_ids}})
    pending_docs = await db.documents.count_documents({"tenant_id": {"$in": tenant_ids}, "status": "review"})
    processed_docs = await db.documents.count_documents({"tenant_id": {"$in": tenant_ids}, "status": "approved"})
    
    # Transaction stats
    total_tx = await db.transactions.count_documents({"tenant_id": {"$in": tenant_ids}})
    unmatched_tx = await db.transactions.count_documents({"tenant_id": {"$in": tenant_ids}, "matched": False})
    
    # Calculate average risk score
    risk_scores = []
    for tid in tenant_ids[:5]:  # Limit for performance
        analysis = await db.vat_reports.find_one({"tenant_id": tid}, {"_id": 0, "data.risk_score": 1}, sort=[("generated_at", -1)])
        if analysis and "data" in analysis:
            risk_scores.append(analysis["data"].get("risk_score", 0))
    
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    
    # Estimate time saved (approx 5 min per document)
    time_saved = processed_docs * 5 / 60
    
    return DashboardStats(
        total_documents=total_docs,
        pending_documents=pending_docs,
        processed_documents=processed_docs,
        total_transactions=total_tx,
        unmatched_transactions=unmatched_tx,
        vat_risk_score=avg_risk,
        time_saved_hours=round(time_saved, 1)
    )

# ==================== ACCOUNTANT DASHBOARD ====================

@api_router.get("/accountant/overview")
async def get_accountant_overview(user: dict = Depends(require_role([UserRole.ACCOUNTANT, UserRole.ADMIN]))):
    # Get all tenants this accountant manages
    tenants = await db.tenants.find({"users": user["id"]}, {"_id": 0}).to_list(100)
    
    overview = []
    for tenant in tenants:
        pending = await db.documents.count_documents({"tenant_id": tenant["id"], "status": "review"})
        risk_report = await db.vat_reports.find_one(
            {"tenant_id": tenant["id"]},
            {"_id": 0, "data.risk_score": 1, "data.anomalies": 1},
            sort=[("generated_at", -1)]
        )
        
        overview.append({
            "tenant_id": tenant["id"],
            "tenant_name": tenant["name"],
            "pending_documents": pending,
            "risk_score": risk_report["data"]["risk_score"] if risk_report else 0,
            "anomalies_count": len(risk_report["data"].get("anomalies", [])) if risk_report else 0
        })
    
    # Sort by pending documents and risk
    overview.sort(key=lambda x: (-x["pending_documents"], -x["risk_score"]))
    
    return {"clients": overview, "total_clients": len(tenants)}

# ==================== HEALTH CHECK ====================

@api_router.get("/")
async def root():
    return {"message": "AI Accounting Copilot API", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    try:
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

# ==================== INCLUDE ROUTERS ====================

api_router.include_router(auth_router)
api_router.include_router(tenant_router)
api_router.include_router(document_router)
api_router.include_router(reconciliation_router)
api_router.include_router(vat_router)
api_router.include_router(billing_router)
api_router.include_router(admin_router)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
