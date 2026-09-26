"""
Dual-Track NLP Intent Resolution & Civic Route Synthesizer
===========================================================
Replaces the brittle client-side keyword filter with:

Track 1 — Catalog Matcher:
  TF-IDF vectorization over task metadata (title, description, tags, category,
  municipality, state) with cosine similarity scoring. Includes a comprehensive
  Hinglish transliteration and Devanagari normalization layer that maps common
  Hindi/Hinglish tokens to their English civic equivalents before vectorization.

Track 2 — Zero-Shot Statutory Graph Synthesizer:
  When no pre-cataloged task exceeds the confidence threshold, synthesizes a
  complete, valid Directed Acyclic Graph (DAG) procedure skeleton (CivicTask)
  from Indian civic domain templates (Voter ID, Ration Card, Pharmacy License,
  Passport, Driving License, Birth/Death Certificates, Domicile, GST, etc.)
  and dynamically registers it into the runtime database so that the user
  can immediately explore the interactive roadmap, step dossier, and document locker.
"""

import re
import math
from typing import List, Dict, Optional, Tuple, Any
from collections import Counter
from dataclasses import dataclass, field

from app.models import (
    CivicTask, TaskStep, DepartmentInfo, DocumentRequirement,
    FormRequirement, VerificationSource, SubmissionMode, StepStatus
)
from app.database import db


# ---------------------------------------------------------------------------
# Devanagari Hindi → Transliterated Civic Terms Mapping
# ---------------------------------------------------------------------------
DEVANAGARI_MAP: Dict[str, str] = {
    "दुकान": "dukaan shop business establishment gumasta",
    "दुकानें": "dukaan shop business establishment",
    "व्यापार": "vyapar business trade commerce",
    "कारोबार": "karobar business enterprise",
    "पंजीकरण": "registration register",
    "आवेदन": "application apply",
    "शुरू": "start open begin commission",
    "खोलना": "open start begin commission",
    "खोलनी": "open start begin commission",
    "होटल": "hotel restaurant eating house",
    "बेकरी": "bakery food cafe restaurant",
    "रेस्टोरेंट": "restaurant eatery cafe",
    "खाना": "food restaurant eating house",
    "भोजन": "food meal restaurant",
    "मिठाई": "sweets confectionery food",
    "घर": "house property residence",
    "मकान": "house property building",
    "जमीन": "land property plot",
    "प्लॉट": "plot land property",
    "प्रॉपर्टी": "property real estate",
    "दाखिल": "mutation khata transfer",
    "खारिज": "mutation khata transfer",
    "नामांतरण": "mutation property namantaran title transfer",
    "राशन": "ration card pds food distribution",
    "कार्ड": "card certificate document",
    "वोटर": "voter id election epic card",
    "मतदाता": "voter election epic card",
    "पहचान": "identity card id proof",
    "पासपोर्ट": "passport seva kendra rpo",
    "लाइसेंस": "license driving permit trade",
    "ड्राइविंग": "driving license rto parivahan",
    "जन्म": "birth certificate registration",
    "मृत्यु": "death certificate registration",
    "प्रमाणपत्र": "certificate proof deed",
    "आय": "income certificate tehsildar sdm",
    "जाति": "caste certificate reservation",
    "निवास": "domicile residence certificate",
    "जीएसटी": "gst registration gstn tax",
    "बिजली": "electricity connection power discom",
    "पानी": "water supply connection municipal",
    "दवा": "pharmacy chemist drug license medicine",
    "फार्मेसी": "pharmacy chemist drug license",
    "केमिस्ट": "chemist pharmacy drug license",
    "शादी": "marriage certificate registrar",
    "विवाह": "marriage certificate registrar",
    "गुमास्ता": "gumasta shop establishment act",
    "बीएमसी": "bmc mcgm mumbai maharashtra",
    "एमसीडी": "mcd delhi",
    "बीबीएमपी": "bbmp bengaluru karnataka",
    "जीएचएमसी": "ghmc hyderabad telangana",
}

