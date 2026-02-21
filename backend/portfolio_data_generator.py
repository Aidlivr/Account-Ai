# Mock Data Generator for Portfolio Risk Platform
# Generates realistic Danish client portfolios with transactions and anomalies

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import math

# ==================== DANISH COMPANY DATA ====================

DANISH_COMPANY_NAMES = [
    ("Nordisk Handel ApS", "trading", "retail"),
    ("TechStart Denmark A/S", "technology", "software"),
    ("Café Strøget IVS", "hospitality", "restaurant"),
    ("Maritime Solutions ApS", "logistics", "shipping"),
    ("Green Energy DK A/S", "energy", "renewable"),
    ("København Consulting", "services", "consulting"),
    ("Dansk Bygge & Anlæg ApS", "construction", "building"),
    ("Nordic Food Import A/S", "trading", "wholesale"),
    ("FinTech Nordic ApS", "technology", "fintech"),
    ("Aarhus Manufacturing A/S", "manufacturing", "industrial"),
    ("Scandia Logistics ApS", "logistics", "transport"),
    ("Digital Marketing DK", "services", "marketing"),
    ("BioTech Research A/S", "technology", "biotech"),
    ("Retail Solutions Nordic", "retail", "ecommerce"),
    ("Clean Services Danmark", "services", "cleaning"),
    ("Odense IT Solutions", "technology", "it_services"),
    ("Nordic Property Invest", "real_estate", "investment"),
    ("Danish Design Studio", "services", "design"),
    ("Aalborg Produktion A/S", "manufacturing", "production"),
    ("Vejle Transport ApS", "logistics", "freight"),
    ("Esbjerg Shipping A/S", "logistics", "maritime"),
    ("Roskilde Retail Group", "retail", "chain"),
    ("Kolding Konsulent ApS", "services", "advisory"),
    ("Horsens Hardware A/S", "retail", "electronics"),
    ("Fredericia Foods ApS", "manufacturing", "food"),
]

DANISH_VENDOR_NAMES = [
    "TDC Erhverv", "Dansk Supermarked", "ISS Facility Services",
    "PostNord Danmark", "KPMG Denmark", "Deloitte Danmark",
    "Microsoft Danmark", "IBM Danmark", "Nets Denmark",
    "Beierholm", "EY Denmark", "PwC Denmark",
    "Atea Danmark", "Dustin Denmark", "Logitech Nordic",
    "Office Depot", "Lyreco Danmark", "Staples Solutions",
    "El-Salg", "Elgiganten Erhverv", "Computersalg",
    "Silvan Erhverv", "Bauhaus Pro", "STARK Danmark",
    "Circle K Business", "OK Erhverv", "Q8 Business",
    "SAS Business", "DSB Erhverv", "Scandlines Business",
    "Norlys Erhverv", "Ørsted Business", "Andel Energi",
]

EXPENSE_CATEGORIES = {
    "6100": {"name": "Husleje", "avg_monthly": 25000, "variance": 0.05},
    "6200": {"name": "El, vand, varme", "avg_monthly": 8000, "variance": 0.15},
    "6310": {"name": "IT-udstyr", "avg_monthly": 3500, "variance": 0.40},
    "6320": {"name": "Software & licenser", "avg_monthly": 5000, "variance": 0.20},
    "6510": {"name": "Kontorartikler", "avg_monthly": 2000, "variance": 0.30},
    "6520": {"name": "Telefon & internet", "avg_monthly": 3000, "variance": 0.10},
    "6610": {"name": "Revisor & rådgivning", "avg_monthly": 8000, "variance": 0.25},
    "6620": {"name": "Juridisk bistand", "avg_monthly": 4000, "variance": 0.50},
    "6800": {"name": "Rejser & transport", "avg_monthly": 6000, "variance": 0.35},
    "6820": {"name": "Repræsentation", "avg_monthly": 3000, "variance": 0.40},
    "6830": {"name": "Reklame & marketing", "avg_monthly": 10000, "variance": 0.45},
    "7100": {"name": "Lønninger", "avg_monthly": 150000, "variance": 0.08},
    "7200": {"name": "Pensionsbidrag", "avg_monthly": 15000, "variance": 0.08},
    "7300": {"name": "ATP & sociale bidrag", "avg_monthly": 5000, "variance": 0.08},
}

