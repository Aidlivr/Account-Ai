# Nordic VAT Rules Module
# Modular VAT logic for Denmark, Sweden, Norway
# Currently only Denmark is active

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

# ==================== VAT RULE INTERFACE ====================

class VATRuleEngine(ABC):
    """Abstract base class for country-specific VAT rules"""
    
    @property
    @abstractmethod
    def country_code(self) -> str:
        pass
    
    @property
    @abstractmethod
    def standard_rate(self) -> float:
        pass
    
    @property
    @abstractmethod
    def vat_codes(self) -> List[Dict]:
        pass
    
    @abstractmethod
    def apply_rules(self, invoice_data: Dict, ocr_text: str) -> Dict:
        """Apply country-specific VAT rules to invoice data"""
        pass
    
    @abstractmethod
    def validate_vat_number(self, vat_number: str) -> bool:
        """Validate VAT number format for this country"""
        pass
    
    @abstractmethod
    def calculate_vat(self, net_amount: float, vat_code: str) -> float:
        """Calculate VAT amount based on code"""
        pass


# ==================== DENMARK VAT RULES (ACTIVE) ====================

class DanishVATRules(VATRuleEngine):
    """Danish VAT rules implementation"""
    
    @property
    def country_code(self) -> str:
        return "DK"
    
    @property
    def standard_rate(self) -> float:
        return 25.0
    
    @property
    def vat_codes(self) -> List[Dict]:
        return [
            {"code": "I25", "name": "Indgående moms 25%", "rate": 25.0, "type": "input"},
            {"code": "I0", "name": "Indgående moms 0%", "rate": 0.0, "type": "input"},
            {"code": "IEU", "name": "EU-erhvervelser", "rate": 25.0, "type": "input_eu", "reverse_charge": True},
            {"code": "IREV", "name": "Reverse charge", "rate": 25.0, "type": "input_reverse", "reverse_charge": True},
            {"code": "U25", "name": "Udgående moms 25%", "rate": 25.0, "type": "output"},
            {"code": "U0", "name": "Udgående moms 0%", "rate": 0.0, "type": "output"},
            {"code": "UEU", "name": "Salg til EU", "rate": 0.0, "type": "output_eu"},
            {"code": "UEXP", "name": "Eksport", "rate": 0.0, "type": "output_export"},
            {"code": "MOMSFRI", "name": "Momsfritaget", "rate": 0.0, "type": "exempt"},
        ]
    
    REVERSE_CHARGE_KEYWORDS = [
        "reverse charge",
        "omvendt betalingspligt",
        "intra-community",
        "eu-leverance",
        "momsfri leverance",
        "article 196",
        "artikel 196",
    ]
    
    EU_COUNTRY_CODES = [
        "AT", "BE", "BG", "HR", "CY", "CZ", "EE", "FI", "FR", 
        "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", 
        "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"
    ]
    
    def apply_rules(self, invoice_data: Dict, ocr_text: str) -> Dict:
        """Apply Danish VAT rules"""
        result = invoice_data.copy()
        text_lower = ocr_text.lower()
        
        # Rule 1: Detect reverse charge
        if any(kw in text_lower for kw in self.REVERSE_CHARGE_KEYWORDS):
            result["vat_code"] = "IREV"
            result["_vat_rule"] = "reverse_charge_detected"
            return result
        
        # Rule 2: Detect EU acquisition
        for code in self.EU_COUNTRY_CODES:
            if f" {code}" in ocr_text.upper() or f"VAT {code}" in ocr_text.upper():
                result["vat_code"] = "IEU"
                result["_vat_rule"] = f"eu_acquisition_{code}"
                return result
        
        # Rule 3: Standard Danish VAT
        vat_amount = float(result.get("vat_amount", 0) or 0)
        net_amount = float(result.get("net_amount", 0) or 0)
        
        if net_amount > 0:
            if vat_amount > 0:
                # Calculate effective rate
                rate = (vat_amount / net_amount) * 100
                if 23 <= rate <= 27:  # Approximately 25%
                    result["vat_code"] = "I25"
                    result["_vat_rule"] = "standard_25_percent"
            else:
                # Zero VAT - could be exempt
                result["vat_code"] = "MOMSFRI"
                result["_vat_rule"] = "zero_vat_exempt"
        
        return result
    
    def validate_vat_number(self, vat_number: str) -> bool:
        """Validate Danish CVR number (8 digits)"""
        import re
        # Danish CVR: 8 digits
        if re.match(r"^(DK)?[\s-]?\d{8}$", vat_number.replace(" ", "")):
            return True
        return False
    
    def calculate_vat(self, net_amount: float, vat_code: str) -> float:
        """Calculate VAT based on code"""
        for vc in self.vat_codes:
            if vc["code"] == vat_code:
                return round(net_amount * (vc["rate"] / 100), 2)
        return round(net_amount * 0.25, 2)  # Default to 25%


