# Deterministic Rule Engine for Invoice Processing
# Post-AI rules to improve account, VAT, and currency accuracy

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# ==================== CONFIGURATION ====================

@dataclass
class CompanyConfig:
    """Company-specific configuration for rule engine"""
    asset_threshold_dkk: float = 15000.0  # Items above this are assets, not expenses
    enable_asset_detection: bool = True
    default_currency: str = "DKK"
    country_code: str = "DK"


# ==================== ACCOUNT CATEGORY RULES ====================

class AccountCategory(Enum):
    OFFICE_SUPPLIES = "office_supplies"
    IT_EQUIPMENT = "it_equipment"
    SOFTWARE = "software"
    TELECOM = "telecom"
    FUEL = "fuel"
    VEHICLE = "vehicle"
    RENT = "rent"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    LEGAL = "legal"
    ACCOUNTING = "accounting"
    CONSULTING = "consulting"
    MARKETING = "marketing"
    TRAVEL = "travel"
    REPRESENTATION = "representation"
    EDUCATION = "education"
    POSTAL = "postal"
    CLEANING = "cleaning"
    BANK_FEES = "bank_fees"
    RAW_MATERIALS = "raw_materials"
    SUBCONTRACTOR = "subcontractor"
    PERSONNEL = "personnel"
    FIXED_ASSET = "fixed_asset"
    PREPAYMENT = "prepayment"
    GOVERNMENT = "government"
    LEASING = "leasing"
    UNKNOWN = "unknown"


