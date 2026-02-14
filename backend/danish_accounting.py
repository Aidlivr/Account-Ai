# Danish Standard Accounting Data
# Chart of Accounts, VAT Codes, Journals for Danish bookkeeping

from typing import Dict, List, Any

# ==================== DANISH CHART OF ACCOUNTS (KONTOPLAN) ====================

DANISH_CHART_OF_ACCOUNTS: List[Dict[str, Any]] = [
    # 1000-1999: Assets (Aktiver)
    {"code": "1000", "name": "Kasse", "type": "asset", "category": "current_asset"},
    {"code": "1010", "name": "Bank", "type": "asset", "category": "current_asset"},
    {"code": "1100", "name": "Debitorer", "type": "asset", "category": "receivable"},
    {"code": "1200", "name": "Forudbetalte omkostninger", "type": "asset", "category": "prepaid"},
    {"code": "1300", "name": "Varelager", "type": "asset", "category": "inventory"},
    {"code": "1400", "name": "Igangværende arbejder", "type": "asset", "category": "wip"},
    {"code": "1500", "name": "Driftsmidler og inventar", "type": "asset", "category": "fixed_asset"},
    {"code": "1510", "name": "Edb-udstyr", "type": "asset", "category": "fixed_asset"},
    {"code": "1520", "name": "Biler", "type": "asset", "category": "fixed_asset"},
    {"code": "1600", "name": "Goodwill", "type": "asset", "category": "intangible"},
    
    # 2000-2999: Liabilities (Passiver)
    {"code": "2000", "name": "Egenkapital", "type": "equity", "category": "equity"},
    {"code": "2100", "name": "Resultat indeværende år", "type": "equity", "category": "equity"},
    {"code": "2200", "name": "Hensættelser", "type": "liability", "category": "provision"},
    {"code": "2300", "name": "Langfristet gæld", "type": "liability", "category": "long_term"},
    {"code": "2400", "name": "Kortfristet gæld", "type": "liability", "category": "short_term"},
    {"code": "2500", "name": "Leverandørgæld", "type": "liability", "category": "payable"},
    {"code": "2600", "name": "Skyldig moms", "type": "liability", "category": "vat_payable"},
    {"code": "2610", "name": "Skyldig A-skat", "type": "liability", "category": "tax_payable"},
    {"code": "2620", "name": "Skyldig AM-bidrag", "type": "liability", "category": "tax_payable"},
    {"code": "2700", "name": "Periodeafgrænsning", "type": "liability", "category": "accrual"},
    
    # 3000-3999: Revenue (Omsætning)
    {"code": "3000", "name": "Salg af varer", "type": "revenue", "category": "sales"},
    {"code": "3100", "name": "Salg af tjenesteydelser", "type": "revenue", "category": "services"},
    {"code": "3200", "name": "Eksportsalg EU", "type": "revenue", "category": "export_eu"},
    {"code": "3300", "name": "Eksportsalg ikke-EU", "type": "revenue", "category": "export_non_eu"},
    {"code": "3400", "name": "Øvrige indtægter", "type": "revenue", "category": "other"},
    
    # 4000-4999: Cost of Goods Sold (Vareforbrug)
    {"code": "4000", "name": "Varekøb", "type": "expense", "category": "cogs"},
    {"code": "4100", "name": "Varekøb EU", "type": "expense", "category": "cogs_eu"},
    {"code": "4200", "name": "Varekøb ikke-EU", "type": "expense", "category": "cogs_non_eu"},
    {"code": "4300", "name": "Fremmed arbejde", "type": "expense", "category": "subcontract"},
    {"code": "4400", "name": "Lagerregulering", "type": "expense", "category": "inventory_adj"},
    
    # 5000-5999: Personnel (Personaleomkostninger)
    {"code": "5000", "name": "Lønninger", "type": "expense", "category": "salary"},
    {"code": "5100", "name": "Feriepengeforpligtelse", "type": "expense", "category": "vacation"},
    {"code": "5200", "name": "ATP og pensioner", "type": "expense", "category": "pension"},
    {"code": "5300", "name": "Andre personaleomkostninger", "type": "expense", "category": "personnel_other"},
    {"code": "5400", "name": "Kørselsgodtgørelse", "type": "expense", "category": "mileage"},
    {"code": "5500", "name": "Personalegoder", "type": "expense", "category": "benefits"},
    
    # 6000-6999: Operating Expenses (Driftsomkostninger)
    {"code": "6000", "name": "Lokaleomkostninger", "type": "expense", "category": "premises"},
    {"code": "6010", "name": "Husleje", "type": "expense", "category": "rent"},
    {"code": "6020", "name": "El, vand og varme", "type": "expense", "category": "utilities"},
    {"code": "6030", "name": "Rengøring", "type": "expense", "category": "cleaning"},
    {"code": "6100", "name": "Småanskaffelser", "type": "expense", "category": "small_purchases"},
    {"code": "6200", "name": "Vedligeholdelse", "type": "expense", "category": "maintenance"},
    {"code": "6300", "name": "Kontorartikler", "type": "expense", "category": "office_supplies"},
    {"code": "6310", "name": "IT-udgifter", "type": "expense", "category": "it_expenses"},
    {"code": "6320", "name": "Software og licenser", "type": "expense", "category": "software"},
    {"code": "6400", "name": "Telefon og internet", "type": "expense", "category": "telecom"},
    {"code": "6500", "name": "Porto og gebyrer", "type": "expense", "category": "postage"},
    {"code": "6600", "name": "Forsikringer", "type": "expense", "category": "insurance"},
    {"code": "6700", "name": "Bilomkostninger", "type": "expense", "category": "vehicle"},
    {"code": "6710", "name": "Brændstof", "type": "expense", "category": "fuel"},
    {"code": "6720", "name": "Bilforsikring", "type": "expense", "category": "vehicle_insurance"},
    {"code": "6730", "name": "Bilreparation", "type": "expense", "category": "vehicle_repair"},
    {"code": "6800", "name": "Rejse og ophold", "type": "expense", "category": "travel"},
    {"code": "6900", "name": "Repræsentation", "type": "expense", "category": "representation"},
    {"code": "6910", "name": "Restaurantbesøg (25% fradrag)", "type": "expense", "category": "restaurant"},
    
    # 7000-7999: Other Operating Expenses
    {"code": "7000", "name": "Reklame og markedsføring", "type": "expense", "category": "marketing"},
    {"code": "7100", "name": "Faglitteratur og kurser", "type": "expense", "category": "education"},
    {"code": "7200", "name": "Advokat og revisor", "type": "expense", "category": "professional_fees"},
    {"code": "7300", "name": "Konsulenthonorar", "type": "expense", "category": "consulting"},
    {"code": "7400", "name": "Tab på debitorer", "type": "expense", "category": "bad_debt"},
    {"code": "7500", "name": "Andre driftsomkostninger", "type": "expense", "category": "other_operating"},
    
    # 8000-8999: Depreciation and Financial
    {"code": "8000", "name": "Afskrivninger", "type": "expense", "category": "depreciation"},
    {"code": "8100", "name": "Afskrivning driftsmidler", "type": "expense", "category": "depreciation_equipment"},
    {"code": "8200", "name": "Afskrivning biler", "type": "expense", "category": "depreciation_vehicles"},
    {"code": "8300", "name": "Renteindtægter", "type": "revenue", "category": "interest_income"},
    {"code": "8400", "name": "Renteudgifter", "type": "expense", "category": "interest_expense"},
    {"code": "8500", "name": "Kursgevinst/-tab", "type": "expense", "category": "exchange"},
    {"code": "8600", "name": "Bankgebyrer", "type": "expense", "category": "bank_fees"},
    
    # 9000-9999: VAT and Tax Accounts
    {"code": "9000", "name": "Indgående moms", "type": "asset", "category": "vat_input"},
    {"code": "9100", "name": "Udgående moms", "type": "liability", "category": "vat_output"},
    {"code": "9200", "name": "Momsafregning", "type": "liability", "category": "vat_settlement"},
    {"code": "9300", "name": "EU-erhvervelsesmoms", "type": "liability", "category": "vat_eu_acquisition"},
    {"code": "9400", "name": "Skat af årets resultat", "type": "expense", "category": "income_tax"},
]

