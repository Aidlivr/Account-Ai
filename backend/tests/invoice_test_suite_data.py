# Invoice Test Suite - Ground Truth Data
# 50 invoices: simulating 25 "real-world patterns" + 25 edge cases

import json
from typing import List, Dict, Any

# ==================== REALISTIC DANISH VENDOR INVOICES (25) ====================
# Simulating common Danish vendor patterns with realistic amounts and formatting

REALISTIC_INVOICES: List[Dict[str, Any]] = [
    # 1. Standard office supplies vendor
    {
        "id": "INV-001",
        "category": "realistic",
        "ocr_text": """
LYRECO DENMARK A/S
Transformervej 12
2860 Søborg
CVR: 10035164

FAKTURA
Fakturanummer: 4521876
Fakturadato: 15-01-2026
Forfaldsdato: 14-02-2026

Kunde: Test Company ApS
Kundenr: 45892

Beskrivelse                      Antal    Pris     Total
------------------------------------------------------
Printerpapir A4 80g             10 pk    89,00    890,00
Kuglepen blå (pakke)             5 pk    45,00    225,00
Ringbind A4                      20 stk   18,50    370,00
Post-it blokke                   8 pk     32,00    256,00

Nettobeløb:                               1.741,00 DKK
Moms 25%:                                   435,25 DKK
Total:                                    2.176,25 DKK

Betalingsoplysninger:
Bank: Danske Bank
Reg.nr: 3409 Kontonr: 0010452789
""",
        "ground_truth": {
            "vendor_name": "LYRECO DENMARK A/S",
            "cvr_number": "10035164",
            "invoice_number": "4521876",
            "invoice_date": "2026-01-15",
            "due_date": "2026-02-14",
            "currency": "DKK",
            "net_amount": 1741.00,
            "vat_amount": 435.25,
            "total_amount": 2176.25,
            "vat_code": "I25",
            "suggested_account": "6300",
            "journal": "KOB"
        }
    },
    # 2. IT equipment vendor
    {
        "id": "INV-002",
        "category": "realistic",
        "ocr_text": """
Dustin A/S
Generatorvej 8B
2860 Søborg
CVR-nr: 25856059

Invoice / Faktura
Invoice No: DK-2026-78542
Date: 22-01-2026
Due Date: 21-02-2026

Bill To:
Test Company ApS
Vestergade 45
1456 København K

Item Description                 Qty    Unit Price    Amount
------------------------------------------------------------
Dell Latitude 5540 Laptop         2     12.450,00   24.900,00
USB-C Docking Station             2      1.895,00    3.790,00
Logitech MX Master 3 Mouse        3        749,00    2.247,00

Subtotal:                                          30.937,00 DKK
VAT (25%):                                          7.734,25 DKK
Total Amount:                                      38.671,25 DKK

Payment Terms: Net 30 days
""",
        "ground_truth": {
            "vendor_name": "Dustin A/S",
            "cvr_number": "25856059",
            "invoice_number": "DK-2026-78542",
            "invoice_date": "2026-01-22",
            "due_date": "2026-02-21",
            "currency": "DKK",
            "net_amount": 30937.00,
            "vat_amount": 7734.25,
            "total_amount": 38671.25,
            "vat_code": "I25",
            "suggested_account": "6310",
            "journal": "KOB"
        }
    },
    # 3. Software license
    {
        "id": "INV-003",
        "category": "realistic",
        "ocr_text": """
Microsoft Denmark ApS
Tuborg Boulevard 12
2900 Hellerup
CVR: 28114207

FAKTURA

Fakturanr.: MS-DK-2026-9854
Dato: 01-02-2026
Betalingsdato: 01-03-2026

Licens oversigt:
Microsoft 365 Business Premium
12 måneder x 5 brugere

Produkt                          Pris
--------------------------------------
Microsoft 365 Business Premium   
5 licenser x 12 mdr              
@ 199,00 kr/mdr/bruger           11.940,00

Subtotal:                        11.940,00 DKK
Moms (25%):                       2.985,00 DKK
I alt:                           14.925,00 DKK
""",
        "ground_truth": {
            "vendor_name": "Microsoft Denmark ApS",
            "cvr_number": "28114207",
            "invoice_number": "MS-DK-2026-9854",
            "invoice_date": "2026-02-01",
            "due_date": "2026-03-01",
            "currency": "DKK",
            "net_amount": 11940.00,
            "vat_amount": 2985.00,
            "total_amount": 14925.00,
            "vat_code": "I25",
            "suggested_account": "6320",
            "journal": "KOB"
        }
    },
    # 4. Cleaning service
    {
        "id": "INV-004",
        "category": "realistic",
        "ocr_text": """
ISS Facility Services A/S
Buddingevej 197
2860 Søborg
CVR-nr: 28503641

Faktura for rengøringsydelser

Fakturanummer: 2026-154789
Fakturadato: 31-01-2026
Betalingsfrist: 14-02-2026

Kunde: Test Company ApS

Periode: Januar 2026

Ydelse                           Beløb
---------------------------------------
Månedlig kontorrengøring         4.500,00
Vinduespolering                    800,00
Ekstra hovedrengøring            1.200,00

Netto:                           6.500,00 DKK
Moms 25%:                        1.625,00 DKK
Total:                           8.125,00 DKK

Betaling via Betalingsservice
""",
        "ground_truth": {
            "vendor_name": "ISS Facility Services A/S",
            "cvr_number": "28503641",
            "invoice_number": "2026-154789",
            "invoice_date": "2026-01-31",
            "due_date": "2026-02-14",
            "currency": "DKK",
            "net_amount": 6500.00,
            "vat_amount": 1625.00,
            "total_amount": 8125.00,
            "vat_code": "I25",
            "suggested_account": "6030",
            "journal": "KOB"
        }
    },
    # 5. Telecom provider
    {
        "id": "INV-005",
        "category": "realistic",
        "ocr_text": """
TDC Erhverv
Teglholmsgade 1
2450 København SV
CVR: 14773908

ERHVERVSFAKTURA

Fakturanr: E-2026-4521876
Udstedt: 01-02-2026
Forfaldsdato: 20-02-2026

Abonnent: Test Company ApS
Kundeid: 78945612

Faktureringsperiode: 01-01-2026 til 31-01-2026

Beskrivelse                             Beløb
---------------------------------------------
Erhverv Fiber 500/500 Mbit              599,00
5 x Mobilabonnementer @199,-            995,00
Udlandsopkald                            87,50
Ekstra data                              50,00

I alt ekskl. moms:                    1.731,50 DKK
Moms 25%:                               432,88 DKK
I alt inkl. moms:                     2.164,38 DKK
""",
        "ground_truth": {
            "vendor_name": "TDC Erhverv",
            "cvr_number": "14773908",
            "invoice_number": "E-2026-4521876",
            "invoice_date": "2026-02-01",
            "due_date": "2026-02-20",
            "currency": "DKK",
            "net_amount": 1731.50,
            "vat_amount": 432.88,
            "total_amount": 2164.38,
            "vat_code": "I25",
            "suggested_account": "6400",
            "journal": "KOB"
        }
    },
    # 6. Accounting firm
    {
        "id": "INV-006",
        "category": "realistic",
        "ocr_text": """
Beierholm
Statsautoriseret Revisionspartnerselskab
Gribskovvej 2
2100 København Ø
CVR: 32895368

FAKTURA

Faktura nr.: 2026-08754
Dato: 15-01-2026
Forfald: 29-01-2026

Klient: Test Company ApS

Honorar for regnskabsassistance
December 2025

Timer    Sats       Beløb
---------------------------
12,5    1.450,00   18.125,00

Subtotal:                  18.125,00 DKK
Moms 25%:                   4.531,25 DKK
Total:                     22.656,25 DKK

Betalingsinfo:
Reg. 9570 Konto 1478523698
""",
        "ground_truth": {
            "vendor_name": "Beierholm",
            "cvr_number": "32895368",
            "invoice_number": "2026-08754",
            "invoice_date": "2026-01-15",
            "due_date": "2026-01-29",
            "currency": "DKK",
            "net_amount": 18125.00,
            "vat_amount": 4531.25,
            "total_amount": 22656.25,
            "vat_code": "I25",
            "suggested_account": "7200",
            "journal": "KOB"
        }
    },
    # 7. Vehicle fuel
    {
        "id": "INV-007",
        "category": "realistic",
        "ocr_text": """
OK a.m.b.a.
Åhave Parkvej 11
8260 Viby J
CVR-nr: 42759216

Faktura

Fakturanr: OK-2026-785412
Dato: 31-01-2026
Betalingsdato: 14-02-2026

Kunde: Test Company ApS
Kortnr: 4521-****-8745

Brændstofkøb januar 2026

Dato        Station          Liter    Beløb
-------------------------------------------
05-01       OK Vesterbro     45,2     542,40
12-01       OK Amager        38,7     464,40
19-01       OK Nørrebro      42,1     505,20
26-01       OK Østerbro      39,5     474,00

Total brændstof:                   1.986,00
Moms 25%:                            496,50
Total:                             2.482,50 DKK
""",
        "ground_truth": {
            "vendor_name": "OK a.m.b.a.",
            "cvr_number": "42759216",
            "invoice_number": "OK-2026-785412",
            "invoice_date": "2026-01-31",
            "due_date": "2026-02-14",
            "currency": "DKK",
            "net_amount": 1986.00,
            "vat_amount": 496.50,
            "total_amount": 2482.50,
            "vat_code": "I25",
            "suggested_account": "6710",
            "journal": "KOB"
        }
    },
    # 8. Insurance premium
    {
        "id": "INV-008",
        "category": "realistic",
        "ocr_text": """
Tryg Forsikring A/S
Klausdalsbrovej 601
2750 Ballerup
CVR: 24260666

Forsikringsfaktura

Fakturanummer: TRY-2026-145287
Udstedelsesdato: 01-01-2026
Betalingsfrist: 31-01-2026

Forsikringstager: Test Company ApS
Policenr: 45-789-4521

Forsikringspræmie 2026

Erhvervsansvar                   8.500,00
Løsøreforsikring                 4.200,00
Arbejdsskadeforsikring           6.800,00

I alt forsikringspræmie:        19.500,00 DKK

(Forsikringspræmier er momsfrie)
""",
        "ground_truth": {
            "vendor_name": "Tryg Forsikring A/S",
            "cvr_number": "24260666",
            "invoice_number": "TRY-2026-145287",
            "invoice_date": "2026-01-01",
            "due_date": "2026-01-31",
            "currency": "DKK",
            "net_amount": 19500.00,
            "vat_amount": 0.00,
            "total_amount": 19500.00,
            "vat_code": "MOMSFRI",
            "suggested_account": "6600",
            "journal": "KOB"
        }
    },
    # 9. Office rent
    {
        "id": "INV-009",
        "category": "realistic",
        "ocr_text": """
Jeudan A/S
Bredgade 30
1260 København K
CVR-nr: 14247910

Huslejefaktura

Faktura: JEU-2026-00145
Dato: 01-02-2026
Forfaldsdato: 01-02-2026

Lejer: Test Company ApS
Lejemål: Vestergade 45, 1. sal
Areal: 120 m²

Husleje februar 2026

Husleje:                        25.000,00
Aconto varme:                    1.500,00
Aconto el:                         800,00
Fællesudgifter:                  2.200,00

Subtotal:                       29.500,00 DKK
Moms 25%:                        7.375,00 DKK
Total:                          36.875,00 DKK
""",
        "ground_truth": {
            "vendor_name": "Jeudan A/S",
            "cvr_number": "14247910",
            "invoice_number": "JEU-2026-00145",
            "invoice_date": "2026-02-01",
            "due_date": "2026-02-01",
            "currency": "DKK",
            "net_amount": 29500.00,
            "vat_amount": 7375.00,
            "total_amount": 36875.00,
            "vat_code": "I25",
            "suggested_account": "6010",
            "journal": "KOB"
        }
    },
    # 10. Marketing agency
    {
        "id": "INV-010",
        "category": "realistic",
        "ocr_text": """
Magnetix ApS
Borgergade 28, 3. sal
1300 København K
CVR: 35874521

FAKTURA

Fakturanr: MAG-2026-0089
Udstedt: 20-01-2026
Betalingsfrist: 03-02-2026

Til: Test Company ApS

Marketing services december 2025

Ydelse                          Timer    Sats      Beløb
---------------------------------------------------------
Strategisk rådgivning           8       1.200    9.600,00
Content produktion              15        850   12.750,00
Social media management         20        650   13.000,00
Annoncering (Google/Meta)       -          -    8.500,00

Netto:                                         43.850,00 DKK
Moms 25%:                                      10.962,50 DKK
Total:                                         54.812,50 DKK
""",
        "ground_truth": {
            "vendor_name": "Magnetix ApS",
            "cvr_number": "35874521",
            "invoice_number": "MAG-2026-0089",
            "invoice_date": "2026-01-20",
            "due_date": "2026-02-03",
            "currency": "DKK",
            "net_amount": 43850.00,
            "vat_amount": 10962.50,
            "total_amount": 54812.50,
            "vat_code": "I25",
            "suggested_account": "7000",
            "journal": "KOB"
        }
    },
    # 11. Consulting services
    {
        "id": "INV-011",
        "category": "realistic",
        "ocr_text": """
McKinsey & Company Denmark ApS
Kongens Nytorv 26
1050 København K
CVR-nr: 27154896

Invoice

Invoice Number: MCK-DK-2026-00421
Invoice Date: January 25, 2026
Due Date: February 24, 2026

Client: Test Company ApS

Strategic Advisory Services
Project: Digital Transformation Assessment

Professional Fees:              145.000,00 DKK
Expenses:                         8.500,00 DKK

Subtotal:                       153.500,00 DKK
VAT 25%:                         38.375,00 DKK
Total Amount:                   191.875,00 DKK

Wire Transfer:
IBAN: DK5030000010785421
""",
        "ground_truth": {
            "vendor_name": "McKinsey & Company Denmark ApS",
            "cvr_number": "27154896",
            "invoice_number": "MCK-DK-2026-00421",
            "invoice_date": "2026-01-25",
            "due_date": "2026-02-24",
            "currency": "DKK",
            "net_amount": 153500.00,
            "vat_amount": 38375.00,
            "total_amount": 191875.00,
            "vat_code": "I25",
            "suggested_account": "7300",
            "journal": "KOB"
        }
    },
    # 12. Electricity bill
    {
        "id": "INV-012",
        "category": "realistic",
        "ocr_text": """
Ørsted Salg & Service A/S
Nesa Allé 1
2820 Gentofte
CVR: 27210538

Elregning

Fakturanr: ØSS-2026-4587412
Periode: 01-12-2025 til 31-12-2025
Fakturadato: 05-01-2026
Sidste rettidige betaling: 20-01-2026

Kunde: Test Company ApS
Installationsnr: 571452148745

Forbrug: 1.245 kWh

El-forbrug                       2.987,50
Abonnement                         89,00
Afgifter                        1.245,00
Transport                         456,25

I alt ekskl. moms:               4.777,75 DKK
Moms 25%:                        1.194,44 DKK
I alt at betale:                 5.972,19 DKK
""",
        "ground_truth": {
            "vendor_name": "Ørsted Salg & Service A/S",
            "cvr_number": "27210538",
            "invoice_number": "ØSS-2026-4587412",
            "invoice_date": "2026-01-05",
            "due_date": "2026-01-20",
            "currency": "DKK",
            "net_amount": 4777.75,
            "vat_amount": 1194.44,
            "total_amount": 5972.19,
            "vat_code": "I25",
            "suggested_account": "6020",
            "journal": "KOB"
        }
    },
    # 13. Travel expenses
    {
        "id": "INV-013",
        "category": "realistic",
        "ocr_text": """
SAS Scandinavian Airlines
Lufthavnsvej 1
2770 Kastrup
CVR: 25144414

REJSEFAKTURA / TRAVEL INVOICE

Booking ref: ABC123
Fakturanr: SAS-2026-78541256
Dato: 10-01-2026
Betales straks

Passager: Hans Jensen
Virksomhed: Test Company ApS

Rejse: København - London - København
Dato: 15-01-2026

Flybillet:                       4.250,00
Sædereservation:                   350,00
Baggage:                           450,00

Subtotal:                        5.050,00 DKK
Moms 0% (international):             0,00 DKK
Total:                           5.050,00 DKK

Betalt med kort
""",
        "ground_truth": {
            "vendor_name": "SAS Scandinavian Airlines",
            "cvr_number": "25144414",
            "invoice_number": "SAS-2026-78541256",
            "invoice_date": "2026-01-10",
            "due_date": "2026-01-10",
            "currency": "DKK",
            "net_amount": 5050.00,
            "vat_amount": 0.00,
            "total_amount": 5050.00,
            "vat_code": "MOMSFRI",
            "suggested_account": "6800",
            "journal": "KOB"
        }
    },
    # 14. Restaurant/representation
    {
        "id": "INV-014",
        "category": "realistic",
        "ocr_text": """
Restaurant Noma ApS
Refshalevej 96
1432 København K
CVR-nr: 27591753

FAKTURA

Faktura: NOMA-2026-0452
Dato: 18-01-2026
Forfald: 01-02-2026

Gæst: Test Company ApS
Antal personer: 4

Dato: 18-01-2026

Menu (4 pers.)                   9.800,00
Vinmenu                          3.200,00
Minermalvand                       240,00

Subtotal:                       13.240,00 DKK
Moms 25%:                        3.310,00 DKK
Total:                          16.550,00 DKK

Note: Restaurantbesøg - 25% momsfradrag
""",
        "ground_truth": {
            "vendor_name": "Restaurant Noma ApS",
            "cvr_number": "27591753",
            "invoice_number": "NOMA-2026-0452",
            "invoice_date": "2026-01-18",
            "due_date": "2026-02-01",
            "currency": "DKK",
            "net_amount": 13240.00,
            "vat_amount": 3310.00,
            "total_amount": 16550.00,
            "vat_code": "I25",
            "suggested_account": "6910",
            "journal": "KOB"
        }
    },
    # 15. Professional course
    {
        "id": "INV-015",
        "category": "realistic",
        "ocr_text": """
Kursuslex ApS
Ny Østergade 3
1101 København K
CVR: 31458796

FAKTURA

Fakturanummer: KL-2026-1254
Fakturadato: 05-01-2026
Betalingsdato: 19-01-2026

Deltager: Maria Nielsen
Firma: Test Company ApS

Kursus: Projektledelse - Niveau 2
Dato: 20-21 januar 2026

Kursusgebyr:                     8.500,00 DKK
Kursusmaterialer:                  750,00 DKK

Subtotal:                        9.250,00 DKK
Moms 25%:                        2.312,50 DKK
Total:                          11.562,50 DKK
""",
        "ground_truth": {
            "vendor_name": "Kursuslex ApS",
            "cvr_number": "31458796",
            "invoice_number": "KL-2026-1254",
            "invoice_date": "2026-01-05",
            "due_date": "2026-01-19",
            "currency": "DKK",
            "net_amount": 9250.00,
            "vat_amount": 2312.50,
            "total_amount": 11562.50,
            "vat_code": "I25",
            "suggested_account": "7100",
            "journal": "KOB"
        }
    },
    # 16. Postal services
    {
        "id": "INV-016",
        "category": "realistic",
        "ocr_text": """
PostNord Danmark A/S
Hedegaardsvej 88
2300 København S
CVR-nr: 26667903

Faktura

Fakturanr: PN-2026-8745123
Dato: 31-01-2026
Forfald: 14-02-2026

Kunde: Test Company ApS
Aftalenr: 45-789-123

Forsendelser januar 2026

Brevpost (45 stk)                  562,50
Pakker (12 stk)                  1.440,00
Expresspost (3 stk)                297,00
Gebyrer                             45,00

Netto:                           2.344,50 DKK
Moms 25%:                          586,13 DKK
Total:                           2.930,63 DKK
""",
        "ground_truth": {
            "vendor_name": "PostNord Danmark A/S",
            "cvr_number": "26667903",
            "invoice_number": "PN-2026-8745123",
            "invoice_date": "2026-01-31",
            "due_date": "2026-02-14",
            "currency": "DKK",
            "net_amount": 2344.50,
            "vat_amount": 586.13,
            "total_amount": 2930.63,
            "vat_code": "I25",
            "suggested_account": "6500",
            "journal": "KOB"
        }
    },
    # 17. Raw materials / goods
    {
        "id": "INV-017",
        "category": "realistic",
        "ocr_text": """
Lemvigh-Müller A/S
Stationsparken 25
2600 Glostrup
CVR: 56813718

SALGSFAKTURA

Faktura nr: LM-2026-458712
Ordrenr: 78945612
Fakturadato: 22-01-2026
Betalingsbetingelser: 30 dage netto

Køber: Test Company ApS

Varelinie                        Antal    Pris      Beløb
----------------------------------------------------------
Stålrør 40mm x 3m               25 stk    189,00   4.725,00
Fittings sortiment              10 sæt    245,00   2.450,00
Rørskærer prof.                  2 stk    875,00   1.750,00
Gevindtape                      20 rul     35,00     700,00

Varebeløb:                                         9.625,00 DKK
Moms 25%:                                          2.406,25 DKK
Fakturabeløb:                                     12.031,25 DKK
""",
        "ground_truth": {
            "vendor_name": "Lemvigh-Müller A/S",
            "cvr_number": "56813718",
            "invoice_number": "LM-2026-458712",
            "invoice_date": "2026-01-22",
            "due_date": "2026-02-21",
            "currency": "DKK",
            "net_amount": 9625.00,
            "vat_amount": 2406.25,
            "total_amount": 12031.25,
            "vat_code": "I25",
            "suggested_account": "4000",
            "journal": "KOB"
        }
    },
    # 18. Vehicle repair
    {
        "id": "INV-018",
        "category": "realistic",
        "ocr_text": """
FDM Bilservice
Firskovvej 32
2800 Kongens Lyngby
CVR: 10636912

REPARATIONSFAKTURA

Fakturanr: FDM-2026-12458
Dato: 28-01-2026
Forfald: 11-02-2026

Kunde: Test Company ApS
Reg.nr: AB 12 345
KM-stand: 45.892

Service 30.000 km

Arbejdsløn (2,5 timer)           1.562,50
Olieskift                          450,00
Oliefilter                         285,00
Luftfilter                         375,00
Bremsecheck                        350,00

Subtotal:                        3.022,50 DKK
Moms 25%:                          755,63 DKK
Total:                           3.778,13 DKK
""",
        "ground_truth": {
            "vendor_name": "FDM Bilservice",
            "cvr_number": "10636912",
            "invoice_number": "FDM-2026-12458",
            "invoice_date": "2026-01-28",
            "due_date": "2026-02-11",
            "currency": "DKK",
            "net_amount": 3022.50,
            "vat_amount": 755.63,
            "total_amount": 3778.13,
            "vat_code": "I25",
            "suggested_account": "6730",
            "journal": "KOB"
        }
    },
    # 19. Web hosting
    {
        "id": "INV-019",
        "category": "realistic",
        "ocr_text": """
one.com Group AB
Kalvebod Brygge 24
1560 København V
CVR: 36656712

Faktura

Fakturanr: ONE-2026-DK785412
Dato: 01-01-2026
Forfaldsdato: 15-01-2026

Kunde: Test Company ApS
Domæne: testcompany.dk

Hosting-pakke 2026

Webhotel Business (1 år)         1.188,00
SSL-certifikat                      0,00
Domænefornyelse                   119,00
Ekstra mailbokse (5 stk)          295,00

Subtotal:                        1.602,00 DKK
Moms 25%:                          400,50 DKK
Total:                           2.002,50 DKK
""",
        "ground_truth": {
            "vendor_name": "one.com Group AB",
            "cvr_number": "36656712",
            "invoice_number": "ONE-2026-DK785412",
            "invoice_date": "2026-01-01",
            "due_date": "2026-01-15",
            "currency": "DKK",
            "net_amount": 1602.00,
            "vat_amount": 400.50,
            "total_amount": 2002.50,
            "vat_code": "I25",
            "suggested_account": "6320",
            "journal": "KOB"
        }
    },
    # 20. Subcontractor
    {
        "id": "INV-020",
        "category": "realistic",
        "ocr_text": """
Hansen & Co. Entreprise ApS
Industriholmen 7
2650 Hvidovre
CVR-nr: 38547812

FAKTURA

Faktura nr: HCE-2026-0078
Dato: 25-01-2026
Betalingsbetingelser: 14 dage

Bygherre: Test Company ApS

Projekt: Kontorombygging Vestergade 45

Entreprise uge 3-4, 2026

Nedrivningsarbejde               12.500,00
El-installation                  28.750,00
VVS-arbejde                      18.400,00
Malerarbejde                     15.200,00
Rengøring                         3.500,00

I alt ekskl. moms:               78.350,00 DKK
Moms 25%:                        19.587,50 DKK
I alt inkl. moms:                97.937,50 DKK
""",
        "ground_truth": {
            "vendor_name": "Hansen & Co. Entreprise ApS",
            "cvr_number": "38547812",
            "invoice_number": "HCE-2026-0078",
            "invoice_date": "2026-01-25",
            "due_date": "2026-02-08",
            "currency": "DKK",
            "net_amount": 78350.00,
            "vat_amount": 19587.50,
            "total_amount": 97937.50,
            "vat_code": "I25",
            "suggested_account": "4300",
            "journal": "KOB"
        }
    },
    # 21. Small purchases
    {
        "id": "INV-021",
        "category": "realistic",
        "ocr_text": """
Bauhaus A/S
Roskildevej 201
2620 Albertslund
CVR: 31568741

KVITTERING / FAKTURA

Butik: Bauhaus Albertslund
Fakturanr: BH-2026-45872145
Dato: 15-01-2026

Køber: Test Company ApS

Vare                             Antal    Pris
----------------------------------------------
Skruemaskine Makita               1     1.299,00
Borsæt HSS                        1       199,00
Skruer sortiment                  2       149,00
Kabelbindere                      3        45,00

Varekøb:                                 1.791,00
Moms 25%:                                  447,75
Total:                                   2.238,75 DKK

Betalt kontant
""",
        "ground_truth": {
            "vendor_name": "Bauhaus A/S",
            "cvr_number": "31568741",
            "invoice_number": "BH-2026-45872145",
            "invoice_date": "2026-01-15",
            "due_date": "2026-01-15",
            "currency": "DKK",
            "net_amount": 1791.00,
            "vat_amount": 447.75,
            "total_amount": 2238.75,
            "vat_code": "I25",
            "suggested_account": "6100",
            "journal": "KASSE"
        }
    },
    # 22. Bank fees
    {
        "id": "INV-022",
        "category": "realistic",
        "ocr_text": """
Danske Bank A/S
Holmens Kanal 2-12
1092 København K
CVR: 61126228

Gebyrspecifikation

Reference: DB-2026-Q1-45821
Periode: Januar 2026
Dato: 31-01-2026

Kunde: Test Company ApS
Kontonr: 3409-10452789

Gebyrer januar 2026

Månedligt kontogebyr                89,00
Udlandsoverførsler (3 stk)        225,00
MobilePay Business                  99,00
Kortgebyrer                        145,00

I alt gebyrer:                     558,00 DKK

(Bankgebyrer er momsfrie)
""",
        "ground_truth": {
            "vendor_name": "Danske Bank A/S",
            "cvr_number": "61126228",
            "invoice_number": "DB-2026-Q1-45821",
            "invoice_date": "2026-01-31",
            "due_date": "2026-01-31",
            "currency": "DKK",
            "net_amount": 558.00,
            "vat_amount": 0.00,
            "total_amount": 558.00,
            "vat_code": "MOMSFRI",
            "suggested_account": "8600",
            "journal": "BANK"
        }
    },
    # 23. Membership/subscription
    {
        "id": "INV-023",
        "category": "realistic",
        "ocr_text": """
Dansk Erhverv
Børsen
1217 København K
CVR: 10073211

KONTINGENTFAKTURA

Fakturanr: DE-2026-00458
Dato: 02-01-2026
Forfald: 31-01-2026

Medlem: Test Company ApS
Medlemsnr: DE-45821

Kontingent 2026

Grundkontingent                  8.450,00
Juridisk hotline                 2.200,00
HR-rådgivning                    1.500,00

I alt:                          12.150,00 DKK
Moms 25%:                        3.037,50 DKK
Total:                          15.187,50 DKK
""",
        "ground_truth": {
            "vendor_name": "Dansk Erhverv",
            "cvr_number": "10073211",
            "invoice_number": "DE-2026-00458",
            "invoice_date": "2026-01-02",
            "due_date": "2026-01-31",
            "currency": "DKK",
            "net_amount": 12150.00,
            "vat_amount": 3037.50,
            "total_amount": 15187.50,
            "vat_code": "I25",
            "suggested_account": "7500",
            "journal": "KOB"
        }
    },
    # 24. Furniture
    {
        "id": "INV-024",
        "category": "realistic",
        "ocr_text": """
IKEA Business
Gentofte Storcenter 100
2820 Gentofte
CVR-nr: 16930444

Erhvervsfaktura

Faktura: IKEA-DK-2026-14587
Dato: 08-01-2026
Betalingsfrist: 22-01-2026

Kunde: Test Company ApS

Varer                            Antal    Pris      Beløb
----------------------------------------------------------
BEKANT skrivebord 160x80          4     3.499    13.996,00
MARKUS kontorstol                 4     1.699     6.796,00
KALLAX reol                       2       799     1.598,00
SKÅDIS vægtavle                   4       299     1.196,00

Subtotal:                                        23.586,00 DKK
Moms 25%:                                         5.896,50 DKK
Total:                                           29.482,50 DKK

Levering inkl.
""",
        "ground_truth": {
            "vendor_name": "IKEA Business",
            "cvr_number": "16930444",
            "invoice_number": "IKEA-DK-2026-14587",
            "invoice_date": "2026-01-08",
            "due_date": "2026-01-22",
            "currency": "DKK",
            "net_amount": 23586.00,
            "vat_amount": 5896.50,
            "total_amount": 29482.50,
            "vat_code": "I25",
            "suggested_account": "1500",
            "journal": "KOB"
        }
    },
    # 25. Legal services
    {
        "id": "INV-025",
        "category": "realistic",
        "ocr_text": """
Plesner Advokatpartnerselskab
Amerika Plads 37
2100 København Ø
CVR: 32202926

FAKTURA

Fakturanr: PLE-2026-0412
Dato: 30-01-2026
Betalingsfrist: 13-02-2026

Klient: Test Company ApS
Sagsnr: 45821-00125

Juridisk rådgivning
Sag: Kontraktgennemgang

Advokatbistand (5,5 timer @ 3.500) 19.250,00
Retsafgifter                       1.750,00

Subtotal:                         21.000,00 DKK
Moms 25%:                          5.250,00 DKK
Total:                            26.250,00 DKK
""",
        "ground_truth": {
            "vendor_name": "Plesner Advokatpartnerselskab",
            "cvr_number": "32202926",
            "invoice_number": "PLE-2026-0412",
            "invoice_date": "2026-01-30",
            "due_date": "2026-02-13",
            "currency": "DKK",
            "net_amount": 21000.00,
            "vat_amount": 5250.00,
            "total_amount": 26250.00,
            "vat_code": "I25",
            "suggested_account": "7200",
            "journal": "KOB"
        }
    },
]

# Continue in part 2...
