"""
Accountrix — Demo Setup Script
Run this once to create the demo user and seed portfolio data.

Usage:
  python3 setup_demo.py
"""

import asyncio
import uuid
import bcrypt
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# ── Config ──────────────────────────────────────────────────────────────────
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://accountrix:Accountrix2026!@cluster0.f0a4bi3.mongodb.net/accountrix")
DB_NAME   = os.environ.get("DB_NAME", "accountrix")

DEMO_USERS = [
    {
        "email":    "demo@accountrix.dk",
        "password": "Demo123!",
        "name":     "Demo Accountant",
        "role":     "accountant",
    },
    {
        "email":    "admin@accountrix.dk",
        "password": "Admin123!",
        "name":     "Admin User",
        "role":     "admin",
    },
]

# ── Helpers ──────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

# ── Main ─────────────────────────────────────────────────────────────────────
async def main():
    print(f"\n🔗 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    try:
        await client.admin.command("ping")
        print("✅ Connected to MongoDB\n")
    except Exception as e:
        print(f"❌ Cannot connect to MongoDB: {e}")
        print("\nMake sure you have set MONGO_URL correctly.")
        sys.exit(1)

    # ── Create demo users ────────────────────────────────────────────────────
    print("👤 Creating demo users...")
    for u in DEMO_USERS:
        existing = await db.users.find_one({"email": u["email"]})
        if existing:
            # Update password in case it changed
            await db.users.update_one(
                {"email": u["email"]},
                {"$set": {"password": hash_password(u["password"]), "updated_at": now()}}
            )
            print(f"   ↻  Updated:  {u['email']}  (password reset to {u['password']})")
        else:
            user_doc = {
                "id":         str(uuid.uuid4()),
                "email":      u["email"],
                "password":   hash_password(u["password"]),
                "name":       u["name"],
                "role":       u["role"],
                "created_at": now(),
                "updated_at": now(),
            }
            await db.users.insert_one(user_doc)
            print(f"   ✅ Created:  {u['email']}  /  {u['password']}")

    # ── Seed portfolio demo data ──────────────────────────────────────────────
    print("\n📊 Seeding portfolio demo data...")

    # Check if already seeded
    existing_clients = await db.portfolio_clients.count_documents({})
    if existing_clients > 0:
        print(f"   ℹ️  Portfolio already has {existing_clients} clients — skipping seed.")
        print("      (Delete collection 'portfolio_clients' in Atlas to re-seed)")
    else:
        clients = _generate_clients()
        await db.portfolio_clients.insert_many(clients)
        print(f"   ✅ Inserted {len(clients)} portfolio clients")

        exceptions = _generate_exceptions(clients)
        await db.portfolio_exceptions.insert_many(exceptions)
        print(f"   ✅ Inserted {len(exceptions)} portfolio exceptions")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "─"*50)
    print("🎉 Setup complete! You can now log in with:\n")
    print("   Email:    demo@accountrix.dk")
    print("   Password: Demo123!\n")
    print("   Email:    admin@accountrix.dk")
    print("   Password: Admin123!\n")
    print("   URL:      http://localhost:3000/login")
    print("─"*50 + "\n")

    client.close()


