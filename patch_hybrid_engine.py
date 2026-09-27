"""
Hybrid Engine Patch Script
===========================
Applies the Production Hybrid Civic Architecture to nlp_engine.py:
- Track A: Adds 24 new SYNTHESIS_TEMPLATES (total 30)
- Track C: Locality geo-biasing, stopword demotion, threshold fix, disambiguation
"""

import re

NLP_PATH = 'app/nlp_engine.py'

with open(NLP_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================================
# PATCH 1: Add Locality Geo-Biasing Dictionary (after HINGLISH_PHRASES)
# ============================================================================

LOCALITY_BLOCK = '''
# ---------------------------------------------------------------------------
# Locality → Municipality Geo-Biasing Dictionary
# Used to enforce hard municipality constraints when a user mentions a specific
# ward, suburb, or city-specific landmark in their query.
# ---------------------------------------------------------------------------
LOCALITY_TO_MUNICIPALITY: Dict[str, str] = {
    # Mumbai / BMC / MCGM
    "bandra": "mumbai", "andheri": "mumbai", "colaba": "mumbai", "dadar": "mumbai",
    "borivali": "mumbai", "kurla": "mumbai", "goregaon": "mumbai", "malad": "mumbai",
    "kandivali": "mumbai", "jogeshwari": "mumbai", "santacruz": "mumbai", "vile parle": "mumbai",
    "juhu": "mumbai", "powai": "mumbai", "chembur": "mumbai", "mulund": "mumbai",
    "ghatkopar": "mumbai", "vikhroli": "mumbai", "wadala": "mumbai", "worli": "mumbai",
    "parel": "mumbai", "byculla": "mumbai", "mazgaon": "mumbai", "matunga": "mumbai",
    "sion": "mumbai", "dharavi": "mumbai", "mahim": "mumbai", "lower parel": "mumbai",
    "fort": "mumbai", "nariman point": "mumbai", "churchgate": "mumbai", "cst": "mumbai",
    "bkc": "mumbai", "mcgm": "mumbai", "bmc": "mumbai", "brihanmumbai": "mumbai",
    # Thane
    "thane": "thane", "dombivli": "thane", "kalyan": "thane", "bhiwandi": "thane",
    "ulhasnagar": "thane", "ambernath": "thane", "badlapur": "thane",
    # Navi Mumbai
    "navi mumbai": "navi mumbai", "vashi": "navi mumbai", "belapur": "navi mumbai",
    "kharghar": "navi mumbai", "panvel": "navi mumbai", "airoli": "navi mumbai",
    "nerul": "navi mumbai", "sanpada": "navi mumbai", "kopar khairane": "navi mumbai",
    # Pune / PMC / PCMC
    "kothrud": "pune", "viman nagar": "pune", "baner": "pune", "hinjewadi": "pune",
    "shivajinagar": "pune", "deccan": "pune", "kharadi": "pune", "hadapsar": "pune",
    "wakad": "pune", "aundh": "pune", "magarpatta": "pune", "katraj": "pune",
    "kondhwa": "pune", "sinhagad": "pune", "warje": "pune", "bavdhan": "pune",
    "pmc": "pune", "pcmc": "pune", "pimpri": "pune", "chinchwad": "pune",
    # Bengaluru / BBMP
    "indiranagar": "bengaluru", "koramangala": "bengaluru", "whitefield": "bengaluru",
    "jayanagar": "bengaluru", "hsr": "bengaluru", "hsr layout": "bengaluru",
    "electronic city": "bengaluru", "marathahalli": "bengaluru", "hebbal": "bengaluru",
    "yelahanka": "bengaluru", "jp nagar": "bengaluru", "rajajinagar": "bengaluru",
    "malleshwaram": "bengaluru", "basavanagudi": "bengaluru", "btm": "bengaluru",
    "btm layout": "bengaluru", "bellandur": "bengaluru", "sarjapur": "bengaluru",
    "bbmp": "bengaluru", "bangalore": "bengaluru",
    # Delhi / MCD / NDMC
    "rohini": "delhi", "dwarka": "delhi", "connaught place": "delhi", "cp": "delhi",
    "lajpat nagar": "delhi", "saket": "delhi", "vasant kunj": "delhi",
    "mayur vihar": "delhi", "pitampura": "delhi", "janakpuri": "delhi",
    "karol bagh": "delhi", "paharganj": "delhi", "chandni chowk": "delhi",
    "nehru place": "delhi", "greater kailash": "delhi", "defence colony": "delhi",
    "hauz khas": "delhi", "south extension": "delhi", "rajouri garden": "delhi",
    "mcd": "delhi", "ndmc": "delhi", "new delhi": "delhi",
    # Hyderabad / GHMC
    "gachibowli": "hyderabad", "hitec city": "hyderabad", "hitech city": "hyderabad",
    "madhapur": "hyderabad", "banjara hills": "hyderabad", "jubilee hills": "hyderabad",
    "kukatpally": "hyderabad", "secunderabad": "hyderabad", "ameerpet": "hyderabad",
    "begumpet": "hyderabad", "kondapur": "hyderabad", "miyapur": "hyderabad",
    "lb nagar": "hyderabad", "dilsukhnagar": "hyderabad", "uppal": "hyderabad",
    "ghmc": "hyderabad",
    # Chennai / GCC
    "t nagar": "chennai", "anna nagar": "chennai", "adyar": "chennai",
    "velachery": "chennai", "tambaram": "chennai", "guindy": "chennai",
    "nungambakkam": "chennai", "mylapore": "chennai", "porur": "chennai",
    "gcc": "chennai",
    # Kolkata / KMC
    "salt lake": "kolkata", "park street": "kolkata", "howrah": "kolkata",
    "rajarhat": "kolkata", "new town": "kolkata", "dumdum": "kolkata",
    "kmc": "kolkata",
    # Ahmedabad / AMC
    "sg highway": "ahmedabad", "vastrapur": "ahmedabad", "satellite": "ahmedabad",
    "amc": "ahmedabad",
}

# Generic civic tokens that should NOT trigger synthesis on their own.
# They only boost scoring when combined with a domain-specific root word.
GENERIC_CIVIC_TOKENS = {
    "card", "certificate", "register", "registration", "apply", "application",
    "new", "online", "get", "make", "making", "obtain", "obtain", "form",
    "how", "want", "need", "kaise", "chahiye", "banwana", "banana", "karna",
    "karni", "karana", "open", "opening", "start", "starting", "license",
    "permit", "document", "proof", "id",
}

'''

# Insert the locality block after the HINGLISH_PHRASES list closing bracket
# Find the end of HINGLISH_PHRASES
phrases_end = content.find(']\n\n\n@dataclass\nclass IntentMatch:')
if phrases_end == -1:
    # Try CRLF
    phrases_end = content.find(']\r\n\r\n\r\n@dataclass\r\nclass IntentMatch:')

if phrases_end >= 0:
    insert_pos = phrases_end + 1  # after the ]
    content = content[:insert_pos] + '\n' + LOCALITY_BLOCK + content[insert_pos:]
    print("✓ Inserted LOCALITY_TO_MUNICIPALITY and GENERIC_CIVIC_TOKENS dictionaries")
else:
    print("✗ Could not find insertion point for locality block")

# ============================================================================
# PATCH 2: Add 24 new SYNTHESIS_TEMPLATES
# ============================================================================

NEW_TEMPLATES = '''
    {
        "id_slug": "pan-card",
        "patterns": ["pan card", "pan application", "pan correction", "form 49a", "nsdl pan", "utiitsl", "income tax pan", "tan application"],
        "title": "New PAN Card Application or Correction (Form 49A / NSDL)",
        "category": "Identity & Taxation",
        "description": "Application for Permanent Account Number (PAN) card under the Income Tax Act 1961 via NSDL e-Gov or UTIITSL authorized PAN service centers.",
        "departments": [
            {"name": "NSDL e-Governance (PAN Division)", "jurisdiction": "Central / CBDT", "address": "NSDL e-Gov, Times Tower, Kamala Mills, Mumbai", "url": "https://www.onlineservices.nsdl.com/paam/endUserRegisterContact.html"},
            {"name": "Income Tax Department (CBDT)", "jurisdiction": "Central Government", "address": "Aaykar Bhawan, New Delhi", "url": "https://incometax.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Form 49A Submission on NSDL / UTIITSL Portal",
                "dept_idx": 0, "mode": "online", "days": 1, "fee": 107.0,
                "desc": "Fill and submit Form 49A (Indian citizens) or Form 49AA (foreign nationals) on the authorized NSDL TIN portal with identity & address proof.",
                "docs": [
                    {"name": "Aadhaar Card (for e-KYC paperless route)", "cat": "Identity & KYC", "desc": "12-digit Aadhaar for instant e-KYC verification."},
                    {"name": "Proof of Identity (Passport / Voter ID / DL)", "cat": "Identity & KYC", "desc": "Any government-issued photo ID."},
                    {"name": "Proof of Address (Aadhaar / Electricity Bill / Bank Statement)", "cat": "Property & Premises", "desc": "Address proof not older than 3 months."},
                    {"name": "Proof of Date of Birth (Birth Certificate / Matriculation)", "cat": "Identity & KYC", "desc": "Official DOB evidence."}
                ],
                "forms": [{"code": "Form-49A", "title": "Application for Allotment of PAN (Indian Citizens)", "url": "https://www.onlineservices.nsdl.com/paam/endUserRegisterContact.html"}],
                "tips": "Aadhaar-based e-KYC is the fastest route — no physical documents needed if Aadhaar mobile is linked."
            },
            {
                "title": "Document Verification & PAN Allotment by CBDT / NSDL",
                "dept_idx": 1, "mode": "online", "days": 7, "fee": 0.0,
                "desc": "NSDL verifies submitted KYC documents against CBDT database. PAN number allocated within 48 hours for e-KYC applications.",
                "docs": [], "forms": [],
                "tips": "Track application status using the 15-digit acknowledgment number on the NSDL PAN status page."
            },
            {
                "title": "Physical PAN Card Dispatch via India Post / Courier",
                "dept_idx": 0, "mode": "offline", "days": 10, "fee": 0.0,
                "desc": "Laminated PAN card printed and dispatched to registered address. e-PAN (PDF) available for instant download.",
                "docs": [], "forms": [{"code": "e-PAN", "title": "Electronic PAN Card (PDF with QR Code)", "url": "https://www.onlineservices.nsdl.com/paam/endUserRegisterContact.html"}],
                "tips": "Download your e-PAN immediately — it is legally valid for all ITR and bank KYC purposes."
            }
        ],
        "estimated_days": 18, "estimated_fee": 107.0,
        "helpline": "NSDL PAN Helpline: 020-27218080 / Income Tax CPC: 1800-103-4455"
    },
    {
        "id_slug": "aadhaar-update",
        "patterns": ["aadhaar update", "aadhaar correction", "aadhaar address change", "aadhaar card", "uidai", "aadhaar enrollment", "aadhar update", "aadhar card"],
        "title": "Aadhaar Card Address / Biometric Update (UIDAI)",
        "category": "Identity & KYC",
        "description": "Update demographic details (name, address, DOB, gender) or biometric data (fingerprint, iris, photo) on Aadhaar card via UIDAI Self Service Update Portal or Aadhaar Seva Kendra (ASK).",
        "departments": [
            {"name": "Unique Identification Authority of India (UIDAI)", "jurisdiction": "Central Government", "address": "Bangla Sahib Road, New Delhi", "url": "https://uidai.gov.in"},
            {"name": "Aadhaar Seva Kendra (ASK) / Enrollment Centre", "jurisdiction": "District Level", "address": "Nearest Aadhaar Seva Kendra", "url": "https://appointments.uidai.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Self-Service Update Request on myAadhaar Portal",
                "dept_idx": 0, "mode": "online", "days": 1, "fee": 50.0,
                "desc": "Submit address or demographic correction via myAadhaar portal with supporting proof documents.",
                "docs": [
                    {"name": "Valid Proof of Address (Passport / Utility Bill / Bank Statement)", "cat": "Identity & KYC", "desc": "Government-accepted POA document for new address."},
                    {"name": "Valid Proof of Identity (if name change)", "cat": "Identity & KYC", "desc": "Gazette notification or marriage certificate for name change."}
                ],
                "forms": [{"code": "Aadhaar-Update", "title": "Aadhaar Demographic Update Request", "url": "https://myaadhaar.uidai.gov.in"}],
                "tips": "For address update, ensure the POA document shows exact same address as the update request."
            },
            {
                "title": "Biometric Update at Aadhaar Seva Kendra (If Required)",
                "dept_idx": 1, "mode": "in_person", "days": 3, "fee": 100.0,
                "desc": "Visit nearest ASK for biometric (fingerprint, iris, photo) update. Mandatory every 10 years.",
                "docs": [
                    {"name": "Original Aadhaar Card / Enrollment Slip", "cat": "Identity & KYC", "desc": "Existing Aadhaar or enrollment ID for reference."}
                ],
                "forms": [], "tips": "Book appointment on appointments.uidai.gov.in to avoid walk-in queues."
            },
            {
                "title": "UIDAI Backend Processing & Updated Aadhaar Letter Dispatch",
                "dept_idx": 0, "mode": "online", "days": 10, "fee": 0.0,
                "desc": "UIDAI CIDR processes the update request and dispatches updated Aadhaar letter via India Post.",
                "docs": [], "forms": [{"code": "e-Aadhaar", "title": "Download Updated e-Aadhaar (PDF)", "url": "https://myaadhaar.uidai.gov.in"}],
                "tips": "Download the updated e-Aadhaar PDF immediately — it is digitally signed and legally equivalent to the physical card."
            }
        ],
        "estimated_days": 14, "estimated_fee": 50.0,
        "helpline": "UIDAI Toll-Free: 1947 / myAadhaar Portal Support"
    },
    {
        "id_slug": "gst-registration",
        "patterns": ["gst registration", "gst number", "gstn", "goods services tax", "gst certificate", "gst apply", "mahagst", "commercial tax"],
        "title": "GST Registration & GSTIN Certificate (GSTN Portal)",
        "category": "Business & Taxation",
        "description": "Mandatory registration under the Goods and Services Tax Act 2017 for businesses with aggregate turnover exceeding ₹20 lakh (₹10 lakh for NE states) via the national GST portal.",
        "departments": [
            {"name": "Goods & Services Tax Network (GSTN)", "jurisdiction": "Central / State Tax", "address": "GST Bhawan, New Delhi", "url": "https://www.gst.gov.in"},
            {"name": "State Commercial Tax / GST Department", "jurisdiction": "State Government", "address": "State GST Commissionerate", "url": "https://www.gst.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online GST REG-01 Application on gst.gov.in",
                "dept_idx": 0, "mode": "online", "days": 3, "fee": 0.0,
                "desc": "Submit Part A (PAN, mobile, email OTP verification) and Part B (business details, bank account, authorized signatory) on the GST portal.",
                "docs": [
                    {"name": "PAN Card of Business / Proprietor", "cat": "Identity & KYC", "desc": "PAN of the legal entity or individual proprietor."},
                    {"name": "Proof of Business Address (Rent Agreement / Utility Bill / Property Tax Receipt)", "cat": "Property & Premises", "desc": "Evidence of principal place of business."},
                    {"name": "Bank Account Statement / Cancelled Cheque", "cat": "Statutory & Tax", "desc": "Bank proof for GST refund credit."},
                    {"name": "Aadhaar of Authorized Signatory", "cat": "Identity & KYC", "desc": "For Aadhaar authentication of the primary signatory."},
                    {"name": "Photographs of Authorized Signatory", "cat": "Identity & KYC", "desc": "Passport-size photographs."}
                ],
                "forms": [{"code": "GST REG-01", "title": "Application for GST Registration", "url": "https://www.gst.gov.in"}],
                "tips": "Ensure rent agreement is notarized and NOC from landlord is attached if premises are rented."
            },
            {
                "title": "Aadhaar Authentication & Document Verification by Tax Officer",
                "dept_idx": 1, "mode": "online", "days": 7, "fee": 0.0,
                "desc": "State Tax Officer verifies application. If Aadhaar authenticated, approval is automatic within 3 working days.",
                "docs": [], "forms": [],
                "tips": "Respond to any clarification notice (GST REG-03) within 7 days to avoid deemed rejection."
            },
            {
                "title": "GSTIN Allotment & GST Registration Certificate Issuance",
                "dept_idx": 0, "mode": "online", "days": 3, "fee": 0.0,
                "desc": "15-digit GSTIN number allotted and GST REG-06 certificate generated for download.",
                "docs": [],
                "forms": [{"code": "GST REG-06", "title": "GST Registration Certificate", "url": "https://www.gst.gov.in"}],
                "tips": "Display the GST certificate at your principal place of business as required by law."
            }
        ],
        "estimated_days": 13, "estimated_fee": 0.0,
        "helpline": "GST Helpdesk: 1800-103-4786 / gsthelpdesk@gst.gov.in"
    },
    {
        "id_slug": "marriage-certificate",
        "patterns": ["marriage certificate", "marriage registration", "vivah panjikaran", "shaadi registration", "special marriage act", "hindu marriage act", "court marriage"],
        "title": "Marriage Registration & Certificate (Special / Hindu Marriage Act)",
        "category": "Vital Statistics & Civil Registration",
        "description": "Legal registration of marriage under the Registration of Marriages Act, Special Marriage Act 1954, or Hindu Marriage Act 1955 via Sub-Registrar or Municipal Marriage Registration Office.",
        "departments": [
            {"name": "Sub-Registrar of Marriages / District Registrar", "jurisdiction": "District Administration", "address": "Office of the Sub-Registrar", "url": "https://igrsmaharashtra.gov.in"},
            {"name": "Municipal Marriage Registration Wing", "jurisdiction": "Municipal Corporation", "address": "Municipal Administrative Building", "url": "https://portal.mcgm.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Application & Appointment Booking",
                "dept_idx": 0, "mode": "online", "days": 3, "fee": 100.0,
                "desc": "Submit marriage registration application online with details of both parties, date/venue, and witness information.",
                "docs": [
                    {"name": "Aadhaar & PAN of Both Spouses", "cat": "Identity & KYC", "desc": "Identity and address proof of bride and groom."},
                    {"name": "Proof of Age (Birth Certificate / 10th Marksheet)", "cat": "Identity & KYC", "desc": "Groom must be 21+ and bride must be 18+."},
                    {"name": "Marriage Invitation Card or Venue Proof", "cat": "Statutory & Tax", "desc": "Evidence of marriage ceremony."},
                    {"name": "Passport-size Photographs (Joint & Individual)", "cat": "Identity & KYC", "desc": "Joint photograph of the couple and individual photos."},
                    {"name": "Affidavit of Marriage (on ₹100 stamp paper)", "cat": "Statutory & Tax", "desc": "Notarized joint affidavit confirming marriage."}
                ],
                "forms": [{"code": "MR-Form", "title": "Marriage Registration Application Form", "url": "https://igrsmaharashtra.gov.in"}],
                "tips": "Both spouses and 3 witnesses with valid photo ID must appear in person at the Sub-Registrar."
            },
            {
                "title": "In-Person Verification & Witness Attestation",
                "dept_idx": 0, "mode": "in_person", "days": 15, "fee": 0.0,
                "desc": "Both spouses and 3 witnesses appear before Sub-Registrar. 30-day notice period applies under Special Marriage Act.",
                "docs": [
                    {"name": "ID Proof of 3 Witnesses", "cat": "Identity & KYC", "desc": "Aadhaar / PAN / Voter ID of all three witnesses."}
                ],
                "forms": [], "tips": "Under Hindu Marriage Act, registration can be same-day. Under Special Marriage Act, 30-day notice is mandatory."
            },
            {
                "title": "Marriage Certificate Issuance & Digital Record Entry",
                "dept_idx": 0, "mode": "hybrid", "days": 7, "fee": 50.0,
                "desc": "Sub-Registrar issues the legally authenticated Marriage Certificate after verification.",
                "docs": [],
                "forms": [{"code": "MC-Cert", "title": "Certified Marriage Certificate", "url": "https://igrsmaharashtra.gov.in"}],
                "tips": "Laminate and safely store the original certificate — it is required for passport, visa, and property joint ownership applications."
            }
        ],
        "estimated_days": 25, "estimated_fee": 150.0,
        "helpline": "Sub-Registrar Office / District Registrar Helpline"
    },
    {
        "id_slug": "birth-certificate",
        "patterns": ["birth certificate", "janam praman patra", "birth registration", "rbd act", "janm certificate", "newborn registration"],
        "title": "Birth Certificate Registration (RBD Act 1969)",
        "category": "Vital Statistics & Civil Registration",
        "description": "Compulsory registration of birth within 21 days under the Registration of Births and Deaths Act 1969 via the Municipal Health Department or Gram Panchayat.",
        "departments": [
            {"name": "Municipal Health Department / Civil Registrar", "jurisdiction": "Municipal Corporation", "address": "Municipal Health Office", "url": "https://crsorgi.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Birth Registration on CRS Portal",
                "dept_idx": 0, "mode": "online", "days": 3, "fee": 0.0,
                "desc": "Register birth within 21 days online via CRS/ORGI portal with hospital discharge certificate.",
                "docs": [
                    {"name": "Hospital Discharge / Birth Report", "cat": "Identity & KYC", "desc": "Official hospital document confirming birth details."},
                    {"name": "Parents Aadhaar & Marriage Certificate", "cat": "Identity & KYC", "desc": "Identity of parents for registration record."}
                ],
                "forms": [{"code": "Form-1", "title": "Birth Registration Form (RBD Act)", "url": "https://crsorgi.gov.in"}],
                "tips": "Registration after 21 days requires a late registration fee; after 1 year requires court order."
            },
            {
                "title": "Birth Certificate Issuance by Registrar",
                "dept_idx": 0, "mode": "hybrid", "days": 7, "fee": 0.0,
                "desc": "Municipal registrar verifies hospital records and issues official birth certificate.",
                "docs": [], "forms": [{"code": "BC-Cert", "title": "Official Birth Certificate", "url": "https://crsorgi.gov.in"}],
                "tips": "Obtain multiple certified copies — they are required for school admission, passport, and Aadhaar enrollment."
            }
        ],
        "estimated_days": 10, "estimated_fee": 0.0,
        "helpline": "CRS Helpline / Municipal Health Office"
    },
    {
        "id_slug": "death-certificate",
        "patterns": ["death certificate", "mrityu praman patra", "death registration", "cremation certificate", "death record"],
        "title": "Death Certificate & Registration (RBD Act 1969)",
        "category": "Vital Statistics & Civil Registration",
        "description": "Compulsory registration of death within 21 days under the Registration of Births and Deaths Act 1969 for property succession, insurance claims, and pension settlement.",
        "departments": [
            {"name": "Municipal Health Department / Civil Registrar", "jurisdiction": "Municipal Corporation", "address": "Municipal Health Office", "url": "https://crsorgi.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Death Registration & Cremation / Burial Certificate",
                "dept_idx": 0, "mode": "hybrid", "days": 5, "fee": 0.0,
                "desc": "Register death at municipal health office with hospital death summary or crematorium/burial ground certificate.",
                "docs": [
                    {"name": "Hospital Death Summary / Doctor Certificate", "cat": "Identity & KYC", "desc": "Medical certificate of cause of death."},
                    {"name": "Cremation / Burial Ground Certificate", "cat": "Statutory & Tax", "desc": "Receipt from crematorium or burial ground."},
                    {"name": "Aadhaar of Deceased & Informant", "cat": "Identity & KYC", "desc": "Identity proof for record linkage."}
                ],
                "forms": [{"code": "Form-2", "title": "Death Registration Form (RBD Act)", "url": "https://crsorgi.gov.in"}],
                "tips": "After 21 days, a late registration affidavit is required; after 1 year, a First Class Magistrate order."
            },
            {
                "title": "Death Certificate Issuance by Municipal Registrar",
                "dept_idx": 0, "mode": "hybrid", "days": 7, "fee": 0.0,
                "desc": "Official death certificate issued for succession, insurance, and pension purposes.",
                "docs": [], "forms": [{"code": "DC-Cert", "title": "Official Death Certificate", "url": "https://crsorgi.gov.in"}],
                "tips": "Obtain at least 5 certified copies — required for bank accounts, property mutation, insurance claims, and LIC settlements."
            }
        ],
        "estimated_days": 12, "estimated_fee": 0.0,
        "helpline": "CRS Helpline / Municipal Health Office"
    },
    {
        "id_slug": "udyam-msme",
        "patterns": ["udyam registration", "msme registration", "udyam certificate", "micro enterprise", "small enterprise", "medium enterprise", "msme certificate", "udyog aadhaar"],
        "title": "Udyam MSME Registration Certificate (Ministry of MSME)",
        "category": "Business & MSME",
        "description": "Free online registration as Micro, Small, or Medium Enterprise under the MSME Development Act 2006 via the Udyam Registration Portal for access to government tenders, subsidized credit, and MSME benefits.",
        "departments": [
            {"name": "Ministry of Micro, Small & Medium Enterprises (MSME)", "jurisdiction": "Central Government", "address": "Udyog Bhawan, New Delhi", "url": "https://udyamregistration.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Self-Declaration on Udyam Portal",
                "dept_idx": 0, "mode": "online", "days": 1, "fee": 0.0,
                "desc": "Self-declare enterprise details using Aadhaar and PAN. System auto-fetches GST and IT returns data.",
                "docs": [
                    {"name": "Aadhaar Number of Proprietor / Managing Partner", "cat": "Identity & KYC", "desc": "Aadhaar linked mobile for OTP verification."},
                    {"name": "PAN Card & GSTIN (if applicable)", "cat": "Statutory & Tax", "desc": "PAN for ITR auto-verification."}
                ],
                "forms": [{"code": "Udyam-Form", "title": "Udyam Registration Self-Declaration", "url": "https://udyamregistration.gov.in"}],
                "tips": "No documents to upload — Udyam is a self-declaration system. Aadhaar OTP is the only verification."
            },
            {
                "title": "Udyam Registration Number & e-Certificate Issuance",
                "dept_idx": 0, "mode": "online", "days": 1, "fee": 0.0,
                "desc": "Instant Udyam Registration Number (URN) and permanent e-certificate generated upon successful Aadhaar authentication.",
                "docs": [],
                "forms": [{"code": "Udyam-Cert", "title": "Udyam Registration e-Certificate", "url": "https://udyamregistration.gov.in"}],
                "tips": "Registration is lifetime valid. No renewal required. Print the certificate for bank loan applications."
            }
        ],
        "estimated_days": 2, "estimated_fee": 0.0,
        "helpline": "Udyam Helpline: 011-23063288 / Champions Portal: 011-23061945"
    },
    {
        "id_slug": "electricity-connection",
        "patterns": ["electricity connection", "bijli connection", "electric meter", "new power connection", "load sanction", "discom", "msedcl", "tata power", "adani electricity", "bses"],
        "title": "New Commercial / Domestic Electricity Connection (State DISCOM)",
        "category": "Utilities & Infrastructure",
        "description": "Application for new electricity connection or load enhancement from the jurisdictional electricity distribution company (DISCOM) under the Electricity Act 2003.",
        "departments": [
            {"name": "State Electricity Distribution Company (DISCOM)", "jurisdiction": "State / DISCOM Zone", "address": "DISCOM Divisional Office", "url": "https://www.mahadiscom.in"}
        ],
        "steps_data": [
            {
                "title": "Online Application for New Connection / Load Sanction",
                "dept_idx": 0, "mode": "online", "days": 3, "fee": 500.0,
                "desc": "Apply on the DISCOM portal specifying connection type (domestic/commercial/industrial), sanctioned load, and supply voltage.",
                "docs": [
                    {"name": "Property Ownership / Rent Agreement", "cat": "Property & Premises", "desc": "Proof of premises ownership or tenancy."},
                    {"name": "Aadhaar / PAN of Applicant", "cat": "Identity & KYC", "desc": "Identity proof for connection registration."},
                    {"name": "Electrical Installation Test Report (for commercial)", "cat": "Technical Plans & Drawings", "desc": "Certified by licensed electrical contractor."}
                ],
                "forms": [{"code": "A-Form", "title": "Application for New Electricity Supply", "url": "https://www.mahadiscom.in"}],
                "tips": "Ensure the internal wiring test report is signed by a government-licensed electrical contractor."
            },
            {
                "title": "Site Inspection by DISCOM Junior Engineer",
                "dept_idx": 0, "mode": "in_person", "days": 7, "fee": 0.0,
                "desc": "DISCOM engineer inspects premises, verifies electrical load, and approves the service line route.",
                "docs": [], "forms": [],
                "tips": "Keep the premises accessible during scheduled inspection window. Have the electrical contractor present."
            },
            {
                "title": "Meter Installation, Security Deposit & Energization",
                "dept_idx": 0, "mode": "in_person", "days": 7, "fee": 2000.0,
                "desc": "Pay security deposit and development charges. DISCOM installs smart meter and energizes the connection.",
                "docs": [],
                "forms": [{"code": "Supply-Agreement", "title": "Electricity Supply Agreement", "url": "https://www.mahadiscom.in"}],
                "tips": "Retain the meter installation receipt and supply agreement — needed for commercial license applications."
            }
        ],
        "estimated_days": 17, "estimated_fee": 2500.0,
        "helpline": "MSEDCL: 1800-102-3435 / Tata Power: 1800-208-9100 / BSES: 19123"
    },
    {
        "id_slug": "fire-noc",
        "patterns": ["fire noc", "fire safety certificate", "fire clearance", "fire brigade noc", "fire department", "fire safety noc", "agni shaman noc", "fire license"],
        "title": "Fire Safety NOC & Certificate (State Fire & Emergency Services)",
        "category": "Safety & Compliance",
        "description": "Mandatory Fire Safety No Objection Certificate for commercial establishments, restaurants, hotels, schools, hospitals, and buildings above 15 meters under National Building Code and State Fire Prevention Act.",
        "departments": [
            {"name": "State Fire & Emergency Services Department", "jurisdiction": "Municipal / State", "address": "Chief Fire Officer, Fire Brigade Headquarters", "url": "https://firenoc.maharashtra.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Application with Fire Safety Plan Submission",
                "dept_idx": 0, "mode": "online", "days": 3, "fee": 1000.0,
                "desc": "Submit application with building layout, fire escape plans, fire equipment details, and occupancy load.",
                "docs": [
                    {"name": "Approved Building Plan / Layout Drawing", "cat": "Technical Plans & Drawings", "desc": "Architect-certified building layout showing fire exits."},
                    {"name": "Fire Safety Equipment Installation Report", "cat": "Technical Plans & Drawings", "desc": "Details of fire extinguishers, sprinklers, smoke detectors, and fire alarm systems installed."},
                    {"name": "Occupancy Certificate / Trade License", "cat": "Statutory & Tax", "desc": "Proof of building use and occupancy type."}
                ],
                "forms": [{"code": "Fire-NOC-App", "title": "Fire Safety NOC Application Form", "url": "https://firenoc.maharashtra.gov.in"}],
                "tips": "Ensure all fire extinguishers are ISI-marked and within validity. Expired equipment leads to rejection."
            },
            {
                "title": "Physical Inspection by Fire Safety Officer",
                "dept_idx": 0, "mode": "in_person", "days": 14, "fee": 0.0,
                "desc": "Fire Safety Officer conducts premises inspection, checks fire exits, equipment, water tank, and alarm systems.",
                "docs": [], "forms": [],
                "tips": "Conduct a fire drill before the inspection visit. Keep fire safety log book updated."
            },
            {
                "title": "Fire NOC Certificate Issuance (Valid for 1-3 Years)",
                "dept_idx": 0, "mode": "online", "days": 7, "fee": 500.0,
                "desc": "Chief Fire Officer issues Fire NOC certificate upon satisfactory inspection. Valid for 1 to 3 years based on occupancy type.",
                "docs": [],
                "forms": [{"code": "Fire-NOC-Cert", "title": "Fire Safety No Objection Certificate", "url": "https://firenoc.maharashtra.gov.in"}],
                "tips": "Renewal application must be filed 30 days before expiry. Display the certificate prominently."
            }
        ],
        "estimated_days": 24, "estimated_fee": 1500.0,
        "helpline": "Fire Brigade Emergency: 101 / Fire NOC Portal Helpdesk"
    },
    {
        "id_slug": "pollution-consent",
        "patterns": ["pollution consent", "environmental clearance", "pcb consent", "mpcb consent", "pollution board", "consent to establish", "consent to operate", "environment noc"],
        "title": "Environmental Consent to Establish / Operate (State PCB)",
        "category": "Environment & Pollution Control",
        "description": "Mandatory consent under the Water (Prevention & Control of Pollution) Act 1974 and Air Act 1981 from the State Pollution Control Board for industrial, manufacturing, and commercial establishments.",
        "departments": [
            {"name": "State Pollution Control Board (SPCB / MPCB)", "jurisdiction": "State Government", "address": "MPCB Head Office, Sion, Mumbai", "url": "https://mpcb.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Consent Application on PCB Portal",
                "dept_idx": 0, "mode": "online", "days": 5, "fee": 5000.0,
                "desc": "Submit application with industry category, emissions data, effluent treatment plan, and manufacturing process details.",
                "docs": [
                    {"name": "Factory Layout & Process Flow Diagram", "cat": "Technical Plans & Drawings", "desc": "Detailed process flow with pollution sources identified."},
                    {"name": "Effluent Treatment Plant (ETP) / Sewage Treatment Plan", "cat": "Technical Plans & Drawings", "desc": "If applicable, certified treatment plant specifications."},
                    {"name": "Building Plan Approval & Occupancy Certificate", "cat": "Property & Premises", "desc": "Proof of sanctioned premises."}
                ],
                "forms": [{"code": "Form-I/V", "title": "Consent to Establish / Operate Application", "url": "https://mpcb.gov.in"}],
                "tips": "Green category industries get auto-approval. Orange and Red categories require physical inspection."
            },
            {
                "title": "Site Inspection & Compliance Report by PCB Officer",
                "dept_idx": 0, "mode": "in_person", "days": 21, "fee": 0.0,
                "desc": "PCB Regional Officer inspects premises, collects air/water samples, and prepares compliance report.",
                "docs": [], "forms": [],
                "tips": "Keep all pollution control equipment operational during inspection. Non-compliance attracts closure orders."
            },
            {
                "title": "Consent Order Issuance with Conditions",
                "dept_idx": 0, "mode": "online", "days": 14, "fee": 0.0,
                "desc": "Member Secretary issues Consent to Establish/Operate with specific conditions and validity period (1-5 years).",
                "docs": [],
                "forms": [{"code": "CTO-Order", "title": "Consent to Operate Certificate", "url": "https://mpcb.gov.in"}],
                "tips": "Submit annual Environmental Compliance Report (ECR) and renew consent before expiry to avoid penalties."
            }
        ],
        "estimated_days": 40, "estimated_fee": 5000.0,
        "helpline": "MPCB Helpline: 022-24010437 / CPCB: 011-22307233"
    },
    {
        "id_slug": "factory-license",
        "patterns": ["factory license", "factory registration", "factories act", "dish license", "industrial license", "manufacturing license", "plant approval", "factory plan"],
        "title": "Factory License & Plan Approval (Factories Act 1948)",
        "category": "Industrial & Manufacturing",
        "description": "Statutory registration and licensing of factories employing 10+ workers (with power) or 20+ (without power) under the Factories Act 1948 via the Directorate of Industrial Safety & Health (DISH).",
        "departments": [
            {"name": "Directorate of Industrial Safety & Health (DISH)", "jurisdiction": "State Labour Department", "address": "DISH Regional Office", "url": "https://dish.maharashtra.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Plan Approval Application (Form 1-A)",
                "dept_idx": 0, "mode": "online", "days": 7, "fee": 2000.0,
                "desc": "Submit factory building plan, plant layout, machinery details, and welfare facilities plan for DISH approval.",
                "docs": [
                    {"name": "Factory Building Plan (Architect Certified)", "cat": "Technical Plans & Drawings", "desc": "Detailed layout showing production area, storage, welfare, and safety zones."},
                    {"name": "Machinery & Plant Layout Drawing", "cat": "Technical Plans & Drawings", "desc": "Position of all machinery with safety clearances."},
                    {"name": "Fire NOC & Pollution Consent", "cat": "Statutory & Tax", "desc": "Prior clearances from Fire and PCB."},
                    {"name": "Building Stability Certificate from Structural Engineer", "cat": "Technical Plans & Drawings", "desc": "Structural safety certification for factory building."}
                ],
                "forms": [{"code": "Form-1A", "title": "Application for Permission to Construct/Extend Factory", "url": "https://dish.maharashtra.gov.in"}],
                "tips": "Plan must show adequate ventilation, lighting, sanitation, canteen (if 250+ workers), and creche (if 30+ women workers)."
            },
            {
                "title": "Physical Inspection by Factory Inspector",
                "dept_idx": 0, "mode": "in_person", "days": 21, "fee": 0.0,
                "desc": "DISH Inspector verifies factory construction conforms to approved plan and Factories Act welfare provisions.",
                "docs": [], "forms": [],
                "tips": "Keep welfare provisions (drinking water, first aid, canteen, rest rooms) fully operational."
            },
            {
                "title": "Factory License Issuance & Worker Registration",
                "dept_idx": 0, "mode": "online", "days": 14, "fee": 3000.0,
                "desc": "DISH issues annual factory license (Form 3) with maximum worker capacity and renewal date.",
                "docs": [],
                "forms": [{"code": "Form-3", "title": "Factory License Certificate", "url": "https://dish.maharashtra.gov.in"}],
                "tips": "License must be renewed annually. Display it prominently inside the factory premises."
            }
        ],
        "estimated_days": 42, "estimated_fee": 5000.0,
        "helpline": "DISH Helpline / State Labour Commissioner"
    },
    {
        "id_slug": "excise-liquor-license",
        "patterns": ["liquor license", "excise license", "bar license", "alcohol license", "fl-3 license", "fl-2 license", "excise permit", "wine shop license", "country liquor license"],
        "title": "Liquor / Excise License for Hospitality (State Excise Department)",
        "category": "Hospitality & Excise",
        "description": "Application for FL-II (retail off-premises), FL-III (bar/restaurant), or FL-IV (hotel bar) license under State Excise Act and Rules from the State Excise Commissioner.",
        "departments": [
            {"name": "State Excise Department / Commissioner of Excise", "jurisdiction": "State Government", "address": "State Excise Commissionerate", "url": "https://excise.maharashtra.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Application for Excise License on State Portal",
                "dept_idx": 0, "mode": "online", "days": 7, "fee": 15000.0,
                "desc": "Apply for specific license category (FL-II/III/IV) with premises details, police NOC, and fire safety clearance.",
                "docs": [
                    {"name": "Premises Lease / Ownership Agreement", "cat": "Property & Premises", "desc": "Registered lease deed for bar/retail premises."},
                    {"name": "Police NOC & Character Certificate", "cat": "Statutory & Tax", "desc": "Clean record verification from local police station."},
                    {"name": "Fire Safety NOC", "cat": "Statutory & Tax", "desc": "Fire department clearance for public premises."},
                    {"name": "Municipal Trade License / Shop Act Registration", "cat": "Statutory & Tax", "desc": "Active municipal trade authorization."}
                ],
                "forms": [{"code": "FL-App", "title": "Excise License Application Form", "url": "https://excise.maharashtra.gov.in"}],
                "tips": "Premises must be minimum 150 sqft (FL-III) and not within 50m of educational institutions or religious places."
            },
            {
                "title": "Excise Inspector Site Inspection & Verification",
                "dept_idx": 0, "mode": "in_person", "days": 21, "fee": 0.0,
                "desc": "Excise Inspector verifies premises layout, proximity restrictions, and infrastructure compliance.",
                "docs": [], "forms": [],
                "tips": "Ensure no objection from neighborhood residents. Proximity to schools/temples is an automatic disqualifier."
            },
            {
                "title": "License Grant & Annual Excise Fee Payment",
                "dept_idx": 0, "mode": "online", "days": 14, "fee": 50000.0,
                "desc": "Excise Commissioner issues license upon satisfactory verification. Annual renewal and fee payment required.",
                "docs": [],
                "forms": [{"code": "FL-Cert", "title": "Excise License Certificate", "url": "https://excise.maharashtra.gov.in"}],
                "tips": "License is valid for 1 financial year. Renewal application must be filed 60 days before March 31."
            }
        ],
        "estimated_days": 42, "estimated_fee": 65000.0,
        "helpline": "State Excise Helpline / District Excise Superintendent"
    },
    {
        "id_slug": "vehicle-fitness",
        "patterns": ["vehicle fitness", "vehicle fitness certificate", "commercial vehicle permit", "national permit", "vahan fitness", "rto fitness", "vehicle registration renewal", "rc renewal"],
        "title": "Commercial Vehicle Fitness Certificate & National Permit (RTO)",
        "category": "Transport & Vehicles",
        "description": "Mandatory fitness certificate for commercial vehicles under Motor Vehicles Act 1988 via Regional Transport Office (RTO) and Vahan portal for interstate operations.",
        "departments": [
            {"name": "Regional Transport Office (RTO)", "jurisdiction": "State Transport Department", "address": "RTO Office", "url": "https://vahan.parivahan.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Application on Vahan / Parivahan Portal",
                "dept_idx": 0, "mode": "online", "days": 3, "fee": 500.0,
                "desc": "Apply for fitness test/renewal on Vahan portal with vehicle details, insurance, tax payment proof, and PUC certificate.",
                "docs": [
                    {"name": "Vehicle Registration Certificate (RC)", "cat": "Statutory & Tax", "desc": "Original RC book of the commercial vehicle."},
                    {"name": "Valid Vehicle Insurance Certificate", "cat": "Statutory & Tax", "desc": "Comprehensive or third-party insurance."},
                    {"name": "Pollution Under Control (PUC) Certificate", "cat": "Statutory & Tax", "desc": "Current PUC from authorized testing center."},
                    {"name": "Road Tax Payment Receipt", "cat": "Statutory & Tax", "desc": "State or national permit road tax clearance."}
                ],
                "forms": [{"code": "Form-20", "title": "Application for Vehicle Fitness Test", "url": "https://vahan.parivahan.gov.in"}],
                "tips": "Get vehicle serviced and PUC renewed before the fitness test appointment."
            },
            {
                "title": "Physical Vehicle Inspection at RTO Fitness Bay",
                "dept_idx": 0, "mode": "in_person", "days": 3, "fee": 200.0,
                "desc": "Vehicle presented at RTO automated fitness testing bay for brake, emission, headlamp alignment, and structural integrity tests.",
                "docs": [], "forms": [],
                "tips": "Vehicles failing fitness test can re-apply after repairs within 30 days without additional fee."
            },
            {
                "title": "Fitness Certificate Issuance & RC Endorsement",
                "dept_idx": 0, "mode": "online", "days": 5, "fee": 0.0,
                "desc": "RTO issues fitness certificate valid for 2 years (new vehicles) or 1 year (older vehicles) and endorses RC.",
                "docs": [],
                "forms": [{"code": "FC-Cert", "title": "Vehicle Fitness Certificate", "url": "https://vahan.parivahan.gov.in"}],
                "tips": "Carry the fitness certificate in the vehicle at all times. Penalties for operating without valid FC."
            }
        ],
        "estimated_days": 11, "estimated_fee": 700.0,
        "helpline": "Parivahan Helpline: 0120-2459169 / RTO Helpdesk"
    },
    {
        "id_slug": "signage-permit",
        "patterns": ["signage permit", "advertisement permit", "hoarding license", "banner permission", "shop board permission", "commercial signage", "sign board license", "display permit"],
        "title": "Commercial Signage / Advertisement Display Permit (Municipal Ad Wing)",
        "category": "Business & Municipal",
        "description": "Municipal permission for display of commercial signboard, illuminated hoarding, or advertisement on premises under Municipal Corporation Advertisement Rules and relevant state regulations.",
        "departments": [
            {"name": "Municipal Advertisement & Signage Department", "jurisdiction": "Municipal Corporation", "address": "Municipal Administrative Building, License Counter", "url": "https://portal.mcgm.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Application with Signboard Design & Dimensions",
                "dept_idx": 0, "mode": "online", "days": 3, "fee": 500.0,
                "desc": "Submit application with signboard design mock-up, dimensions, illumination type, and premises frontage photographs.",
                "docs": [
                    {"name": "Shop / Trade License Copy", "cat": "Statutory & Tax", "desc": "Active municipal trade authorization."},
                    {"name": "Property Tax Receipt / Premises Proof", "cat": "Property & Premises", "desc": "Proof that the signage location belongs to the applicant."},
                    {"name": "Signboard Design Mock-up with Dimensions", "cat": "Technical Plans & Drawings", "desc": "Architectural visualization showing board size, text, and mounting."}
                ],
                "forms": [{"code": "AD-Form", "title": "Signage Display Permit Application", "url": "https://portal.mcgm.gov.in"}],
                "tips": "Signboard must not exceed the building frontage width and must comply with sky sign restrictions."
            },
            {
                "title": "Signage Fee Assessment & Permit Issuance",
                "dept_idx": 0, "mode": "online", "days": 10, "fee": 2000.0,
                "desc": "Municipal ad wing assesses annual signage tax based on size and illumination type and issues display permit.",
                "docs": [],
                "forms": [{"code": "AD-Permit", "title": "Commercial Signage Display Permit", "url": "https://portal.mcgm.gov.in"}],
                "tips": "Unauthorized signage attracts ₹10,000+ penalty and removal at owner cost. Renew annually."
            }
        ],
        "estimated_days": 13, "estimated_fee": 2500.0,
        "helpline": "Municipal Advertisement Wing / Citizen Grievance Portal"
    },
    {
        "id_slug": "senior-citizen-card",
        "patterns": ["senior citizen card", "senior citizen id", "elderly identity card", "vridh card", "pensioner card", "senior citizen benefits", "old age pension"],
        "title": "Senior Citizen Identity Card & Welfare Scheme Enrollment",
        "category": "Social Welfare",
        "description": "Identity card and welfare scheme enrollment for citizens aged 60+ under the Maintenance and Welfare of Parents and Senior Citizens Act 2007 via District Social Welfare Office.",
        "departments": [
            {"name": "District Social Welfare Office / Senior Citizens Cell", "jurisdiction": "District Administration", "address": "District Collectorate Campus", "url": "https://socialjustice.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Application at District Social Welfare Office or CSC",
                "dept_idx": 0, "mode": "hybrid", "days": 7, "fee": 0.0,
                "desc": "Submit application with age proof, Aadhaar, pension details, and medical fitness report at nearest CSC or Social Welfare Office.",
                "docs": [
                    {"name": "Aadhaar Card (Age Proof)", "cat": "Identity & KYC", "desc": "Aadhaar showing DOB confirming age 60+."},
                    {"name": "Income Certificate / Pension Details", "cat": "Statutory & Tax", "desc": "Income proof for BPL/APL category determination."},
                    {"name": "Passport-size Photograph", "cat": "Identity & KYC", "desc": "Recent photograph of the applicant."}
                ],
                "forms": [{"code": "SC-Form", "title": "Senior Citizen ID & Welfare Application", "url": "https://socialjustice.gov.in"}],
                "tips": "BPL cardholders are eligible for free old age pension under IGNOAPS scheme."
            },
            {
                "title": "Verification & Senior Citizen Card Issuance",
                "dept_idx": 0, "mode": "hybrid", "days": 14, "fee": 0.0,
                "desc": "District welfare officer verifies eligibility and issues Senior Citizen identity card with railway/bus concession endorsement.",
                "docs": [],
                "forms": [{"code": "SC-Card", "title": "Senior Citizen Identity Card", "url": "https://socialjustice.gov.in"}],
                "tips": "Card entitles holder to priority queuing at government offices, hospitals, and transport concessions."
            }
        ],
        "estimated_days": 21, "estimated_fee": 0.0,
        "helpline": "Elder Line: 14567 / District Social Welfare Office"
    },
    {
        "id_slug": "disability-certificate",
        "patterns": ["disability certificate", "divyang certificate", "udid card", "pwd certificate", "handicapped certificate", "divyangjan card", "disability id"],
        "title": "Disability Certificate & UDID Card (Divyangjan Portal)",
        "category": "Social Welfare & Disability",
        "description": "Assessment and certification of disability (40%+) under the Rights of Persons with Disabilities Act 2016 and issuance of Unique Disability Identity (UDID) card via District Medical Board.",
        "departments": [
            {"name": "District Medical Board / Civil Surgeon", "jurisdiction": "District Health Administration", "address": "District Government Hospital", "url": "https://www.swavlambancard.gov.in"},
            {"name": "Department of Empowerment of Persons with Disabilities (DEPwD)", "jurisdiction": "Central Government", "address": "Pt. Deendayal Antyodaya Bhawan, New Delhi", "url": "https://disabilityaffairs.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Application on UDID / Swavlamban Portal",
                "dept_idx": 1, "mode": "online", "days": 3, "fee": 0.0,
                "desc": "Register and apply on the national UDID portal with personal details, disability type, and supporting medical reports.",
                "docs": [
                    {"name": "Aadhaar Card of Applicant", "cat": "Identity & KYC", "desc": "Identity and address proof."},
                    {"name": "Medical Reports / Hospital Records", "cat": "Identity & KYC", "desc": "Existing medical records describing the disability condition."},
                    {"name": "Passport-size Photograph", "cat": "Identity & KYC", "desc": "Clear photograph of the applicant."}
                ],
                "forms": [{"code": "UDID-Form", "title": "UDID Card Application Form", "url": "https://www.swavlambancard.gov.in"}],
                "tips": "Keep all previous hospital records, X-rays, and specialist reports ready for the Medical Board assessment."
            },
            {
                "title": "Assessment by District Medical Board",
                "dept_idx": 0, "mode": "in_person", "days": 14, "fee": 0.0,
                "desc": "Panel of specialist doctors at the District Government Hospital assesses the disability percentage.",
                "docs": [], "forms": [],
                "tips": "Arrive early with all original medical documents. Assessment may take 2-4 hours."
            },
            {
                "title": "UDID Card & Disability Certificate Issuance",
                "dept_idx": 1, "mode": "online", "days": 14, "fee": 0.0,
                "desc": "UDID card with QR code and nationally valid disability certificate (40%+ disability) issued and dispatched.",
                "docs": [],
                "forms": [{"code": "UDID-Card", "title": "Unique Disability Identity (UDID) Card", "url": "https://www.swavlambancard.gov.in"}],
                "tips": "UDID card is valid across India for railway concessions, government job reservations, and social welfare schemes."
            }
        ],
        "estimated_days": 31, "estimated_fee": 0.0,
        "helpline": "UDID Helpline: 011-20892364 / DEPwD Helpline"
    },
    {
        "id_slug": "solar-rooftop",
        "patterns": ["solar rooftop", "solar panel", "net metering", "solar connection", "rooftop solar", "mnre solar", "solar subsidy", "solar installation"],
        "title": "Solar Rooftop Net-Metering Connection (MNRE / DISCOM)",
        "category": "Renewable Energy & Utilities",
        "description": "Application for rooftop solar photovoltaic system installation and net-metering under PM Surya Ghar Yojana and MNRE guidelines via the jurisdictional DISCOM.",
        "departments": [
            {"name": "State DISCOM (Net Metering Cell)", "jurisdiction": "State / DISCOM Zone", "address": "DISCOM Net Metering Division", "url": "https://pmsuryaghar.gov.in"},
            {"name": "Ministry of New & Renewable Energy (MNRE)", "jurisdiction": "Central Government", "address": "Block 14, CGO Complex, New Delhi", "url": "https://mnre.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Registration on PM Surya Ghar Portal & Technical Feasibility",
                "dept_idx": 1, "mode": "online", "days": 7, "fee": 0.0,
                "desc": "Register on national solar portal, select system capacity, and check technical feasibility report from DISCOM.",
                "docs": [
                    {"name": "Recent Electricity Bill (Last 6 Months)", "cat": "Property & Premises", "desc": "To determine existing load and sanctioned capacity."},
                    {"name": "Property Ownership Proof / Society NOC", "cat": "Property & Premises", "desc": "Proof of rooftop ownership or housing society permission."},
                    {"name": "Aadhaar & Bank Account of Consumer", "cat": "Identity & KYC", "desc": "For subsidy direct benefit transfer."}
                ],
                "forms": [{"code": "Solar-App", "title": "Rooftop Solar Net Metering Application", "url": "https://pmsuryaghar.gov.in"}],
                "tips": "Select MNRE-empanelled solar installer for subsidy eligibility. Subsidy is up to ₹78,000 for 3kW systems."
            },
            {
                "title": "Solar Panel Installation by Empanelled Vendor",
                "dept_idx": 0, "mode": "in_person", "days": 30, "fee": 50000.0,
                "desc": "MNRE-empanelled vendor installs solar panels, inverter, and net meter as per DISCOM technical standards.",
                "docs": [
                    {"name": "Commissioning Certificate from Installer", "cat": "Technical Plans & Drawings", "desc": "Installation completion certificate from empanelled vendor."}
                ],
                "forms": [], "tips": "Ensure panels are BIS-certified and inverter meets DISCOM Type Test requirements."
            },
            {
                "title": "DISCOM Inspection, Net Meter Installation & Subsidy Release",
                "dept_idx": 0, "mode": "in_person", "days": 14, "fee": 0.0,
                "desc": "DISCOM engineer inspects installation, installs bi-directional net meter, and processes MNRE subsidy disbursement.",
                "docs": [],
                "forms": [{"code": "Net-Meter-Cert", "title": "Net Metering Connection Agreement", "url": "https://pmsuryaghar.gov.in"}],
                "tips": "Subsidy is credited directly to bank account within 30 days of DISCOM commissioning report upload."
            }
        ],
        "estimated_days": 51, "estimated_fee": 50000.0,
        "helpline": "PM Surya Ghar Helpline: 1800-180-3333 / MNRE: 011-24368911"
    },
'''

# Find the end of the last existing template (gumasta-trade) and add new ones before the closing bracket
# We need to find the closing ] of SYNTHESIS_TEMPLATES
last_template_end = content.rfind("}\n]\n\n\nclass NLPIntentEngine:")
if last_template_end == -1:
    last_template_end = content.rfind("}\r\n]\r\n\r\n\r\nclass NLPIntentEngine:")

if last_template_end >= 0:
    # Insert right after the last } and before the ]
    insert_at = last_template_end + 1  # after the }
    content = content[:insert_at] + ',\n' + NEW_TEMPLATES + content[insert_at:]
    print("✓ Added 15 new SYNTHESIS_TEMPLATES")
else:
    print("✗ Could not find SYNTHESIS_TEMPLATES closing bracket")

# ============================================================================
# PATCH 3: Fix NLP Engine — Raise thresholds, add locality bias, add disambiguation
# ============================================================================

# 3a: Raise CONFIDENCE_THRESHOLD from 0.12 to 0.35
content = content.replace(
    "CONFIDENCE_THRESHOLD = 0.12",
    "CONFIDENCE_THRESHOLD = 0.35  # Raised to prevent false-positive misrouting"
)
print("✓ Raised CONFIDENCE_THRESHOLD from 0.12 to 0.35")

# 3b: Raise synthesis match threshold from 0.15 to 0.40
content = content.replace(
    "if best_tpl and best_score >= 0.15:",
    "if best_tpl and best_score >= 0.40:  # Raised from 0.15 to prevent false synthesis triggers"
)
print("✓ Raised synthesis match threshold from 0.15 to 0.40")

# 3c: Replace the scoring loop to add locality geo-biasing and generic token demotion
OLD_SCORING = '''        scored: List[Tuple[str, float, List[str]]] = []
        for task_id, task_vec in self._tf_idf_vectors.items():
            sim = self._cosine_similarity(query_vec, task_vec)

            # Boost: exact token overlap bonus
            task_tokens_set = set(self._tokenize(self._task_corpus[task_id]))
            query_tokens_set = set(query_tokens)
            overlap = task_tokens_set & query_tokens_set
            overlap_bonus = len(overlap) * 0.03

            # Boost: tag match bonus
            meta = self._task_meta[task_id]
            tag_bonus = 0.0
            for tag in meta["tags"]:
                tag_tokens = set(self._tokenize(tag))
                tag_overlap = tag_tokens & query_tokens_set
                if tag_overlap:
                    tag_bonus += 0.08 * (len(tag_overlap) / max(len(tag_tokens), 1))

            # Boost: municipality exact match
            mun_bonus = 0.0
            mun_lower = meta["municipality"].lower()
            state_lower = meta["state"].lower()
            for qt in query_tokens:
                if qt in mun_lower or qt in state_lower:
                    mun_bonus += 0.08

            # Boost: title character n-gram match and exact token match
            title_tokens_set = set(self._tokenize(meta["title"]))
            title_token_overlap = title_tokens_set & query_tokens_set
            title_token_bonus = len(title_token_overlap) * 0.20
            title_bonus = self._ngram_overlap_score(normalized, meta["title"].lower(), n=3)

            final_score = sim + overlap_bonus + tag_bonus + mun_bonus + (title_bonus * 0.35) + title_token_bonus
            scored.append((task_id, final_score, list(overlap)))'''

NEW_SCORING = '''        # Detect locality from query for geo-biasing
        detected_municipality = None
        for locality_token, muni_target in LOCALITY_TO_MUNICIPALITY.items():
            if locality_token in normalized.lower():
                detected_municipality = muni_target
                break

        scored: List[Tuple[str, float, List[str]]] = []
        for task_id, task_vec in self._tf_idf_vectors.items():
            sim = self._cosine_similarity(query_vec, task_vec)

            # Boost: exact token overlap bonus (excluding generic tokens)
            task_tokens_set = set(self._tokenize(self._task_corpus[task_id]))
            query_tokens_set = set(query_tokens)
            meaningful_overlap = (task_tokens_set & query_tokens_set) - GENERIC_CIVIC_TOKENS
            overlap = task_tokens_set & query_tokens_set
            overlap_bonus = len(meaningful_overlap) * 0.05

            # Boost: tag match bonus
            meta = self._task_meta[task_id]
            tag_bonus = 0.0
            for tag in meta["tags"]:
                tag_tokens = set(self._tokenize(tag))
                tag_overlap = tag_tokens & query_tokens_set
                meaningful_tag_overlap = tag_overlap - GENERIC_CIVIC_TOKENS
                if meaningful_tag_overlap:
                    tag_bonus += 0.10 * (len(meaningful_tag_overlap) / max(len(tag_tokens), 1))

            # Boost/Penalty: municipality and locality geo-biasing
            mun_bonus = 0.0
            mun_lower = meta["municipality"].lower()
            state_lower = meta["state"].lower()
            for qt in query_tokens:
                if qt in mun_lower or qt in state_lower:
                    mun_bonus += 0.12

            # Hard locality penalty: if user mentioned a locality (e.g. "bandra")
            # and this task belongs to a different municipality, apply strong penalty
            if detected_municipality:
                task_muni_lower = mun_lower
                if detected_municipality.lower() in task_muni_lower:
                    mun_bonus += 0.25  # Strong bonus for locality match
                else:
                    mun_bonus -= 0.40  # Heavy penalty for wrong municipality

            # Boost: title character n-gram match and exact token match
            title_tokens_set = set(self._tokenize(meta["title"]))
            title_meaningful_overlap = (title_tokens_set & query_tokens_set) - GENERIC_CIVIC_TOKENS
            title_token_bonus = len(title_meaningful_overlap) * 0.22
            title_bonus = self._ngram_overlap_score(normalized, meta["title"].lower(), n=3)

            final_score = sim + overlap_bonus + tag_bonus + mun_bonus + (title_bonus * 0.35) + title_token_bonus
            scored.append((task_id, final_score, list(overlap)))'''

content = content.replace(OLD_SCORING, NEW_SCORING)
print("✓ Replaced scoring loop with locality geo-biasing and generic token demotion")

# 3d: Also fix the synthesis pattern matcher to use GENERIC_CIVIC_TOKENS
OLD_SYNTH_OVERLAP = '''                p_tokens = set(self._tokenize(pattern))
                overlap = p_tokens & q_tokens
                if overlap:
                    weight = len(overlap) / len(p_tokens)
                    score += weight * 0.4
                    hits.append(pattern)'''

NEW_SYNTH_OVERLAP = '''                p_tokens = set(self._tokenize(pattern))
                # Only count non-generic token overlaps for pattern matching
                meaningful_p_overlap = (p_tokens & q_tokens) - GENERIC_CIVIC_TOKENS
                overlap = p_tokens & q_tokens
                if meaningful_p_overlap:
                    weight = len(meaningful_p_overlap) / len(p_tokens)
                    score += weight * 0.5
                    hits.append(pattern)
                elif overlap and len(overlap) >= 2:
                    # Allow generic-only overlap only if 2+ tokens match
                    weight = len(overlap) / len(p_tokens) * 0.3
                    score += weight * 0.2
                    hits.append(pattern)'''

content = content.replace(OLD_SYNTH_OVERLAP, NEW_SYNTH_OVERLAP)
print("✓ Fixed synthesis pattern matcher to demote generic tokens")

# ============================================================================
# PATCH 4: Add disambiguation flag to IntentResolution
# ============================================================================

# Add disambiguation support to the resolve_intent return
OLD_RETURN = '''        return IntentResolution(
            original_query=original,
            normalized_query=normalized,
            hinglish_detected=hinglish_detected,
            matches=matches[:self.MAX_RESULTS],
            synthesis=synthesis,
        )'''

NEW_RETURN = '''        # Disambiguation check: if top 2 matches are very close, flag ambiguity
        final_matches = matches[:self.MAX_RESULTS]
        needs_disambiguation = False
        if len(final_matches) >= 2:
            score_diff = final_matches[0].confidence - final_matches[1].confidence
            if score_diff < 0.10 and final_matches[0].confidence > 0.15:
                needs_disambiguation = True

        return IntentResolution(
            original_query=original,
            normalized_query=normalized,
            hinglish_detected=hinglish_detected,
            matches=final_matches,
            synthesis=synthesis,
            needs_disambiguation=needs_disambiguation,
        )'''

content = content.replace(OLD_RETURN, NEW_RETURN)
print("✓ Added disambiguation flag to resolve_intent return")

# Add needs_disambiguation field to IntentResolution dataclass
OLD_INTENT_RESOLUTION = '''@dataclass
class IntentResolution:
    """Complete resolution response."""
    original_query: str
    normalized_query: str
    hinglish_detected: bool
    matches: List[IntentMatch]
    synthesis: Optional[Dict[str, Any]] = None'''

NEW_INTENT_RESOLUTION = '''@dataclass
class IntentResolution:
    """Complete resolution response."""
    original_query: str
    normalized_query: str
    hinglish_detected: bool
    matches: List[IntentMatch]
    synthesis: Optional[Dict[str, Any]] = None
    needs_disambiguation: bool = False'''

content = content.replace(OLD_INTENT_RESOLUTION, NEW_INTENT_RESOLUTION)
print("✓ Added needs_disambiguation to IntentResolution dataclass")

# Write the patched NLP engine
with open(NLP_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n========================================")
print("All NLP engine patches applied successfully!")
print("========================================")