# ==================== DANISH VAT CODES ====================

DANISH_VAT_CODES: List[Dict[str, Any]] = [
    # Input VAT (Indgående moms)
    {"code": "I25", "name": "Indgående moms 25%", "rate": 25.0, "type": "input", "account": "9000"},
    {"code": "I0", "name": "Indgående moms 0%", "rate": 0.0, "type": "input", "account": "9000"},
    {"code": "IEU", "name": "EU-erhvervelser moms", "rate": 25.0, "type": "input_eu", "account": "9300", "reverse_charge": True},
    {"code": "IREV", "name": "Reverse charge (ydelser)", "rate": 25.0, "type": "input_reverse", "account": "9300", "reverse_charge": True},
    
    # Output VAT (Udgående moms)
    {"code": "U25", "name": "Udgående moms 25%", "rate": 25.0, "type": "output", "account": "9100"},
    {"code": "U0", "name": "Udgående moms 0%", "rate": 0.0, "type": "output", "account": "9100"},
    {"code": "UEU", "name": "Salg til EU (momsfrit)", "rate": 0.0, "type": "output_eu", "account": "9100"},
    {"code": "UEXP", "name": "Eksport (momsfrit)", "rate": 0.0, "type": "output_export", "account": "9100"},
    
    # Special codes
    {"code": "MOMSFRI", "name": "Momsfritaget", "rate": 0.0, "type": "exempt", "account": None},
    {"code": "IKKEMOMS", "name": "Ikke momsbelagt", "rate": 0.0, "type": "non_vat", "account": None},
]

