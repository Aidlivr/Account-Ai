#!/usr/bin/env python3
"""
Invoice Extraction Evaluation Script
Runs the 50-invoice test suite and generates comprehensive accuracy reports.
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# Import test data
from tests.invoice_test_suite_data import REALISTIC_INVOICES
from tests.invoice_test_suite_edge_cases import EDGE_CASE_INVOICES

# Import production AI service
from ai_production import ProductionAIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== EVALUATION METRICS ====================

class EvaluationMetrics:
    """Tracks and calculates evaluation metrics"""
    
    def __init__(self):
        self.total_invoices = 0
        self.processed_invoices = 0
        self.failed_invoices = 0
        
        # Field-level tracking
        self.field_results: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            "correct": 0, "incorrect": 0, "missing": 0
        })
        
        # Error severity tracking
        self.errors: Dict[str, List[Dict]] = {
            "critical": [],
            "major": [],
            "minor": []
        }
        
        # VAT code confusion matrix
        self.vat_confusion: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Account confusion matrix
        self.account_confusion: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Vendor correction tracking
        self.vendor_corrections: Dict[str, List[Dict]] = defaultdict(list)
        
        # Needs review tracking
        self.needs_review: List[Dict] = []
        
        # Per-invoice results
        self.invoice_results: List[Dict] = []
    
    def add_result(self, invoice_id: str, ground_truth: Dict, extracted: Dict, 
                   success: bool, category: str, edge_type: Optional[str] = None):
        """Add a single invoice evaluation result"""
        self.total_invoices += 1
        
        if not success:
            self.failed_invoices += 1
            self.errors["critical"].append({
                "invoice_id": invoice_id,
                "error": "AI extraction failed",
                "category": category
            })
            return
        
        self.processed_invoices += 1
        
        result = {
            "invoice_id": invoice_id,
            "category": category,
            "edge_type": edge_type,
            "field_accuracy": {},
            "errors": [],
            "needs_review": False
        }
        
        # Evaluate each field
        fields_to_check = [
            ("vendor_name", "minor", self._compare_string),
            ("cvr_number", "major", self._compare_cvr),
            ("invoice_number", "major", self._compare_string),
            ("invoice_date", "major", self._compare_date),
            ("due_date", "minor", self._compare_date),
            ("currency", "minor", self._compare_string),
            ("net_amount", "critical", self._compare_amount),
            ("vat_amount", "critical", self._compare_amount),
            ("total_amount", "critical", self._compare_amount),
            ("vat_code", "major", self._compare_string),
            ("suggested_account", "major", self._compare_account),
            ("journal", "minor", self._compare_string),
        ]
        
        for field, severity, compare_func in fields_to_check:
            gt_value = ground_truth.get(field)
            ex_value = extracted.get(field)
            
            is_correct, error_msg = compare_func(gt_value, ex_value, field)
            
            if gt_value is None and ex_value is None:
                # Both missing - not an error
                continue
            elif gt_value is None:
                self.field_results[field]["missing"] += 1
            elif is_correct:
                self.field_results[field]["correct"] += 1
                result["field_accuracy"][field] = True
            else:
                self.field_results[field]["incorrect"] += 1
                result["field_accuracy"][field] = False
                
                error_detail = {
                    "invoice_id": invoice_id,
                    "field": field,
                    "expected": gt_value,
                    "actual": ex_value,
                    "message": error_msg
                }
                
                self.errors[severity].append(error_detail)
                result["errors"].append(error_detail)
                
                # Track vendor corrections
                vendor = ground_truth.get("vendor_name", "Unknown")
                self.vendor_corrections[vendor].append(error_detail)
                
                # Track VAT confusion
                if field == "vat_code":
                    self.vat_confusion[str(gt_value)][str(ex_value)] += 1
                
                # Track account confusion
                if field == "suggested_account":
                    self.account_confusion[str(gt_value)][str(ex_value)] += 1
        
        # Check if needs review (low confidence or critical errors)
        confidence = extracted.get("confidence_score", 0)
        if confidence < 0.7 or any(e["field"] in ["net_amount", "vat_amount", "total_amount"] 
                                   for e in result["errors"]):
            result["needs_review"] = True
            self.needs_review.append(result)
        
        self.invoice_results.append(result)
    
    def _compare_string(self, expected: Any, actual: Any, field: str) -> Tuple[bool, str]:
        """Compare string values with normalization"""
        if expected is None:
            return actual is None, f"Expected None, got {actual}"
        
        exp_str = str(expected).lower().strip()
        act_str = str(actual).lower().strip() if actual else ""
        
        # Exact match
        if exp_str == act_str:
            return True, ""
        
        # Fuzzy match for vendor names (allow partial)
        if field == "vendor_name" and (exp_str in act_str or act_str in exp_str):
            return True, ""
        
        return False, f"Expected '{expected}', got '{actual}'"
    
    def _compare_account(self, expected: Any, actual: Any, field: str) -> Tuple[bool, str]:
        """Compare account codes with category tolerance"""
        if expected is None:
            return actual is None, f"Expected None, got {actual}"
        
        exp_str = str(expected).strip()
        act_str = str(actual).strip() if actual else ""
        
        # Exact match
        if exp_str == act_str:
            return True, ""
        
        # Same first 2 digits = same account category (considered acceptable)
        # E.g., 6310 IT-udgifter vs 6320 Software are both IT expenses
        if len(exp_str) >= 2 and len(act_str) >= 2:
            if exp_str[:2] == act_str[:2]:
                return True, ""  # Same category - acceptable
        
        # Related categories that are often interchangeable
        related_pairs = [
            ("6310", "6320"),  # IT vs Software
            ("6320", "6310"),
            ("6000", "6010"),  # Lokale vs Husleje
            ("6010", "6000"),
            ("7200", "7300"),  # Advokat/revisor vs Konsulent
            ("7300", "7200"),
            ("4000", "4100"),  # Varekøb vs Varekøb EU
            ("4100", "4000"),
            ("4300", "6200"),  # Fremmed arbejde vs Vedligeholdelse (both maintenance)
            ("6200", "4300"),
        ]
        
        if (exp_str, act_str) in related_pairs:
            return True, ""
        
        return False, f"Expected account '{expected}', got '{actual}'"
    
    def _compare_cvr(self, expected: Any, actual: Any, field: str) -> Tuple[bool, str]:
        """Compare CVR numbers with normalization"""
        if expected is None:
            return actual is None, f"Expected None, got {actual}"
        
        # Normalize: remove spaces, dashes, country prefixes
        def normalize_cvr(val):
            if val is None:
                return None
            s = str(val).upper().replace(" ", "").replace("-", "")
            # Remove country prefixes
            for prefix in ["DK", "DE", "SE", "NO", "VAT"]:
                if s.startswith(prefix):
                    s = s[len(prefix):]
            return s
        
        exp_norm = normalize_cvr(expected)
        act_norm = normalize_cvr(actual)
        
        if exp_norm == act_norm:
            return True, ""
        
        return False, f"Expected CVR '{expected}', got '{actual}'"
    
    def _compare_date(self, expected: Any, actual: Any, field: str) -> Tuple[bool, str]:
        """Compare dates with format flexibility"""
        if expected is None:
            return actual is None, f"Expected None, got {actual}"
        
        if actual is None:
            return False, f"Expected '{expected}', got None"
        
        # Try to parse both dates to YYYY-MM-DD format
        def parse_date(val):
            if isinstance(val, str):
                # Already in ISO format
                if len(val) >= 10 and val[4] == '-':
                    return val[:10]
                # Danish format DD-MM-YYYY
                if len(val) >= 10 and val[2] == '-':
                    parts = val.split('-')
                    if len(parts) == 3:
                        return f"{parts[2]}-{parts[1]}-{parts[0]}"
            return str(val)[:10]
        
        exp_parsed = parse_date(expected)
        act_parsed = parse_date(actual)
        
        if exp_parsed == act_parsed:
            return True, ""
        
        return False, f"Expected date '{expected}', got '{actual}'"
    
    def _compare_amount(self, expected: Any, actual: Any, field: str) -> Tuple[bool, str]:
        """Compare monetary amounts with tolerance"""
        if expected is None:
            return actual is None, f"Expected None, got {actual}"
        
        try:
            exp_val = float(expected)
            act_val = float(actual) if actual is not None else 0.0
            
            # Allow small rounding differences (0.01 tolerance or 0.1%)
            tolerance = max(0.01, abs(exp_val) * 0.001)
            
            if abs(exp_val - act_val) <= tolerance:
                return True, ""
            
            return False, f"Expected amount {exp_val:.2f}, got {act_val:.2f}"
        except (ValueError, TypeError) as e:
            return False, f"Amount comparison error: {e}"
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive evaluation report"""
        
        # Calculate field-level accuracy
        field_accuracy = {}
        for field, counts in self.field_results.items():
            total = counts["correct"] + counts["incorrect"]
            accuracy = (counts["correct"] / total * 100) if total > 0 else 0
            field_accuracy[field] = {
                "accuracy_percent": round(accuracy, 2),
                "correct": counts["correct"],
                "incorrect": counts["incorrect"],
                "missing": counts["missing"]
            }
        
        # Overall accuracy
        total_fields = sum(c["correct"] + c["incorrect"] for c in self.field_results.values())
        correct_fields = sum(c["correct"] for c in self.field_results.values())
        overall_accuracy = (correct_fields / total_fields * 100) if total_fields > 0 else 0
        
        # Critical field accuracy (amounts)
        critical_fields = ["net_amount", "vat_amount", "total_amount"]
        critical_correct = sum(self.field_results[f]["correct"] for f in critical_fields)
        critical_total = sum(self.field_results[f]["correct"] + self.field_results[f]["incorrect"] 
                           for f in critical_fields)
        critical_accuracy = (critical_correct / critical_total * 100) if critical_total > 0 else 0
        
        # Top vendors causing corrections
        vendor_error_counts = [
            (vendor, len(errors)) 
            for vendor, errors in self.vendor_corrections.items()
        ]
        vendor_error_counts.sort(key=lambda x: x[1], reverse=True)
        top_10_vendors = vendor_error_counts[:10]
        
        # VAT confusion matrix
        vat_confusion_report = {}
        for expected, actuals in self.vat_confusion.items():
            vat_confusion_report[expected] = dict(actuals)
        
        # Account confusion matrix
        account_confusion_report = {}
        for expected, actuals in self.account_confusion.items():
            account_confusion_report[expected] = dict(actuals)
        
        report = {
            "summary": {
                "total_invoices": self.total_invoices,
                "processed_successfully": self.processed_invoices,
                "failed_processing": self.failed_invoices,
                "success_rate_percent": round(self.processed_invoices / self.total_invoices * 100, 2) if self.total_invoices > 0 else 0,
                "overall_field_accuracy_percent": round(overall_accuracy, 2),
                "critical_field_accuracy_percent": round(critical_accuracy, 2),
                "needs_review_count": len(self.needs_review),
                "needs_review_percent": round(len(self.needs_review) / self.total_invoices * 100, 2) if self.total_invoices > 0 else 0,
            },
            "field_level_accuracy": field_accuracy,
            "error_counts": {
                "critical": len(self.errors["critical"]),
                "major": len(self.errors["major"]),
                "minor": len(self.errors["minor"]),
                "total": sum(len(e) for e in self.errors.values())
            },
            "error_details": {
                "critical": self.errors["critical"][:20],  # Limit for readability
                "major": self.errors["major"][:20],
                "minor": self.errors["minor"][:10]
            },
            "vat_confusion_matrix": vat_confusion_report,
            "account_confusion_matrix": account_confusion_report,
            "top_10_vendors_with_corrections": [
                {"vendor": v, "correction_count": c} for v, c in top_10_vendors
            ],
            "needs_review_invoices": [
                {"invoice_id": r["invoice_id"], "category": r["category"], "errors": len(r["errors"])}
                for r in self.needs_review
            ],
            "by_category": {
                "realistic": self._get_category_stats("realistic"),
                "edge_case": self._get_category_stats("edge_case")
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0"
        }
        
        return report
    
    def _get_category_stats(self, category: str) -> Dict[str, Any]:
        """Get stats for a specific category"""
        category_results = [r for r in self.invoice_results if r["category"] == category]
        
        if not category_results:
            return {"count": 0, "accuracy": 0}
        
        total_fields = 0
        correct_fields = 0
        
        for result in category_results:
            for field, is_correct in result["field_accuracy"].items():
                total_fields += 1
                if is_correct:
                    correct_fields += 1
        
        return {
            "count": len(category_results),
            "field_accuracy_percent": round(correct_fields / total_fields * 100, 2) if total_fields > 0 else 0,
            "errors_total": sum(len(r["errors"]) for r in category_results),
            "needs_review": sum(1 for r in category_results if r["needs_review"])
        }


# ==================== EVALUATION RUNNER ====================

class InvoiceEvaluationRunner:
    """Runs the evaluation suite"""
    
    def __init__(self, db_url: str, db_name: str, llm_key: str):
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]
        self.llm_key = llm_key
        self.metrics = EvaluationMetrics()
        self.ai_service: Optional[ProductionAIService] = None
    
    async def initialize(self):
        """Initialize AI service"""
        self.ai_service = ProductionAIService(self.db, self.llm_key)
        logger.info("AI service initialized")
    
    async def run_evaluation(self, invoices: List[Dict], tenant_id: str = "test-tenant"):
        """Run evaluation on all invoices"""
        logger.info(f"Starting evaluation of {len(invoices)} invoices")
        
        for i, invoice in enumerate(invoices):
            invoice_id = invoice["id"]
            ocr_text = invoice["ocr_text"]
            ground_truth = invoice["ground_truth"]
            category = invoice.get("category", "unknown")
            edge_type = invoice.get("edge_type")
            
            logger.info(f"Processing invoice {i+1}/{len(invoices)}: {invoice_id}")
            
            try:
                # Extract using production AI
                result = await self.ai_service.extract_invoice_data(
                    ocr_text=ocr_text,
                    tenant_id=tenant_id,
                    company_context={"industry": "general", "currency": "DKK"}
                )
                
                if result["success"]:
                    extracted = result["data"]
                    self.metrics.add_result(
                        invoice_id=invoice_id,
                        ground_truth=ground_truth,
                        extracted=extracted,
                        success=True,
                        category=category,
                        edge_type=edge_type
                    )
                else:
                    self.metrics.add_result(
                        invoice_id=invoice_id,
                        ground_truth=ground_truth,
                        extracted={},
                        success=False,
                        category=category,
                        edge_type=edge_type
                    )
                    logger.warning(f"Invoice {invoice_id} failed: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error processing invoice {invoice_id}: {e}")
                self.metrics.add_result(
                    invoice_id=invoice_id,
                    ground_truth=ground_truth,
                    extracted={},
                    success=False,
                    category=category,
                    edge_type=edge_type
                )
        
        return self.metrics.generate_report()
    
    async def close(self):
        """Close database connection"""
        self.client.close()


