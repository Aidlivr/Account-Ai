# Invoice Test Suite - Edge Cases (25)
# Part 2: Edge cases to test AI robustness

from typing import List, Dict, Any

# ==================== EDGE CASE INVOICES (25) ====================
# Testing various challenging scenarios

EDGE_CASE_INVOICES: List[Dict[str, Any]] = [
    # 26. EU Reverse Charge - Services from Germany
    {
        "id": "INV-026",
        "category": "edge_case",
        "edge_type": "reverse_charge_eu",
        "ocr_text": """
SAP SE
Dietmar-Hopp-Allee 16
69190 Walldorf, Germany
VAT: DE143464973

INVOICE

Invoice No: SAP-2026-EU-78541
Date: 15-01-2026
Due: 14-02-2026

Customer: Test Company ApS
Denmark
CVR: 12345678

SAP Business One License
Annual Maintenance 2026

License Fee:                    45.000,00 EUR
Support & Maintenance:          12.500,00 EUR

Subtotal:                       57.500,00 EUR
VAT: 0% (Reverse Charge - Article 196)

IMPORTANT: Reverse charge applies.
Customer must self-assess VAT.
Intra-community service.
""",
        "ground_truth": {
            "vendor_name": "SAP SE",
            "cvr_number": "DE143464973",
            "invoice_number": "SAP-2026-EU-78541",
            "invoice_date": "2026-01-15",
            "due_date": "2026-02-14",
            "currency": "EUR",
            "net_amount": 57500.00,
            "vat_amount": 0.00,
            "total_amount": 57500.00,
            "vat_code": "IREV",
            "suggested_account": "6320",
            "journal": "KOB"
        }
    },
    # 27. EU Goods Purchase - Intra-community
    {
        "id": "INV-027",
        "category": "edge_case",
        "edge_type": "eu_acquisition",
        "ocr_text": """
Bechtle AG
Bechtle Platz 1
74172 Neckarsulm
Germany
VAT-ID: DE146151045

Rechnung / Invoice

Rechnungsnr: BT-2026-14587
Datum: 20-01-2026
Zahlungsziel: 19-02-2026

Käufer / Buyer:
Test Company ApS
Vestergade 45
1456 København K
Denmark
VAT: DK12345678

Artikel                          Menge   Preis      Gesamt
-----------------------------------------------------------
HP ProBook 450 G10                5    899,00    4.495,00
HP USB-C Dock G5                  5    229,00    1.145,00
HP Business Backpack              5     69,00      345,00

Warenwert:                                       5.985,00 EUR
MwSt: 0% (EU-Lieferung)                             0,00 EUR
Gesamtbetrag:                                    5.985,00 EUR

VAT exempt intra-community delivery
Steuerfreie innergemeinschaftliche Lieferung
""",
        "ground_truth": {
            "vendor_name": "Bechtle AG",
            "cvr_number": "DE146151045",
            "invoice_number": "BT-2026-14587",
            "invoice_date": "2026-01-20",
            "due_date": "2026-02-19",
            "currency": "EUR",
            "net_amount": 5985.00,
            "vat_amount": 0.00,
            "total_amount": 5985.00,
            "vat_code": "IEU",
            "suggested_account": "4100",
            "journal": "KOB"
        }
    },
    # 28. Credit note (negative amounts)
    {
        "id": "INV-028",
        "category": "edge_case",
        "edge_type": "credit_note",
        "ocr_text": """
Lyreco Denmark A/S
Transformervej 12
2860 Søborg
CVR: 10035164

KREDITNOTA

Kreditnota nr: KN-4521877
Original faktura: 4521800
Dato: 25-01-2026

Kunde: Test Company ApS

Retur af defekte varer

Beskrivelse                      Antal    Pris     Krediteres
-------------------------------------------------------------
Printerpapir A4 80g defekt       -5 pk   89,00    -445,00
Kuglepen defekt                  -2 pk   45,00     -90,00

Netto krediteres:                               -535,00 DKK
Moms 25%:                                       -133,75 DKK
Total krediteres:                               -668,75 DKK

Beløbet vil blive modregnet næste faktura.
""",
        "ground_truth": {
            "vendor_name": "Lyreco Denmark A/S",
            "cvr_number": "10035164",
            "invoice_number": "KN-4521877",
            "invoice_date": "2026-01-25",
            "due_date": "2026-01-25",
            "currency": "DKK",
            "net_amount": -535.00,
            "vat_amount": -133.75,
            "total_amount": -668.75,
            "vat_code": "I25",
            "suggested_account": "6300",
            "journal": "KOB"
        }
    },
    # 29. Multiple VAT rates (mixed)
    {
        "id": "INV-029",
        "category": "edge_case",
        "edge_type": "mixed_vat",
        "ocr_text": """
Coop Trading A/S
Roskildevej 65
2620 Albertslund
CVR: 45785412

FAKTURA

Fakturanr: COOP-2026-87451
Dato: 18-01-2026
Forfald: 01-02-2026

Kunde: Test Company ApS

Indkøb til firmaarrangement

Vare                             Moms%    Netto      Moms
----------------------------------------------------------
Kaffe, te (25 pk)                25%    1.250,00   312,50
Kager (catering)                 25%    2.800,00   700,00
Sodavand                         25%      450,00   112,50
Frugt og grønt                   25%      680,00   170,00

Totaler:
Netto 25%:                               5.180,00 DKK
Moms 25%:                                1.295,00 DKK
I alt:                                   6.475,00 DKK
""",
        "ground_truth": {
            "vendor_name": "Coop Trading A/S",
            "cvr_number": "45785412",
            "invoice_number": "COOP-2026-87451",
            "invoice_date": "2026-01-18",
            "due_date": "2026-02-01",
            "currency": "DKK",
            "net_amount": 5180.00,
            "vat_amount": 1295.00,
            "total_amount": 6475.00,
            "vat_code": "I25",
            "suggested_account": "6900",
            "journal": "KOB"
        }
    },
    # 30. Very small amount (under 100 DKK)
    {
        "id": "INV-030",
        "category": "edge_case",
        "edge_type": "small_amount",
        "ocr_text": """
7-Eleven Danmark A/S
Østergade 23
1100 København K
CVR: 17896534

Kvittering

Butik: 7-Eleven Rådhuspladsen
Bon nr: 7E-2026-458712
Dato: 22-01-2026 kl. 08:45

Vare                                  Pris
------------------------------------------
Kaffe stor                           35,00
Croissant                            28,00

Subtotal:                            63,00
Heraf moms 25%:                      12,60
Total:                               63,00 DKK

Kontant betaling
""",
        "ground_truth": {
            "vendor_name": "7-Eleven Danmark A/S",
            "cvr_number": "17896534",
            "invoice_number": "7E-2026-458712",
            "invoice_date": "2026-01-22",
            "due_date": "2026-01-22",
            "currency": "DKK",
            "net_amount": 50.40,
            "vat_amount": 12.60,
            "total_amount": 63.00,
            "vat_code": "I25",
            "suggested_account": "5300",
            "journal": "KASSE"
        }
    },
    # 31. Very large amount (over 500,000 DKK)
    {
        "id": "INV-031",
        "category": "edge_case",
        "edge_type": "large_amount",
        "ocr_text": """
Mercedes-Benz Danmark A/S
Kirstinehøj 62
2770 Kastrup
CVR: 11111470

FAKTURA

Fakturanummer: MBD-2026-00045
Fakturadato: 10-01-2026
Betalingsdato: 24-01-2026

Køber: Test Company ApS

Køretøj: Mercedes-Benz EQS 450+
Stelnr: W1K2970231A123456

Købspris ekskl. afgifter:        485.000,00
Registreringsafgift:             198.500,00
Nummerplader:                      1.180,00
Levering:                          5.000,00

I alt ekskl. moms:               689.680,00 DKK
Moms 25%:                        172.420,00 DKK
Total købesum:                   862.100,00 DKK
""",
        "ground_truth": {
            "vendor_name": "Mercedes-Benz Danmark A/S",
            "cvr_number": "11111470",
            "invoice_number": "MBD-2026-00045",
            "invoice_date": "2026-01-10",
            "due_date": "2026-01-24",
            "currency": "DKK",
            "net_amount": 689680.00,
            "vat_amount": 172420.00,
            "total_amount": 862100.00,
            "vat_code": "I25",
            "suggested_account": "1520",
            "journal": "KOB"
        }
    },
    # 32. Foreign currency (USD)
    {
        "id": "INV-032",
        "category": "edge_case",
        "edge_type": "foreign_currency",
        "ocr_text": """
Amazon Web Services, Inc.
410 Terry Avenue North
Seattle, WA 98109, USA
Tax ID: 91-1646860

INVOICE

Invoice Number: AWS-2026-US-78541
Invoice Date: January 31, 2026
Due Date: February 28, 2026

Bill To:
Test Company ApS
Vestergade 45
1456 København K, Denmark
VAT: DK12345678

AWS Usage - January 2026

Service                              Amount USD
-----------------------------------------------
EC2 Instances                          1,245.50
S3 Storage                               389.25
RDS Database                             567.80
CloudFront CDN                           123.45
Data Transfer                            234.00

Subtotal:                              2,560.00 USD
Tax: 0.00 USD (Non-US customer)
Total:                                 2,560.00 USD

VAT Reverse Charge applies for EU customers
""",
        "ground_truth": {
            "vendor_name": "Amazon Web Services, Inc.",
            "cvr_number": "91-1646860",
            "invoice_number": "AWS-2026-US-78541",
            "invoice_date": "2026-01-31",
            "due_date": "2026-02-28",
            "currency": "USD",
            "net_amount": 2560.00,
            "vat_amount": 0.00,
            "total_amount": 2560.00,
            "vat_code": "IREV",
            "suggested_account": "6310",
            "journal": "KOB"
        }
    },
    # 33. Norwegian vendor (NOK)
    {
        "id": "INV-033",
        "category": "edge_case",
        "edge_type": "nordic_currency",
        "ocr_text": """
Visma Software AS
Biskop Gunnerus gate 6
0155 Oslo
Norge
Org.nr: 981 106 715 MVA

FAKTURA

Fakturanr: VS-2026-NO-45821
Fakturadato: 15-01-2026
Forfallsdato: 14-02-2026

Kunde:
Test Company ApS
Vestergade 45
1456 København K
Danmark
CVR: DK12345678

Visma e-conomic Integration
Annual License 2026

Lisens:                          18.500,00 NOK
Support:                          4.500,00 NOK

Sum ekskl. mva:                  23.000,00 NOK
MVA 0% (Eksport):                     0,00 NOK
Sum inkl. mva:                   23.000,00 NOK

Eksport til EU - omvendt avgiftsplikt gjelder
""",
        "ground_truth": {
            "vendor_name": "Visma Software AS",
            "cvr_number": "981106715",
            "invoice_number": "VS-2026-NO-45821",
            "invoice_date": "2026-01-15",
            "due_date": "2026-02-14",
            "currency": "NOK",
            "net_amount": 23000.00,
            "vat_amount": 0.00,
            "total_amount": 23000.00,
            "vat_code": "IREV",
            "suggested_account": "6320",
            "journal": "KOB"
        }
    },
    # 34. Swedish vendor (SEK)
    {
        "id": "INV-034",
        "category": "edge_case",
        "edge_type": "nordic_currency",
        "ocr_text": """
Spotify AB
Regeringsgatan 19
111 53 Stockholm
Sverige
Org.nr: 556703-7485
VAT: SE556703748501

FAKTURA

Fakturanummer: SP-2026-SE-145287
Fakturadatum: 2026-01-01
Förfallodatum: 2026-01-31

Kund:
Test Company ApS
Danmark
Momsreg.nr: DK12345678

Spotify Business Premium
50 användare x 12 månader

Licenser:                        54.000,00 SEK
Rabatt -10%:                     -5.400,00 SEK

Summa exkl. moms:                48.600,00 SEK
Moms 0% (EU tjänst):                  0,00 SEK
Att betala:                      48.600,00 SEK

Omvänd skattskyldighet tillämpas (EU B2B)
""",
        "ground_truth": {
            "vendor_name": "Spotify AB",
            "cvr_number": "SE556703748501",
            "invoice_number": "SP-2026-SE-145287",
            "invoice_date": "2026-01-01",
            "due_date": "2026-01-31",
            "currency": "SEK",
            "net_amount": 48600.00,
            "vat_amount": 0.00,
            "total_amount": 48600.00,
            "vat_code": "IREV",
            "suggested_account": "6320",
            "journal": "KOB"
        }
    },
    # 35. Handwritten-style invoice (messy formatting)
    {
        "id": "INV-035",
        "category": "edge_case",
        "edge_type": "poor_formatting",
        "ocr_text": """
FAKTURA
Hans Petersens VVS
Skovvej 12  3400 Hillerød
cvr 28 45 78 12

Fakt nr 2026-15
d. 28/1-2026
bet 14 dg

Til: Test Company
     Vestergade 45 Kbh

Skift af vandhaner           kr 2.450
Rør og fittings                  875
Kørsel                           350
Timer 3,5 x 450               1.575

ialt         5.250
+ moms 25%   1.312,50
---------
TOTAL        6.562,50 kr

Betal til reg 9570 konto 4521875
""",
        "ground_truth": {
            "vendor_name": "Hans Petersens VVS",
            "cvr_number": "28457812",
            "invoice_number": "2026-15",
            "invoice_date": "2026-01-28",
            "due_date": "2026-02-11",
            "currency": "DKK",
            "net_amount": 5250.00,
            "vat_amount": 1312.50,
            "total_amount": 6562.50,
            "vat_code": "I25",
            "suggested_account": "6200",
            "journal": "KOB"
        }
    },
    # 36. Bilingual invoice (Danish/English)
    {
        "id": "INV-036",
        "category": "edge_case",
        "edge_type": "bilingual",
        "ocr_text": """
Zendesk Denmark ApS
Sankt Annæ Plads 13
1250 København K
CVR-nr/VAT: DK35127485

INVOICE / FAKTURA

Invoice No / Fakturanr: ZD-2026-DK-4521
Date / Dato: 2026-02-01
Due Date / Forfaldsdato: 2026-03-01

Customer / Kunde: Test Company ApS

Description / Beskrivelse          Amount / Beløb
-------------------------------------------------
Zendesk Suite Professional
50 agents x 12 months
50 agenter x 12 måneder            89.400,00 DKK

Subtotal / Subtotal:               89.400,00 DKK
VAT 25% / Moms 25%:                22.350,00 DKK
Total / I alt:                    111.750,00 DKK

Payment by wire transfer / Betaling ved bankoverførsel
""",
        "ground_truth": {
            "vendor_name": "Zendesk Denmark ApS",
            "cvr_number": "35127485",
            "invoice_number": "ZD-2026-DK-4521",
            "invoice_date": "2026-02-01",
            "due_date": "2026-03-01",
            "currency": "DKK",
            "net_amount": 89400.00,
            "vat_amount": 22350.00,
            "total_amount": 111750.00,
            "vat_code": "I25",
            "suggested_account": "6320",
            "journal": "KOB"
        }
    },
    # 37. Prepayment invoice
    {
        "id": "INV-037",
        "category": "edge_case",
        "edge_type": "prepayment",
        "ocr_text": """
Event Danmark ApS
Havnegade 25
1058 København K
CVR: 31245896

FORUDBETALING / DEPOSIT INVOICE

Fakturanr: ED-2026-DEP-0045
Dato: 15-01-2026
Forfald: Straks

Kunde: Test Company ApS

Arrangement: Årsfest 2026
Dato: 15-03-2026
Sted: Havnegade 25

Depositum for arrangement (50%)

Estimeret total:                 45.000,00
Depositum 50%:                   22.500,00

Netto:                           22.500,00 DKK
Moms 25%:                         5.625,00 DKK
Total depositum:                 28.125,00 DKK

Restbeløb faktureres efter arrangement.
""",
        "ground_truth": {
            "vendor_name": "Event Danmark ApS",
            "cvr_number": "31245896",
            "invoice_number": "ED-2026-DEP-0045",
            "invoice_date": "2026-01-15",
            "due_date": "2026-01-15",
            "currency": "DKK",
            "net_amount": 22500.00,
            "vat_amount": 5625.00,
            "total_amount": 28125.00,
            "vat_code": "I25",
            "suggested_account": "1200",
            "journal": "KOB"
        }
    },
    # 38. Subscription with discount
    {
        "id": "INV-038",
        "category": "edge_case",
        "edge_type": "discount",
        "ocr_text": """
Salesforce Denmark ApS
Arne Jacobsens Allé 15
2300 København S
CVR-nr: 33451287

INVOICE

Invoice: SF-2026-DK-00145
Date: 01-02-2026
Terms: Net 30

Customer: Test Company ApS

Salesforce Sales Cloud
Enterprise Edition
10 Users Annual License

List Price:                     198.000,00
Partner Discount -15%:          -29.700,00
Volume Discount -5%:             -8.415,00

Subtotal:                       159.885,00 DKK
VAT 25%:                         39.971,25 DKK
Total:                          199.856,25 DKK
""",
        "ground_truth": {
            "vendor_name": "Salesforce Denmark ApS",
            "cvr_number": "33451287",
            "invoice_number": "SF-2026-DK-00145",
            "invoice_date": "2026-02-01",
            "due_date": "2026-03-03",
            "currency": "DKK",
            "net_amount": 159885.00,
            "vat_amount": 39971.25,
            "total_amount": 199856.25,
            "vat_code": "I25",
            "suggested_account": "6320",
            "journal": "KOB"
        }
    },
    # 39. Government/public entity (different VAT handling)
    {
        "id": "INV-039",
        "category": "edge_case",
        "edge_type": "government",
        "ocr_text": """
SKAT
Nykøbingvej 76
4990 Sakskøbing
CVR: 19552101

OPKRÆVNING

Referencenr: SKAT-2026-45821475
Opkrævningsdato: 01-01-2026
Sidste rettidige betaling: 20-01-2026

Betaler: Test Company ApS
SE-nr: 12345678

A-skat og AM-bidrag
December 2025

A-skat:                          28.450,00
AM-bidrag:                        9.120,00
ATP:                              2.880,00

I alt at betale:                 40.450,00 DKK

(Offentlige afgifter - ingen moms)
""",
        "ground_truth": {
            "vendor_name": "SKAT",
            "cvr_number": "19552101",
            "invoice_number": "SKAT-2026-45821475",
            "invoice_date": "2026-01-01",
            "due_date": "2026-01-20",
            "currency": "DKK",
            "net_amount": 40450.00,
            "vat_amount": 0.00,
            "total_amount": 40450.00,
            "vat_code": "IKKEMOMS",
            "suggested_account": "2610",
            "journal": "KOB"
        }
    },
    # 40. Partial delivery invoice
    {
        "id": "INV-040",
        "category": "edge_case",
        "edge_type": "partial_delivery",
        "ocr_text": """
Dell Technologies Denmark ApS
Stationsparken 37
2600 Glostrup
CVR: 17489624

DELFAKTURA / PARTIAL INVOICE

Fakturanr: DELL-2026-P1-45821
Ordrenr: DK-2026-78541
Delfaktura: 1 af 3
Dato: 20-01-2026
Forfald: 19-02-2026

Kunde: Test Company ApS

Total ordre: 20 x Dell Precision 5570
Denne leverance: 7 stk

Dell Precision 5570               7    18.500   129.500,00
Levering                          1     1.200     1.200,00

Dellevering subtotal:                          130.700,00 DKK
Moms 25%:                                       32.675,00 DKK
Denne faktura:                                 163.375,00 DKK

Restordre: 13 stk - leveres uge 6-8
""",
        "ground_truth": {
            "vendor_name": "Dell Technologies Denmark ApS",
            "cvr_number": "17489624",
            "invoice_number": "DELL-2026-P1-45821",
            "invoice_date": "2026-01-20",
            "due_date": "2026-02-19",
            "currency": "DKK",
            "net_amount": 130700.00,
            "vat_amount": 32675.00,
            "total_amount": 163375.00,
            "vat_code": "I25",
            "suggested_account": "1510",
            "journal": "KOB"
        }
    },
    # 41. Invoice with rounding differences
    {
        "id": "INV-041",
        "category": "edge_case",
        "edge_type": "rounding",
        "ocr_text": """
Metro Cash & Carry Danmark A/S
Stamholmen 193
2650 Hvidovre
CVR: 36451287

FAKTURA

Fakturanr: METRO-2026-4521879
Dato: 25-01-2026
Forfald: 08-02-2026

Kunde: Test Company ApS
Kundenr: M-45821

Vare                             Antal    Pris      Beløb
----------------------------------------------------------
Kaffe 500g (3 for 2)              3      67,33    201,99
Mælk 10L                          5      89,99    449,95
Sukker 1kg                       10      12,99    129,90
Te sortiment                      2     145,00    290,00

Subtotal:                                        1.071,84
Øreafrunding:                                        0,16

Netto:                                           1.072,00 DKK
Moms 25%:                                          268,00 DKK
Total:                                           1.340,00 DKK
""",
        "ground_truth": {
            "vendor_name": "Metro Cash & Carry Danmark A/S",
            "cvr_number": "36451287",
            "invoice_number": "METRO-2026-4521879",
            "invoice_date": "2026-01-25",
            "due_date": "2026-02-08",
            "currency": "DKK",
            "net_amount": 1072.00,
            "vat_amount": 268.00,
            "total_amount": 1340.00,
            "vat_code": "I25",
            "suggested_account": "5300",
            "journal": "KOB"
        }
    },
    # 42. Split payment terms
    {
        "id": "INV-042",
        "category": "edge_case",
        "edge_type": "split_payment",
        "ocr_text": """
EY Danmark P/S
Dirch Passers Allé 36
2000 Frederiksberg
CVR: 35458152

FAKTURA

Fakturanr: EY-2026-DK-0087
Dato: 31-01-2026

Klient: Test Company ApS
Sagsnr: 2026-00125

Årsregnskab og revision 2025

Revisionshonorar                185.000,00
Regnskabsassistance              45.000,00
Rådgivning                       28.000,00

Subtotal:                       258.000,00 DKK
Moms 25%:                        64.500,00 DKK
Total:                          322.500,00 DKK

BETALINGSPLAN:
Rate 1: 161.250,00 - forfald 14-02-2026
Rate 2: 161.250,00 - forfald 14-03-2026
""",
        "ground_truth": {
            "vendor_name": "EY Danmark P/S",
            "cvr_number": "35458152",
            "invoice_number": "EY-2026-DK-0087",
            "invoice_date": "2026-01-31",
            "due_date": "2026-02-14",
            "currency": "DKK",
            "net_amount": 258000.00,
            "vat_amount": 64500.00,
            "total_amount": 322500.00,
            "vat_code": "I25",
            "suggested_account": "7200",
            "journal": "KOB"
        }
    },
    # 43. Invoice with SKU/product codes
    {
        "id": "INV-043",
        "category": "edge_case",
        "edge_type": "product_codes",
        "ocr_text": """
RS Components A/S
Erhvervsvej 21
2610 Rødovre
CVR: 15489623

FAKTURA

Fakturanr: RS-2026-452187
Ordrenr: WEB-2026-78541
Dato: 22-01-2026
Forfald: 05-02-2026

Leveret til: Test Company ApS

SKU             Beskrivelse              Antal   Pris    Beløb
--------------------------------------------------------------
RS-125-4521     Arduino Uno R3              5    249,00  1.245,00
RS-789-1452     Breadboard 830 point       10     89,00    890,00
RS-456-7821     LED Kit 100stk              3    145,00    435,00
RS-321-9874     Jumper Wire Set             5     65,00    325,00
RS-654-1236     Resistor Kit 600stk         2    175,00    350,00

Varesubtotal:                                            3.245,00
Fragt:                                                      79,00

Netto:                                                   3.324,00 DKK
Moms 25%:                                                  831,00 DKK
Total:                                                   4.155,00 DKK
""",
        "ground_truth": {
            "vendor_name": "RS Components A/S",
            "cvr_number": "15489623",
            "invoice_number": "RS-2026-452187",
            "invoice_date": "2026-01-22",
            "due_date": "2026-02-05",
            "currency": "DKK",
            "net_amount": 3324.00,
            "vat_amount": 831.00,
            "total_amount": 4155.00,
            "vat_code": "I25",
            "suggested_account": "4000",
            "journal": "KOB"
        }
    },
    # 44. Pro forma invoice (should not be booked)
    {
        "id": "INV-044",
        "category": "edge_case",
        "edge_type": "proforma",
        "ocr_text": """
Schneider Electric Danmark A/S
Lautrupvang 1
2750 Ballerup
CVR: 54123678

PRO FORMA FAKTURA
(IKKE ET REGNSKABSBILAG)

Pro forma nr: SE-2026-PF-0045
Dato: 28-01-2026

Kunde: Test Company ApS
Tilbudsnr: TIL-2026-00125

Estimat for el-installation

Produkt                          Antal    Pris      Beløb
----------------------------------------------------------
Tavle komplet                      1   45.000    45.000,00
Installation                       -        -    18.500,00
Kabler og tilbehør                 -        -    12.750,00

Estimeret netto:                             76.250,00 DKK
Estimeret moms 25%:                          19.062,50 DKK
Estimeret total:                             95.312,50 DKK

DETTE ER IKKE EN FAKTURA
Endelig faktura sendes ved levering
""",
        "ground_truth": {
            "vendor_name": "Schneider Electric Danmark A/S",
            "cvr_number": "54123678",
            "invoice_number": "SE-2026-PF-0045",
            "invoice_date": "2026-01-28",
            "due_date": "2026-01-28",
            "currency": "DKK",
            "net_amount": 76250.00,
            "vat_amount": 19062.50,
            "total_amount": 95312.50,
            "vat_code": "I25",
            "suggested_account": "6200",
            "journal": "KOB",
            "notes": "PRO FORMA - Should be flagged for review"
        }
    },
    # 45. Leasing payment
    {
        "id": "INV-045",
        "category": "edge_case",
        "edge_type": "leasing",
        "ocr_text": """
Nordea Finans Danmark A/S
Strandgade 3
0900 København C
CVR: 89456123

LEASINGFAKTURA

Fakturanr: NFL-2026-02-45821
Periode: Februar 2026
Fakturadato: 01-02-2026
Forfaldsdato: 01-02-2026

Leasingtager: Test Company ApS
Aftalenr: L-2025-00458
Objekt: Produktionsmaskine XYZ-500

Månedlig leasingydelse

Afdrag på hovedstol              4.250,00
Rente                            1.180,00
Administration                     150,00

Leasingydelse i alt:             5.580,00 DKK
Moms 25% af ydelse:              1.395,00 DKK
Total at betale:                 6.975,00 DKK

Restgæld pr. 01-02-2026: 89.500,00 DKK
""",
        "ground_truth": {
            "vendor_name": "Nordea Finans Danmark A/S",
            "cvr_number": "89456123",
            "invoice_number": "NFL-2026-02-45821",
            "invoice_date": "2026-02-01",
            "due_date": "2026-02-01",
            "currency": "DKK",
            "net_amount": 5580.00,
            "vat_amount": 1395.00,
            "total_amount": 6975.00,
            "vat_code": "I25",
            "suggested_account": "8400",
            "journal": "KOB"
        }
    },
    # 46. Utility with consumption details
    {
        "id": "INV-046",
        "category": "edge_case",
        "edge_type": "utility_complex",
        "ocr_text": """
HOFOR A/S
Ørestads Boulevard 35
2300 København S
CVR: 10073022

VAND- OG AFLØBSREGNING

Fakturanr: HOF-2026-Q1-458721
Aflæsningsperiode: 01-10-2025 til 31-12-2025
Fakturadato: 10-01-2026
Betalingsfrist: 01-02-2026

Forbruger: Test Company ApS
Installationsadresse: Vestergade 45, 1456 Kbh K
Målernr: 78541254

Forbrug                        m³      Pris/m³    Beløb
-------------------------------------------------------
Vandforbrug                   45       45,85    2.063,25
Afledning                     45       28,75    1.293,75
Statsafgift vand              45        6,37      286,65
Grundafgift                    -           -      450,00

Nettobeløb:                                    4.093,65 DKK
Moms 25%:                                      1.023,41 DKK
I alt at betale:                               5.117,06 DKK

Aconto næste kvartal: 1.706,00 DKK
""",
        "ground_truth": {
            "vendor_name": "HOFOR A/S",
            "cvr_number": "10073022",
            "invoice_number": "HOF-2026-Q1-458721",
            "invoice_date": "2026-01-10",
            "due_date": "2026-02-01",
            "currency": "DKK",
            "net_amount": 4093.65,
            "vat_amount": 1023.41,
            "total_amount": 5117.06,
            "vat_code": "I25",
            "suggested_account": "6020",
            "journal": "KOB"
        }
    },
    # 47. Commission invoice
    {
        "id": "INV-047",
        "category": "edge_case",
        "edge_type": "commission",
        "ocr_text": """
Dansk Ejendomsmæglerforening
Postboks 2, Herlev Hovedgade 195
2730 Herlev
CVR: 71455413

PROVISIONSFAKTURA

Fakturanr: DEF-2026-PROV-0089
Dato: 30-01-2026
Forfald: 13-02-2026

Mægler: Test Company ApS
Sagsnr: 2026-00458

Salg af ejendom
Adresse: Strandvejen 100, 2900 Hellerup

Salgspris:                    8.500.000,00 DKK

Provision 2,5% af salgspris:    212.500,00 DKK
Markedsføringspakke:              8.500,00 DKK
Fotooptagelser:                   4.500,00 DKK

Subtotal:                       225.500,00 DKK
Moms 25%:                        56.375,00 DKK
Total provision:                281.875,00 DKK
""",
        "ground_truth": {
            "vendor_name": "Dansk Ejendomsmæglerforening",
            "cvr_number": "71455413",
            "invoice_number": "DEF-2026-PROV-0089",
            "invoice_date": "2026-01-30",
            "due_date": "2026-02-13",
            "currency": "DKK",
            "net_amount": 225500.00,
            "vat_amount": 56375.00,
            "total_amount": 281875.00,
            "vat_code": "I25",
            "suggested_account": "7500",
            "journal": "KOB"
        }
    },
    # 48. Invoice with environmental fee
    {
        "id": "INV-048",
        "category": "edge_case",
        "edge_type": "environmental_fee",
        "ocr_text": """
Stena Recycling A/S
Banemarksvej 40
2605 Brøndby
CVR: 16457892

FAKTURA

Fakturanr: SR-2026-45821
Dato: 31-01-2026
Forfald: 14-02-2026

Kunde: Test Company ApS

Affaldshåndtering januar 2026

Container 660L (4 tømninger)     1.200,00
Papir/pap genbrug                  450,00
Elektronikaffald 125 kg          1.875,00
Miljøgebyr                         350,00
CO2-afgift                         185,00

Netto:                           4.060,00 DKK
Moms 25%:                        1.015,00 DKK
Total:                           5.075,00 DKK
""",
        "ground_truth": {
            "vendor_name": "Stena Recycling A/S",
            "cvr_number": "16457892",
            "invoice_number": "SR-2026-45821",
            "invoice_date": "2026-01-31",
            "due_date": "2026-02-14",
            "currency": "DKK",
            "net_amount": 4060.00,
            "vat_amount": 1015.00,
            "total_amount": 5075.00,
            "vat_code": "I25",
            "suggested_account": "7500",
            "journal": "KOB"
        }
    },
    # 49. Very long invoice number
    {
        "id": "INV-049",
        "category": "edge_case",
        "edge_type": "long_invoice_number",
        "ocr_text": """
Siemens A/S
Borupvang 9
2750 Ballerup
CVR: 16993085

INVOICE

Invoice Number: SI-DK-2026-PRJ-DIGITALFACTORY-REF78541254-001
Order Reference: PO-2026-DIG-FAC-IMPLEMENTATION-PHASE1
Date: 2026-01-28
Due Date: 2026-02-27

Customer: Test Company ApS
Project: Digital Factory Implementation

Professional Services:           145.000,00 DKK
Software Licenses:                85.000,00 DKK
Hardware Components:              62.500,00 DKK

Subtotal:                        292.500,00 DKK
VAT 25%:                          73.125,00 DKK
Total:                           365.625,00 DKK
""",
        "ground_truth": {
            "vendor_name": "Siemens A/S",
            "cvr_number": "16993085",
            "invoice_number": "SI-DK-2026-PRJ-DIGITALFACTORY-REF78541254-001",
            "invoice_date": "2026-01-28",
            "due_date": "2026-02-27",
            "currency": "DKK",
            "net_amount": 292500.00,
            "vat_amount": 73125.00,
            "total_amount": 365625.00,
            "vat_code": "I25",
            "suggested_account": "6310",
            "journal": "KOB"
        }
    },
    # 50. Missing vendor CVR (incomplete data)
    {
        "id": "INV-050",
        "category": "edge_case",
        "edge_type": "missing_data",
        "ocr_text": """
Quick Print Service
Nørregade 45
1165 København K

FAKTURA

Fakturanr: QPS-2026-125
Dato: 20-01-2026
Betales: Kontant

Kunde: Test Company ApS

Tryksager til markedsføring

Brochurer A4 4-farvet (500 stk)  2.450,00
Visitkort (1000 stk)               850,00
Plakater A2 (25 stk)             1.125,00
Kuverter trykt (500 stk)           680,00

Subtotal:                        5.105,00
Moms 25%:                        1.276,25
Total:                           6.381,25 DKK

Kontant betaling modtaget
""",
        "ground_truth": {
            "vendor_name": "Quick Print Service",
            "cvr_number": None,
            "invoice_number": "QPS-2026-125",
            "invoice_date": "2026-01-20",
            "due_date": "2026-01-20",
            "currency": "DKK",
            "net_amount": 5105.00,
            "vat_amount": 1276.25,
            "total_amount": 6381.25,
            "vat_code": "I25",
            "suggested_account": "7000",
            "journal": "KASSE",
            "notes": "Missing CVR - needs manual lookup"
        }
    },
]

# Combine all invoices
def get_all_invoices() -> List[Dict[str, Any]]:
    """Get all 50 test invoices"""
    from invoice_test_suite_data import REALISTIC_INVOICES
    return REALISTIC_INVOICES + EDGE_CASE_INVOICES

def get_invoices_by_category(category: str) -> List[Dict[str, Any]]:
    """Get invoices by category (realistic or edge_case)"""
    all_invoices = get_all_invoices()
    return [inv for inv in all_invoices if inv.get("category") == category]

def get_edge_cases_by_type(edge_type: str) -> List[Dict[str, Any]]:
    """Get edge cases by specific type"""
    return [inv for inv in EDGE_CASE_INVOICES if inv.get("edge_type") == edge_type]