# ==================== DANISH STANDARD JOURNALS ====================

DANISH_STANDARD_JOURNALS: List[Dict[str, Any]] = [
    {"code": "KOB", "name": "Købsjournal", "type": "purchase", "description": "Indkøb og leverandørfakturaer"},
    {"code": "SALG", "name": "Salgsjournal", "type": "sales", "description": "Salg og kundefakturaer"},
    {"code": "BANK", "name": "Bankjournal", "type": "bank", "description": "Bankbevægelser"},
    {"code": "KASSE", "name": "Kassejournal", "type": "cash", "description": "Kontante transaktioner"},
    {"code": "LON", "name": "Lønjournal", "type": "payroll", "description": "Lønudbetalinger"},
    {"code": "AFSKR", "name": "Afskrivningsjournal", "type": "depreciation", "description": "Afskrivninger"},
    {"code": "PRIMO", "name": "Primojournal", "type": "opening", "description": "Åbningsposteringer"},
    {"code": "DIV", "name": "Diversejournal", "type": "general", "description": "Øvrige posteringer"},
]

# ==================== REVERSE CHARGE KEYWORDS ====================

REVERSE_CHARGE_KEYWORDS = [
    "reverse charge",
    "omvendt betalingspligt",
    "intra-community",
    "eu-leverance",
    "momsfri leverance",
    "article 196",
    "artikel 196",
    "vat reverse",
]

# ==================== HELPER FUNCTIONS ====================

def get_account_by_code(code: str) -> Dict[str, Any]:
    """Get account by code"""
    for account in DANISH_CHART_OF_ACCOUNTS:
        if account["code"] == code:
            return account
    return None

def get_accounts_by_type(account_type: str) -> List[Dict[str, Any]]:
    """Get all accounts of a specific type"""
    return [a for a in DANISH_CHART_OF_ACCOUNTS if a["type"] == account_type]

def get_accounts_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all accounts of a specific category"""
    return [a for a in DANISH_CHART_OF_ACCOUNTS if a.get("category") == category]

def validate_account_code(code: str) -> bool:
    """Check if account code exists in chart"""
    return any(a["code"] == code for a in DANISH_CHART_OF_ACCOUNTS)

def get_vat_code_by_code(code: str) -> Dict[str, Any]:
    """Get VAT code details"""
    for vat in DANISH_VAT_CODES:
        if vat["code"] == code:
            return vat
    return None

def validate_vat_code(code: str) -> bool:
    """Check if VAT code is valid"""
    return any(v["code"] == code for v in DANISH_VAT_CODES)

def get_journal_by_code(code: str) -> Dict[str, Any]:
    """Get journal by code"""
    for journal in DANISH_STANDARD_JOURNALS:
        if journal["code"] == code:
            return journal
    return None

def validate_journal_code(code: str) -> bool:
    """Check if journal code is valid"""
    return any(j["code"] == code for j in DANISH_STANDARD_JOURNALS)

def detect_reverse_charge(text: str) -> bool:
    """Detect if invoice contains reverse charge keywords"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in REVERSE_CHARGE_KEYWORDS)

def get_expense_accounts() -> List[Dict[str, Any]]:
    """Get all expense accounts for invoice processing"""
    return [a for a in DANISH_CHART_OF_ACCOUNTS if a["type"] == "expense"]

def format_chart_for_prompt() -> str:
    """Format chart of accounts for AI prompt"""
    lines = []
    for account in DANISH_CHART_OF_ACCOUNTS:
        if account["type"] == "expense":
            lines.append(f"- {account['code']}: {account['name']} ({account['category']})")
    return "\n".join(lines)

def format_vat_codes_for_prompt() -> str:
    """Format VAT codes for AI prompt"""
    lines = []
    for vat in DANISH_VAT_CODES:
        if vat["type"] in ["input", "input_eu", "input_reverse"]:
            rc = " [REVERSE CHARGE]" if vat.get("reverse_charge") else ""
            lines.append(f"- {vat['code']}: {vat['name']} ({vat['rate']}%){rc}")
    return "\n".join(lines)

def format_journals_for_prompt() -> str:
    """Format journals for AI prompt"""
    lines = []
    for journal in DANISH_STANDARD_JOURNALS:
        lines.append(f"- {journal['code']}: {journal['name']}")
    return "\n".join(lines)
