# Accountrix - Product Requirements Document

## Version: 3.1.0 (Professional Repositioning)
## Last Updated: Feb 17, 2026

---

## STRATEGIC PIVOT SUMMARY

**OLD CATEGORY:** Invoice automation / OCR tool  
**NEW CATEGORY:** AI Portfolio Risk & Exception Management Platform

**Core Mission:** Reduce cognitive overload, compliance risk, and review time for accounting firms with large client portfolios (100+ clients).

---

## TARGET USER PROFILE

| User Type | Description |
|-----------|-------------|
| **Primary** | Accounting firm partner or senior reviewer managing 100–300 clients |
| **Secondary** | Junior bookkeepers whose work needs review |

The product is designed for firms handling high transaction volume, multiple staff, and VAT deadline pressure.

---

## CORE VALUE PROPOSITION

We do NOT replace accounting systems. We provide:
- Cross-client risk visibility
- Exception prioritization  
- Pre-VAT anomaly detection
- Review workflow intelligence
- Professional control layer

**Key Questions We Answer:**
1. Which clients require attention before VAT submission?
2. Which transactions deviate from historical patterns?
3. Where are unusual VAT fluctuations?
4. Which postings require senior review?
5. Which clients present compliance risk signals?

---

## MVP MODULES (Priority Order)

### MODULE 1 — Portfolio Risk Dashboard ⭐ P0
A dashboard showing:
- All connected clients
- Risk score per client
- Traffic-light indicators (Low / Medium / High)
- Abnormal VAT trend detection
- Expense spike detection
- Duplicate invoice detection
- Missing documentation indicators

**Sorting Options:**
- Highest risk
- Upcoming VAT deadline
- Most anomalies

### MODULE 2 — Exception Inbox ⭐ P0
Shows ONLY:
- Unusual transactions
- Large deviations from normal pattern
- High VAT impact entries
- Suspicious vendor patterns
- Out-of-pattern account usage

**Each exception includes:**
- Explanation (why flagged)
- Confidence score
- Historical comparison
- Quick review action (Approve / Investigate / Assign)

### MODULE 3 — Pre-VAT Control Mode ⭐ P0
When VAT deadline approaches:
- Flags abnormal VAT percentage changes
- Compares quarter vs historical quarter
- Identifies unusual deduction patterns
- Highlights missing VAT-coded entries
- Generates Pre-VAT Risk Summary per client

### MODULE 4 — Staff Review Intelligence (P1)
For firms with junior staff:
- Track which junior posted what
- Detect unusual account use per staff member
- Highlight entries that differ from their normal pattern
- Create review queue for senior accountant

### MODULE 5 — Transaction Intelligence (Rebranded Invoice AI) (P2)
- AI-powered invoice data extraction
- Rule-based validation
- Vendor learning system
- Account classification suggestions
- *Secondary feature, not hero*

---

## DATA MODEL

```
Firm (Accounting Practice)
├── Users (Staff members with roles)
├── Clients (Connected companies)
│   ├── Transactions (Normalized from e-conomic)
│   │   ├── VAT Periods
│   │   ├── Exception Flags
│   │   └── Staff Assignments
│   ├── Risk Scores (Calculated)
│   └── Historical Patterns (Baseline)
└── Settings (Thresholds, notifications)
```

---

## ARCHITECTURE

### System Position
```
┌─────────────────────────────────┐
│         ACCOUNTRIX              │
│   Risk & Control Intelligence   │
└──────────────┬──────────────────┘
               │ API Connection
┌──────────────┴──────────────────┐
│     Accounting Systems          │
│  e-conomic | Dinero | Fortnox   │
└─────────────────────────────────┘
```

### Tech Stack
- **Frontend:** React + Tailwind + Shadcn/UI
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **AI:** OpenAI GPT-4o via Emergent Universal Key (or direct API)
- **Integrations:** e-conomic API (primary), others planned

---

## PRICING MODEL

| Tier | Price | Included |
|------|-------|----------|
| Professional | 2,499 DKK/month | Up to 100 clients |
| Additional clients | +15 DKK/client/month | — |

**NOT per-invoice. NOT per-transaction. Per-firm.**

---

## WHAT WE ARE NOT BUILDING

- Generic invoice OCR improvements
- Basic bookkeeping automation
- Competing with native accounting features
- Per-client feature duplication

---

## DIFFERENTIATION

| Competitor | Their Focus | Our Difference |
|------------|-------------|----------------|
| e-conomic Premium | Per-client features | Portfolio-wide intelligence |
| Dext / FileAI | Invoice OCR | Risk detection & control |
| Basic automation | Process speed | Professional oversight |

---

## COMPLETED WORK

### Landing Page ✅
- New positioning: "Air Traffic Control for Accounting Firms"
- Dark theme, professional design
- Three core modules highlighted
- Per-firm pricing model
- Demo request form functional

### AI Infrastructure ✅
- OpenAI integration ready (direct API or Universal Key)
- 50-invoice evaluation: 98.33% accuracy
- Rule engine for Danish VAT
- Vendor learning system

### Authentication ✅
- Multi-tenant JWT auth
- Roles: SME User, Accountant, Admin

---

## NEXT STEPS

### Phase 1: Data Foundation
1. Create mock client portfolio data generator
2. Build normalized transaction schema
3. Implement risk score calculation engine
4. Create historical pattern baseline system

### Phase 2: Portfolio Risk Dashboard
1. Build client list with risk indicators
2. Implement VAT trend analysis
3. Add expense spike detection
4. Create duplicate invoice detection
5. Build missing documentation alerts

### Phase 3: Exception Inbox
1. Define exception types and rules
2. Build exception detection engine
3. Create exception card UI
4. Implement quick actions (Approve/Investigate/Assign)
5. Add AI explanations

### Phase 4: Pre-VAT Control Mode
1. VAT deadline tracking
2. Period comparison logic
3. Pre-submission checklist
4. Risk summary generation

---

## DESIGN PRINCIPLES

The UI must communicate:
- **Control** — You're in charge
- **Clarity** — No noise, only signals
- **Prioritization** — Most important first
- **Professional oversight** — Trust, not gimmicks

**Metaphor:** "Air traffic control for accounting firms"

---

## FILES OF REFERENCE

### Core Application
- `/app/frontend/src/pages/landing/LandingPage.jsx` - New landing page
- `/app/frontend/src/App.js` - Main router
- `/app/backend/server.py` - API server
- `/app/backend/ai_production.py` - AI service
- `/app/backend/openai_live.py` - Direct OpenAI integration
- `/app/backend/rule_engine.py` - Deterministic rules

### Configuration
- `/app/backend/.env` - Environment variables
- `/app/frontend/.env` - Frontend config

---

## MOCKED INTEGRATIONS

| Integration | Status | Notes |
|-------------|--------|-------|
| e-conomic API | MOCKED | OAuth + API calls simulated |
| Stripe payments | MOCKED | Admin activates subscriptions |
| Email notifications | MOCKED | Logged to database |

---

## TEST CREDENTIALS

- Register new users at `/register`
- Landing page at `/`
- App dashboard at `/app/dashboard` (after login)