# Keyword to category mapping (case-insensitive)
ACCOUNT_CATEGORY_KEYWORDS: Dict[AccountCategory, List[str]] = {
    AccountCategory.INSURANCE: [
        "forsikring", "insurance", "præmie", "premium", "police", "dækning",
        "tryg", "topdanmark", "if skadeforsikring", "alm brand", "codan",
        "erhvervsforsikring", "ansvarsforsikring", "arbejdsskade"
    ],
    AccountCategory.TELECOM: [
        "telefon", "mobil", "internet", "fiber", "bredbånd", "broadband",
        "tdc", "telenor", "telia", "3 danmark", "yousee", "fastnet",
        "roaming", "opkald", "data", "abonnement telecom"
    ],
    AccountCategory.FUEL: [
        "brændstof", "benzin", "diesel", "fuel", "tankstation", "tank",
        "ok a.m.b.a", "shell", "q8", "circle k", "ingo", "uno-x",
        "liter", "påfyldning"
    ],
    AccountCategory.VEHICLE: [
        "bil", "køretøj", "vehicle", "auto", "værksted", "reparation",
        "service bil", "dæk", "olie", "fdm", "autoreparation",
        "bilservice", "bilforsikring", "vægtafgift", "nummerplader"
    ],
    AccountCategory.RENT: [
        "husleje", "leje", "rent", "lokale", "kontorlokale", "lejemål",
        "aconto varme", "fællesudgifter", "ejendom", "jeudan", "datea",
        "erhvervsleje", "depositum leje"
    ],
    AccountCategory.UTILITIES: [
        "el ", "elektricitet", "electricity", "vand", "water", "varme",
        "heating", "gas", "energi", "ørsted", "hofor", "radius",
        "forsyning", "kwh", "forbrug el", "fjernvarme"
    ],
    AccountCategory.SOFTWARE: [
        "software", "licens", "license", "saas", "cloud", "abonnement software",
        "microsoft", "adobe", "salesforce", "hubspot", "slack", "zoom",
        "office 365", "google workspace", "dropbox", "github", "atlassian",
        "subscription", "annual license", "årslicens"
    ],
    AccountCategory.IT_EQUIPMENT: [
        "computer", "laptop", "pc ", "server", "printer", "skærm", "monitor",
        "tastatur", "mus", "mouse", "keyboard", "dell", "hp ", "lenovo",
        "apple", "macbook", "hardware", "it-udstyr", "docking"
    ],
    AccountCategory.LEGAL: [
        "advokat", "lawyer", "juridisk", "legal", "retsafgift", "sagkyndig",
        "plesner", "kromann", "bech-bruun", "gorrissen", "horten",
        "rådgivning juridisk", "kontrakt", "retssag"
    ],
    AccountCategory.ACCOUNTING: [
        "revisor", "regnskab", "accounting", "audit", "bogholderi",
        "beierholm", "deloitte", "pwc", "kpmg", "ey ", "ernst",
        "årsregnskab", "bogføring", "momsregnskab"
    ],
    AccountCategory.CONSULTING: [
        "konsulent", "consultant", "rådgivning", "advisory", "strategi",
        "mckinsey", "bcg", "bain", "accenture", "implement",
        "management consulting", "projekt konsulent"
    ],
    AccountCategory.MARKETING: [
        "marketing", "reklame", "annonce", "advertisement", "kampagne",
        "google ads", "facebook ads", "linkedin", "seo", "sem",
        "branding", "design", "grafisk", "content", "social media"
    ],
    AccountCategory.TRAVEL: [
        "rejse", "travel", "fly", "flight", "hotel", "tog", "train",
        "sas", "norwegian", "lufthansa", "booking", "airbnb",
        "transport", "taxa", "uber", "parkering"
    ],
    AccountCategory.REPRESENTATION: [
        "repræsentation", "representation", "restaurant", "frokost",
        "middag", "dinner", "catering", "forplejning", "noma",
        "gæster", "kundemøde", "firmaarrangement"
    ],
    AccountCategory.EDUCATION: [
        "kursus", "course", "uddannelse", "training", "seminar",
        "konference", "conference", "workshop", "certificering",
        "faglitteratur", "bøger", "e-learning", "kursusgebyr",
        "kursusmaterialer", "projektledelse", "kursuslex"
    ],
    AccountCategory.POSTAL: [
        "porto", "postage", "forsendelse", "shipping", "fragt", "freight",
        "postnord", "gls", "dao", "bring", "ups", "fedex", "dhl",
        "pakke", "brev", "kuvert"
    ],
    AccountCategory.CLEANING: [
        "rengøring", "cleaning", "vinduespolering", "sanitet",
        "iss ", "coor", "forenede service", "facility",
        "hovedrengøring", "gulvvask"
    ],
    AccountCategory.BANK_FEES: [
        "bankgebyr", "bank fee", "kontogebyr", "overførsel", "transfer fee",
        "danske bank", "nordea", "jyske bank", "nykredit", "mobilepay",
        "kortgebyr", "valutaveksling", "rente bank"
    ],
    AccountCategory.OFFICE_SUPPLIES: [
        "kontor", "office", "papir", "printer", "kuglepen", "pen",
        "lyreco", "staples", "kontorartikler", "ringbind", "post-it",
        "hæftemaskine", "tape", "saks"
    ],
    AccountCategory.RAW_MATERIALS: [
        "vare", "goods", "materiale", "material", "råvare", "lager",
        "komponenter", "dele", "parts", "indkøb varer",
        "varekøb", "eu-erhverv", "innergemeinschaftliche", "eu-leverance",
        "laptop", "probook", "docking", "backpack"
    ],
    AccountCategory.SUBCONTRACTOR: [
        "underentreprenør", "subcontractor", "fremmed arbejde", "entreprise",
        "håndværker", "el-installation", "vvs", "murer", "tømrer",
        "maler", "nedrivning", "vandhaner", "rør og fittings",
        "vedligeholdelse", "reparation bygning"
    ],
    AccountCategory.PERSONNEL: [
        "personale", "staff", "medarbejder", "employee", "kantine",
        "frugtordning", "kaffe", "firmafest", "julegave",
        "kaffe stor", "croissant", "morgenmad", "frokost til medarbejder"
    ],
    AccountCategory.PREPAYMENT: [
        "forudbetaling", "prepayment", "deposit", "depositum", "aconto",
        "forskud", "advance payment", "rate 1", "delbet"
    ],
    AccountCategory.GOVERNMENT: [
        "skat", "told", "afgift", "moms afregning", "a-skat", "am-bidrag",
        "atp", "feriepenge", "arbejdsmarkedsbidrag"
    ],
    AccountCategory.LEASING: [
        "leasing", "lease", "finansiel", "operationel", "afdrag",
        "nordea finans", "jyske finans", "danske leasing",
        "leasingydelse", "restværdi"
    ],
    AccountCategory.FIXED_ASSET: [
        "anlæg", "asset", "inventar", "furniture", "møbel", "kontorstol",
        "skrivebord", "reol", "maskine", "machine", "equipment",
        "bekant", "markus", "ikea business"
    ],
}