# ==================== SWEDEN VAT RULES (PREPARED) ====================

class SwedishVATRules(VATRuleEngine):
    """Swedish VAT rules implementation (prepared for future)"""
    
    @property
    def country_code(self) -> str:
        return "SE"
    
    @property
    def standard_rate(self) -> float:
        return 25.0
    
    @property
    def vat_codes(self) -> List[Dict]:
        return [
            {"code": "MP1", "name": "Ingående moms 25%", "rate": 25.0, "type": "input"},
            {"code": "MP2", "name": "Ingående moms 12%", "rate": 12.0, "type": "input"},
            {"code": "MP3", "name": "Ingående moms 6%", "rate": 6.0, "type": "input"},
            {"code": "MP0", "name": "Ingående moms 0%", "rate": 0.0, "type": "input"},
            {"code": "MF", "name": "Momsfri", "rate": 0.0, "type": "exempt"},
            {"code": "OMVAND", "name": "Omvänd skattskyldighet", "rate": 25.0, "type": "reverse"},
        ]
    
    def apply_rules(self, invoice_data: Dict, ocr_text: str) -> Dict:
        """Apply Swedish VAT rules"""
        result = invoice_data.copy()
        
        # Detect rate from amount
        vat_amount = float(result.get("vat_amount", 0) or 0)
        net_amount = float(result.get("net_amount", 0) or 0)
        
        if net_amount > 0 and vat_amount > 0:
            rate = (vat_amount / net_amount) * 100
            
            if 24 <= rate <= 26:
                result["vat_code"] = "MP1"  # 25%
            elif 11 <= rate <= 13:
                result["vat_code"] = "MP2"  # 12%
            elif 5 <= rate <= 7:
                result["vat_code"] = "MP3"  # 6%
            else:
                result["vat_code"] = "MP1"  # Default to 25%
        
        return result
    
    def validate_vat_number(self, vat_number: str) -> bool:
        """Validate Swedish organization number"""
        import re
        # Swedish org number: 10 or 12 digits
        cleaned = vat_number.replace(" ", "").replace("-", "").upper()
        if cleaned.startswith("SE"):
            cleaned = cleaned[2:]
        return bool(re.match(r"^\d{10,12}$", cleaned))
    
    def calculate_vat(self, net_amount: float, vat_code: str) -> float:
        """Calculate VAT based on code"""
        for vc in self.vat_codes:
            if vc["code"] == vat_code:
                return round(net_amount * (vc["rate"] / 100), 2)
        return round(net_amount * 0.25, 2)


# ==================== NORWAY VAT RULES (PREPARED) ====================

