# AI Accounting Copilot - Product Requirements Document

## Version: 2.1.0-beta (Beta Activation Phase Complete)
## Last Updated: Feb 14, 2026

## Original Problem Statement
Build an AI Accounting Copilot SaaS with modular architecture for Danish SMEs and accountants. Focus on:
- Upload invoice → AI extraction → Review → Approve → Voucher creation → Activity logging
- Integration-ready architecture for e-conomic (live credentials pending)
- Stable enough for beta testing with real accountants

## Architecture

### Tech Stack
- **Frontend:** React 19 + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend:** FastAPI (Python) v2.1.0-beta
- **Database:** MongoDB
- **AI:** OpenAI GPT-5.2 via Emergent LLM Key
- **OCR:** Tesseract (local)
- **Payments:** Stripe (admin-activated, live integration pending)
- **Accounting:** e-conomic (integration-ready, credentials pending)
- **Email:** MockEmailService (logs to DB, SendGrid pending)

### Modular Architecture
```
/app
├── backend/
│   └── server.py          # All backend modules (~2200 lines)
│       ├── Auth Module
│       ├── Tenant Module
│       ├── Document Module (with AI confidence scoring)
│       ├── Voucher Module (draft voucher engine)
│       ├── Activity Module (time tracking)
│       ├── Vendor Learning Module
│       ├── Reconciliation Module
│       ├── VAT Module
│       ├── Billing Module (admin-activated)
│       ├── Admin Module
│       ├── Feedback Module (NEW - Beta)
│       ├── Export Module (NEW - Beta)
│       └── Email Module (NEW - MOCKED)
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── auth/
│       │   ├── dashboard/
│       │   ├── documents/ (with confidence UI)
│       │   ├── vouchers/ (with preview & export)
│       │   ├── activity/ (time saved)
│       │   └── admin/ (subscription management)
│       └── components/
│           ├── beta/       (NEW - BetaBanner, FeedbackDialog)
│           ├── export/     (NEW - ExportButton)
│           └── layout/
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
- Access to feedback and email logs

## Core Requirements

### ✅ Phase 1 - System Hardening (COMPLETE)
- [x] Integration-ready accounting provider architecture
- [x] Provider configuration panel in admin
- [x] Simulated voucher creation engine with preview
- [x] Encrypted storage for provider credentials

### ✅ Phase 2 - AI Accuracy & User Control (COMPLETE)
- [x] Field-level confidence scores (0.0-1.0)
- [x] Highlight uncertain fields (<70% confidence)
- [x] Manual edit before approval
- [x] Vendor learning system

### ✅ Phase 3 - MVP Professionalization (COMPLETE)
- [x] Activity logging for all actions
- [x] Time saved calculation per activity type
- [x] Role-based access hardening
- [x] Error handling and loading states

### ✅ Phase 4 - Billing Ready (COMPLETE)
- [x] Subscription table with 3 plans
- [x] Admin-activated subscriptions
- [x] Usage tracking (documents/month)

### ✅ Phase 5 - Beta Activation (COMPLETE - Feb 14, 2026)
- [x] **Beta Mode UI Banner** - Prominent full-width dismissible banner
- [x] **Feedback System** - In-app form with star rating and categories
- [x] **Bug Report System** - AI error reporting with specific hints
- [x] **Data Export** - CSV and PDF export for vouchers
- [x] **Mock Email Notifications** - Log-based system (MOCKED)
- [x] Welcome email on registration
- [x] Shadcn Select component for consistency

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

### Voucher Engine
- Draft voucher creation on approval
- Double-entry accounting preview
- Debit/Credit entries with VAT
- Balance verification
- Ready-to-push status
- Integration-ready push endpoint
- **CSV/PDF export** (NEW)

### Activity Logging
- All actions logged with timestamps
- Time saved calculation per activity
- Activity breakdown by type
- 30-day statistics

### Vendor Learning
- Learns from user corrections
- Stores account mapping per vendor
- Suggests learned patterns on next upload
- Usage count tracking

### Billing (Admin-Activated)
- 3 plans: Starter (299 DKK), Professional (799 DKK), Accountant (1499 DKK)
- Admin manually activates subscriptions
- Subscription requests queue
- Usage limits enforcement ready

### Beta Features (NEW)
- **BetaBanner** - Full-width amber banner with BETA badge
- **FeedbackDialog** - Star rating, category select, text feedback
- **Bug Report** - AI extraction category with helpful hints
- **ExportButton** - Dropdown with CSV/PDF options
- **MockEmailService** - Logs to db.email_logs (MOCKED)

## API Endpoints (v2.1.0-beta)

### Auth
- POST /api/auth/register (triggers welcome email - MOCKED)
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
- GET /api/tenants/{id}/provider
- PUT /api/tenants/{id}/provider
- POST /api/tenants/{id}/provider/test

### Documents
- POST /api/documents/upload
- GET /api/documents/
- GET /api/documents/{id}
- PUT /api/documents/{id}/edit
- PUT /api/documents/{id}/approve

### Vouchers
- GET /api/vouchers/{tenant_id}
- GET /api/vouchers/{tenant_id}/{voucher_id}
- POST /api/vouchers/{tenant_id}/push

### Activity
- GET /api/activity/{tenant_id}
- GET /api/activity/{tenant_id}/time-saved

### Vendors
- GET /api/vendors/{tenant_id}
- PUT /api/vendors/{tenant_id}/{pattern_id}

### Billing
- GET /api/billing/plans
- POST /api/billing/request
- GET /api/billing/subscription
- DELETE /api/billing/subscription

### Admin
- GET /api/admin/users
- GET /api/admin/stats
- PUT /api/admin/users/{id}/role
- GET /api/admin/subscription-requests
- POST /api/admin/subscriptions/activate

### Feedback (NEW - Beta)
- POST /api/feedback - Submit feedback/bug report
- GET /api/feedback - Admin only, list all feedback

### Export (NEW - Beta)
- POST /api/export/{tenant_id}/vouchers - Export as CSV/PDF

### Email (NEW - MOCKED)
- GET /api/emails/logs - Admin only, view email logs

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

### Email Notifications (NEW)
- **Status:** MOCKED
- **What works:** MockEmailService logs all emails to db.email_logs
- **What's mocked:** No actual email sending
- **To activate:** Integrate SendGrid/Resend with live API keys

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

## Test Results (Latest - iteration_3.json)

- **Backend:** 86% (12/14 - 2 skipped due to no vouchers)
- **Frontend:** 100% (all beta UI components working)
- **Version:** 2.1.0-beta
- **Test User:** betatest@example.dk / test123

## Next Steps

### P0 - Required for Production
1. Integrate live Stripe keys (replace admin activation)
2. Connect e-conomic API with real credentials
3. Integrate SendGrid for real email notifications

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
3. Extended export options (Excel)