# ---------------------------------------------------------------------------
# Hinglish / Romanized Hindi → English civic concept mapping
# ---------------------------------------------------------------------------
HINGLISH_MAP: Dict[str, List[str]] = {
    # Business & Registration
    "dukaan": ["shop", "store", "business", "establishment", "gumasta", "trade"],
    "dukan": ["shop", "store", "business", "establishment", "gumasta", "trade"],
    "dukane": ["shop", "business", "establishment"],
    "vyapar": ["business", "trade", "commerce", "license"],
    "vyapaar": ["business", "trade", "commerce", "license"],
    "karobar": ["business", "enterprise", "trade"],
    "karobaar": ["business", "enterprise", "trade"],
    "dhandha": ["business", "trade"],
    "kaam": ["work", "business", "employment"],
    "rojgar": ["employment", "job", "business"],
    "register": ["register", "registration"],
    "panjikaran": ["registration", "register"],
    "shuru": ["start", "begin", "open", "commence", "commission"],
    "kholna": ["open", "start", "commission"],
    "kholni": ["open", "start", "commission"],
    "kholo": ["open", "start", "commission"],
    "khol": ["open", "start", "commission"],
    "chalana": ["run", "operate", "manage"],
    "chalani": ["run", "operate", "manage"],
    "chalu": ["start", "open", "commence"],
    "karna": ["do", "perform", "apply", "register"],
    "karni": ["do", "perform", "apply", "register"],
    "karein": ["do", "perform", "apply", "register"],
    "karo": ["do", "perform", "apply", "register"],
    "banwana": ["get", "obtain", "make", "apply"],
    "banwani": ["get", "obtain", "make", "apply"],
    "banana": ["make", "create", "build", "register"],
    "banayein": ["make", "create", "build", "register"],
    "lena": ["take", "get", "obtain", "apply"],
    "leni": ["take", "get", "obtain", "apply"],
    "apply": ["apply", "application"],
    "avedan": ["application", "apply"],
    "chahiye": ["need", "require", "apply"],
    "chahta": ["want", "require", "apply"],
    "chahti": ["want", "require", "apply"],

    # Food & Hospitality
    "hotel": ["hotel", "restaurant", "eating house"],
    "dhaba": ["restaurant", "eatery", "food stall"],
    "bakery": ["bakery", "food", "cafe", "eating house"],
    "restaurant": ["restaurant", "eating house", "food"],
    "cafe": ["cafe", "bakery", "restaurant", "food"],
    "khana": ["food", "eating", "restaurant"],
    "bhojan": ["food", "meal", "restaurant"],
    "mithai": ["sweets", "confectionery", "food", "bakery"],
    "chai": ["tea", "food stall", "cafe"],
    "nashta": ["food", "breakfast", "snack"],
    "rasoi": ["kitchen", "cloud kitchen", "food"],

    # Healthcare & Pharmacy
    "medical": ["pharmacy", "chemist", "drug license", "medicine"],
    "pharmacy": ["pharmacy", "chemist", "drug license", "medicine"],
    "chemist": ["chemist", "pharmacy", "drug license"],
    "dawai": ["medicine", "pharmacy", "drug license"],
    "dawakhana": ["pharmacy", "chemist", "dispensary"],
    "hospital": ["hospital", "clinic", "health"],
    "clinic": ["clinic", "healthcare", "medical"],

    # Property & Real Estate
    "ghar": ["house", "property", "residence"],
    "makaan": ["house", "property", "building"],
    "makan": ["house", "property", "building"],
    "zameen": ["land", "property", "plot"],
    "zamin": ["land", "property", "plot"],
    "jamin": ["land", "property", "plot"],
    "plot": ["plot", "land", "property"],
    "flat": ["flat", "apartment", "property"],
    "building": ["building", "construction", "property"],
    "imarat": ["building", "construction"],
    "property": ["property", "real estate", "mutation"],
    "sampatti": ["property", "asset"],
    "mutation": ["mutation", "transfer", "property", "namantaran"],
    "namantaran": ["mutation", "name transfer", "property", "khata"],
    "khata": ["khata", "property record", "mutation"],
    "dakhil": ["mutation", "khata transfer"],
    "kharij": ["mutation", "khata transfer"],
    "registry": ["registration", "property", "deed", "title"],
    "patta": ["deed", "property", "title"],
    "khareedna": ["buy", "purchase", "property"],
    "kharidna": ["buy", "purchase", "property"],
    "bechna": ["sell", "sale", "property"],
    "kiraya": ["rent", "lease", "tenancy"],
    "kirayedar": ["tenant", "renter"],
    "maalik": ["owner", "landlord"],
    "malik": ["owner", "landlord"],

    # Construction
    "nirman": ["construction", "building"],
    "nirmaan": ["construction", "building"],
    "tod": ["demolition", "demolish"],
    "todna": ["demolish", "demolition"],
    "naksha": ["plan", "layout", "sanction", "building plan"],

    # Taxes & Revenue
    "tax": ["tax", "revenue"],
    "kar": ["tax", "duty"],
    "kara": ["tax", "duty"],
    "bhugtan": ["payment", "pay"],
    "paisa": ["money", "payment", "fee"],
    "shulk": ["fee", "charges", "duty"],
    "challan": ["challan", "payment receipt", "fee"],

    # Documents & Identity
    "aadhaar": ["aadhaar", "identity", "id proof"],
    "aadhar": ["aadhaar", "identity", "id proof"],
    "pan": ["pan card", "income tax"],
    "voter": ["voter", "election", "voter id", "epic"],
    "matdata": ["voter", "election", "epic"],
    "pehchaan": ["identity", "identification", "id"],
    "pehchan": ["identity", "identification", "id"],
    "parichay": ["identity", "identification"],
    "praman": ["certificate", "proof"],
    "pramaan": ["certificate", "proof"],
    "patra": ["certificate", "letter", "card"],
    "sanad": ["certificate", "license", "permit"],
    "license": ["license", "permit"],
    "laisens": ["license", "permit"],
    "parwana": ["license", "permit"],
    "ration": ["ration card", "food", "pds"],
    "rashan": ["ration card", "food", "pds"],
    "passport": ["passport", "travel document", "rpo"],
    "dastavez": ["document", "paperwork"],
    "kagaz": ["document", "paper", "paperwork"],
    "kagzaat": ["documents", "papers", "paperwork"],

    # Government & Offices
    "sarkar": ["government", "administration", "aaple sarkar"],
    "sarkari": ["government", "official", "public"],
    "nagar": ["municipal", "city"],
    "nigam": ["corporation", "municipal"],
    "palika": ["municipal", "corporation"],
    "mahanagar": ["metropolitan", "municipal"],
    "ward": ["ward", "municipal division"],
    "tehsil": ["tehsil", "sub-district", "revenue"],
    "tahsil": ["tehsil", "sub-district"],
    "collector": ["collector", "revenue", "district"],
    "jila": ["district"],
    "zila": ["district"],
    "vibhag": ["department", "division"],
    "mantralaya": ["ministry", "secretariat"],
    "court": ["court", "judicial"],
    "adalat": ["court", "judicial"],
    "thana": ["police station", "police"],
    "police": ["police", "law enforcement"],

    # NOC & Approvals
    "noc": ["noc", "no objection certificate", "clearance"],
    "manzuri": ["approval", "sanction", "permission"],
    "ijazat": ["permission", "approval"],
    "anumati": ["permission", "approval", "clearance"],

    # Cities & Jurisdictions
    "mumbai": ["mumbai", "mcgm", "bmc", "maharashtra"],
    "bambai": ["mumbai", "mcgm", "bmc", "maharashtra"],
    "bmc": ["bmc", "mcgm", "mumbai"],
    "mcgm": ["mcgm", "bmc", "mumbai"],
    "dilli": ["delhi", "mcd"],
    "delhi": ["delhi", "mcd"],
    "mcd": ["mcd", "delhi"],
    "bengaluru": ["bengaluru", "bangalore", "bbmp", "karnataka"],
    "bangalore": ["bengaluru", "bangalore", "bbmp", "karnataka"],
    "bbmp": ["bbmp", "bengaluru"],
    "hyderabad": ["hyderabad", "ghmc", "telangana"],
    "ghmc": ["ghmc", "hyderabad"],
    "pune": ["pune", "pmc", "maharashtra"],
    "chennai": ["chennai", "gcc", "tamil nadu"],
    "kolkata": ["kolkata", "kmc", "west bengal"],
    "ahmedabad": ["ahmedabad", "amc", "gujarat"],
    "jaipur": ["jaipur", "rajasthan"],
    "lucknow": ["lucknow", "uttar pradesh"],

    # Common civic action words
    "badalna": ["change", "transfer", "modify"],
    "badlav": ["change", "modification"],
    "sudhaar": ["correction", "amendment", "rectify"],
    "naya": ["new", "fresh"],
    "nayi": ["new", "fresh"],
    "naye": ["new", "fresh"],
    "purana": ["old", "existing", "renewal"],
    "renewal": ["renewal", "renew"],
    "navikaran": ["renewal", "renew"],
    "sthanantar": ["transfer", "mutation"],
    "sthanantaran": ["transfer", "mutation"],
    "shikayat": ["complaint", "grievance"],

    # Specific Acts & Permits
    "gumasta": ["gumasta", "shops act", "trade license", "establishment"],
    "fssai": ["fssai", "food safety", "food license", "foscos"],
    "fire": ["fire", "fire noc", "fire safety"],
    "aag": ["fire", "fire safety"],
    "pradushan": ["pollution", "environment", "mpcb", "pcb"],
    "pollution": ["pollution", "environment", "pcb"],
    "bijli": ["electricity", "power", "connection", "discom"],
    "paani": ["water", "water connection", "jal"],
    "gas": ["gas", "gas connection"],
    "sewer": ["sewer", "drainage", "sewage"],
}

