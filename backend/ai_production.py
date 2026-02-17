# Production AI Service for Invoice Processing
# Implements structured prompts, validation, vendor learning, and correction tracking
# Supports both Emergent LLM key and direct OpenAI API

import json
import re
import uuid
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from danish_accounting import (
    DANISH_CHART_OF_ACCOUNTS,
    DANISH_VAT_CODES,
    DANISH_STANDARD_JOURNALS,
    validate_account_code,
    validate_vat_code,
    validate_journal_code,
    get_account_by_code,
    get_vat_code_by_code,
    detect_reverse_charge,
    format_chart_for_prompt,
    format_vat_codes_for_prompt,
    format_journals_for_prompt,
)

# Import deterministic rule engine
from rule_engine import apply_deterministic_rules, CompanyConfig

# Import live OpenAI service (for direct API usage)
from openai_live import LiveOpenAIService

logger = logging.getLogger(__name__)

# ==================== AI CONFIGURATION ====================

# Check if we should use direct OpenAI API
USE_LIVE_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))

AI_CONFIG = {
    "temperature": 0.1,  # Low temperature for consistent output
    "top_p": 1,
    "max_retries": 3,
    "model": os.environ.get("OPENAI_MODEL", "gpt-4o"),
    "provider": "openai",
}

# ==================== SYSTEM PROMPT (STATIC) ====================

SYSTEM_PROMPT = """You are an expert Danish accounting assistant specialized in bookkeeping for companies using e-conomic.

Your task:
Analyze invoice OCR text and return structured accounting data.

Rules:
- You must return valid JSON only.
- Never invent account numbers.
- Only use accounts provided in the chart of accounts list.
- Only use VAT codes provided.
- If vendor history exists, prioritize historical mapping.
- If uncertain, lower confidence score.
- Confidence must be between 0.0 and 1.0.
- Do not explain reasoning.
- Do not include extra text."""

# ==================== PRODUCTION AI SERVICE ====================

