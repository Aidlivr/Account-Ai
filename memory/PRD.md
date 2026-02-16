# AI Accounting Copilot - Product Requirements Document

## Version: 2.5.0-beta (Landing Page Complete)
## Last Updated: Feb 16, 2026

## What's New in v2.5.0

### Professional Landing Page (Completed)
A fully functional, European-style B2B landing page has been built for the AI Accounting Copilot (branded as "Accountrix"). The landing page is designed to attract Danish and European accounting firms to the beta program.

#### Sections Implemented:
1. **Hero Section** - Value proposition with mock invoice review queue
2. **Problem Section** - 6 pain points addressed
3. **Solution Section** - 6-step workflow diagram
4. **Features Section** - 6 key features with icons
5. **Validation Results** - AI accuracy metrics display
6. **Security Section** - Compliance and data security focus
7. **Pricing Section** - 399 DKK/month base + 69 DKK per company
8. **Beta Invitation Form** - Full backend integration
9. **Footer** - Contact and legal links

#### Backend Integration:
- New `/api/beta/request-access` endpoint (public, no auth required)
- Beta requests stored in `beta_requests` MongoDB collection
- Duplicate submission detection
- Admin endpoints for viewing/managing requests
- Mock email notifications for new requests

---

## 50-Invoice Baseline Test Results (Previous Phase)

### Summary vs Targets
| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Account Accuracy | ≥85% | **88.0%** | ✅ **Passed** |
| Error Rate | <4% | **2.17%** | ✅ **Passed** |
| Needs Review | ≤10% | **12.0%** | ⚠️ Acceptable* |
| Overall Accuracy | - | **97.83%** | ✅ |
| Critical Accuracy | - | **98.0%** | ✅ |

*Needs Review at 12% is driven by complex edge cases (pro forma, leasing, EU reverse charge) which correctly trigger safety reviews.

### Field-Level Accuracy
| Field | Accuracy | Notes |
|-------|----------|-------|
| vendor_name | 100.0% | Perfect extraction |
| invoice_number | 100.0% | Perfect extraction |
| invoice_date | 100.0% | Perfect extraction |
| net_amount | 98.0% | 1 edge case error |
| vat_amount | 98.0% | 1 edge case error |
| total_amount | 98.0% | 1 edge case error |
| currency | 100.0% | Fixed by rule engine |
| vat_code | 98.0% | Fixed by MOMSFRI rules |
| cvr_number | 97.96% | 1 missing CVR |
| due_date | 98.0% | 1 edge case |
| suggested_account | 88.0% | Improved from 70% |
| journal | 98.0% | Fixed by cash/bank rules |

---

## Architecture

### Processing Pipeline
```
1. OCR Text → 
2. AI Extraction (GPT-5.2, temp 0.1-0.2) →
3. Schema Validation →
4. Vendor Override (3+ corrections) →
5. VAT Enforcement Rules →
6. Deterministic Rule Engine →
7. Confidence Adjustment →
8. Final Result
```

### Key Files
```
/app
├── backend/
│   ├── server.py                 # Main FastAPI app with beta router
│   ├── ai_production.py          # Production AI service
│   ├── danish_accounting.py      # Chart of accounts, VAT codes
│   ├── rule_engine.py            # Deterministic rule engine
│   ├── vat_rules.py              # Modular VAT logic
│   └── tests/
│       ├── invoice_test_suite_data.py
│       ├── invoice_test_suite_edge_cases.py
│       └── run_invoice_evaluation.py
├── frontend/
│   └── src/
│       ├── App.js                # Main router
│       ├── pages/
│       │   └── landing/LandingPage.jsx  # Professional landing page
│       └── components/
│           └── beta/             # BetaBanner, FeedbackDialog
└── memory/
    └── PRD.md
```

---

## Completed Features

### Phase 1: Beta-Ready MVP ✅
- Multi-tenant authentication (SME, Accountant, Admin roles)
- Document upload and management
- AI-powered invoice extraction
- Voucher creation workflow
- Basic dashboard

### Phase 2: Production AI Architecture ✅
- Deterministic rule engine
- Vendor learning system
- Danish VAT rules implementation
- 50-invoice test suite
- AI accuracy dashboard

### Phase 3: Beta Activation ✅
- Site-wide beta banner
- In-app feedback dialog
- Mock data export (CSV/PDF)
- AI error reporting

### Phase 4: Landing Page ✅
- Professional B2B landing page
- Beta request form with backend
- Admin management endpoints

---

## API Endpoints

### Public Endpoints
- `POST /api/beta/request-access` - Submit beta access request

### Protected Endpoints
- `GET /api/beta/requests` - Admin: View all beta requests
- `PATCH /api/beta/requests/{id}` - Admin: Update request status
- `POST /api/feedback` - Submit user feedback
- `GET /api/ai-dashboard/stats` - AI performance metrics
- `/api/export/vouchers` - Export vouchers as CSV/PDF

---

## Mocked Integrations (Beta Phase)
- **Stripe**: Payment processing is mocked (admin activates subscriptions)
- **e-conomic**: OAuth and API calls are mocked (voucher creation simulated)
- **Email**: Notifications are logged to database instead of sent

---

## Backlog

### P0 - Production Ready
All P0 items completed ✅

### P1 - Post-Beta
1. Real e-conomic Integration (OAuth2 flow)
2. Stripe Live Activation (webhook handling)
3. Live Email Notifications (SendGrid)

### P2 - Future Enhancements
1. Expand Integrations (Dinero, Billy adapters)
2. Smart Reconciliation Engine
3. Enhanced VAT Risk module
4. Machine learning-based account prediction
5. Multi-language invoice support

---

## Test Commands

### Run AI Evaluation
```bash
cd /app/backend
python3 tests/run_invoice_evaluation.py
```

### Test Beta API
```bash
curl -X POST "https://accounto.preview.emergentagent.com/api/beta/request-access" \
  -H "Content-Type: application/json" \
  -d '{"firm_name": "Test Firm", "email": "test@firm.dk"}'
```

---

## Credentials for Testing
- Register new users at `/register`
- Admin user can be created with `role: "admin"`
- Landing page accessible at `/`
- Main app accessible at `/app/dashboard` (after login)