# Category to default account mapping
CATEGORY_TO_ACCOUNT: Dict[AccountCategory, Tuple[str, str]] = {
    AccountCategory.OFFICE_SUPPLIES: ("6300", "Kontorartikler"),
    AccountCategory.IT_EQUIPMENT: ("6310", "IT-udgifter"),
    AccountCategory.SOFTWARE: ("6320", "Software og licenser"),
    AccountCategory.TELECOM: ("6400", "Telefon og internet"),
    AccountCategory.FUEL: ("6710", "Brændstof"),
    AccountCategory.VEHICLE: ("6700", "Bilomkostninger"),
    AccountCategory.RENT: ("6010", "Husleje"),
    AccountCategory.UTILITIES: ("6020", "El, vand og varme"),
    AccountCategory.INSURANCE: ("6600", "Forsikringer"),
    AccountCategory.LEGAL: ("7200", "Advokat og revisor"),
    AccountCategory.ACCOUNTING: ("7200", "Advokat og revisor"),
    AccountCategory.CONSULTING: ("7300", "Konsulenthonorar"),
    AccountCategory.MARKETING: ("7000", "Reklame og markedsføring"),
    AccountCategory.TRAVEL: ("6800", "Rejse og ophold"),
    AccountCategory.REPRESENTATION: ("6900", "Repræsentation"),
    AccountCategory.EDUCATION: ("7100", "Faglitteratur og kurser"),
    AccountCategory.POSTAL: ("6500", "Porto og gebyrer"),
    AccountCategory.CLEANING: ("6030", "Rengøring"),
    AccountCategory.BANK_FEES: ("8600", "Bankgebyrer"),
    AccountCategory.RAW_MATERIALS: ("4000", "Varekøb"),
    AccountCategory.SUBCONTRACTOR: ("6200", "Vedligeholdelse"),
    AccountCategory.PERSONNEL: ("5300", "Andre personaleomkostninger"),
    AccountCategory.PREPAYMENT: ("1200", "Forudbetalte omkostninger"),
    AccountCategory.GOVERNMENT: ("2610", "Skyldig A-skat"),
    AccountCategory.LEASING: ("8400", "Renteudgifter"),
    AccountCategory.FIXED_ASSET: ("1500", "Driftsmidler og inventar"),
}

# ==================== MOMSFRI (VAT EXEMPT) KEYWORDS ====================

MOMSFRI_KEYWORDS: List[str] = [
    # Insurance
    "forsikring", "insurance", "forsikringspræmie", "police",
    "erhvervsforsikring", "ansvarsforsikring", "arbejdsskadeforsikring",
    # Banking
    "bankgebyr", "kontogebyr", "overførselsgebyr", "rente",
    "gebyr bank", "kortgebyr", "valutaomkostning",
    # International transport
    "international", "flybillet", "flight", "fly ", "lufthavn",
    "international transport", "eksport", "import fragt",
    # Government
    "skat ", "told", "afgift", "moms afregning", "a-skat",
    "am-bidrag", "atp", "registreringsafgift",
    # Exempt services
    "uddannelse momsfri", "sundhed", "social", "kultur momsfri"
]

# ==================== CURRENCY DETECTION ====================

