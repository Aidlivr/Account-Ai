# Live OpenAI Integration for Invoice Processing
# Uses direct OpenAI API with structured JSON output, retry logic, and token tracking

import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from openai import AsyncOpenAI
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# ==================== OPENAI CONFIGURATION ====================

OPENAI_CONFIG = {
    "model": os.environ.get("OPENAI_MODEL", "gpt-4o"),
    "temperature": 0.1,
    "max_retries": 3,
    "max_tokens": 2000,
}

# ==================== SYSTEM PROMPT ====================

INVOICE_SYSTEM_PROMPT = """You are an expert Danish accounting assistant specialized in bookkeeping for companies using e-conomic.

Your task: Analyze invoice OCR text and return structured accounting data as JSON.

CRITICAL RULES:
1. Return ONLY valid JSON - no explanations, no markdown, no extra text.
2. Never invent account numbers - only use accounts from the provided list.
3. Only use VAT codes from the provided list.
4. If vendor history exists with 3+ uses, prioritize the historical mapping.
5. If uncertain about any field, set confidence_score lower (0.5-0.7).
6. Confidence must be between 0.0 and 1.0.
7. All amounts must be numeric (no currency symbols in the values).
8. Dates must be in YYYY-MM-DD format.
9. For Danish invoices, default currency is DKK unless explicitly stated otherwise.
10. Default journal is "KOB" for purchases."""

# ==================== LIVE OPENAI SERVICE ====================