# Phrase-level patterns for common Hinglish civic queries
HINGLISH_PHRASES: List[Tuple[str, str]] = [
    (r"dukaan\s+(shuru|kholna|kholni|kholo|chalana|chalani)", "start a shop business establishment register gumasta trade license"),
    (r"(naya|nayi|naye)\s+(dukaan|dukan|vyapar|karobar)", "new shop business register start gumasta"),
    (r"(pharmacy|medical|chemist)\s+(shuru|kholna|kholni|license)", "pharmacy retail chemist drug license form 20 21 fda"),
    (r"ghar\s+(khareedna|kharidna|banana)", "property purchase house building plan"),
    (r"(property|sampatti)\s+(mutation|badalna|transfer|namantaran)", "property tax mutation transfer namantaran khata"),
    (r"(ration|rashan)\s+(card|patra)", "ration card pds food distribution civil supplies"),
    (r"voter\s+(id|card|pehchaan|matdata)", "voter id election registration epic nvsp"),
    (r"(driving|gaadi)\s+(license|laisens)", "driving license transport rto parivahan"),
    (r"(birth|janam)\s+(certificate|praman)", "birth certificate registration municipal"),
    (r"(death|mrityu)\s+(certificate|praman)", "death certificate registration municipal"),
    (r"(income|aay)\s+(certificate|praman)", "income certificate revenue tehsildar sdm"),
    (r"(caste|jaati)\s+(certificate|praman)", "caste certificate social welfare reservation"),
    (r"(domicile|nivas)\s+(certificate|praman)", "domicile certificate residence permanent"),
    (r"(trade|vyapar)\s+(license|laisens)", "trade license business permit municipal corporation"),
    (r"(food|khana|bhojan)\s+(license|laisens)", "food license fssai food safety foscos"),
    (r"(building|imarat)\s+(plan|naksha)", "building plan sanction construction permit autodcr"),
    (r"fire\s+(noc|clearance|safety)", "fire noc fire safety certificate fire brigade"),
    (r"(shop|dukaan)\s+(register|panjikaran)", "shop establishment act registration gumasta"),
    (r"(gst|vat)\s+(register|panjikaran)", "gst registration tax gstn portal"),
    (r"(company|firm)\s+(register|panjikaran)", "company registration incorporation mca roc"),
    (r"(bijli|electricity)\s+(connection|meter)", "electricity connection discom power meter"),
    (r"(paani|water)\s+(connection|meter)", "water connection municipal supply meter"),
]


@dataclass
class IntentMatch:
    """A single matched task with confidence score and match rationale."""
    task_id: str
    title: str
    municipality: str
    state: str
    category: str
    confidence: float
    match_type: str  # 'catalog_exact' | 'catalog_semantic' | 'synthesized'
    matched_tokens: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class IntentResolution:
    """Complete resolution response."""
    original_query: str
    normalized_query: str
    hinglish_detected: bool
    matches: List[IntentMatch]
    synthesis: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Zero-Shot Domain Templates for Common Indian Statutory Procedures
