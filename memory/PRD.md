# AI Accounting Copilot - Product Requirements Document

## Version: 2.0.0-beta (Beta-Ready MVP)
## Last Updated: Feb 14, 2026

## Original Problem Statement
Build an AI Accounting Copilot SaaS with modular architecture for Danish SMEs and accountants. Focus on:
- Upload invoice → AI extraction → Review → Approve → Voucher creation → Activity logging
- Integration-ready architecture for e-conomic (live credentials pending)
- Stable enough for beta testing with real accountants

## Architecture

### Tech Stack
- **Frontend:** React 19 + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend:** FastAPI (Python) v2.0.0-beta
- **Database:** MongoDB
- **AI:** OpenAI GPT-5.2 via Emergent LLM Key
- **OCR:** Tesseract (local)
- **Payments:** Stripe (admin-activated, live integration pending)
- **Accounting:** e-conomic (integration-ready, credentials pending)

### Modular Architecture
```
/app
├── backend/
│   └── server.py          # All backend modules (1800+ lines)
│       ├── Auth Module
│       ├── Tenant Module
│       ├── Document Module (with AI confidence scoring)
│       ├── Voucher Module (draft voucher engine)
│       ├── Activity Module (time tracking)
│       ├── Vendor Learning Module
│       ├── Reconciliation Module
│       ├── VAT Module
│       ├── Billing Module (admin-activated)
│       └── Admin Module
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── auth/
│       │   ├── dashboard/
│       │   ├── documents/ (with confidence UI)
│       │   ├── vouchers/ (with preview)
│       │   ├── activity/ (time saved)
│       │   └── admin/ (subscription management)
│       └── components/
```

## User Personas

### SME User (sme_user)
- Sees only own company
- Uploads invoices
- Reviews AI-extracted data with confidence indicators
- Edits uncertain fields
- Approves documents, creating vouchers

### Accountant (accountant)
- Manages multiple client companies
- Reviews pending documents across clients
- Monitors VAT risk scores
- Bulk operations

### Admin (admin)
- System administration
- Manually activates subscriptions
- Manages user roles
- Views platform statistics

## Core Requirements (Implemented)

### ✅ Phase 1 - System Hardening
- [x] Integration-ready accounting provider architecture
- [x] Provider configuration panel in admin
- [x] Simulated voucher creation engine with preview
- [x] Encrypted storage for provider credentials

### ✅ Phase 2 - AI Accuracy & User Control
- [x] Field-level confidence scores (0.0-1.0)
- [x] Highlight uncertain fields (<70% confidence)
- [x] Manual edit before approval
- [x] Vendor learning system

### ✅ Phase 3 - MVP Professionalization
- [x] Activity logging for all actions
- [x] Time saved calculation per activity type
- [x] Role-based access hardening
- [x] Error handling and loading states

### ✅ Phase 4 - Billing Ready
- [x] Subscription table with 3 plans
- [x] Admin-activated subscriptions
- [x] Usage tracking (documents/month)

## What's Been Implemented

### Authentication
- JWT-based authentication
- 3 roles: SME User, Accountant, Admin
- Password reset flow
- Token refresh

### Multi-Tenancy
- Create/manage companies
- Assign users to companies
- Tenant data isolation
- Provider configuration per tenant

### Document Processing (Enhanced)
- Upload PDF/image invoices
- Tesseract OCR extraction
- AI extraction with **field-level confidence scores**
- CVR validation (Danish 8-digit)
- VAT consistency check (25%)
- Duplicate detection
- **Manual field editing before approval**
- **Vendor pattern learning on approval**

### Voucher Engine (NEW)
- Draft voucher creation on approval
- Double-entry accounting preview
- Debit/Credit entries with VAT
- Balance verification
- Ready-to-push status
- Integration-ready push endpoint

### Activity Logging (NEW)
- All actions logged with timestamps
- Time saved calculation per activity
- Activity breakdown by type
- 30-day statistics

