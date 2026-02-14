# AI Accounting Copilot - Product Requirements Document

## Original Problem Statement
Build an AI Accounting Copilot SaaS with modular architecture for Danish SMEs and accountants. The system should include:
- Authentication with role-based access (SME User, Accountant, Admin)
- Multi-tenant company structure
- Document Processing with OCR and AI extraction
- Smart Reconciliation Engine
- VAT Risk Analysis Module
- Billing with Stripe integration
- Admin Dashboard

## Architecture

### Tech Stack
- **Frontend:** React 19 + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **AI:** OpenAI GPT-5.2 via Emergent LLM Key
- **OCR:** Tesseract (local)
- **Payments:** Stripe (demo mode)

### Modular Architecture
```
/app
├── backend/
│   └── server.py          # All backend modules
├── frontend/
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── contexts/      # Auth & Tenant contexts
│   │   ├── lib/           # API client & utilities
│   │   └── pages/         # All page components
```

### Backend Modules
1. **Auth Module** - JWT-based authentication
2. **Tenant Module** - Multi-company structure
3. **Document Module** - Upload, OCR, AI extraction
4. **Reconciliation Module** - Transaction matching
5. **VAT Module** - Risk analysis
6. **Billing Module** - Stripe integration
7. **Admin Module** - System administration

## User Personas

### SME User
- Small/medium business owner
- Uploads invoices and receipts
- Reviews AI-extracted data
- Approves documents for booking

### Accountant
- Manages multiple client companies
- Reviews pending documents across clients
- Monitors VAT risk scores
- Bulk approves reconciliation matches

### Admin
- System administrator
- Manages users and roles
- Views platform statistics

## Core Requirements (Static)

### Authentication
- [x] Email/password registration
- [x] JWT token-based login
- [x] Password reset flow
- [x] Role-based access control

### Multi-Tenancy
- [x] Create/manage companies
- [x] Assign users to companies
- [x] Tenant data isolation
- [x] Tenant selector in UI

### Document Processing
- [x] Upload PDF/image invoices
- [x] Tesseract OCR extraction
- [x] AI-powered data extraction (GPT-5.2)
- [x] CVR validation (Danish 8-digit)
- [x] VAT consistency check (25%)
- [x] Duplicate detection
- [x] Manual review/approval flow

### Reconciliation
- [x] Unmatched transaction listing
- [x] AI match suggestions
- [x] Manual matching
- [x] Bulk approval

### VAT Analysis
- [x] Period-based analysis
- [x] Anomaly detection
- [x] Risk scoring
- [x] AI risk summary

### Billing
- [x] Subscription plans (Starter, Professional, Enterprise)
- [x] Stripe integration (demo mode)
- [x] Plan limits enforcement

## What's Been Implemented (Feb 14, 2026)

### Phase 1 - Core Foundation ✅
- Authentication system (register, login, password reset)
- Role-based access control (SME User, Accountant, Admin)
- Multi-tenant company structure
- Basic dashboard with stats

### Phase 2 - Document Processing ✅
- File upload (PDF, JPG, PNG)
- Tesseract OCR integration
- AI extraction with GPT-5.2
- CVR and VAT validation
- Duplicate detection
- Review/approval workflow

### Phase 3 - Reconciliation ✅
- Unmatched transaction API
- AI match suggestions
- Individual and bulk matching

### Phase 4 - VAT Analysis ✅
- Quarterly VAT analysis
- Anomaly detection
- Risk scoring system
- AI-generated risk summaries

### Phase 5 - Billing ✅
- Three-tier subscription plans
- Stripe integration (demo mode)
- Subscription management

### Phase 6 - Dashboards ✅
- Main dashboard with KPIs
- Accountant multi-client overview
- Admin panel with user management

## Prioritized Backlog

### P0 (Critical) - None remaining

### P1 (High Priority)
- Real Stripe integration with live keys
- Email notifications for document processing
- Accounting system integration (e-conomic API)
- PDF report generation for VAT

### P2 (Medium Priority)
- OAuth login (Google, Microsoft)
- Bank transaction import
- DineroProvider and BillyProvider adapters
- Advanced reconciliation algorithms

### P3 (Nice to Have)
- Mobile responsive improvements
- Multi-language support (Danish)
- Custom chart of accounts
- Export to CSV/Excel

## API Endpoints

### Auth
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/password-reset/request
- POST /api/auth/password-reset/confirm
- GET /api/auth/me
- POST /api/auth/refresh

### Tenants
- POST /api/tenants/
- GET /api/tenants/
- GET /api/tenants/{id}
- PUT /api/tenants/{id}
- POST /api/tenants/{id}/users/{email}

### Documents
- POST /api/documents/upload
- GET /api/documents/
- GET /api/documents/{id}
- PUT /api/documents/{id}/approve

### Reconciliation
- GET /api/reconciliation/{tenant_id}/unmatched
- POST /api/reconciliation/{tenant_id}/match
- POST /api/reconciliation/{tenant_id}/bulk-approve

### VAT
- GET /api/vat/{tenant_id}/analysis
- GET /api/vat/{tenant_id}/report

### Billing
- GET /api/billing/plans
- POST /api/billing/subscribe
- GET /api/billing/subscription
- DELETE /api/billing/subscription

### Dashboard
- GET /api/dashboard/stats
- GET /api/accountant/overview

### Admin
- GET /api/admin/users
- GET /api/admin/stats
- PUT /api/admin/users/{id}/role

## Environment Variables

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=ai_accounting_copilot
JWT_SECRET=<secret>
EMERGENT_LLM_KEY=<key>
STRIPE_SECRET_KEY=<key>
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=<backend_url>
```

## Notes

### MOCKED Components
1. **Accounting Provider (e-conomic)** - Returns placeholder data
2. **Stripe** - Running in demo mode without live API calls

### Design System
- Theme: "Nordic Precision"
- Primary: Teal (#0F766E)
- Accent: Orange (#EA580C)
- Fonts: Manrope (headings), Inter (body), JetBrains Mono (data)