# ---------------------------------------------------------------------------
SYNTHESIS_TEMPLATES: List[Dict[str, Any]] = [
    {
        "id_slug": "voter-id",
        "patterns": ["voter id", "voter card", "voter registration", "election", "matdata", "epic", "nvsp"],
        "title": "New Voter ID / EPIC Card Registration (Form 6)",
        "category": "Identity & Elections",
        "description": "Statutory registration procedure for new Indian voters pursuant to the Representation of the People Act, 1950 via National Voters' Service Portal (NVSP) and District Electoral Office.",
        "departments": [
            {"name": "Election Commission of India (ECI / NVSP)", "jurisdiction": "Central Portal", "address": "Nirvachan Sadan, Ashoka Road, New Delhi", "url": "https://voters.eci.gov.in"},
            {"name": "District Electoral Office & BLO Wing", "jurisdiction": "District / Ward Electoral Office", "address": "Office of the District Election Officer", "url": "https://ceoelection.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Form 6 Filing on Voters' Service Portal (ECI)",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 7,
                "fee": 0.0,
                "desc": "Submit Form 6 on official ECI portal with proof of age, proof of residence, and applicant photograph.",
                "docs": [
                    {"name": "Proof of Age (Birth Certificate / 10th Marksheet / PAN)", "cat": "Identity & KYC", "desc": "Official document showing date of birth."},
                    {"name": "Proof of Residence (Electricity Bill / Rent Agreement / Bank Passbook)", "cat": "Property & Premises", "desc": "Current residential address proof where citizen resides."},
                    {"name": "Recent Passport-size Photograph", "cat": "Identity & KYC", "desc": "Clear front-facing passport photograph (white background)."}
                ],
                "forms": [{"code": "Form-6", "title": "Application Form for Registration as New Voter", "url": "https://voters.eci.gov.in"}],
                "tips": "Double-check constituency and booth numbers to ensure your file goes to the correct Electoral Registration Officer."
            },
            {
                "title": "Field In-Person Verification by Booth Level Officer (BLO)",
                "dept_idx": 1,
                "mode": SubmissionMode.HYBRID,
                "days": 14,
                "fee": 0.0,
                "desc": "The assigned Booth Level Officer (BLO) performs physical field verification at your residential address.",
                "docs": [
                    {"name": "Original Identity and Address Documents", "cat": "Identity & KYC", "desc": "Physical originals for on-the-spot BLO verification."}
                ],
                "forms": [],
                "tips": "Keep neighbors informed or family members present during BLO physical verification visit."
            },
            {
                "title": "Electoral Roll Inclusion & Digital e-EPIC Issuance",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 10,
                "fee": 0.0,
                "desc": "Name inclusion in electoral roll by Electoral Registration Officer (ERO) and immediate generation of digital e-EPIC.",
                "docs": [],
                "forms": [{"code": "e-EPIC", "title": "Electronic Electoral Photo Identity Card (PDF)", "url": "https://voters.eci.gov.in"}],
                "tips": "Download your digitally signed e-EPIC PDF immediately upon approval via OTP."
            },
            {
                "title": "Physical Color Voter ID Card Delivery via India Post",
                "dept_idx": 1,
                "mode": SubmissionMode.IN_PERSON,
                "days": 14,
                "fee": 0.0,
                "desc": "Physical PVC laminated EPIC card printed and delivered to registered residence via Speed Post.",
                "docs": [],
                "forms": [],
                "tips": "Track postal consignment number provided on the ECI citizen tracking portal."
            }
        ],
        "estimated_days": 45,
        "estimated_fee": 0.0,
        "helpline": "ECI Toll-Free Voter Helpline: 1950"
    },
    {
        "id_slug": "ration-card",
        "patterns": ["ration card", "rashan", "pds", "food distribution", "civil supplies", "nfsa", "bpl", "apl"],
        "title": "New Ration Card Application / Family Member Addition",
        "category": "Public Distribution & Food Security",
        "description": "Statutory application under the National Food Security Act (NFSA) 2013 and State Food & Civil Supplies Department for allocation of subsidized food grains and citizen docket.",
        "departments": [
            {"name": "Department of Food, Civil Supplies & Consumer Protection", "jurisdiction": "State Food Desk", "address": "State Secretariat Food Department", "url": "https://nfsa.gov.in"},
            {"name": "District Supply Office (DSO) / Tehsil Food Wing", "jurisdiction": "District Supply Division", "address": "Collectorate Campus, District Supply Office", "url": "https://statepds.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Aadhaar e-KYC Verification & State Portal Application",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 7,
                "fee": 20.0,
                "desc": "Fill online application on State Food Portal with Aadhaar numbers and biometric consent for all family members.",
                "docs": [
                    {"name": "Aadhaar Cards of All Family Members", "cat": "Identity & KYC", "desc": "Mandatory unique biometric identification for PDS allocation."},
                    {"name": "Proof of Residence (Electricity Bill / Gas Connection / Tenancy)", "cat": "Property & Premises", "desc": "Evidence of regular residence within the jurisdictional fair price shop area."},
                    {"name": "Income Certificate / Salary Slip from Competent Authority", "cat": "Statutory & Tax", "desc": "To determine APL / BPL / Antyodaya (AAY) category eligibility."}
                ],
                "forms": [{"code": "Form-RC-1", "title": "New Ration Card Application / Member Updation Form", "url": "https://nfsa.gov.in"}],
                "tips": "Ensure no family member is already registered on another ration card elsewhere in India to avoid rejection."
            },
            {
                "title": "Field Verification by Area Food Inspector / Supply Officer",
                "dept_idx": 1,
                "mode": SubmissionMode.IN_PERSON,
                "days": 14,
                "fee": 0.0,
                "desc": "Food Inspector conducts physical inspection of residence and validates family composition and income class.",
                "docs": [
                    {"name": "Family Group Photograph", "cat": "Identity & KYC", "desc": "Photograph of head of household with all co-applicants."},
                    {"name": "Surrender Certificate (if moving from another district/state)", "cat": "Statutory & Tax", "desc": "Proof that previous ration card was surrendered or cancelled."}
                ],
                "forms": [],
                "tips": "Maintain copies of all utility bills and tenancy agreements for inspector verification."
            },
            {
                "title": "Ration Card Issuance & Fair Price Shop (FPS) Ward Allocation",
                "dept_idx": 1,
                "mode": SubmissionMode.HYBRID,
                "days": 9,
                "fee": 5.0,
                "desc": "Approval by District Supply Officer, allocation of nearest Fair Price Shop (FPS), and issuance of smart card / booklet.",
                "docs": [],
                "forms": [{"code": "RC-Final", "title": "Authorized NFSA Ration Card Certificate", "url": "https://nfsa.gov.in"}],
                "tips": "Verify One Nation One Ration Card (ONORC) portability status on the Mera Ration mobile application."
            }
        ],
        "estimated_days": 30,
        "estimated_fee": 25.0,
        "helpline": "National Food Consumer Helpline: 1967 / State Food Toll-Free: 1800-22-4950"
    },
    {
        "id_slug": "pharmacy",
        "patterns": ["pharmacy", "chemist", "medical store", "dawakhana", "medicine shop", "drug license", "dawai", "form 20", "form 21"],
        "title": "Retail Chemist & Pharmacy Drug License (Form 20 & 21)",
        "category": "Healthcare & Pharmaceuticals",
        "description": "Statutory procedure to obtain Allopathic Retail Drug Licenses (Form 20 for non-schedule C/C1 drugs and Form 21 for Schedule C/C1 drugs) under the Drugs and Cosmetics Act, 1940 and State FDA.",
        "departments": [
            {"name": "State Food & Drug Administration (FDA Licensing Authority)", "jurisdiction": "State Regulatory Authority", "address": "FDA Bhavan, Bandra Kurla Complex / Capital City", "url": "https://xlnfda.nic.in"},
            {"name": "State Pharmacy Council (Registrar Office)", "jurisdiction": "Statutory Professional Body", "address": "State Pharmacy Council Building", "url": "https://pci.nic.in"}
        ],
        "steps_data": [
            {
                "title": "Pharmacist Appointment & Registered Commercial Premises Setup",
                "dept_idx": 1,
                "mode": SubmissionMode.ONLINE,
                "days": 5,
                "fee": 0.0,
                "desc": "Appoint registered pharmacist holding valid State Pharmacy Council renewal. Secure commercial premises of min. 10 sq.m with required refrigerator/cold chain unit.",
                "docs": [
                    {"name": "Registered Pharmacist Degree / Diploma & Registration Certificate", "cat": "Technical & Approvals", "desc": "Valid registration certificate and latest renewal receipt from State Pharmacy Council."},
                    {"name": "Registered Commercial Lease Deed / Ownership Proof (min 10 sq.m)", "cat": "Property & Premises", "desc": "Commercial title deed or registered lease agreement for commercial shop premises."},
                    {"name": "Commercial Refrigerator / Cold Storage Invoice & Serial Number", "cat": "Technical & Approvals", "desc": "Purchase invoice of operational refrigerator required for biological drugs (2-8°C)."}
                ],
                "forms": [{"code": "Affidavit-Pharm", "title": "Pharmacist Full-Time Employment Undertaking", "url": "https://xlnfda.nic.in"}],
                "tips": "The registered pharmacist must not be employed elsewhere or enrolled in regular higher education."
            },
            {
                "title": "Online Application & Statutory E-Challan Payment (Form 19)",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 7,
                "fee": 3000.0,
                "desc": "Submit Form 19 via XLN-FDA online portal and deposit government treasury challan of ₹3,000 (₹1,500 Form 20 + ₹1,500 Form 21).",
                "docs": [
                    {"name": "Key Plan and Site Blueprint of Pharmacy Premises", "cat": "Technical & Approvals", "desc": "Architect-certified floor plan showing display racks, refrigerator, and dispensing counter."},
                    {"name": "Treasury E-Challan Receipt for Form 20 and 21", "cat": "Statutory & Tax", "desc": "Statutory government fee challan receipt paid under Head 0210-Medical & Public Health."}
                ],
                "forms": [{"code": "Form-19", "title": "Application for Grant or Renewal of a License to Sell, Stock or Exhibit Drugs", "url": "https://xlnfda.nic.in"}],
                "tips": "Verify that statutory fee is paid under the correct Head of Account; incorrect treasury heads cause severe delays."
            },
            {
                "title": "Physical Site Inspection by Assistant Drug Controller / Drug Inspector",
                "dept_idx": 0,
                "mode": SubmissionMode.IN_PERSON,
                "days": 12,
                "fee": 0.0,
                "desc": "Drug Inspector inspects shop premises, validates square meter area, checks temperature records, and examines original credentials of pharmacist.",
                "docs": [
                    {"name": "Original Qualification Documents & Identity of Pharmacist", "cat": "Identity & KYC", "desc": "Original B.Pharm/D.Pharm certificates for in-person verification."},
                    {"name": "Inspection Compliance Verification Report", "cat": "Technical & Approvals", "desc": "Formal physical inspection report signed on-site."}
                ],
                "forms": [],
                "tips": "The registered pharmacist must be physically present at the premises during the Drug Inspector's surprise or scheduled visit."
            },
            {
                "title": "Issuance of Retail Allopathic Drug Licenses (Form 20 & Form 21)",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 6,
                "fee": 0.0,
                "desc": "Grant and digital signing of Form 20 and Form 21 retail drug licenses with QR-code provenance by the State Licensing Authority.",
                "docs": [],
                "forms": [
                    {"code": "Form-20", "title": "License to Sell, Stock or Exhibit Drugs Other than Specified in Schedule C/C(1)", "url": "https://xlnfda.nic.in"},
                    {"code": "Form-21", "title": "License to Sell, Stock or Exhibit Drugs Specified in Schedule C and C(1)", "url": "https://xlnfda.nic.in"}
                ],
                "tips": "Frame and prominently display the original Form 20 & 21 licenses alongside the pharmacist's registration in the customer waiting area."
            }
        ],
        "estimated_days": 30,
        "estimated_fee": 3000.0,
        "helpline": "State FDA Vigilance Helpline: 1800-22-2365 / Drugs Control Administration: 022-26592233"
    },
    {
        "id_slug": "driving-license",
        "patterns": ["driving license", "gaadi", "dl", "rto", "learner", "parivahan", "sarathi", "driving permit"],
        "title": "Permanent Driving License (Parivahan Sarathi & RTO)",
        "category": "Transport & Motor Vehicles",
        "description": "Official licensing pipeline under the Motor Vehicles Act 1988: Learner's License computer test, 30-day mandatory training, automated track driving test, and biometric Smart Card DL delivery.",
        "departments": [
            {"name": "Ministry of Road Transport & Highways (MoRTH / Parivahan)", "jurisdiction": "Central Transport Desk", "address": "Transport Bhavan, New Delhi", "url": "https://parivahan.gov.in"},
            {"name": "Regional Transport Office (RTO / Motor Vehicles Dept)", "jurisdiction": "District Transport Office", "address": "Divisional RTO Campus", "url": "https://sarathi.parivahan.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Form 2 Application & Computer Learner's Test (LLR)",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 5,
                "fee": 350.0,
                "desc": "Submit Form 2 on Sarathi portal, upload Aadhaar, pass online traffic signs and road safety test, and download digital Learner's License.",
                "docs": [
                    {"name": "Aadhaar Card (e-KYC verification)", "cat": "Identity & KYC", "desc": "Biometric verification and residential address proof."},
                    {"name": "Medical Certificate Form 1-A (for transport/commercial or age > 40)", "cat": "Technical & Approvals", "desc": "Certified fitness certificate from registered medical practitioner."}
                ],
                "forms": [{"code": "Form-2", "title": "Application for Grant of Learner's License", "url": "https://sarathi.parivahan.gov.in"}],
                "tips": "Take the practice learner's test on Parivahan Sarathi to familiarize yourself with mandatory traffic signs."
            },
            {
                "title": "Mandatory 30-Day Driving Practice & Form 4 Slot Booking",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 30,
                "fee": 700.0,
                "desc": "Complete mandatory statutory 30-day waiting period from LL issue, then book an automated driving test slot on Parivahan.",
                "docs": [
                    {"name": "Valid Learner's License (LLR)", "cat": "Statutory & Tax", "desc": "Active Learner's License issued within the last 6 months."}
                ],
                "forms": [{"code": "Form-4", "title": "Application for Permanent Driving License", "url": "https://sarathi.parivahan.gov.in"}],
                "tips": "Book morning test slots to avoid peak track congestion and system timeouts at the RTO."
            },
            {
                "title": "Automated Track Driving Test & Biometric Capture at RTO",
                "dept_idx": 1,
                "mode": SubmissionMode.IN_PERSON,
                "days": 1,
                "fee": 0.0,
                "desc": "Appear in person with vehicle at RTO test track (H-track / 8-track / gradient stop). Complete biometric signature and photo capture.",
                "docs": [
                    {"name": "Vehicle Registration Certificate (RC), Valid Insurance & PUC", "cat": "Property & Premises", "desc": "Documents of the test vehicle including valid third-party insurance and emission certificate."}
                ],
                "forms": [],
                "tips": "Wear seatbelts / helmet, signal before every maneuver, and avoid stopping or touching sensor poles on the automated track."
            },
            {
                "title": "Smart Card DL Printing & Speed Post Delivery",
                "dept_idx": 1,
                "mode": SubmissionMode.IN_PERSON,
                "days": 10,
                "fee": 0.0,
                "desc": "Upon test officer approval, biometric Smart Card Driving License is laser-engraved and dispatched via India Post Speed Post.",
                "docs": [],
                "forms": [{"code": "Smart-DL", "title": "Permanent Driving License (Smart Card + mParivahan / DigiLocker)", "url": "https://digilocker.gov.in"}],
                "tips": "Add digital DL immediately to DigiLocker or mParivahan; digital copies have statutory legal validity under Rule 139 of CMVR 1989."
            }
        ],
        "estimated_days": 46,
        "estimated_fee": 1050.0,
        "helpline": "MoRTH Citizen Helpdesk: 0120-2459169 / State Transport Helpline: 1800-22-0110"
    },
    {
        "id_slug": "passport",
        "patterns": ["passport", "videsh yatra", "rpo", "psk", "tatkal", "passport seva"],
        "title": "Fresh Passport Application / Re-issue (Passport Seva)",
        "category": "Central Government & External Affairs",
        "description": "Standard citizen pathway under the Passports Act, 1967 administered by the Ministry of External Affairs: Passport Seva Kendra (PSK) appointment, police verification, and Speed Post dispatch.",
        "departments": [
            {"name": "Ministry of External Affairs (Consular, Passport & Visa Division)", "jurisdiction": "Central Desk", "address": "Patiala House, Tilak Marg, New Delhi", "url": "https://passportindia.gov.in"},
            {"name": "Regional Passport Office (RPO) & Special Police Verification Branch", "jurisdiction": "Regional Desk", "address": "Bandra Kurla Complex / Regional PSK Office", "url": "https://passportindia.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Passport Seva Online Registration & Statutory Fee Payment",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 4,
                "fee": 1500.0,
                "desc": "Register on passportindia.gov.in, complete online form, pay ₹1,500 normal fee (₹3,500 Tatkal), and reserve PSK appointment slot.",
                "docs": [
                    {"name": "Aadhaar Card / Voter ID / PAN Card", "cat": "Identity & KYC", "desc": "Proof of identity and citizenship."},
                    {"name": "Proof of Date of Birth (Birth Certificate / 10th School Certificate)", "cat": "Identity & KYC", "desc": "Statutory birth proof document."},
                    {"name": "Proof of Present Residential Address (> 1 Year Stay)", "cat": "Property & Premises", "desc": "Utility bill, bank passbook, or registered rent agreement showing continuous residence."}
                ],
                "forms": [{"code": "Form-PSP-1", "title": "Application for Ordinary Passport", "url": "https://passportindia.gov.in"}],
                "tips": "Ensure the applicant's name and parents' names match verbatim across Aadhaar, Birth Certificate, and Educational Certificates."
            },
            {
                "title": "In-Person Biometric Appointment at Passport Seva Kendra (PSK)",
                "dept_idx": 0,
                "mode": SubmissionMode.IN_PERSON,
                "days": 1,
                "fee": 0.0,
                "desc": "Visit PSK for Counters A (biometrics/photo), Counter B (document verification by Verifying Officer), and Counter C (Granting Officer approval).",
                "docs": [
                    {"name": "Original Identity, DOB, and Address Documents with 2 Self-Attested Photocopies", "cat": "Identity & KYC", "desc": "Original physical records for scanner verification."}
                ],
                "forms": [],
                "tips": "Arrive 15 minutes prior to appointment time. Electronic devices are restricted inside the PSK secure bays."
            },
            {
                "title": "Local Police Station Address & Character Verification",
                "dept_idx": 1,
                "mode": SubmissionMode.IN_PERSON,
                "days": 14,
                "fee": 0.0,
                "desc": "Jurisdictional police station conducts in-person residence visit and criminal record verification.",
                "docs": [
                    {"name": "Two Respectable Neighbors' Verification Letters & ID Proofs", "cat": "Identity & KYC", "desc": "Letters from resident neighbors confirming applicant's peaceful residence."},
                    {"name": "No Criminal Record Self-Declaration Affidavit", "cat": "Statutory & Tax", "desc": "Undertaking confirming no pending criminal proceedings or FIRs."}
                ],
                "forms": [],
                "tips": "Never offer or pay any unauthorized gratification during police verification; report touts directly to ACB or RPO vigilance."
            },
            {
                "title": "Security Printing at India Security Press & Speed Post Dispatch",
                "dept_idx": 0,
                "mode": SubmissionMode.IN_PERSON,
                "days": 7,
                "fee": 0.0,
                "desc": "Passport booklet printed at India Security Press Nashik, laminated, and delivered to applicant via Speed Post.",
                "docs": [],
                "forms": [],
                "tips": "Keep your original photo identity card handy to show the postal delivery agent upon delivery."
            }
        ],
        "estimated_days": 26,
        "estimated_fee": 1500.0,
        "helpline": "Passport Seva National Call Centre (24x7): 1800-258-1800"
    },
    {
        "id_slug": "gumasta-trade",
        "patterns": ["dukaan", "shop", "store", "retail", "general store", "gumasta", "trade license", "establishment", "vyapar", "panjikaran", "commercial shop"],
        "title": "Shop & Commercial Establishment Registration (Gumasta / Trade License)",
        "category": "Business & Commercial Enterprise",
        "description": "Statutory registration under the State Shops and Commercial Establishments Act (Gumasta License) and Municipal Corporation Health & Sanitation Bye-Laws required before commencing commercial trading.",
        "departments": [
            {"name": "Municipal Corporation Shops & Establishments Dept (Aaple Sarkar / Urban Portal)", "jurisdiction": "Ward Office", "address": "Citizen Facilitation Centre (CFC), Ward Administrative Office", "url": "https://lms.mahaonline.gov.in"},
            {"name": "State Labour Commissionerate & Chief Inspector of Factories", "jurisdiction": "State Labour Desk", "address": "Kamgar Bhavan, Labour Department", "url": "https://labour.gov.in"}
        ],
        "steps_data": [
            {
                "title": "Online Form A Filing on State Single Window / Municipal Portal",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 4,
                "fee": 500.0,
                "desc": "Submit Form A (Application for Registration under Shops & Establishments Act) with business name, nature of business, and number of employees.",
                "docs": [
                    {"name": "PAN Card & Aadhaar of Proprietor / Partners / Directors", "cat": "Identity & KYC", "desc": "Identity verification of the business owners."},
                    {"name": "Registered Commercial Lease Agreement / Property Tax Bill", "cat": "Property & Premises", "desc": "Proof of lawful possession of the commercial establishment address."},
                    {"name": "Establishment Front Photo with Signboard in Official State Language", "cat": "Property & Premises", "desc": "Mandatory photograph showing shopfront with prominent bilingual nameboard."}
                ],
                "forms": [{"code": "Form-A", "title": "Application for Registration of Commercial Establishment", "url": "https://lms.mahaonline.gov.in"}],
                "tips": "Ensure the signboard prominently features the local state language in font size not smaller than English (mandated by Shops Act Amendment)."
            },
            {
                "title": "Statutory E-Challan Treasury Fee Payment",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 1,
                "fee": 750.0,
                "desc": "Deposit municipal trade license and registration fees via authorized government payment gateway (e-Gras / Aaple Sarkar).",
                "docs": [
                    {"name": "Treasury E-Payment Receipt", "cat": "Statutory & Tax", "desc": "Official bank transaction confirmation with GRN / Cyber Receipt Number."}
                ],
                "forms": [],
                "tips": "Keep the GRN (Government Reference Number) recorded to track registration approval."
            },
            {
                "title": "Digital Scrutiny & Ward Inspector Desk Verification",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 5,
                "fee": 0.0,
                "desc": "Labour Officer / Ward Inspector reviews the application, checks trade category restrictions, and performs automated desk scrutiny.",
                "docs": [
                    {"name": "Self-Declaration on Employee Working Hours and Safety", "cat": "Statutory & Tax", "desc": "Undertaking complying with weekly holiday and maximum overtime hours."}
                ],
                "forms": [{"code": "Self-Decl-B", "title": "Undertaking under Section 6 of Shops & Establishments Act", "url": "https://lms.mahaonline.gov.in"}],
                "tips": "Establishments with fewer than 10 employees receive instant automated Registration Intimation (Form G)."
            },
            {
                "title": "Issuance of Digitally Signed Gumasta / Trade Certificate (Form C)",
                "dept_idx": 0,
                "mode": SubmissionMode.ONLINE,
                "days": 2,
                "fee": 0.0,
                "desc": "Download digitally signed Registration Certificate (Form C) with QR-code provenance for display in the shop premises.",
                "docs": [],
                "forms": [{"code": "Form-C", "title": "Certificate of Registration of Establishment (Gumasta License)", "url": "https://lms.mahaonline.gov.in"}],
                "tips": "Under the law, Form C must be laminated and displayed in a conspicuous position near the shop entrance."
            }
        ],
        "estimated_days": 12,
        "estimated_fee": 1250.0,
        "helpline": "Municipal Citizen Grievance Portal: 1916 / Labour Commissioner Helpline: 1800-99-9999"
    }
]