CURRENCY_PATTERNS: Dict[str, List[str]] = {
    "EUR": [
        r"\beur\b", r"€", r"\beuro\b", r"\beuros\b",
        r"germany", r"deutschland", r"france", r"spain", r"italy",
        r"netherlands", r"belgium", r"austria", r"ireland",
        r"vatid:\s*de", r"vat:\s*de", r"mwst", r"mehrwertsteuer"
    ],
    "USD": [
        r"\busd\b", r"\$\s*[\d,]+", r"us\s*dollar", r"united states",
        r"usa", r"america", r"seattle", r"california", r"new york",
        r"tax id.*\d{2}-\d{7}"
    ],
    "GBP": [
        r"\bgbp\b", r"£", r"pound", r"sterling", r"united kingdom",
        r"england", r"london", r"uk\b"
    ],
    "SEK": [
        r"\bsek\b", r"swedish", r"sverige", r"sweden", r"stockholm",
        r"org\.nr.*\d{6}-\d{4}", r"kronor"
    ],
    "NOK": [
        r"\bnok\b", r"norwegian", r"norge", r"norway", r"oslo",
        r"org\.nr.*\d{9}", r"mva\b"
    ],
    "DKK": [
        r"\bdkk\b", r"\bkr\b", r"danish", r"danmark", r"denmark",
        r"cvr", r"københavn", r"copenhagen"
    ],
}

# ==================== ASSET VS EXPENSE RULES ====================

ASSET_KEYWORDS: List[str] = [
    "anlæg", "asset", "inventar", "furniture", "møbel",
    "maskine", "machine", "equipment", "køretøj", "vehicle",
    "bil ", "car ", "computer", "laptop", "server",
    "kontormøbel", "reol", "skrivebord", "stol"
]

EXPENSE_KEYWORDS: List[str] = [
    "service", "abonnement", "subscription", "måned", "month",
    "reparation", "repair", "vedligeholdelse", "maintenance",
    "forbrug", "consumption", "årlig", "annual fee"
]


# ==================== RULE ENGINE CLASS ====================

