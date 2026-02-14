# AI Accounting Copilot - Product Requirements Document

## Version: 2.2.0-beta (Production AI Architecture Complete)
## Last Updated: Feb 14, 2026

## Original Problem Statement
Build an AI Accounting Copilot SaaS with modular architecture for Danish SMEs and accountants. Focus on:
- Upload invoice → AI extraction → Review → Approve → Voucher creation → Activity logging
- Integration-ready architecture for e-conomic (live credentials pending)
- Production-grade AI with vendor learning, validation, and Nordic expansion readiness

## Architecture

### Tech Stack
- **Frontend:** React 19 + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend:** FastAPI (Python) v2.2.0-beta
- **Database:** MongoDB
- **AI:** OpenAI GPT-5.2 via Emergent LLM Key (Production AI Service)
- **OCR:** Tesseract (local)
- **Payments:** Stripe (admin-activated, live integration pending)
- **Accounting:** e-conomic (integration-ready, credentials pending)
- **Email:** MockEmailService (logs to DB, SendGrid pending)

### Code Architecture
```
/app
├── backend/
│   ├── server.py              # Main FastAPI app (~2900 lines)
│   ├── ai_production.py       # Production AI Service (NEW)
│   ├── danish_accounting.py   # Chart of Accounts, VAT, Journals (NEW)
│   ├── vat_rules.py           # Nordic VAT Rules Module (NEW)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── ai-dashboard/  # AI Performance Dashboard (NEW)
│       │   ├── auth/
│       │   ├── dashboard/
│       │   ├── documents/
│       │   ├── vouchers/
│       │   └── admin/
│       └── components/
│           ├── beta/          # BetaBanner, FeedbackDialog
│           ├── export/        # ExportButton
│           └── layout/
```

## Completed Phases

### ✅ Phase 1-4 - MVP & Beta Ready (Previous)
- Authentication, Multi-tenancy, Document processing
- Draft voucher engine, Activity logging
- Vendor learning, Billing structure

### ✅ Phase 5 - Beta Activation (Previous)
- Beta Mode UI Banner
- Feedback System
- Data Export (CSV/PDF)
- Mock Email Notifications

### ✅ Phase 6 - Production AI Architecture (Feb 14, 2026)

#### 6.1 AI Request Structure
- Temperature: 0.1-0.2 for consistent output
- Strict JSON-only responses
- Automatic retry on malformed responses
- Structured prompts with company context

#### 6.2 Danish Accounting Data
- **Chart of Accounts:** 73 standard Danish accounts (kontoplan)
  - Assets (1000-1999): 10 accounts
  - Liabilities (2000-2999): 10 accounts
  - Revenue (3000-3999): 5 accounts
  - COGS (4000-4999): 5 accounts
  - Personnel (5000-5999): 6 accounts
  - Operating Expenses (6000-6999): 18 accounts
  - Other Operating (7000-7999): 8 accounts
  - Depreciation/Financial (8000-8999): 7 accounts
  - VAT/Tax (9000-9999): 4 accounts

- **VAT Codes:** 10 Danish VAT codes
  - Input: I25, I0, IEU (EU), IREV (Reverse Charge)
  - Output: U25, U0, UEU, UEXP
  - Special: MOMSFRI, IKKEMOMS

- **Journals:** 8 standard journals
  - KOB, SALG, BANK, KASSE, LON, AFSKR, PRIMO, DIV

#### 6.3 Post-Processing Rule Engine
- Schema validation (required fields, account/VAT code verification)
- Vendor Override Logic (auto-apply after 3+ consistent uses)
- VAT Enforcement Rules:
  - Reverse charge keyword detection
  - EU acquisition detection
  - Standard 25% Danish VAT enforcement
- Confidence adjustment based on vendor history

#### 6.4 Correction Learning System
- Tracks AI vs final values for every approval
- Updates vendor defaults after 3 consistent corrections
- Calculates accuracy percentages (account, VAT, overall)