### Vendor Learning (NEW)
- Learns from user corrections
- Stores account mapping per vendor
- Suggests learned patterns on next upload
- Usage count tracking

### Billing (Admin-Activated)
- 3 plans: Starter (299 DKK), Professional (799 DKK), Accountant (1499 DKK)
- Admin manually activates subscriptions
- Subscription requests queue
- Usage limits enforcement ready

## API Endpoints (v2.0.0-beta)

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
- GET /api/tenants/{id}/provider (NEW)
- PUT /api/tenants/{id}/provider (NEW)
- POST /api/tenants/{id}/provider/test (NEW)

### Documents
- POST /api/documents/upload
- GET /api/documents/
- GET /api/documents/{id}
- PUT /api/documents/{id}/edit (NEW)
- PUT /api/documents/{id}/approve

### Vouchers (NEW)
- GET /api/vouchers/{tenant_id}
- GET /api/vouchers/{tenant_id}/{voucher_id}
- POST /api/vouchers/{tenant_id}/push

### Activity (NEW)
- GET /api/activity/{tenant_id}
- GET /api/activity/{tenant_id}/time-saved

### Vendors (NEW)
- GET /api/vendors/{tenant_id}
- PUT /api/vendors/{tenant_id}/{pattern_id}

### Reconciliation
- GET /api/reconciliation/{tenant_id}/unmatched
- POST /api/reconciliation/{tenant_id}/match
- POST /api/reconciliation/{tenant_id}/bulk-approve

### VAT
- GET /api/vat/{tenant_id}/analysis
- GET /api/vat/{tenant_id}/report

### Billing
- GET /api/billing/plans
- POST /api/billing/request (NEW)
- GET /api/billing/subscription
- DELETE /api/billing/subscription

### Admin
- GET /api/admin/users
- GET /api/admin/stats
- PUT /api/admin/users/{id}/role
- GET /api/admin/subscription-requests (NEW)
- POST /api/admin/subscriptions/activate (NEW)

### Dashboard
- GET /api/dashboard/stats
- GET /api/accountant/overview

## MOCKED / Integration-Ready Components

### e-conomic Accounting Provider
- **Status:** Integration-ready structure
- **What works:** All interface methods defined
- **What's mocked:** API calls return placeholder responses
- **To activate:** Add agreement_number and user_token to tenant provider config

### Stripe Billing
- **Status:** Demo mode
- **What works:** Plan structure, subscription database
- **What's mocked:** No live payment processing
- **To activate:** Admin manually activates subscriptions, Stripe webhook integration pending

## Environment Variables

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=ai_accounting_copilot
JWT_SECRET=<secret>
EMERGENT_LLM_KEY=<key>
STRIPE_SECRET_KEY=<placeholder>
ENCRYPTION_KEY=<auto-generated>
```

## Definition of Done (Beta-Ready) ✅

- [x] User can upload invoice
- [x] AI extracts with confidence scores
- [x] User can edit uncertain fields
- [x] User approves document
- [x] System creates internal draft voucher with preview
- [x] Vendor learning works
- [x] Activity logging with time saved
- [x] Multi-tenant stable
- [x] No critical errors

## Next Steps (Post-Beta)

### P0 - Required for Production
1. Integrate live Stripe keys
2. Connect e-conomic API with real credentials
3. Email notifications (welcome, invoice processed)

### P1 - High Priority
1. PDF report generation for VAT
2. Bank transaction import (CSV/OFX)
3. Advanced reconciliation algorithms

### P2 - Medium Priority
1. OAuth login (Google, Microsoft)
2. DineroProvider implementation
3. BillyProvider implementation

### P3 - Nice to Have
1. Danish language support
2. Mobile responsive improvements
3. Export to CSV/Excel

## Test Results (Latest)

- **Backend:** 95% (18/19 tests passing)
- **Frontend:** 90% (27/30 tests passing)
- **Version:** 2.0.0-beta