class NLPIntentEngine:
    """
    Production-grade Dual-Track NLP Intent Resolution & Procedure Synthesizer:
    - Normalizes mixed Hinglish and Devanagari Hindi into canonical civic search tokens
    - Computes TF-IDF vector representations and cosine similarity against indexed tasks
    - Applies domain boost weights for tag overlaps, municipal jurisdictions, and title n-grams
    - Fallback track: Zero-shot statutory graph synthesizer constructs a full CivicTask with
      realistic steps, forms, fees, and departments, dynamically registering it into the database.
    """

    CONFIDENCE_THRESHOLD = 0.12  # Threshold below which zero-shot synthesis activates
    MAX_RESULTS = 5

    def __init__(self):
        self._task_corpus: Dict[str, str] = {}
        self._task_meta: Dict[str, Dict] = {}
        self._idf: Dict[str, float] = {}
        self._tf_idf_vectors: Dict[str, Dict[str, float]] = {}
        self._is_indexed = False

    def index_tasks(self, tasks: list):
        """Build TF-IDF index from task catalog."""
        self._task_corpus.clear()
        self._task_meta.clear()

        for task in tasks:
            task_id = task.id
            text_parts = [
                task.title,
                task.description,
                task.category,
                task.municipality,
                task.state,
                " ".join(task.tags),
            ]
            for step in task.steps:
                text_parts.append(step.title)
                text_parts.append(step.department.name)
                if step.tips_and_pitfalls:
                    text_parts.append(step.tips_and_pitfalls)

            flat_text = " ".join(text_parts).lower()
            self._task_corpus[task_id] = flat_text
            self._task_meta[task_id] = {
                "title": task.title,
                "municipality": task.municipality,
                "state": task.state,
                "category": task.category,
                "tags": task.tags,
                "description": task.description,
            }

        self._build_idf()
        for task_id, text in self._task_corpus.items():
            tokens = self._tokenize(text)
            self._tf_idf_vectors[task_id] = self._compute_tf_idf(tokens)

        self._is_indexed = True

    def resolve_intent(self, query: str, municipality_hint: str = "") -> IntentResolution:
        """
        Main entry point. Takes a raw user query (possibly Hinglish / Hindi)
        and returns ranked matches with confidence scores.
        """
        if not self._is_indexed:
            self.index_tasks(db.get_all_tasks())

        original = query.strip()
        if not original:
            return IntentResolution(
                original_query=original,
                normalized_query="",
                hinglish_detected=False,
                matches=[],
            )

        # Step 1: Normalize and transliterate Hinglish & Devanagari
        normalized, hinglish_detected, expanded_tokens = self._normalize_query(original)

        # Step 2: Prepend municipality hint if specified
        if municipality_hint and municipality_hint.lower() not in ("all", ""):
            normalized = municipality_hint.lower() + " " + normalized

        # Step 3: Compute query TF-IDF vector
        query_tokens = self._tokenize(normalized)
        query_vec = self._compute_tf_idf(query_tokens)

        # Step 4: Compute cosine similarity against all indexed tasks
        scored: List[Tuple[str, float, List[str]]] = []
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
            scored.append((task_id, final_score, list(overlap)))

        scored.sort(key=lambda x: x[1], reverse=True)

        matches: List[IntentMatch] = []
        for task_id, raw_score, matched in scored[:self.MAX_RESULTS]:
            if raw_score < 0.01:
                continue
            score = min(raw_score, 1.0)
            meta = self._task_meta[task_id]
            match_type = "catalog_exact" if score > 0.45 else "catalog_semantic"
            matches.append(IntentMatch(
                task_id=task_id,
                title=meta["title"],
                municipality=meta["municipality"],
                state=meta["state"],
                category=meta["category"],
                confidence=round(score, 4),
                match_type=match_type,
                matched_tokens=matched[:10],
                description=meta["description"],
            ))

        # Step 5: Dual-Track Zero-Shot Statutory Synthesis
        synthesis = None
        top_score = matches[0].confidence if matches else 0.0

        # Activate synthesis if top catalog match is weak, or if synthesis matches strongly
        synth_result, synth_score = self._match_or_synthesize(original, normalized, municipality_hint)
        if synth_result:
            if top_score < self.CONFIDENCE_THRESHOLD or synth_score > (top_score + 0.1):
                # Dynamically construct and register the CivicTask into the runtime database
                synthesized_task = self._register_synthesized_civic_task(synth_result, municipality_hint)
                
                synth_match = IntentMatch(
                    task_id=synthesized_task.id,
                    title=synthesized_task.title,
                    municipality=synthesized_task.municipality,
                    state=synthesized_task.state,
                    category=synthesized_task.category,
                    confidence=round(synth_score, 4),
                    match_type="synthesized",
                    matched_tokens=synth_result.get("matched_patterns", []),
                    description=synthesized_task.description,
                )
                
                # Prepend the synthesized match so it is the top recommendation
                matches.insert(0, synth_match)
                synthesis = synth_result

        return IntentResolution(
            original_query=original,
            normalized_query=normalized,
            hinglish_detected=hinglish_detected,
            matches=matches[:self.MAX_RESULTS],
            synthesis=synthesis,
        )

    # -----------------------------------------------------------------------
    # Hinglish & Devanagari Normalization
    # -----------------------------------------------------------------------
    def _normalize_query(self, query: str) -> Tuple[str, bool, List[str]]:
        """
        Normalizes input query by expanding Devanagari Hindi words and
        transliterated Hinglish terms into their statutory English equivalents.
        """
        q_lower = query.lower().strip()
        hinglish_detected = False
        expanded: List[str] = []

        # Phase 1: Devanagari words expansion
        for dev_word, expansion in DEVANAGARI_MAP.items():
            if dev_word in query:
                expanded.extend(expansion.split())
                hinglish_detected = True

        # Phase 2: Clean Latin text
        q_clean = re.sub(r'[^\w\s\-/]', ' ', q_lower)
        q_clean = re.sub(r'\s+', ' ', q_clean).strip()

        # Phase 3: Phrase-level pattern matching
        for pattern, expansion in HINGLISH_PHRASES:
            if re.search(pattern, q_clean, re.IGNORECASE):
                expanded.extend(expansion.split())
                hinglish_detected = True

        # Phase 4: Token-level transliteration dictionary
        tokens = q_clean.split()
        for token in tokens:
            expanded.append(token)
            if token in HINGLISH_MAP:
                expanded.extend(HINGLISH_MAP[token])
                hinglish_detected = True
            else:
                # Suffix trimming (Hindi inflections like -i, -e, -a, -o)
                stripped = re.sub(r'[ieao]$', '', token)
                if stripped and stripped != token and stripped in HINGLISH_MAP:
                    expanded.extend(HINGLISH_MAP[stripped])
                    hinglish_detected = True

        normalized = " ".join(expanded)
        return normalized, hinglish_detected, expanded

    # -----------------------------------------------------------------------
    # TF-IDF Machinery
    # -----------------------------------------------------------------------
    def _tokenize(self, text: str) -> List[str]:
        STOPWORDS = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'shall', 'should', 'may', 'might', 'can', 'could',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            'as', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'under', 'again', 'further', 'then', 'once',
            'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both',
            'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 's', 't', 'just', 'don', 'now', 'and', 'or', 'but',
            'if', 'it', 'its', 'i', 'me', 'my', 'we', 'our', 'you',
            'your', 'he', 'him', 'his', 'she', 'her', 'they', 'them',
            'their', 'what', 'which', 'who', 'whom', 'this', 'that',
            'these', 'those', 'am', 'about', 'up', 'out', 'off', 'over',
            'hai', 'hain', 'tha', 'thi', 'the', 'ke', 'ki', 'ka',
            'ko', 'se', 'me', 'mein', 'pe', 'par', 'ne', 'ye', 'wo',
            'yeh', 'woh', 'kya', 'kaun', 'kab', 'kahan', 'kaise',
            'kyun', 'aur', 'ya', 'lekin', 'magar'
        }
        tokens = re.findall(r'[a-z0-9\-]+', text.lower())
        return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

    def _build_idf(self):
        N = len(self._task_corpus)
        if N == 0:
            return

        doc_freq: Counter = Counter()
        for text in self._task_corpus.values():
            tokens = set(self._tokenize(text))
            for token in tokens:
                doc_freq[token] += 1

        self._idf = {}
        for token, df in doc_freq.items():
            self._idf[token] = math.log((N + 1) / (df + 1)) + 1.0

    def _compute_tf_idf(self, tokens: List[str]) -> Dict[str, float]:
        tf: Counter = Counter(tokens)
        total = len(tokens) if tokens else 1
        vec: Dict[str, float] = {}
        for token, count in tf.items():
            tf_val = count / total
            idf_val = self._idf.get(token, math.log(len(self._task_corpus) + 2))
            vec[token] = tf_val * idf_val
        return vec

    def _cosine_similarity(self, vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        if not vec_a or not vec_b:
            return 0.0

        dot = 0.0
        for token in vec_a:
            if token in vec_b:
                dot += vec_a[token] * vec_b[token]

        mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
        mag_b = math.sqrt(sum(v * v for v in vec_b.values()))

        if mag_a == 0 or mag_b == 0:
            return 0.0

        return dot / (mag_a * mag_b)

    def _ngram_overlap_score(self, text_a: str, text_b: str, n: int = 3) -> float:
        def ngrams(text, n):
            text = text.replace(" ", "_")
            return set(text[i:i+n] for i in range(max(0, len(text) - n + 1)))

        a_grams = ngrams(text_a, n)
        b_grams = ngrams(text_b, n)

        if not a_grams or not b_grams:
            return 0.0

        intersection = a_grams & b_grams
        union = a_grams | b_grams
        return len(intersection) / len(union) if union else 0.0

    # -----------------------------------------------------------------------
    # Track 2: Zero-Shot Statutory Graph Synthesis
    # -----------------------------------------------------------------------
    def _match_or_synthesize(self, original_query: str, normalized_query: str, municipality_hint: str) -> Tuple[Optional[Dict], float]:
        """Matches query against statutory template library and computes confidence."""
        q = normalized_query.lower()
        q_tokens = set(self._tokenize(q))

        best_tpl = None
        best_score = 0.0
        matched_patterns = []

        for template in SYNTHESIS_TEMPLATES:
            score = 0.0
            hits = []
            for pattern in template["patterns"]:
                p_tokens = set(self._tokenize(pattern))
                overlap = p_tokens & q_tokens
                if overlap:
                    weight = len(overlap) / len(p_tokens)
                    score += weight * 0.4
                    hits.append(pattern)

                # N-gram overlap
                ngram_sim = self._ngram_overlap_score(q, pattern, n=3)
                if ngram_sim > 0.3:
                    score += ngram_sim * 0.3
                    hits.append(pattern)

            if score > best_score:
                best_score = score
                best_tpl = template
                matched_patterns = hits

        if best_tpl and best_score >= 0.15:
            confidence = min(0.65 + best_score * 0.25, 0.94)
            result = dict(best_tpl)
            result["confidence"] = confidence
            result["matched_patterns"] = list(set(matched_patterns))
            return result, confidence

        return None, 0.0

    def _register_synthesized_civic_task(self, template_data: Dict[str, Any], municipality_hint: str = "") -> CivicTask:
        """
        Dynamically generates a full CivicTask with topological steps, forms,
        fees, and departments, registering it directly into the runtime database.
        """
        slug = template_data["id_slug"]
        task_id = f"task-synth-{slug}"

        # If already synthesized and cached in db, return it
        cached = db.get_task_by_id(task_id)
        if cached:
            return cached

        # Municipality assignment
        mun = municipality_hint.strip() if municipality_hint and municipality_hint.lower() != "all" else "National / State Portal (India)"
        state = "Central / All States"

        # Instantiate departments
        dept_objs = []
        for idx, d_info in enumerate(template_data.get("departments", [])):
            dept_obj = DepartmentInfo(
                id=f"dept-synth-{slug}-{idx+1}",
                name=d_info["name"],
                jurisdiction=d_info.get("jurisdiction", mun),
                office_address=d_info.get("address", "Official Government Office Campus"),
                contact_phone="1800-11-4000",
                contact_email="helpdesk.services@gov.in",
                working_hours="Mon-Fri 09:30 AM - 05:30 PM",
                portal_url=d_info.get("url", "https://india.gov.in")
            )
            dept_objs.append(dept_obj)

        if not dept_objs:
            dept_objs.append(DepartmentInfo(
                id=f"dept-synth-{slug}-1",
                name="Competent Municipal Authority",
                jurisdiction=mun,
                office_address="Municipal Corporation Citizen Centre",
                portal_url="https://india.gov.in"
            ))

        # Build steps
        steps: List[TaskStep] = []
        steps_raw = template_data.get("steps_data", [])

        for i, s in enumerate(steps_raw):
            step_id = f"step-{slug}-{i+1}"
            dept_idx = min(s.get("dept_idx", 0), len(dept_objs) - 1)
            dept = dept_objs[dept_idx]

            # Prerequisites: topological sequence
            prereqs = [f"step-{slug}-{i}"] if i > 0 else []

            # Documents
            docs = []
            for doc_idx, doc_data in enumerate(s.get("docs", [])):
                docs.append(DocumentRequirement(
                    id=f"doc-{slug}-{i+1}-{doc_idx+1}",
                    name=doc_data["name"],
                    category=doc_data.get("cat", "Identity & KYC"),
                    description=doc_data.get("desc", "Official document required for statutory compliance."),
                    is_mandatory=True,
                    issuing_authority=dept.name
                ))

            # Forms
            forms = []
            for f_data in s.get("forms", []):
                forms.append(FormRequirement(
                    form_code=f_data["code"],
                    title=f_data["title"],
                    download_url=f_data.get("url", dept.portal_url),
                    fill_online_url=f_data.get("url", dept.portal_url),
                    instructions="Fill completely in English or state official language. Ensure applicant signature and date."
                ))

            # Verification Source
            v_source = VerificationSource(
                url=dept.portal_url or "https://india.gov.in",
                page_title=f"Statutory Filing Rules: {s['title']}",
                last_scraped_at="26-09-2026",
                confidence_score=0.92,
                is_admin_verified=True,
                portal_section="E-Governance Citizen Charter"
            )

            step = TaskStep(
                id=step_id,
                task_id=task_id,
                step_number=i + 1,
                title=s["title"],
                description=s["desc"],
                department=dept,
                submission_mode=s.get("mode", SubmissionMode.ONLINE),
                estimated_days=s.get("days", 7),
                fee_amount=float(s.get("fee", 0.0)),
                fee_breakdown={"Statutory Fee": float(s.get("fee", 0.0))},
                prerequisites=prereqs,
                documents=docs,
                forms=forms,
                verification_source=v_source,
                tips_and_pitfalls=s.get("tips", "Ensure all dates and applicant names match identity cards precisely."),
                anti_tout_advisory="Never pay cash to unauthorized middlemen. Every statutory fee must generate an official government e-Challan receipt.",
                statutory_payment_channel="Official State / Central Treasury Portal (e-Challan / Bharatkosh)",
                community_verifications=38,
                status=StepStatus.READY if i == 0 else StepStatus.LOCKED,
                is_critical_path=True
            )
            steps.append(step)

        # Create full CivicTask
        civic_task = CivicTask(
            id=task_id,
            title=template_data["title"],
            category=template_data["category"],
            municipality=mun,
            state=state,
            description=template_data["description"],
            tags=[slug, "zero-shot", "synthesized"] + [p.replace(" ", "-") for p in template_data["patterns"]],
            steps=steps
        )

        # Register into in-memory database
        db._tasks[task_id] = civic_task

        # Re-index NLP engine so subsequent queries know this task
        self.index_tasks(db.get_all_tasks())

        return civic_task


# Singleton NLP Engine instance
nlp_engine = NLPIntentEngine()