#### 6.5 Active Company Tracking
- Tracks monthly activity for billing
- Active = at least 1 invoice processed OR 1 voucher pushed

#### 6.6 Admin AI Dashboard
- Overall AI Accuracy %
- Account Accuracy %
- VAT Accuracy %
- Average Confidence Score
- Total Extractions
- Error Rate %
- Time Saved (hours)
- Most Corrected Accounts
- Vendor Accuracy Breakdown

#### 6.7 Nordic VAT Module (Future-Ready)
- Modular VATRuleEngine interface
- DK (Denmark): ACTIVE - 25% standard rate
- SE (Sweden): PREPARED - 25%, 12%, 6% rates
- NO (Norway): PREPARED - 25%, 15%, 12% rates

## API Endpoints (v2.2.0-beta)

### Accounting Data (NEW)
- GET /api/accounting-data/chart-of-accounts
- GET /api/accounting-data/vat-codes
- GET /api/accounting-data/journals
- GET /api/accounting-data/available-countries
- POST /api/accounting-data/company/{tenant_id}/custom-accounts
- POST /api/accounting-data/company/{tenant_id}/custom-journals

### AI Dashboard (NEW)
- GET /api/ai-dashboard/stats
- GET /api/ai-dashboard/corrections
- GET /api/ai-dashboard/vendor-accuracy/{tenant_id}
- GET /api/ai-dashboard/active-companies/{year}/{month}

### Previous Endpoints (Auth, Tenants, Documents, Vouchers, etc.)
- All previous endpoints remain functional

## New Database Collections

### ai_corrections
```json
{
  "id": "uuid",
  "tenant_id": "string",
  "document_id": "string",
  "vendor_name": "string",
  "ai_account": "string",
  "final_account": "string",
  "ai_vat": "string",
  "final_vat": "string",
  "ai_confidence": "float",
  "was_correct": "boolean",
  "corrected_by": "string",
  "timestamp": "datetime"
}
```

### ai_stats
```json
{
  "tenant_id": "string",
  "total_extractions": "int",
  "overall_accuracy": "float",
  "account_accuracy": "float",
  "vat_accuracy": "float",
  "updated_at": "datetime"
}
```

### monthly_activity
```json
{
  "period": "YYYY-MM",
  "active_count": "int",
  "companies": [{"tenant_id", "invoices_processed", "vouchers_created"}],
  "calculated_at": "datetime"
}
```

## Test Results (Latest - iteration_4.json)

- **Backend:** 100% (17/17 tests passed)
- **Frontend:** 100% (all AI Dashboard UI components working)
- **Version:** 2.2.0-beta
- **Test Users:** admin@aiaccounting.dk / admin123, betatest@example.dk / test123

## MOCKED Integrations (By Design)

1. **Email Notifications:** MockEmailService logs to db.email_logs
2. **Stripe Payments:** Admin manually activates subscriptions
3. **e-conomic API:** Integration-ready placeholder structure

## Next Steps

### P0 - Required for Production
1. Live Stripe webhooks integration
2. Real e-conomic API connection
3. SendGrid email integration
4. Invoice processing with real OCR + AI (currently uses simulation)

### P1 - High Priority
1. Bank transaction import (CSV/OFX)
2. PDF report generation for VAT
3. Advanced reconciliation algorithms

### P2 - Medium Priority
1. Activate Swedish VAT rules
2. Activate Norwegian VAT rules
3. OAuth login (Google, Microsoft)

### P3 - Nice to Have
1. Danish language support (UI)
2. Mobile responsive improvements
3. Extended export options (Excel)

## Definition of Done (Production AI)

✅ AI returns structured JSON reliably
✅ No hallucinated accounts (validated against chart)
✅ Vendor learning overrides function correctly
✅ Confidence score reflects correction history
✅ Error rate tracking implemented
⏳ 50 mixed invoices tested successfully (pending real invoice data)