# ==================== MAIN EXECUTION ====================

async def main():
    """Main evaluation runner"""
    
    # Get configuration
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'ai_accounting_copilot')
    
    # Check for API keys - prefer OPENAI_API_KEY for live testing
    openai_key = os.environ.get('OPENAI_API_KEY', '')
    llm_key = os.environ.get('EMERGENT_LLM_KEY', '')
    
    if openai_key:
        logger.info("Using LIVE OpenAI API for evaluation")
        logger.info(f"Model: {os.environ.get('OPENAI_MODEL', 'gpt-4o')}")
    elif llm_key:
        logger.info("Using Emergent LLM integration for evaluation")
    else:
        logger.error("No API key found (OPENAI_API_KEY or EMERGENT_LLM_KEY)")
        return
    
    # Initialize runner
    runner = InvoiceEvaluationRunner(mongo_url, db_name, llm_key)
    
    try:
        await runner.initialize()
        
        # Combine all invoices
        all_invoices = REALISTIC_INVOICES + EDGE_CASE_INVOICES
        logger.info(f"Total invoices to evaluate: {len(all_invoices)}")
        
        # Run evaluation
        report = await runner.run_evaluation(all_invoices)
        
        # Add token usage summary if using live OpenAI
        if openai_key:
            from openai_live import LiveOpenAIService
            live_service = LiveOpenAIService(runner.db)
            token_stats = await live_service.get_usage_stats(days=1)
            report["token_usage"] = token_stats
        
        # Save report
        report_path = Path(__file__).parent.parent / "test_reports" / "invoice_evaluation_report.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Report saved to: {report_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("INVOICE EXTRACTION EVALUATION REPORT")
        print("="*60)
        print(f"\nTotal Invoices: {report['summary']['total_invoices']}")
        print(f"Successfully Processed: {report['summary']['processed_successfully']}")
        print(f"Failed: {report['summary']['failed_processing']}")
        print(f"\nOverall Field Accuracy: {report['summary']['overall_field_accuracy_percent']}%")
        print(f"Critical Field Accuracy: {report['summary']['critical_field_accuracy_percent']}%")
        print(f"\nNeeds Review: {report['summary']['needs_review_count']} ({report['summary']['needs_review_percent']}%)")
        print(f"\nError Counts:")
        print(f"  Critical: {report['error_counts']['critical']}")
        print(f"  Major: {report['error_counts']['major']}")
        print(f"  Minor: {report['error_counts']['minor']}")
        
        if report['top_10_vendors_with_corrections']:
            print(f"\nTop Vendors Causing Corrections:")
            for v in report['top_10_vendors_with_corrections'][:5]:
                print(f"  - {v['vendor']}: {v['correction_count']} corrections")
        
        print("\n" + "="*60)
        
        return report
        
    finally:
        await runner.close()


if __name__ == "__main__":
    asyncio.run(main())
