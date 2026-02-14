# AI Accounting Copilot - Product Requirements Document

## Version: 2.3.0-beta (50-Invoice Baseline Evaluation Complete)
## Last Updated: Feb 14, 2026

## Original Problem Statement
Build an AI Accounting Copilot SaaS with modular architecture for Danish SMEs and accountants.

## 50-Invoice Baseline Test Results

### Summary Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Invoices | 50 | 50 | ✅ |
| Successfully Processed | 50 | 50 | ✅ |
| Overall Field Accuracy | **94.82%** | >90% | ✅ |
| Critical Field Accuracy | **100.0%** | >98% | ✅ |
| Error Rate | 5.18% | <5% | ⚠️ Close |
| Needs Review | 12.0% | <15% | ✅ |

### Field-Level Accuracy
| Field | Accuracy | Status |
|-------|----------|--------|
| vendor_name | 100.0% | ✅ |
| invoice_number | 100.0% | ✅ |
| invoice_date | 100.0% | ✅ |
| due_date | 100.0% | ✅ |
| net_amount | 100.0% | ✅ |
| vat_amount | 100.0% | ✅ |
| total_amount | 100.0% | ✅ |
| cvr_number | 93.88% | ✅ |
| currency | 92.0% | ✅ |
| journal | 92.0% | ✅ |
| vat_code | 90.0% | ✅ |
| suggested_account | 70.0% | ⚠️ Needs improvement |

### Error Classification
- **Critical Errors:** 0 (amounts always correct)
- **Major Errors:** 23 (VAT codes, account suggestions)
- **Minor Errors:** 8 (journals, currency for foreign invoices)

### VAT Code Confusion Matrix
```
Expected → Actual
MOMSFRI → I0 (3 cases) - Insurance, flight tickets, bank fees
IEU → IREV (1 case) - EU goods misclassified as services
IKKEMOMS → I0 (1 case) - Government payment
```

### Account Confusion Pattern
Most account errors are semantic rather than categorical:
- 6010 (Husleje) → 6000 (Lokaleomkostninger) - Same category
- 6320 (Software) → 6310 (IT-udgifter) - Related accounts
- 1500 (Driftsmidler) → 6100 (Småanskaffelser) - Asset vs expense confusion

### Top 10 Vendors Causing Corrections
1. Bechtle AG: 4 corrections (EU goods)
2. Danske Bank A/S: 2 corrections (bank fees)
3. SAP SE: 2 corrections (EU reverse charge)
4. 7-Eleven Danmark A/S: 2 corrections (small purchases)
5. Amazon Web Services, Inc.: 2 corrections (USD)
6. SKAT: 2 corrections (government)
7. Tryg Forsikring A/S: 1 correction
8. Jeudan A/S: 1 correction
9. SAS Scandinavian Airlines: 1 correction
10. one.com Group AB: 1 correction

### By Category Performance
| Category | Count | Field Accuracy | Errors | Needs Review |
|----------|-------|----------------|--------|--------------|
| Realistic (Danish vendors) | 25 | 97.33% | 8 | 0 |
| Edge Cases | 25 | 92.31% | 23 | 6 |

### Invoices Requiring Review
1. INV-026: SAP SE (EU reverse charge, EUR)
2. INV-031: Mercedes-Benz (large vehicle purchase)
3. INV-037: Event Danmark (prepayment/deposit)
4. INV-039: SKAT (government payment)
5. INV-044: Schneider Electric (pro forma invoice)
6. INV-045: Nordea Finans (leasing payment)

## Architecture

### Tech Stack
- **Frontend:** React 19 + Tailwind CSS + Shadcn UI
- **Backend:** FastAPI (Python) v2.3.0-beta
- **Database:** MongoDB
- **AI:** OpenAI GPT-5.2 via Emergent LLM Key
- **OCR:** Tesseract (local)

### Code Structure
```
/app/backend/
├── server.py                      # Main FastAPI app
├── ai_production.py               # Production AI Service
├── danish_accounting.py           # 73 accounts, 10 VAT codes, 8 journals
├── vat_rules.py                   # Nordic VAT rules (DK active)
└── tests/
    ├── invoice_test_suite_data.py      # 25 realistic invoices
    ├── invoice_test_suite_edge_cases.py # 25 edge cases
    └── run_invoice_evaluation.py        # Evaluation script
```

## Completed Features

### ✅ Beta Activation Phase
- Beta Mode UI Banner
- Feedback System
- Data Export (CSV/PDF)
- Mock Email Notifications

### ✅ Production AI Architecture
- Structured prompts (temp 0.1-0.2)
- Schema validation
- Vendor override logic (3+ corrections)
- VAT enforcement rules
- Confidence adjustment
- Admin AI Dashboard

### ✅ 50-Invoice Baseline Suite
- 25 realistic Danish vendor invoices
- 25 edge case invoices
- Ground truth JSON labels
- Automated evaluation script
- Comprehensive accuracy report

## Known Limitations

### Account Suggestion (70% accuracy)
The AI tends to:
1. Confuse asset purchases with operating expenses
2. Default to generic expense accounts
3. Miss specific sub-accounts (6010 vs 6000)

**Recommended Fix:** Enhance vendor learning to override account suggestions after 1-2 corrections instead of 3.

### VAT Code Edge Cases
1. MOMSFRI vs I0 - Need clearer distinction in prompts
2. EU goods (IEU) vs EU services (IREV) - Need better keyword detection

### Foreign Currency
AI defaults to DKK for non-DKK invoices. Need to improve currency detection from OCR text.

## Recommendations for Production

### Immediate (P0)
1. Lower vendor learning threshold from 3 to 2 corrections
2. Add explicit MOMSFRI keywords (forsikring, international flybillet)
3. Improve EU goods vs services detection

### Short-term (P1)
1. Add currency detection from invoice text
2. Improve asset vs expense classification
3. Add pro forma invoice detection

### Medium-term (P2)
1. Train on real anonymized invoices
2. Implement accountant correction feedback loop
3. Add invoice image quality scoring

## Test Suite Maintenance

### Running Evaluation
```bash
cd /app/backend
python3 tests/run_invoice_evaluation.py
```

### Adding New Test Cases
1. Add invoice to `invoice_test_suite_data.py` or `invoice_test_suite_edge_cases.py`
2. Include ground truth JSON
3. Re-run evaluation

### Report Location
`/app/backend/test_reports/invoice_evaluation_report.json`

## Next Steps

1. 🔴 **P0**: Improve account suggestion accuracy to >85%
2. 🔴 **P0**: Fix MOMSFRI vs I0 confusion
3. 🟡 **P1**: Add currency detection
4. 🟡 **P1**: Test with 25 real anonymized invoices
5. 🟢 **P2**: Implement correction feedback loop