class DeterministicRuleEngine:
    """Post-AI deterministic rule engine for improving accuracy"""
    
    def __init__(self, company_config: Optional[CompanyConfig] = None):
        self.config = company_config or CompanyConfig()
        self._build_keyword_index()
    
    def _build_keyword_index(self):
        """Build optimized keyword lookup structures"""
        # Flatten all keywords for quick category lookup
        self._category_keywords: Dict[str, AccountCategory] = {}
        for category, keywords in ACCOUNT_CATEGORY_KEYWORDS.items():
            for kw in keywords:
                self._category_keywords[kw.lower()] = category
    
    def apply_rules(self, ai_result: Dict, ocr_text: str) -> Dict:
        """
        Apply all deterministic rules to improve AI extraction.
        
        Args:
            ai_result: The AI extraction result
            ocr_text: Original OCR text for keyword analysis
            
        Returns:
            Enhanced result with rule-based corrections
        """
        result = ai_result.copy()
        text_lower = ocr_text.lower()
        
        # Track which rules were applied
        result["_rules_applied"] = []
        
        # 1. Currency detection (before other rules as it affects thresholds)
        result = self._apply_currency_rules(result, text_lower)
        
        # 2. VAT code rules (MOMSFRI detection)
        result = self._apply_vat_rules(result, text_lower)
        
        # 3. Account category rules
        result = self._apply_account_category_rules(result, text_lower)
        
        # 4. Asset vs expense threshold rules
        result = self._apply_asset_expense_rules(result, text_lower)
        
        # 5. Journal rules
        result = self._apply_journal_rules(result, text_lower)
        
        return result
    
    def _apply_currency_rules(self, result: Dict, text_lower: str) -> Dict:
        """Detect and correct currency based on text patterns"""
        detected_currency = None
        detection_confidence = 0
        
        for currency, patterns in CURRENCY_PATTERNS.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matches += 1
            
            # More matches = higher confidence
            if matches > detection_confidence:
                detection_confidence = matches
                detected_currency = currency
        
        # Only override if we have strong detection (2+ matches) and it differs
        current_currency = result.get("currency", "DKK")
        if detected_currency and detection_confidence >= 2 and detected_currency != current_currency:
            result["currency"] = detected_currency
            result["_rules_applied"].append(f"currency_detected:{detected_currency}")
        
        return result
    
    def _apply_vat_rules(self, result: Dict, text_lower: str) -> Dict:
        """Apply MOMSFRI and other VAT rules"""
        current_vat = result.get("vat_code", "")
        vat_amount = float(result.get("vat_amount", 0) or 0)
        
        # Check for MOMSFRI keywords
        momsfri_matches = sum(1 for kw in MOMSFRI_KEYWORDS if kw.lower() in text_lower)
        
        # Strong signal for MOMSFRI: multiple keywords AND zero VAT
        if momsfri_matches >= 2 and vat_amount == 0:
            # Determine specific type
            if any(kw in text_lower for kw in ["forsikring", "insurance", "præmie"]):
                result["vat_code"] = "MOMSFRI"
                result["_rules_applied"].append("vat_momsfri:insurance")
            elif any(kw in text_lower for kw in ["bankgebyr", "kontogebyr", "rente"]):
                result["vat_code"] = "MOMSFRI"
                result["_rules_applied"].append("vat_momsfri:bank_fees")
            elif any(kw in text_lower for kw in ["fly", "flight", "international"]):
                result["vat_code"] = "MOMSFRI"
                result["_rules_applied"].append("vat_momsfri:international_transport")
            elif any(kw in text_lower for kw in ["skat", "a-skat", "am-bidrag", "atp"]):
                result["vat_code"] = "IKKEMOMS"
                result["_rules_applied"].append("vat_ikkemoms:government")
        
        # Check for EU reverse charge vs EU goods
        if current_vat in ["IREV", "IEU"]:
            # EU goods keywords
            goods_keywords = ["vare", "goods", "produkt", "hardware", "laptop", "equipment", "lieferung", "delivery"]
            # EU services keywords
            service_keywords = ["service", "license", "licens", "subscription", "abonnement", "maintenance", "support"]
            
            goods_count = sum(1 for kw in goods_keywords if kw in text_lower)
            services_count = sum(1 for kw in service_keywords if kw in text_lower)
            
            if goods_count > services_count and current_vat != "IEU":
                result["vat_code"] = "IEU"
                result["_rules_applied"].append("vat_eu_goods_detected")
            elif services_count > goods_count and current_vat != "IREV":
                result["vat_code"] = "IREV"
                result["_rules_applied"].append("vat_eu_services_detected")
        
        return result
    
    def _apply_account_category_rules(self, result: Dict, text_lower: str) -> Dict:
        """Determine account based on keyword category matching"""
        
        # Special case: EU goods purchases (account 4100)
        if result.get("vat_code") == "IEU":
            eu_goods_keywords = ["laptop", "probook", "hardware", "equipment", "lieferung", 
                                "delivery", "artikel", "produkt", "stück", "stk"]
            if any(kw in text_lower for kw in eu_goods_keywords):
                result["suggested_account"] = "4100"
                result["suggested_account_name"] = "Varekøb EU"
                result["_rules_applied"].append("account_rule:eu_goods_purchase")
                return result
        
        # Score each category
        category_scores: Dict[AccountCategory, int] = {}
        
        for category, keywords in ACCOUNT_CATEGORY_KEYWORDS.items():
            score = 0
            for kw in keywords:
                if kw.lower() in text_lower:
                    # Longer keywords get more weight
                    score += len(kw.split())
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return result
        
        # Get top category
        top_category = max(category_scores.keys(), key=lambda c: category_scores[c])
        top_score = category_scores[top_category]
        
        # Only apply if strong signal (score >= 2)
        if top_score >= 2:
            account_code, account_name = CATEGORY_TO_ACCOUNT.get(
                top_category, 
                (result.get("suggested_account"), result.get("suggested_account_name"))
            )
            
            # Check if this is different from AI suggestion
            current_account = result.get("suggested_account", "")
            
            # Don't override if AI suggested a closely related account
            if account_code and account_code != current_account:
                # Check if they're in the same category (first 2 digits)
                if account_code[:2] != current_account[:2]:
                    result["suggested_account"] = account_code
                    result["suggested_account_name"] = account_name
                    result["_rules_applied"].append(f"account_category:{top_category.value}")
        
        return result
    
    def _apply_asset_expense_rules(self, result: Dict, text_lower: str) -> Dict:
        """Apply asset vs expense threshold and keyword rules"""
        
        if not self.config.enable_asset_detection:
            return result
        
        net_amount = float(result.get("net_amount", 0) or 0)
        current_account = result.get("suggested_account", "")
        
        # Check if amount exceeds asset threshold
        amount_is_high = net_amount >= self.config.asset_threshold_dkk
        
        # Check for asset keywords
        asset_keyword_count = sum(1 for kw in ASSET_KEYWORDS if kw in text_lower)
        expense_keyword_count = sum(1 for kw in EXPENSE_KEYWORDS if kw in text_lower)
        
        # Strong asset signal: high amount AND asset keywords dominate
        is_likely_asset = (
            amount_is_high and 
            asset_keyword_count > expense_keyword_count and
            asset_keyword_count >= 2
        )
        
        # Check if current account is an expense account (6xxx, 7xxx)
        is_expense_account = current_account.startswith(('6', '7'))
        
        if is_likely_asset and is_expense_account:
            # Determine specific asset type
            if any(kw in text_lower for kw in ["bil", "car", "køretøj", "vehicle", "mercedes", "toyota", "vw"]):
                result["suggested_account"] = "1520"
                result["suggested_account_name"] = "Biler"
                result["_rules_applied"].append("asset_rule:vehicle")
            elif any(kw in text_lower for kw in ["computer", "laptop", "server", "it-udstyr", "edb"]):
                result["suggested_account"] = "1510"
                result["suggested_account_name"] = "Edb-udstyr"
                result["_rules_applied"].append("asset_rule:it_equipment")
            elif any(kw in text_lower for kw in ["møbel", "inventar", "skrivebord", "stol", "reol"]):
                result["suggested_account"] = "1500"
                result["suggested_account_name"] = "Driftsmidler og inventar"
                result["_rules_applied"].append("asset_rule:furniture")
            else:
                result["suggested_account"] = "1500"
                result["suggested_account_name"] = "Driftsmidler og inventar"
                result["_rules_applied"].append("asset_rule:general")
        
        return result
    
    def _apply_journal_rules(self, result: Dict, text_lower: str) -> Dict:
        """Apply journal selection rules"""
        
        current_journal = result.get("journal", "KOB")
        
        # Cash payment indicators
        cash_keywords = ["kontant", "cash", "betalt kontant", "kvittering", "bon nr"]
        if any(kw in text_lower for kw in cash_keywords):
            if current_journal != "KASSE":
                result["journal"] = "KASSE"
                result["_rules_applied"].append("journal_rule:cash_payment")
        
        # Bank fee indicators
        if any(kw in text_lower for kw in ["bankgebyr", "kontogebyr", "gebyrspecifikation"]):
            if current_journal != "BANK":
                result["journal"] = "BANK"
                result["_rules_applied"].append("journal_rule:bank_fees")
        
        return result
    
    def get_category_for_text(self, text: str) -> Optional[AccountCategory]:
        """Get the most likely account category for a piece of text"""
        text_lower = text.lower()
        
        category_scores: Dict[AccountCategory, int] = {}
        for category, keywords in ACCOUNT_CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores.keys(), key=lambda c: category_scores[c])
        return None


# ==================== SINGLETON INSTANCE ====================

_default_engine: Optional[DeterministicRuleEngine] = None

def get_rule_engine(config: Optional[CompanyConfig] = None) -> DeterministicRuleEngine:
    """Get or create the default rule engine"""
    global _default_engine
    if _default_engine is None or config is not None:
        _default_engine = DeterministicRuleEngine(config)
    return _default_engine

def apply_deterministic_rules(ai_result: Dict, ocr_text: str, 
                               config: Optional[CompanyConfig] = None) -> Dict:
    """Convenience function to apply all rules"""
    engine = get_rule_engine(config)
    return engine.apply_rules(ai_result, ocr_text)