class NorwegianVATRules(VATRuleEngine):
    """Norwegian VAT rules implementation (prepared for future)"""
    
    @property
    def country_code(self) -> str:
        return "NO"
    
    @property
    def standard_rate(self) -> float:
        return 25.0
    
    @property
    def vat_codes(self) -> List[Dict]:
        return [
            {"code": "MV1", "name": "Inngående mva 25%", "rate": 25.0, "type": "input"},
            {"code": "MV2", "name": "Inngående mva 15%", "rate": 15.0, "type": "input"},  # Food
            {"code": "MV3", "name": "Inngående mva 12%", "rate": 12.0, "type": "input"},  # Transport, hotels
            {"code": "MV0", "name": "Inngående mva 0%", "rate": 0.0, "type": "input"},
            {"code": "MVF", "name": "Mva-fri", "rate": 0.0, "type": "exempt"},
        ]
    
    def apply_rules(self, invoice_data: Dict, ocr_text: str) -> Dict:
        """Apply Norwegian VAT rules"""
        result = invoice_data.copy()
        
        vat_amount = float(result.get("vat_amount", 0) or 0)
        net_amount = float(result.get("net_amount", 0) or 0)
        
        if net_amount > 0 and vat_amount > 0:
            rate = (vat_amount / net_amount) * 100
            
            if 24 <= rate <= 26:
                result["vat_code"] = "MV1"  # 25%
            elif 14 <= rate <= 16:
                result["vat_code"] = "MV2"  # 15%
            elif 11 <= rate <= 13:
                result["vat_code"] = "MV3"  # 12%
            else:
                result["vat_code"] = "MV1"
        
        return result
    
    def validate_vat_number(self, vat_number: str) -> bool:
        """Validate Norwegian organization number"""
        import re
        # Norwegian org number: 9 digits
        cleaned = vat_number.replace(" ", "").replace("NO", "").replace("MVA", "")
        return bool(re.match(r"^\d{9}$", cleaned))
    
    def calculate_vat(self, net_amount: float, vat_code: str) -> float:
        """Calculate VAT based on code"""
        for vc in self.vat_codes:
            if vc["code"] == vat_code:
                return round(net_amount * (vc["rate"] / 100), 2)
        return round(net_amount * 0.25, 2)


# ==================== VAT RULE FACTORY ====================

class VATRuleFactory:
    """Factory for getting country-specific VAT rules"""
    
    _engines: Dict[str, VATRuleEngine] = {}
    _active_country: str = "DK"  # Currently active country
    
    @classmethod
    def register(cls, engine: VATRuleEngine):
        """Register a VAT rule engine"""
        cls._engines[engine.country_code] = engine
    
    @classmethod
    def get(cls, country_code: str = None) -> VATRuleEngine:
        """Get VAT rule engine for country"""
        code = country_code or cls._active_country
        if code not in cls._engines:
            raise ValueError(f"No VAT rules registered for country: {code}")
        return cls._engines[code]
    
    @classmethod
    def set_active_country(cls, country_code: str):
        """Set the active country for VAT rules"""
        if country_code not in cls._engines:
            raise ValueError(f"Cannot activate country {country_code}: not registered")
        cls._active_country = country_code
    
    @classmethod
    def get_available_countries(cls) -> List[str]:
        """Get list of available countries"""
        return list(cls._engines.keys())


# ==================== INITIALIZE DEFAULT RULES ====================

# Register all country rules
VATRuleFactory.register(DanishVATRules())
VATRuleFactory.register(SwedishVATRules())
VATRuleFactory.register(NorwegianVATRules())

# Set Denmark as active (only DK is currently active)
VATRuleFactory.set_active_country("DK")


# ==================== CONVENIENCE FUNCTIONS ====================

def get_vat_rules(country_code: str = None) -> VATRuleEngine:
    """Get VAT rules for a country (defaults to active country)"""
    return VATRuleFactory.get(country_code)

def apply_vat_rules(invoice_data: Dict, ocr_text: str, country_code: str = None) -> Dict:
    """Apply VAT rules to invoice data"""
    engine = VATRuleFactory.get(country_code)
    return engine.apply_rules(invoice_data, ocr_text)

def validate_vat_number(vat_number: str, country_code: str = None) -> bool:
    """Validate VAT number for a country"""
    engine = VATRuleFactory.get(country_code)
    return engine.validate_vat_number(vat_number)