class LiveOpenAIService:
    """Direct OpenAI API integration with structured JSON, retry logic, and token tracking"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set - AI extraction will fail")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        
    async def extract_invoice_data(
        self,
        prompt: str,
        invoice_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract invoice data using OpenAI with structured JSON output.
        
        Args:
            prompt: The full extraction prompt with OCR text and context
            invoice_id: Optional invoice ID for logging
            tenant_id: Optional tenant ID for logging
            
        Returns:
            Dict with success status, data, and token usage
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "data": None,
                "token_usage": None
            }
        
        last_error = None
        total_tokens_used = {"prompt": 0, "completion": 0, "total": 0}
        
        for attempt in range(OPENAI_CONFIG["max_retries"]):
            try:
                logger.info(f"OpenAI extraction attempt {attempt + 1}/{OPENAI_CONFIG['max_retries']} for invoice {invoice_id}")
                
                response = await self.client.chat.completions.create(
                    model=OPENAI_CONFIG["model"],
                    temperature=OPENAI_CONFIG["temperature"],
                    max_tokens=OPENAI_CONFIG["max_tokens"],
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": INVOICE_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Track token usage
                if response.usage:
                    total_tokens_used["prompt"] += response.usage.prompt_tokens
                    total_tokens_used["completion"] += response.usage.completion_tokens
                    total_tokens_used["total"] += response.usage.total_tokens
                
                # Parse response
                content = response.choices[0].message.content
                
                try:
                    parsed_data = json.loads(content)
                    
                    # Validate required fields exist
                    required_fields = ["vendor_name", "invoice_number", "net_amount", "total_amount"]
                    missing_fields = [f for f in required_fields if f not in parsed_data or parsed_data[f] is None]
                    
                    if missing_fields:
                        last_error = f"Missing required fields: {missing_fields}"
                        logger.warning(f"Attempt {attempt + 1}: {last_error}")
                        continue
                    
                    # Log token usage
                    await self._log_token_usage(
                        invoice_id=invoice_id,
                        tenant_id=tenant_id,
                        tokens=total_tokens_used,
                        model=OPENAI_CONFIG["model"],
                        success=True,
                        attempt=attempt + 1
                    )
                    
                    logger.info(f"Invoice {invoice_id} extracted successfully. Tokens: {total_tokens_used['total']}")
                    
                    return {
                        "success": True,
                        "data": parsed_data,
                        "token_usage": total_tokens_used,
                        "model": OPENAI_CONFIG["model"],
                        "attempts": attempt + 1
                    }
                    
                except json.JSONDecodeError as e:
                    last_error = f"JSON parse error: {e}"
                    logger.warning(f"Attempt {attempt + 1}: Malformed JSON response - {e}")
                    continue
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
                continue
        
        # All retries failed
        await self._log_token_usage(
            invoice_id=invoice_id,
            tenant_id=tenant_id,
            tokens=total_tokens_used,
            model=OPENAI_CONFIG["model"],
            success=False,
            attempt=OPENAI_CONFIG["max_retries"],
            error=last_error
        )
        
        logger.error(f"Invoice {invoice_id} extraction failed after {OPENAI_CONFIG['max_retries']} attempts: {last_error}")
        
        return {
            "success": False,
            "error": last_error,
            "data": None,
            "token_usage": total_tokens_used,
            "model": OPENAI_CONFIG["model"],
            "attempts": OPENAI_CONFIG["max_retries"]
        }
    
    async def _log_token_usage(
        self,
        invoice_id: Optional[str],
        tenant_id: Optional[str],
        tokens: Dict[str, int],
        model: str,
        success: bool,
        attempt: int,
        error: Optional[str] = None
    ):
        """Log token usage to database for cost monitoring"""
        
        # Estimate cost (GPT-4o pricing as of 2024: $2.50/1M input, $10/1M output)
        input_cost = (tokens["prompt"] / 1_000_000) * 2.50
        output_cost = (tokens["completion"] / 1_000_000) * 10.00
        total_cost = input_cost + output_cost
        
        usage_record = {
            "invoice_id": invoice_id,
            "tenant_id": tenant_id,
            "model": model,
            "prompt_tokens": tokens["prompt"],
            "completion_tokens": tokens["completion"],
            "total_tokens": tokens["total"],
            "estimated_cost_usd": round(total_cost, 6),
            "success": success,
            "attempts": attempt,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            await self.db.ai_token_usage.insert_one(usage_record)
        except Exception as e:
            logger.error(f"Failed to log token usage: {e}")
    
    async def get_usage_stats(
        self,
        tenant_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get token usage statistics for cost monitoring"""
        
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        match_stage = {"timestamp": {"$gte": cutoff}}
        if tenant_id:
            match_stage["tenant_id"] = tenant_id
        
        pipeline = [
            {"$match": match_stage},
            {"$group": {
                "_id": None,
                "total_requests": {"$sum": 1},
                "successful_requests": {"$sum": {"$cond": ["$success", 1, 0]}},
                "total_prompt_tokens": {"$sum": "$prompt_tokens"},
                "total_completion_tokens": {"$sum": "$completion_tokens"},
                "total_tokens": {"$sum": "$total_tokens"},
                "total_cost_usd": {"$sum": "$estimated_cost_usd"},
                "avg_tokens_per_invoice": {"$avg": "$total_tokens"},
                "avg_attempts": {"$avg": "$attempts"}
            }}
        ]
        
        results = await self.db.ai_token_usage.aggregate(pipeline).to_list(1)
        
        if results:
            r = results[0]
            return {
                "period_days": days,
                "total_requests": r.get("total_requests", 0),
                "successful_requests": r.get("successful_requests", 0),
                "success_rate_percent": round(r.get("successful_requests", 0) / max(r.get("total_requests", 1), 1) * 100, 1),
                "total_prompt_tokens": r.get("total_prompt_tokens", 0),
                "total_completion_tokens": r.get("total_completion_tokens", 0),
                "total_tokens": r.get("total_tokens", 0),
                "total_cost_usd": round(r.get("total_cost_usd", 0), 4),
                "avg_tokens_per_invoice": round(r.get("avg_tokens_per_invoice", 0), 0),
                "avg_attempts_per_request": round(r.get("avg_attempts", 1), 2),
                "model": OPENAI_CONFIG["model"]
            }
        
        return {
            "period_days": days,
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost_usd": 0,
            "model": OPENAI_CONFIG["model"]
        }


# ==================== DAILY/MONTHLY AGGREGATION ====================

async def aggregate_daily_usage(db: AsyncIOMotorDatabase, date_str: str) -> Dict[str, Any]:
    """Aggregate token usage for a specific day"""
    
    pipeline = [
        {"$match": {
            "timestamp": {"$regex": f"^{date_str}"}
        }},
        {"$group": {
            "_id": "$tenant_id",
            "invoices_processed": {"$sum": 1},
            "successful": {"$sum": {"$cond": ["$success", 1, 0]}},
            "total_tokens": {"$sum": "$total_tokens"},
            "total_cost_usd": {"$sum": "$estimated_cost_usd"}
        }}
    ]
    
    results = await db.ai_token_usage.aggregate(pipeline).to_list(100)
    
    daily_summary = {
        "date": date_str,
        "by_tenant": results,
        "totals": {
            "invoices_processed": sum(r["invoices_processed"] for r in results),
            "successful": sum(r["successful"] for r in results),
            "total_tokens": sum(r["total_tokens"] for r in results),
            "total_cost_usd": round(sum(r["total_cost_usd"] for r in results), 4)
        }
    }
    
    return daily_summary