STAFF_MEMBERS = [
    {"name": "Maria Jensen", "role": "junior", "experience_months": 8},
    {"name": "Anders Nielsen", "role": "junior", "experience_months": 14},
    {"name": "Sofie Larsen", "role": "senior", "experience_months": 48},
    {"name": "Lars Pedersen", "role": "senior", "experience_months": 72},
    {"name": "Emma Christensen", "role": "junior", "experience_months": 6},
]


# ==================== MOCK DATA GENERATOR ====================

class PortfolioDataGenerator:
    """Generates realistic mock data for the portfolio risk platform"""
    
    def __init__(self, firm_id: str):
        self.firm_id = firm_id
        self.clients = []
        self.transactions = []
        self.exceptions = []
        
    def generate_full_portfolio(self, num_clients: int = 25) -> Dict[str, Any]:
        """Generate complete portfolio with clients, transactions, and exceptions"""
        
        # Generate clients
        self.clients = self._generate_clients(num_clients)
        
        # Generate transactions for each client
        for client in self.clients:
            client_transactions = self._generate_transactions(client)
            self.transactions.extend(client_transactions)
        
        # Detect and generate exceptions
        self.exceptions = self._generate_exceptions()
        
        # Calculate risk scores
        self._calculate_risk_scores()
        
        return {
            "firm_id": self.firm_id,
            "clients": self.clients,
            "transactions": self.transactions,
            "exceptions": self.exceptions,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_clients(self, num_clients: int) -> List[Dict]:
        """Generate realistic Danish client companies"""
        clients = []
        
        # Use all predefined companies up to num_clients
        companies_to_use = DANISH_COMPANY_NAMES[:num_clients]
        
        for i, (name, industry, sub_industry) in enumerate(companies_to_use):
            # Generate realistic CVR number (8 digits)
            cvr = f"{random.randint(10000000, 99999999)}"
            
            # Assign staff member
            staff = random.choice(STAFF_MEMBERS)
            
            # Random company size affects transaction volume
            size_factor = random.uniform(0.5, 2.0)
            
            # VAT deadline (quarterly: Mar 1, Jun 1, Sep 1, Dec 1)
            today = datetime.now(timezone.utc)
            next_deadlines = [
                datetime(today.year, 3, 1, tzinfo=timezone.utc),
                datetime(today.year, 6, 1, tzinfo=timezone.utc),
                datetime(today.year, 9, 1, tzinfo=timezone.utc),
                datetime(today.year, 12, 1, tzinfo=timezone.utc),
            ]
            # Find next deadline
            vat_deadline = None
            for d in next_deadlines:
                if d > today:
                    vat_deadline = d
                    break
            if not vat_deadline:
                vat_deadline = datetime(today.year + 1, 3, 1, tzinfo=timezone.utc)
            
            days_to_vat = (vat_deadline - today).days
            
            client = {
                "id": str(uuid.uuid4()),
                "firm_id": self.firm_id,
                "name": name,
                "cvr": cvr,
                "industry": industry,
                "sub_industry": sub_industry,
                "size_factor": size_factor,
                "assigned_staff": staff["name"],
                "staff_role": staff["role"],
                "vat_deadline": vat_deadline.isoformat(),
                "days_to_vat_deadline": days_to_vat,
                "created_at": datetime.now(timezone.utc).isoformat(),
                # Risk metrics (calculated later)
                "risk_score": 0,
                "risk_level": "normal",
                "exception_count": 0,
                "open_exceptions": 0,
                "last_review_date": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))).isoformat(),
            }
            clients.append(client)
        
        return clients
    
    def _generate_transactions(self, client: Dict) -> List[Dict]:
        """Generate 6 months of transactions for a client"""
        transactions = []
        
        # Generate 6 months of history
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=180)
        
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:
                # Generate daily transactions
                daily_count = random.randint(2, 8)
                
                for _ in range(daily_count):
                    transaction = self._generate_single_transaction(client, current_date)
                    transactions.append(transaction)
            
            current_date += timedelta(days=1)
        
        # Inject anomalies for some clients
        if random.random() < 0.4:  # 40% of clients have anomalies
            self._inject_anomalies(client, transactions)
        
        return transactions
    
    def _generate_single_transaction(self, client: Dict, date: datetime) -> Dict:
        """Generate a single transaction"""
        
        # Select expense category
        account_code = random.choice(list(EXPENSE_CATEGORIES.keys()))
        category = EXPENSE_CATEGORIES[account_code]
        
        # Calculate amount with variance
        base_amount = category["avg_monthly"] / 20  # ~20 working days
        variance = category["variance"]
        amount = base_amount * client["size_factor"] * random.uniform(1 - variance, 1 + variance)
        amount = round(amount, 2)
        
        # VAT calculation (25% standard rate)
        vat_rate = 0.25
        if account_code in ["7100", "7200", "7300"]:  # Salaries - no VAT
            vat_rate = 0
        
        net_amount = round(amount / (1 + vat_rate), 2) if vat_rate > 0 else amount
        vat_amount = round(amount - net_amount, 2)
        
        # Select vendor
        vendor = random.choice(DANISH_VENDOR_NAMES)
        
        # Assign posting staff
        staff = random.choice(STAFF_MEMBERS)
        
        return {
            "id": str(uuid.uuid4()),
            "client_id": client["id"],
            "firm_id": self.firm_id,
            "date": date.isoformat(),
            "vendor_name": vendor,
            "description": category["name"],
            "account_code": account_code,
            "account_name": category["name"],
            "net_amount": net_amount,
            "vat_amount": vat_amount,
            "total_amount": amount,
            "vat_code": "I25" if vat_rate > 0 else "MOMSFRI",
            "currency": "DKK",
            "posted_by": staff["name"],
            "posted_by_role": staff["role"],
            "posted_at": (date + timedelta(hours=random.randint(8, 17))).isoformat(),
            "invoice_number": f"INV-{random.randint(10000, 99999)}",
            "status": "posted",
        }
    
    def _inject_anomalies(self, client: Dict, transactions: List[Dict]) -> None:
        """Inject realistic anomalies into transaction history"""
        
        anomaly_type = random.choice([
            "expense_spike",
            "duplicate_invoice",
            "unusual_vendor",
            "vat_variance",
            "pattern_deviation"
        ])
        
        if anomaly_type == "expense_spike":
            # Create a large expense spike
            recent_transactions = [t for t in transactions if t["date"] > (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()]
            if recent_transactions:
                target = random.choice(recent_transactions)
                target["total_amount"] = target["total_amount"] * random.uniform(8, 15)
                target["net_amount"] = round(target["total_amount"] / 1.25, 2)
                target["vat_amount"] = round(target["total_amount"] - target["net_amount"], 2)
                target["_anomaly_type"] = "expense_spike"
        
        elif anomaly_type == "duplicate_invoice":
            # Create a duplicate invoice
            if len(transactions) > 10:
                original = random.choice(transactions[-30:])
                duplicate = original.copy()
                duplicate["id"] = str(uuid.uuid4())
                duplicate["date"] = (datetime.fromisoformat(original["date"].replace('Z', '+00:00')) + timedelta(days=random.randint(1, 5))).isoformat()
                duplicate["_anomaly_type"] = "duplicate_invoice"
                duplicate["_duplicate_of"] = original["id"]
                transactions.append(duplicate)
        
        elif anomaly_type == "unusual_vendor":
            # Add transaction from unusual/new vendor
            unusual_transaction = self._generate_single_transaction(client, datetime.now(timezone.utc) - timedelta(days=random.randint(1, 14)))
            unusual_transaction["vendor_name"] = f"Unknown Vendor {random.randint(100, 999)}"
            unusual_transaction["total_amount"] = random.uniform(15000, 50000)
            unusual_transaction["net_amount"] = round(unusual_transaction["total_amount"] / 1.25, 2)
            unusual_transaction["vat_amount"] = round(unusual_transaction["total_amount"] - unusual_transaction["net_amount"], 2)
            unusual_transaction["_anomaly_type"] = "unusual_vendor"
            transactions.append(unusual_transaction)
        
        elif anomaly_type == "vat_variance":
            # Create VAT coding issue
            recent = [t for t in transactions if t["vat_code"] == "I25"][-5:]
            if recent:
                target = random.choice(recent)
                target["vat_code"] = "MOMSFRI"  # Should have VAT but coded as exempt
                target["vat_amount"] = 0
                target["_anomaly_type"] = "vat_variance"
        
        elif anomaly_type == "pattern_deviation":
            # Unusual account usage
            recent_transactions = [t for t in transactions if t["date"] > (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()]
            if recent_transactions:
                target = random.choice(recent_transactions)
                # Change to unusual account for this vendor
                target["account_code"] = "6620"  # Legal fees for a normally different expense
                target["account_name"] = "Juridisk bistand"
                target["_anomaly_type"] = "pattern_deviation"
    
    def _generate_exceptions(self) -> List[Dict]:
        """Generate exceptions from transactions with anomalies"""
        exceptions = []
        
        for transaction in self.transactions:
            if "_anomaly_type" in transaction:
                client = next((c for c in self.clients if c["id"] == transaction["client_id"]), None)
                if not client:
                    continue
                
                exception = self._create_exception(transaction, client)
                exceptions.append(exception)
        
        # Also generate some AI-detected pattern exceptions
        for client in self.clients:
            if random.random() < 0.3:  # 30% chance of pattern-based exception
                exception = self._create_pattern_exception(client)
                if exception:
                    exceptions.append(exception)
        
        return exceptions
    
    def _create_exception(self, transaction: Dict, client: Dict) -> Dict:
        """Create an exception record from an anomalous transaction"""
        
        anomaly_type = transaction.get("_anomaly_type", "unknown")
        
        # Determine severity
        severity_map = {
            "expense_spike": "high",
            "duplicate_invoice": "high",
            "unusual_vendor": "medium",
            "vat_variance": "high",
            "pattern_deviation": "medium",
        }
        severity = severity_map.get(anomaly_type, "low")
        
        # Generate explanation
        explanations = {
            "expense_spike": f"Transaction amount ({transaction['total_amount']:,.0f} DKK) significantly exceeds the 6-month average for account {transaction['account_code']} ({transaction['account_name']}). Historical average: {transaction['total_amount']/10:,.0f} DKK.",
            "duplicate_invoice": f"Potential duplicate detected. Invoice {transaction['invoice_number']} from {transaction['vendor_name']} matches a previous entry within 5 days with identical amount.",
            "unusual_vendor": f"First transaction from vendor '{transaction['vendor_name']}'. No historical pattern established. Amount: {transaction['total_amount']:,.0f} DKK.",
            "vat_variance": f"VAT code mismatch detected. Transaction coded as '{transaction['vat_code']}' but vendor {transaction['vendor_name']} typically charges 25% VAT.",
            "pattern_deviation": f"Unusual account classification. {transaction['vendor_name']} expenses typically posted to different account. Current: {transaction['account_code']} ({transaction['account_name']}).",
        }
        
        return {
            "id": str(uuid.uuid4()),
            "firm_id": self.firm_id,
            "client_id": client["id"],
            "client_name": client["name"],
            "transaction_id": transaction["id"],
            "type": anomaly_type,
            "severity": severity,
            "title": self._get_exception_title(anomaly_type),
            "description": explanations.get(anomaly_type, "Anomaly detected in transaction."),
            "amount": transaction["total_amount"],
            "vendor": transaction["vendor_name"],
            "account_code": transaction["account_code"],
            "account_name": transaction["account_name"],
            "transaction_date": transaction["date"],
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "status": "open",
            "assigned_to": None,
            "reviewed_by": None,
            "reviewed_at": None,
            "resolution": None,
            "historical_avg": transaction["total_amount"] / random.uniform(5, 15) if anomaly_type == "expense_spike" else None,
            "variance_percent": random.uniform(200, 1500) if anomaly_type == "expense_spike" else None,
        }
    
    def _get_exception_title(self, anomaly_type: str) -> str:
        """Get human-readable title for exception type"""
        titles = {
            "expense_spike": "Expense Variance Detected",
            "duplicate_invoice": "Potential Duplicate Invoice",
            "unusual_vendor": "New Vendor Transaction",
            "vat_variance": "VAT Classification Review",
            "pattern_deviation": "Account Classification Deviation",
            "vat_trend": "VAT Trend Anomaly",
        }
        return titles.get(anomaly_type, "Exception Detected")
    
    def _create_pattern_exception(self, client: Dict) -> Dict:
        """Create a pattern-based exception (VAT trends, etc.)"""
        
        return {
            "id": str(uuid.uuid4()),
            "firm_id": self.firm_id,
            "client_id": client["id"],
            "client_name": client["name"],
            "transaction_id": None,
            "type": "vat_trend",
            "severity": random.choice(["medium", "high"]),
            "title": "VAT Trend Anomaly",
            "description": f"Quarter-over-quarter VAT deduction ratio changed by {random.uniform(15, 40):.1f}%. Previous quarter: {random.uniform(20, 30):.1f}%, Current: {random.uniform(35, 50):.1f}%. Recommend verification before VAT submission.",
            "amount": None,
            "vendor": None,
            "account_code": None,
            "account_name": None,
            "transaction_date": None,
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "status": "open",
            "assigned_to": None,
            "reviewed_by": None,
            "reviewed_at": None,
            "resolution": None,
            "previous_quarter_ratio": random.uniform(20, 30),
            "current_quarter_ratio": random.uniform(35, 50),
        }
    
    def _calculate_risk_scores(self) -> None:
        """Calculate risk scores for each client"""
        
        for client in self.clients:
            client_exceptions = [e for e in self.exceptions if e["client_id"] == client["id"]]
            
            # Count by severity
            high_count = len([e for e in client_exceptions if e["severity"] == "high"])
            medium_count = len([e for e in client_exceptions if e["severity"] == "medium"])
            low_count = len([e for e in client_exceptions if e["severity"] == "low"])
            
            open_count = len([e for e in client_exceptions if e["status"] == "open"])
            
            # Calculate risk score (0-100)
            risk_score = min(100, (high_count * 30) + (medium_count * 15) + (low_count * 5))
            
            # Add time pressure factor (closer to VAT deadline = higher risk)
            if client["days_to_vat_deadline"] < 14:
                risk_score = min(100, risk_score + 20)
            elif client["days_to_vat_deadline"] < 30:
                risk_score = min(100, risk_score + 10)
            
            # Determine risk level
            if risk_score >= 60:
                risk_level = "high"
            elif risk_score >= 30:
                risk_level = "elevated"
            else:
                risk_level = "normal"
            
            # Update client
            client["risk_score"] = risk_score
            client["risk_level"] = risk_level
            client["exception_count"] = len(client_exceptions)
            client["open_exceptions"] = open_count


# ==================== HELPER FUNCTIONS ====================

def generate_demo_portfolio(firm_id: str, num_clients: int = 25) -> Dict[str, Any]:
    """Generate a complete demo portfolio"""
    generator = PortfolioDataGenerator(firm_id)
    return generator.generate_full_portfolio(num_clients)
