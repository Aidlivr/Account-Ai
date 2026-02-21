# Accountrix - Product Requirements Document

## Version: 4.0.0 (MVP Complete)
## Last Updated: Feb 21, 2026

---

## PRODUCT SUMMARY

**Accountrix** is a Professional Control & Risk Intelligence Platform for accounting firms managing 100+ clients. It operates as an intelligent control layer ABOVE existing accounting systems (e-conomic, Dinero, Fortnox).

**Core Mission:** Reduce cognitive overload, compliance risk, and review time for accounting firms with large client portfolios.

---

## MVP STATUS: ✅ COMPLETE

All three core modules are built and functional with realistic demo data.

### Module 1: Portfolio Risk Dashboard ✅
- 25 client companies with risk indicators
- Traffic-light system (High/Elevated/Normal)
- Summary cards (Total, High Risk, Elevated, Normal, Open Exceptions, Near VAT Deadline)
- Sortable by: Risk Score, VAT Deadline, Exceptions
- Searchable by company name or CVR
- Staff assignment tracking

### Module 2: Exception Inbox ✅
- 18 detected exceptions across client portfolio
- Filter by: Status, Severity, Exception Type
- Exception types:
  - VAT Trend Anomaly
  - Expense Spike
  - Duplicate Invoice
  - Unusual Vendor
  - VAT Variance
  - Pattern Deviation
- Detail panel with:
  - Transaction details (Amount, Vendor, Account, Date)
  - Historical comparison data
  - AI-generated explanation
  - Quick actions: Approve / Investigate / Dismiss

### Module 3: Pre-VAT Review Mode ✅
- Clients approaching VAT deadline (configurable: 14/30/60 days)
- Summary: Total Clients, Ready, Needs Attention, Readiness Rate
- Per-client checklist:
  - All exceptions reviewed
  - No high-risk items pending
  - Reviewed within 7 days
  - VAT trends verified
- Progress bars per client
- Warning indicators for open exceptions
- Detail modal with exception list

---

## DATA ARCHITECTURE

```
Firm (Accounting Practice)
├── portfolio_clients (25 companies)
│   ├── Risk Score (0-100)
│   ├── Risk Level (normal/elevated/high)
│   ├── Exception Count
│   ├── VAT Deadline
│   └── Assigned Staff
├── portfolio_transactions (16,238 entries)
│   └── 6 months history per client
└── portfolio_exceptions (18 flagged items)
    ├── Type (expense_spike, duplicate, vat_trend, etc.)
    ├── Severity (high/medium/low)
    ├── Status (open/investigating/resolved/dismissed)
    └── AI Explanation
```

---

## API ENDPOINTS

### Portfolio Risk Platform (New)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/portfolio/summary` | Portfolio-wide stats |
| GET | `/api/portfolio/clients` | Client list with risk metrics |
| GET | `/api/portfolio/clients/{id}` | Client detail |
| GET | `/api/portfolio/exceptions` | Exception list with filters |
| POST | `/api/portfolio/exceptions/{id}/action` | Handle exception (approve/investigate/assign/dismiss) |
| GET | `/api/portfolio/pre-vat-review` | Pre-VAT review status |
| POST | `/api/portfolio/generate-demo-data` | Generate demo portfolio |
| DELETE | `/api/portfolio/demo-data` | Clear demo data |

### Legacy Endpoints (Transaction Intelligence)
- `/api/auth/*` - Authentication
- `/api/documents/*` - Document management
- `/api/vouchers/*` - Voucher workflow
- `/api/ai-dashboard/*` - AI performance metrics

---

## DEMO CREDENTIALS

```
Email: demo@accountrix.dk
Password: Demo123!
Role: Accountant
```

---

## FILE STRUCTURE

```
/app
├── backend/
│   ├── server.py                 # Main FastAPI app
│   ├── portfolio_routes.py       # Portfolio API routes (NEW)
│   ├── portfolio_data_generator.py # Mock data generator (NEW)
│   ├── ai_production.py          # AI service
│   ├── openai_live.py           # Direct OpenAI integration
│   └── tests/
├── frontend/
│   └── src/
│       ├── App.js               # Routes
│       ├── pages/
│       │   ├── landing/LandingPage.jsx     # Professional landing page
│       │   └── portfolio/
│       │       ├── PortfolioRiskDashboard.jsx  # Module 1 (NEW)
│       │       ├── ExceptionInbox.jsx          # Module 2 (NEW)
│       │       └── PreVATReview.jsx            # Module 3 (NEW)
│       └── components/
│           └── layout/Sidebar.jsx  # Updated navigation
└── memory/
    └── PRD.md
```

---

## DEPLOYMENT CHECKLIST

✅ Landing page professional and demo-ready
✅ All three MVP modules functional
✅ Demo data generator works
✅ Auth flow works
✅ Navigation updated with Portfolio Control section
✅ Mobile-responsive design
✅ Dark theme consistent throughout

### Ready for deployment with demo data

---

## MOCKED INTEGRATIONS

| Integration | Status | Notes |
|-------------|--------|-------|
| e-conomic API | MOCKED | Demo uses generated mock data |
| Stripe payments | MOCKED | Admin activates subscriptions |
| Email notifications | MOCKED | Logged to database |
| OpenAI | READY | Uses Emergent Universal Key (can switch to direct API) |

---

## POST-MVP ROADMAP

### P1 - Production Ready
1. Real e-conomic OAuth2 integration
2. Live transaction data sync
3. Stripe payment activation
4. Email notifications (SendGrid)

### P2 - Enhanced Features
1. Staff Review Intelligence module
2. Dinero/Fortnox adapters
3. Custom exception rules
4. Audit trail exports
5. Multi-firm management

### P3 - Scale
1. Enterprise SSO
2. API rate limiting
3. Advanced analytics
4. Custom reporting

---

## PRICING MODEL

| Tier | Price | Included |
|------|-------|----------|
| Professional | 2,499 DKK/month | Up to 100 clients |
| Additional clients | +15 DKK/client/month | — |

**Per-firm pricing, not per-transaction.**