class ProductionAIService:
    """Production-grade AI service with validation, vendor learning, and error handling"""
    
    def __init__(self, db: AsyncIOMotorDatabase, llm_key: str):
        self.db = db
        self.llm_key = llm_key
        self._account_cache: Dict[str, List[Dict]] = {}
        self._vendor_cache: Dict[str, Dict] = {}
        
        # Initialize live OpenAI service if API key is available
        self.live_openai = LiveOpenAIService(db) if USE_LIVE_OPENAI else None
        
        if USE_LIVE_OPENAI:
            logger.info(f"Production AI: Using LIVE OpenAI API with model {AI_CONFIG['model']}")
        else:
            logger.info("Production AI: Using Emergent LLM integration")
    
    # ==================== MAIN EXTRACTION METHOD ====================
    
    async def extract_invoice_data(
        self,
        ocr_text: str,
        tenant_id: str,
        company_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Production invoice extraction with validation and vendor learning.
        
        Args:
            ocr_text: Raw OCR text from invoice
            tenant_id: Company/tenant ID
            company_context: Optional company-specific context (industry, currency)
            
        Returns:
            Structured extraction result with validation status
        """
        try:
            # 1. Build dynamic prompt
            prompt = await self._build_extraction_prompt(ocr_text, tenant_id, company_context)
            
            # 2. Call AI with retry
            ai_response = await self._call_ai_with_retry(prompt)
            
            if not ai_response.get("success"):
                return self._create_failure_response(ai_response.get("error", "AI call failed"))
            
            raw_result = ai_response["data"]
            
            # 3. Validate response schema
            validation = self._validate_response_schema(raw_result)
            if not validation["valid"]:
                return self._create_failure_response(f"Schema validation failed: {validation['errors']}")
            
            # 4. Get vendor history for override logic
            vendor_name = raw_result.get("vendor_name")
            vendor_history = await self._get_vendor_history(tenant_id, vendor_name)
            
            # 5. Apply post-processing rules (AI-based)
            processed = await self._apply_post_processing(
                raw_result, 
                tenant_id, 
                vendor_history,
                ocr_text
            )
            
            # 6. Apply deterministic rule engine (keyword-based improvements)
            company_config = await self._get_company_rule_config(tenant_id)
            processed = apply_deterministic_rules(processed, ocr_text, company_config)
            
            # 7. Calculate final confidence
            processed["confidence_score"] = self._calculate_adjusted_confidence(
                processed.get("confidence_score", 0.5),
                vendor_history
            )
            
            return {
                "success": True,
                "data": processed,
                "vendor_override_applied": processed.get("_vendor_override", False),
                "rules_applied": processed.get("_rules_applied", []),
                "validation_passed": True,
                "extraction_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Invoice extraction error: {e}")
            return self._create_failure_response(str(e))
    
    # ==================== PROMPT BUILDING ====================
    
    async def _build_extraction_prompt(
        self,
        ocr_text: str,
        tenant_id: str,
        company_context: Optional[Dict] = None
    ) -> str:
        """Build dynamic user prompt with context"""
        
        context = company_context or {}
        industry = context.get("industry", "general")
        currency = context.get("currency", "DKK")
        
        # Get vendor history if we can detect vendor from OCR
        vendor_history_section = ""
        # Try to extract vendor name from OCR for history lookup
        vendor_hint = await self._extract_vendor_hint(ocr_text)
        if vendor_hint:
            history = await self._get_vendor_history(tenant_id, vendor_hint)
            if history and history.get("usage_count", 0) >= 3:
                vendor_history_section = f"""
VENDOR HISTORY (HIGH CONFIDENCE - use this mapping):
Vendor Name: {history.get('vendor_name')}
Previous Account: {history.get('learned_account_code')} - {history.get('learned_account_name')}
Previous VAT Code: {history.get('learned_vat_code')}
Historical Accuracy: {history.get('accuracy_percent', 90)}%
Times Used: {history.get('usage_count')}
"""
        
        # Get custom company accounts/journals if configured
        company_accounts = await self._get_company_accounts(tenant_id)
        company_journals = await self._get_company_journals(tenant_id)
        
        prompt = f"""INVOICE OCR TEXT:
{ocr_text}

COMPANY CONTEXT:
Industry: {industry}
Currency: {currency}

CHART OF ACCOUNTS (use only these accounts):
{format_chart_for_prompt()}
{company_accounts}

VAT CODES (use only these codes):
{format_vat_codes_for_prompt()}

JOURNALS (use only these journals):
{format_journals_for_prompt()}
{company_journals}
{vendor_history_section}

Return JSON in this exact format:
{{
  "vendor_name": "",
  "cvr_number": "",
  "invoice_number": "",
  "invoice_date": "YYYY-MM-DD",
  "due_date": "YYYY-MM-DD",
  "currency": "{currency}",
  "net_amount": 0.00,
  "vat_amount": 0.00,
  "total_amount": 0.00,
  "vat_code": "",
  "suggested_account": "",
  "suggested_account_name": "",
  "journal": "KOB",
  "line_items": [],
  "confidence_score": 0.0,
  "notes": ""
}}"""
        
        return prompt
    
    async def _extract_vendor_hint(self, ocr_text: str) -> Optional[str]:
        """Try to extract vendor name from OCR text for history lookup"""
        # Simple heuristic: look for company-like patterns at the start
        lines = ocr_text.strip().split('\n')[:5]
        for line in lines:
            line = line.strip()
            if len(line) > 3 and len(line) < 100:
                # Skip obvious non-vendor lines
                if any(skip in line.lower() for skip in ['faktura', 'invoice', 'dato', 'date', 'total']):
                    continue
                return line
        return None
    
    async def _get_company_accounts(self, tenant_id: str) -> str:
        """Get custom company accounts if configured"""
        if tenant_id in self._account_cache:
            accounts = self._account_cache[tenant_id]
        else:
            custom = await self.db.company_accounts.find(
                {"tenant_id": tenant_id, "active": True},
                {"_id": 0}
            ).to_list(100)
            self._account_cache[tenant_id] = custom
            accounts = custom
        
        if accounts:
            lines = ["\nCOMPANY CUSTOM ACCOUNTS:"]
            for acc in accounts:
                lines.append(f"- {acc['code']}: {acc['name']}")
            return "\n".join(lines)
        return ""
    
    async def _get_company_journals(self, tenant_id: str) -> str:
        """Get custom company journals if configured"""
        custom = await self.db.company_journals.find(
            {"tenant_id": tenant_id, "active": True},
            {"_id": 0}
        ).to_list(20)
        
        if custom:
            lines = ["\nCOMPANY CUSTOM JOURNALS:"]
            for j in custom:
                lines.append(f"- {j['code']}: {j['name']}")
            return "\n".join(lines)
        return ""
    
    # ==================== AI CALL WITH RETRY ====================
    
    async def _call_ai_with_retry(self, prompt: str) -> Dict[str, Any]:
        """Call AI with retry logic and strict JSON parsing"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        last_error = None
        
        for attempt in range(AI_CONFIG["max_retries"] + 1):
            try:
                chat = LlmChat(
                    api_key=self.llm_key,
                    session_id=f"invoice-{uuid.uuid4()}",
                    system_message=SYSTEM_PROMPT
                ).with_model(AI_CONFIG["provider"], AI_CONFIG["model"])
                
                response = await chat.send_message(UserMessage(text=prompt))
                
                # Extract JSON from response
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group())
                        return {"success": True, "data": parsed}
                    except json.JSONDecodeError as e:
                        last_error = f"JSON parse error: {e}"
                        logger.warning(f"AI response JSON parse failed (attempt {attempt + 1}): {e}")
                else:
                    last_error = "No JSON found in response"
                    logger.warning(f"AI response contained no JSON (attempt {attempt + 1})")
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"AI call error (attempt {attempt + 1}): {e}")
        
        return {"success": False, "error": last_error}
    
    # ==================== SCHEMA VALIDATION ====================
    
    def _validate_response_schema(self, data: Dict) -> Dict[str, Any]:
        """Validate AI response against required schema"""
        errors = []
        
        # Required fields
        required_fields = [
            "vendor_name", "invoice_number", "net_amount", 
            "vat_amount", "total_amount", "suggested_account"
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate account code
        account = data.get("suggested_account", "")
        if account and not self._is_valid_account(account):
            errors.append(f"Invalid account code: {account}")
        
        # Validate VAT code
        vat_code = data.get("vat_code", "")
        if vat_code and not validate_vat_code(vat_code):
            errors.append(f"Invalid VAT code: {vat_code}")
        
        # Validate journal
        journal = data.get("journal", "KOB")
        if journal and not validate_journal_code(journal):
            errors.append(f"Invalid journal code: {journal}")
        
        # Validate amounts are numeric
        for amount_field in ["net_amount", "vat_amount", "total_amount"]:
            val = data.get(amount_field)
            if val is not None and not isinstance(val, (int, float)):
                try:
                    float(val)
                except (ValueError, TypeError):
                    errors.append(f"Non-numeric {amount_field}: {val}")
        
        # Validate confidence score
        confidence = data.get("confidence_score", 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            errors.append(f"Invalid confidence score: {confidence}")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _is_valid_account(self, code: str) -> bool:
        """Check if account code is valid (standard or custom)"""
        # Check standard accounts
        if validate_account_code(code):
            return True
        # Could also check custom accounts from cache
        return False
    
    # ==================== POST-PROCESSING RULES ====================
    
    async def _apply_post_processing(
        self,
        data: Dict,
        tenant_id: str,
        vendor_history: Optional[Dict],
        ocr_text: str
    ) -> Dict:
        """Apply post-processing rules: vendor override, VAT enforcement"""
        
        result = data.copy()
        result["_vendor_override"] = False
        
        # A. Vendor Override Logic
        if vendor_history and vendor_history.get("usage_count", 0) >= 3:
            # Override AI suggestion with learned pattern
            result["suggested_account"] = vendor_history.get("learned_account_code", result.get("suggested_account"))
            result["suggested_account_name"] = vendor_history.get("learned_account_name", result.get("suggested_account_name"))
            result["vat_code"] = vendor_history.get("learned_vat_code", result.get("vat_code"))
            result["_vendor_override"] = True
            result["_vendor_confidence_boost"] = True
            logger.info(f"Applied vendor override for {result.get('vendor_name')}")
        
        # B. VAT Enforcement Rules
        result = self._apply_vat_rules(result, ocr_text)
        
        # C. Ensure account name is set
        if result.get("suggested_account") and not result.get("suggested_account_name"):
            account_info = get_account_by_code(result["suggested_account"])
            if account_info:
                result["suggested_account_name"] = account_info["name"]
        
        # D. Default journal to KOB for purchases
        if not result.get("journal"):
            result["journal"] = "KOB"
        
        return result
    
    def _apply_vat_rules(self, data: Dict, ocr_text: str) -> Dict:
        """Apply Danish VAT enforcement rules"""
        result = data.copy()
        
        # Check for reverse charge
        if detect_reverse_charge(ocr_text):
            result["vat_code"] = "IREV"
            result["_vat_rule_applied"] = "reverse_charge"
            logger.info("Applied reverse charge VAT rule")
            return result
        
        # Standard Danish VAT (25%)
        vat_amount = float(result.get("vat_amount", 0) or 0)
        net_amount = float(result.get("net_amount", 0) or 0)
        
        if net_amount > 0 and vat_amount > 0:
            # Calculate effective VAT rate
            effective_rate = (vat_amount / net_amount) * 100
            
            # If approximately 25%, use standard input VAT
            if 23 <= effective_rate <= 27:
                if result.get("vat_code") not in ["I25", "IEU", "IREV"]:
                    result["vat_code"] = "I25"
                    result["_vat_rule_applied"] = "standard_dk_25"
        elif vat_amount == 0 and net_amount > 0:
            # No VAT - could be exempt or EU
            if not result.get("vat_code"):
                result["vat_code"] = "MOMSFRI"
                result["_vat_rule_applied"] = "zero_vat"
        
        return result
    
    # ==================== CONFIDENCE CALCULATION ====================
    
    def _calculate_adjusted_confidence(
        self,
        base_confidence: float,
        vendor_history: Optional[Dict]
    ) -> float:
        """Calculate adjusted confidence based on vendor history"""
        confidence = base_confidence
        
        if vendor_history:
            accuracy = vendor_history.get("accuracy_percent", 0)
            usage_count = vendor_history.get("usage_count", 0)
            
            # Boost confidence if vendor has high historical accuracy
            if accuracy > 90 and usage_count >= 3:
                confidence = min(1.0, confidence + 0.05)
            
            # Reduce confidence if vendor is frequently corrected
            correction_rate = vendor_history.get("correction_rate", 0)
            if correction_rate > 0.3:  # 30%+ corrections
                confidence = max(0.1, confidence - 0.1)
        
        return round(confidence, 2)
    
    # ==================== COMPANY CONFIGURATION ====================
    
    async def _get_company_rule_config(self, tenant_id: str) -> CompanyConfig:
        """Get company-specific rule configuration"""
        # Try to get custom config from database
        tenant = await self.db.tenants.find_one({"id": tenant_id}, {"_id": 0})
        
        if tenant and tenant.get("rule_config"):
            config_data = tenant["rule_config"]
            return CompanyConfig(
                asset_threshold_dkk=config_data.get("asset_threshold_dkk", 15000.0),
                enable_asset_detection=config_data.get("enable_asset_detection", True),
                default_currency=config_data.get("default_currency", "DKK"),
                country_code=config_data.get("country_code", "DK")
            )
        
        # Return default config
        return CompanyConfig()
    
    # ==================== VENDOR HISTORY ====================
    
    async def _get_vendor_history(self, tenant_id: str, vendor_name: Optional[str]) -> Optional[Dict]:
        """Get vendor history with accuracy stats"""
        if not vendor_name:
            return None
        
        cache_key = f"{tenant_id}:{vendor_name.lower()}"
        if cache_key in self._vendor_cache:
            return self._vendor_cache[cache_key]
        
        # Find vendor pattern
        pattern = await self.db.vendor_patterns.find_one({
            "tenant_id": tenant_id,
            "vendor_name": {"$regex": f"^{re.escape(vendor_name)}$", "$options": "i"}
        }, {"_id": 0})
        
        if pattern:
            # Calculate accuracy from correction history
            corrections = await self.db.ai_corrections.find({
                "tenant_id": tenant_id,
                "vendor_name": {"$regex": f"^{re.escape(vendor_name)}$", "$options": "i"}
            }).to_list(100)
            
            if corrections:
                correct_count = sum(1 for c in corrections if c.get("was_correct"))
                total_count = len(corrections)
                accuracy = (correct_count / total_count * 100) if total_count > 0 else 90
                correction_rate = 1 - (correct_count / total_count) if total_count > 0 else 0
                
                pattern["accuracy_percent"] = round(accuracy, 1)
                pattern["correction_rate"] = round(correction_rate, 2)
            else:
                pattern["accuracy_percent"] = 90
                pattern["correction_rate"] = 0
            
            self._vendor_cache[cache_key] = pattern
        
        return pattern
    
    # ==================== CORRECTION LEARNING ====================
    
    async def record_correction(
        self,
        tenant_id: str,
        document_id: str,
        vendor_name: str,
        ai_data: Dict,
        final_data: Dict,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Record AI correction for learning.
        After 3 consistent corrections, auto-update vendor default.
        """
        
        # Determine what was corrected
        ai_account = ai_data.get("suggested_account")
        final_account = final_data.get("account_code")
        ai_vat = ai_data.get("vat_code")
        final_vat = final_data.get("vat_code")
        
        was_correct = (ai_account == final_account and ai_vat == final_vat)
        
        # Store correction record
        correction = {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "document_id": document_id,
            "vendor_name": vendor_name,
            "ai_account": ai_account,
            "final_account": final_account,
            "ai_vat": ai_vat,
            "final_vat": final_vat,
            "ai_confidence": ai_data.get("confidence_score", 0),
            "was_correct": was_correct,
            "corrected_by": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.ai_corrections.insert_one(correction)
        
        # Clear vendor cache to force refresh
        cache_key = f"{tenant_id}:{vendor_name.lower()}"
        if cache_key in self._vendor_cache:
            del self._vendor_cache[cache_key]
        
        # Check if we should auto-update vendor default
        update_result = await self._check_auto_update_vendor(
            tenant_id, vendor_name, final_account, final_vat
        )
        
        # Update accuracy stats
        await self._update_accuracy_stats(tenant_id)
        
        return {
            "correction_id": correction["id"],
            "was_correct": was_correct,
            "vendor_default_updated": update_result.get("updated", False)
        }
    
    async def _check_auto_update_vendor(
        self,
        tenant_id: str,
        vendor_name: str,
        final_account: str,
        final_vat: str
    ) -> Dict[str, Any]:
        """Auto-update vendor default after 3 consistent corrections"""
        
        # Get last 5 corrections for this vendor
        corrections = await self.db.ai_corrections.find({
            "tenant_id": tenant_id,
            "vendor_name": {"$regex": f"^{re.escape(vendor_name)}$", "$options": "i"}
        }).sort("timestamp", -1).limit(5).to_list(5)
        
        if len(corrections) < 3:
            return {"updated": False, "reason": "insufficient_data"}
        
        # Check if last 3 corrections used the same account
        recent_accounts = [c.get("final_account") for c in corrections[:3]]
        recent_vats = [c.get("final_vat") for c in corrections[:3]]
        
        if len(set(recent_accounts)) == 1 and len(set(recent_vats)) == 1:
            # Consistent corrections - update vendor default
            consistent_account = recent_accounts[0]
            consistent_vat = recent_vats[0]
            
            account_info = get_account_by_code(consistent_account)
            account_name = account_info["name"] if account_info else "Unknown"
            
            await self.db.vendor_patterns.update_one(
                {
                    "tenant_id": tenant_id,
                    "vendor_name": {"$regex": f"^{re.escape(vendor_name)}$", "$options": "i"}
                },
                {
                    "$set": {
                        "learned_account_code": consistent_account,
                        "learned_account_name": account_name,
                        "learned_vat_code": consistent_vat,
                        "auto_learned": True,
                        "auto_learned_at": datetime.now(timezone.utc).isoformat()
                    },
                    "$inc": {"usage_count": 1}
                },
                upsert=True
            )
            
            logger.info(f"Auto-updated vendor default for {vendor_name}: {consistent_account}")
            
            return {
                "updated": True,
                "account": consistent_account,
                "vat": consistent_vat
            }
        
        return {"updated": False, "reason": "inconsistent_corrections"}
    
    async def _update_accuracy_stats(self, tenant_id: str):
        """Update global accuracy statistics"""
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "correct": {"$sum": {"$cond": ["$was_correct", 1, 0]}},
                "account_matches": {"$sum": {"$cond": [
                    {"$eq": ["$ai_account", "$final_account"]}, 1, 0
                ]}},
                "vat_matches": {"$sum": {"$cond": [
                    {"$eq": ["$ai_vat", "$final_vat"]}, 1, 0
                ]}}
            }}
        ]
        
        results = await self.db.ai_corrections.aggregate(pipeline).to_list(1)
        
        if results:
            r = results[0]
            total = r["total"]
            stats = {
                "tenant_id": tenant_id,
                "total_extractions": total,
                "overall_accuracy": round(r["correct"] / total * 100, 1) if total > 0 else 0,
                "account_accuracy": round(r["account_matches"] / total * 100, 1) if total > 0 else 0,
                "vat_accuracy": round(r["vat_matches"] / total * 100, 1) if total > 0 else 0,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.db.ai_stats.update_one(
                {"tenant_id": tenant_id},
                {"$set": stats},
                upsert=True
            )
    
    # ==================== HELPER METHODS ====================
    
    def _create_failure_response(self, error: str) -> Dict[str, Any]:
        """Create standardized failure response"""
        return {
            "success": False,
            "error": error,
            "data": None,
            "status": "ai_processing_failed",
            "extraction_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def clear_cache(self, tenant_id: Optional[str] = None):
        """Clear caches (call when accounts/journals updated)"""
        if tenant_id:
            if tenant_id in self._account_cache:
                del self._account_cache[tenant_id]
            # Clear vendor cache for this tenant
            keys_to_remove = [k for k in self._vendor_cache if k.startswith(f"{tenant_id}:")]
            for k in keys_to_remove:
                del self._vendor_cache[k]
        else:
            self._account_cache.clear()
            self._vendor_cache.clear()


# ==================== AI DASHBOARD STATS ====================

class AIAnalyticsService:
    """Service for AI dashboard analytics"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_dashboard_stats(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get AI accuracy and performance stats for admin dashboard"""
        
        match_stage = {"$match": {}}
        if tenant_id:
            match_stage["$match"]["tenant_id"] = tenant_id
        
        # Overall accuracy
        pipeline = [
            match_stage,
            {"$group": {
                "_id": None,
                "total_extractions": {"$sum": 1},
                "correct_extractions": {"$sum": {"$cond": ["$was_correct", 1, 0]}},
                "account_correct": {"$sum": {"$cond": [
                    {"$eq": ["$ai_account", "$final_account"]}, 1, 0
                ]}},
                "vat_correct": {"$sum": {"$cond": [
                    {"$eq": ["$ai_vat", "$final_vat"]}, 1, 0
                ]}},
                "avg_confidence": {"$avg": "$ai_confidence"}
            }}
        ]
        
        overall = await self.db.ai_corrections.aggregate(pipeline).to_list(1)
        
        # Most corrected accounts
        most_corrected_pipeline = [
            match_stage,
            {"$match": {"was_correct": False}},
            {"$group": {
                "_id": "$ai_account",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        most_corrected = await self.db.ai_corrections.aggregate(most_corrected_pipeline).to_list(10)
        
        # Vendor accuracy
        vendor_accuracy_pipeline = [
            match_stage,
            {"$group": {
                "_id": "$vendor_name",
                "total": {"$sum": 1},
                "correct": {"$sum": {"$cond": ["$was_correct", 1, 0]}}
            }},
            {"$project": {
                "vendor_name": "$_id",
                "total": 1,
                "accuracy": {"$multiply": [{"$divide": ["$correct", "$total"]}, 100]}
            }},
            {"$sort": {"total": -1}},
            {"$limit": 20}
        ]
        
        vendor_stats = await self.db.ai_corrections.aggregate(vendor_accuracy_pipeline).to_list(20)
        
        # Time saved estimate (5 minutes per invoice)
        total_docs = await self.db.documents.count_documents(
            {"tenant_id": tenant_id} if tenant_id else {}
        )
        time_saved_minutes = total_docs * 5
        
        stats = overall[0] if overall else {}
        total = stats.get("total_extractions", 0)
        
        return {
            "ai_accuracy_percent": round(stats.get("correct_extractions", 0) / total * 100, 1) if total > 0 else 0,
            "account_accuracy_percent": round(stats.get("account_correct", 0) / total * 100, 1) if total > 0 else 0,
            "vat_accuracy_percent": round(stats.get("vat_correct", 0) / total * 100, 1) if total > 0 else 0,
            "average_confidence_score": round(stats.get("avg_confidence", 0), 2),
            "total_extractions": total,
            "most_corrected_accounts": [
                {"account": m["_id"], "corrections": m["count"]}
                for m in most_corrected
            ],
            "vendor_accuracy": [
                {
                    "vendor": v.get("vendor_name", v.get("_id")),
                    "total": v["total"],
                    "accuracy": round(v["accuracy"], 1)
                }
                for v in vendor_stats
            ],
            "time_saved_hours": round(time_saved_minutes / 60, 1),
            "time_saved_estimate_per_invoice_minutes": 5,
            "error_rate_percent": round(100 - (stats.get("correct_extractions", 0) / total * 100), 1) if total > 0 else 0
        }


# ==================== ACTIVE COMPANY TRACKING ====================

class ActiveCompanyService:
    """Service for tracking active companies (for billing)"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def calculate_monthly_activity(self, year: int, month: int) -> List[Dict]:
        """Calculate which companies were active in a given month"""
        
        # Date range for the month
        from datetime import date
        import calendar
        
        start_date = date(year, month, 1).isoformat()
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day).isoformat() + "T23:59:59"
        
        # Find tenants with activity
        active_tenants = set()
        
        # Check for processed invoices
        invoice_activity = await self.db.documents.distinct(
            "tenant_id",
            {
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        )
        active_tenants.update(invoice_activity)
        
        # Check for pushed vouchers
        voucher_activity = await self.db.vouchers.distinct(
            "tenant_id",
            {
                "$or": [
                    {"created_at": {"$gte": start_date, "$lte": end_date}},
                    {"pushed_at": {"$gte": start_date, "$lte": end_date}}
                ]
            }
        )
        active_tenants.update(voucher_activity)
        
        # Get tenant details
        active_companies = []
        for tenant_id in active_tenants:
            tenant = await self.db.tenants.find_one({"id": tenant_id}, {"_id": 0})
            if tenant:
                # Count activity
                doc_count = await self.db.documents.count_documents({
                    "tenant_id": tenant_id,
                    "created_at": {"$gte": start_date, "$lte": end_date}
                })
                voucher_count = await self.db.vouchers.count_documents({
                    "tenant_id": tenant_id,
                    "created_at": {"$gte": start_date, "$lte": end_date}
                })
                
                active_companies.append({
                    "tenant_id": tenant_id,
                    "tenant_name": tenant.get("name"),
                    "owner_id": tenant.get("owner_id"),
                    "invoices_processed": doc_count,
                    "vouchers_created": voucher_count,
                    "is_active": True,
                    "period": f"{year}-{month:02d}"
                })
        
        # Store activity record
        activity_record = {
            "period": f"{year}-{month:02d}",
            "active_count": len(active_companies),
            "companies": active_companies,
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.monthly_activity.update_one(
            {"period": f"{year}-{month:02d}"},
            {"$set": activity_record},
            upsert=True
        )
        
        return active_companies