# ── Data generators ───────────────────────────────────────────────────────────
def _generate_clients():
    import random
    random.seed(42)

    companies = [
        ("Hansen & Søn ApS",        "12345678", "high"),
        ("Nordisk Teknik A/S",       "23456789", "elevated"),
        ("Grøn Energi ApS",          "34567890", "normal"),
        ("Bjarke Consulting IVS",    "45678901", "high"),
        ("Vestergaard Transport",    "56789012", "normal"),
        ("Petersen Byg A/S",         "67890123", "elevated"),
        ("Dansk Digital ApS",        "78901234", "normal"),
        ("Malmros & Partner",        "89012345", "high"),
        ("Fiducia Revision",         "90123456", "normal"),
        ("Nordjylland Invest A/S",   "01234567", "elevated"),
        ("Holm Arkitekter ApS",      "11223344", "normal"),
        ("Skandia Logistik",         "22334455", "normal"),
        ("Toft & Nielsen ApS",       "33445566", "elevated"),
        ("Bjørn IT Solutions",       "44556677", "high"),
        ("Svendsen Ejendomme",       "55667788", "normal"),
        ("Lykke Media ApS",          "66778899", "normal"),
        ("Agri Nord A/S",            "77889900", "elevated"),
        ("Christensen Dental",       "88990011", "normal"),
        ("Kvist & Larsen ApS",       "99001122", "high"),
        ("ProConsult DK",            "10111213", "normal"),
        ("Baltica Trading ApS",      "21222324", "normal"),
        ("Nexum Services A/S",       "32333435", "elevated"),
        ("Elgaard Finans",           "43444546", "normal"),
        ("Thrane Produktion ApS",    "54555657", "normal"),
        ("Øresund Partners A/S",     "65666768", "high"),
    ]

    staff = ["Mette K.", "Lars P.", "Sofie H.", "Anders N.", "Rikke M."]
    now_ts = datetime.now(timezone.utc)

    clients = []
    for i, (name, cvr, risk_level) in enumerate(companies):
        risk_score = {"high": random.randint(72, 95), "elevated": random.randint(45, 71), "normal": random.randint(10, 44)}[risk_level]
        exc_count  = {"high": random.randint(3, 6), "elevated": random.randint(1, 3), "normal": random.randint(0, 1)}[risk_level]
        vat_days   = random.choice([7, 9, 12, 14, 21, 28, 35, 45, 60])

        clients.append({
            "id":             str(uuid.uuid4()),
            "company_name":   name,
            "cvr_number":     cvr,
            "risk_level":     risk_level,
            "risk_score":     risk_score,
            "exception_count": exc_count,
            "vat_deadline_days": vat_days,
            "assigned_staff": random.choice(staff),
            "last_reviewed":  now_ts.isoformat(),
            "created_at":     now_ts.isoformat(),
            "is_demo":        True,
        })

    return clients


def _generate_exceptions(clients):
    import random
    random.seed(99)

    exc_types = [
        ("expense_spike",    "Expense Spike",       "high"),
        ("duplicate_invoice","Duplicate Invoice",   "medium"),
        ("vat_trend",        "VAT Trend Anomaly",   "high"),
        ("unusual_vendor",   "Unusual Vendor",      "medium"),
        ("vat_variance",     "VAT Variance",        "low"),
        ("pattern_deviation","Pattern Deviation",   "medium"),
    ]

    explanations = {
        "expense_spike":     "Office supplies spending increased 340% vs 3-month average. Likely bulk purchase or data entry error.",
        "duplicate_invoice": "Invoice #INV-2024-0892 appears twice with identical amount and vendor. Possible double entry.",
        "vat_trend":         "VAT deduction rate dropped from 24.8% to 18.2% this quarter. Unusual change requires review.",
        "unusual_vendor":    "First-time vendor 'Meridian Supplies Ltd' with no CVR number. Verify legitimacy before approval.",
        "vat_variance":      "VAT declared differs from calculated amount by 1.247 DKK. Rounding error or missing line item.",
        "pattern_deviation": "Fuel expenses pattern changed significantly. Previous Tuesdays average 420 DKK, now 1.850 DKK.",
    }

    high_risk_clients = [c for c in clients if c["risk_level"] in ("high", "elevated")]
    exceptions = []
    now_ts = datetime.now(timezone.utc)

    for i in range(18):
        client   = random.choice(high_risk_clients)
        exc_type, exc_name, severity = random.choice(exc_types)
        exceptions.append({
            "id":           str(uuid.uuid4()),
            "client_id":    client["id"],
            "client_name":  client["company_name"],
            "type":         exc_type,
            "type_label":   exc_name,
            "severity":     severity,
            "status":       random.choice(["open", "open", "open", "investigating"]),
            "amount":       round(random.uniform(500, 45000), 2),
            "vendor":       f"Vendor {chr(65 + i)}",
            "account_code": random.choice(["4000", "4100", "4200", "5000", "6000"]),
            "date":         now_ts.isoformat(),
            "explanation":  explanations[exc_type],
            "created_at":   now_ts.isoformat(),
            "is_demo":      True,
        })

    return exceptions


if __name__ == "__main__":
    asyncio.run(main())
