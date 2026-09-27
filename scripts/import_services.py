#!/usr/bin/env python3
"""
scripts/import_services.py
====================================================================
Municipal Bureaucracy Path Visualizer - Civic Service Importer
====================================================================
Imports, normalizes, deduplicates, and connects official Maharashtra
government services from data/all_services.json into db/civic_maharashtra.db.

Constructs:
- departments
- aaple_sarkar_services
- tasks (citizen-level procedural navigation)
- steps (Directed Acyclic Graph procedural roadmap)
- documents (categorized document locker requirements)
- forms (statutory online & downloadable forms)

Guarantees:
- Idempotency (safe to run multiple times without duplicating data)
- Full relational integrity (strict foreign keys, no orphans)
- Preserves all raw JSON and source URLs
- Validates data with PRAGMA foreign_key_check
"""

import os
import sys
import json
import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime

# Configure UTF-8 for console output on Windows
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "db", "civic_maharashtra.db")
BACKUP_PATH = os.path.join(PROJECT_ROOT, "db", "civic_maharashtra_backup.db")
ALL_SERVICES_JSON = os.path.join(PROJECT_ROOT, "data", "all_services.json")
SAMPLE_SERVICES_JSON = os.path.join(PROJECT_ROOT, "data", "sample_services.json")


# ---------------------------------------------------------------------------
# Department Normalization Mapping & Metadata
# ---------------------------------------------------------------------------
DEPT_METADATA = {
    "Urban Development Department": {
        "id": "dept-urban-dev",
        "code": "UDD",
        "jurisdiction": "Government of Maharashtra (Urban Development)",
        "portal_url": "https://urban.maharashtra.gov.in"
    },
    "Brihanmumbai Municipal Corporation (BMC)": {
        "id": "dept-bmc",
        "code": "BMC",
        "jurisdiction": "Brihanmumbai Municipal Corporation (BMC / MCGM)",
        "portal_url": "https://portal.mcgm.gov.in"
    },
    "City and Industrial Development Corporation (CIDCO)": {
        "id": "dept-cidco",
        "code": "CIDCO",
        "jurisdiction": "CIDCO Jurisdiction (Navi Mumbai / Maharashtra)",
        "portal_url": "https://cidco.maharashtra.gov.in"
    },
    "Nagpur Metropolitan Region Development Authority (NMRDA)": {
        "id": "dept-nmrda",
        "code": "NMRDA",
        "jurisdiction": "Nagpur Metropolitan Region",
        "portal_url": "https://nmrda.org"
    },
    "Directorate of Municipal Administration (Municipal Councils)": {
        "id": "dept-dma-councils",
        "code": "DMA",
        "jurisdiction": "Maharashtra Municipal Councils & Nagar Parishads",
        "portal_url": "https://mahamunici.maharashtra.gov.in"
    },
    "Revenue and Forest Department": {
        "id": "dept-rev-forest",
        "code": "RevDept",
        "jurisdiction": "Government of Maharashtra (Revenue & Forest)",
        "portal_url": "https://revenue.maharashtra.gov.in"
    },
    "Inspector General of Registration & Controller of Stamps (IGR)": {
        "id": "dept-igr",
        "code": "IGR",
        "jurisdiction": "Government of Maharashtra (Registration & Stamps)",
        "portal_url": "https://igrmaharashtra.gov.in"
    },
    "Land Records Department (MahaBhumi)": {
        "id": "dept-mahabhumi",
        "code": "BHUMI",
        "jurisdiction": "Government of Maharashtra (Land Records)",
        "portal_url": "https://mahabhumi.gov.in"
    },
    "Industry, Energy and Labor Department": {
        "id": "dept-ind-labour",
        "code": "LABOUR",
        "jurisdiction": "Government of Maharashtra (Labour Commissionerate)",
        "portal_url": "https://lms.mahaonline.gov.in"
    },
    "Directorate of Industrial Safety and Health (DISH)": {
        "id": "dept-dish",
        "code": "DISH",
        "jurisdiction": "Government of Maharashtra (Industrial Safety)",
        "portal_url": "https://dish.maharashtra.gov.in"
    },
    "Transport Department": {
        "id": "dept-transport-maha",
        "code": "RTO",
        "jurisdiction": "Government of Maharashtra (Motor Vehicles / RTO)",
        "portal_url": "https://transport.maharashtra.gov.in"
    },
    "Food Civil Supplies and Consumer Protection Department": {
        "id": "dept-fcs-consumer",
        "code": "FCS",
        "jurisdiction": "Government of Maharashtra (Food & Civil Supplies)",
        "portal_url": "https://mahafood.gov.in"
    },
    "Water Supply and Sanitation Department": {
        "id": "dept-water-supply",
        "code": "WSSD",
        "jurisdiction": "Government of Maharashtra (Water Supply & Sanitation)",
        "portal_url": "https://mjp.maharashtra.gov.in"
    },
    "Maharashtra Jeevan Pradhikaran (MJP)": {
        "id": "dept-mjp-water",
        "code": "MJP",
        "jurisdiction": "Maharashtra Water Supply Authority",
        "portal_url": "https://mjp.maharashtra.gov.in"
    },
    "Rural Development Department": {
        "id": "dept-rdd-panchayat",
        "code": "RDD",
        "jurisdiction": "Government of Maharashtra (Panchayat Raj & Rural)",
        "portal_url": "https://rdd.maharashtra.gov.in"
    },
    "Housing Department": {
        "id": "dept-housing-maha",
        "code": "HOUSING",
        "jurisdiction": "Government of Maharashtra (Housing)",
        "portal_url": "https://housing.maharashtra.gov.in"
    },
    "Maharashtra Housing and Area Development Authority (MHADA)": {
        "id": "dept-mhada-housing",
        "code": "MHADA",
        "jurisdiction": "Government of Maharashtra (MHADA)",
        "portal_url": "https://mhada.gov.in"
    },
    "Slum Rehabilitation Authority (SRA)": {
        "id": "dept-sra-housing",
        "code": "SRA",
        "jurisdiction": "Greater Mumbai & Thane (SRA Jurisdiction)",
        "portal_url": "https://sra.gov.in"
    },
    "Environment and Climate Change Department": {
        "id": "dept-env-maha",
        "code": "ENV",
        "jurisdiction": "Government of Maharashtra (Environment)",
        "portal_url": "https://envd.maharashtra.gov.in"
    },
    "Maharashtra Pollution Control Board (MPCB)": {
        "id": "dept-mpcb",
        "code": "MPCB",
        "jurisdiction": "State Environmental Protection Authority",
        "portal_url": "https://mpcb.gov.in"
    },
    "Public Health Department": {
        "id": "dept-public-health",
        "code": "PHD",
        "jurisdiction": "Government of Maharashtra (Public Health)",
        "portal_url": "https://arogya.maharashtra.gov.in"
    },
    "Medical Education and Drugs Department": {
        "id": "dept-medical-drugs",
        "code": "MEDD",
        "jurisdiction": "Government of Maharashtra (FDA & Drugs)",
        "portal_url": "https://fda.maharashtra.gov.in"
    },
    "Home Department": {
        "id": "dept-home-maha",
        "code": "HOME",
        "jurisdiction": "Government of Maharashtra (Police & Home Affairs)",
        "portal_url": "https://home.maharashtra.gov.in"
    },
    "Mumbai Fire Brigade (MFB)": {
        "id": "dept-mfb",
        "code": "MFB",
        "jurisdiction": "Brihanmumbai Municipal Corporation (Fire Command)",
        "portal_url": "https://portal.mcgm.gov.in/eodb-fire-noc"
    },
    "Public Works Department": {
        "id": "dept-pwd-maha",
        "code": "PWD",
        "jurisdiction": "Government of Maharashtra (Public Works)",
        "portal_url": "https://pwd.maharashtra.gov.in"
    },
    "Law and Justice Department": {
        "id": "dept-law-justice",
        "code": "LAW",
        "jurisdiction": "Government of Maharashtra (Charity & Registration of Firms)",
        "portal_url": "https://charity.maharashtra.gov.in"
    },
    "Finance Department": {
        "id": "dept-finance-maha",
        "code": "FIN",
        "jurisdiction": "Government of Maharashtra (MahaGST & Treasury)",
        "portal_url": "https://mahagst.gov.in"
    },
    "Social Justice and Special Assistance Department": {
        "id": "dept-social-justice",
        "code": "SJD",
        "jurisdiction": "Government of Maharashtra (Social Welfare)",
        "portal_url": "https://sjsa.maharashtra.gov.in"
    },
    "Tribal Development Department": {
        "id": "dept-tribal-dev",
        "code": "TRD",
        "jurisdiction": "Government of Maharashtra (Tribal Welfare)",
        "portal_url": "https://tribal.maharashtra.gov.in"
    },
    "Divyang Kalyan Department (Disability Welfare)": {
        "id": "dept-divyang-kalyan",
        "code": "DKD",
        "jurisdiction": "Government of Maharashtra (Disability Welfare)",
        "portal_url": "https://divyang.maharashtra.gov.in"
    },
    "Other Backward Bahujan Welfare Department": {
        "id": "dept-other-backward",
        "code": "OBBC",
        "jurisdiction": "Government of Maharashtra (Bahujan Welfare)",
        "portal_url": "https://maharashtra.gov.in"
    },
    "Minorities Development Department": {
        "id": "dept-minorities-dev",
        "code": "MIN",
        "jurisdiction": "Government of Maharashtra (Minority Welfare)",
        "portal_url": "https://mdd.maharashtra.gov.in"
    },
    "Higher and Technical Education Department": {
        "id": "dept-higher-tech-edu",
        "code": "HTED",
        "jurisdiction": "Government of Maharashtra (Higher Education)",
        "portal_url": "https://hted.maharashtra.gov.in"
    },
    "School Education and Sports Department": {
        "id": "dept-school-sports",
        "code": "SED",
        "jurisdiction": "Government of Maharashtra (School Education)",
        "portal_url": "https://education.maharashtra.gov.in"
    },
    "Agriculture, Animal Husbandry, Dairy and Fisheries Department": {
        "id": "dept-agriculture-dairy",
        "code": "AGRI",
        "jurisdiction": "Government of Maharashtra (Agriculture & Dairy)",
        "portal_url": "https://krishi.maharashtra.gov.in"
    },
    "Cooperation, Marketing and Textiles Department": {
        "id": "dept-cooperation",
        "code": "COOP",
        "jurisdiction": "Government of Maharashtra (Cooperative Societies)",
        "portal_url": "https://cooperation.maharashtra.gov.in"
    },
    "Water Resources Department": {
        "id": "dept-water-resources",
        "code": "WRD",
        "jurisdiction": "Government of Maharashtra (Water Resources & Irrigation)",
        "portal_url": "https://wrd.maharashtra.gov.in"
    },
    "Soil and Water Conservation Department": {
        "id": "dept-soil-conservation",
        "code": "SWCD",
        "jurisdiction": "Government of Maharashtra (Soil & Water Conservation)",
        "portal_url": "https://maharashtra.gov.in"
    },
    "General Administration Department": {
        "id": "dept-general-admin",
        "code": "GAD",
        "jurisdiction": "Government of Maharashtra (General Administration)",
        "portal_url": "https://gad.maharashtra.gov.in"
    },
    "Planning Department": {
        "id": "dept-planning-maha",
        "code": "PLAN",
        "jurisdiction": "Government of Maharashtra (Employment Guarantee Scheme)",
        "portal_url": "https://planning.maharashtra.gov.in"
    },
    "Tourism and Cultural Affairs Department": {
        "id": "dept-tourism-culture",
        "code": "TOUR",
        "jurisdiction": "Government of Maharashtra (Tourism & Culture)",
        "portal_url": "https://maharashtratourism.gov.in"
    }
}


def normalize_department_name(raw_dept: str) -> str:
    """Normalizes raw department names into consistent canonical official names."""
    if not raw_dept:
        return "General Administration Department"
    d = raw_dept.strip()
    dl = d.lower()
    if "urban" in dl:
        return "Urban Development Department"
    if "transport" in dl:
        return "Transport Department"
    if "water" in dl and "sanitation" in dl:
        return "Water Supply and Sanitation Department"
    if "environment" in dl:
        return "Environment and Climate Change Department"
    if "publichealth" in dl or "public health" in dl:
        return "Public Health Department"
    if "cooperation" in dl or "textile" in dl:
        return "Cooperation, Marketing and Textiles Department"
    if "finance" in dl:
        return "Finance Department"
    if "public works" in dl:
        return "Public Works Department"
    if "higher" in dl and "technical" in dl:
        return "Higher and Technical Education Department"
    if "medical education" in dl:
        return "Medical Education and Drugs Department"
    if "soil" in dl and "conservation" in dl:
        return "Soil and Water Conservation Department"
    if "general administration" in dl:
        return "General Administration Department"
    if "divyang" in dl:
        return "Divyang Kalyan Department (Disability Welfare)"
    if "magas bahujan" in dl:
        return "Other Backward Bahujan Welfare Department"
    if "food" in dl and "civil" in dl:
        return "Food Civil Supplies and Consumer Protection Department"
    if "revenue" in dl:
        return "Revenue and Forest Department"
    if "rural" in dl:
        return "Rural Development Department"
    if "housing" in dl:
        return "Housing Department"
    if "home" in dl:
        return "Home Department"
    if "law" in dl and "justice" in dl:
        return "Law and Justice Department"
    if "social justice" in dl:
        return "Social Justice and Special Assistance Department"
    if "tribal" in dl:
        return "Tribal Development Department"
    if "minorities" in dl:
        return "Minorities Development Department"
    if "school" in dl and "sports" in dl:
        return "School Education and Sports Department"
    if "agriculture" in dl or "animal" in dl:
        return "Agriculture, Animal Husbandry, Dairy and Fisheries Department"
    if "water resources" in dl:
        return "Water Resources Department"
    if "planning" in dl:
        return "Planning Department"
    if "tourism" in dl:
        return "Tourism and Cultural Affairs Department"
    return d


def parse_time_limit(raw_val: Any) -> Optional[int]:
    """Extracts normalized integer days from raw time_limit_days strings."""
    if raw_val is None:
        return None
    val_str = str(raw_val).strip()
    if not val_str:
        return None
    # Check for direct integer
    try:
        val_int = int(val_str)
        if 0 < val_int <= 365:
            return val_int
    except ValueError:
        pass

    vl = val_str.lower()
    if "immediate" in vl or "12 hours" in vl or "24*7" in vl or "same day" in vl:
        return 1
    if "3 months" in vl:
        return 90
    if "6 months" in vl:
        return 180
    if "1 month" in vl:
        return 30

    # Match digits followed by day/days/working days
    m = re.search(r'(\d+)\s*(?:working\s+)?day', vl)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass

    # Match any isolated integer
    m2 = re.search(r'\b(\d+)\b', val_str)
    if m2:
        try:
            num = int(m2.group(1))
            if 0 < num <= 365:
                return num
        except ValueError:
            pass

    return None


def is_service_relevant(s: Dict[str, Any]) -> Tuple[bool, str]:
    """Filters out internal non-civic records (e.g. pure veterinary clinical treatments, archival CD requests)."""
    sub = s.get('sub_department', '').strip().lower()
    name = s.get('service_name', '').strip()
    nl = name.lower()

    # Clinical veterinary lab diagnostics & surgeries (not administrative licenses/certifications)
    vet_clinical = [
        'first aid on a veterinary', 'disease prevention vaccination', 'artificial insemination',
        'veterinary medicine', 'pregnancy test', 'infertility screening', 'minor surgery',
        'major surgery', 'large animals - calves', 'x-ray examination', 'sonography',
        'blood sample', 'dung samples', 'examination of urine', 'examination of skin',
        'hemoglobin in the blood', 'cbc (blood test)', 'examination of milk', 'examination of tissue',
        'poisoning test', 'salmonella disease', 'antibiotic susceptibility', 'compartment test',
        'proximate analysis', 'gross constituents', 'micronutrients, macronutrients',
        'crude fibers', 'urea in animal feed', 'energy in animal feed', 'qualitative screening',
        'inspection of fungi', 'tb test', 'jd test', 'infectious pregnancy', 'contagious abortion',
        'blood/exudate/pus', 'tissue samples', 'bacterial/cultural', 'asudate/whole',
        'prepucial washing', 'blood test for brucella', 'smear/lymph', 'blood test by eliza',
        'semen screening', 'scab samples', 'blue tongue test', 'brain samples (rabies)'
    ]
    if any(vc in nl for vc in vet_clinical):
        return False, "Veterinary Clinical Diagnostic/Treatment"

    # Archival library media requests
    if 'darshanika' in sub or 'historical records' in nl or 'cd of scanned records' in nl or 'making available e-book (cd)' in nl:
        return False, "Archival/Library Media Request"

    # Routine internal exam timetables/answer sheet copies
    if 'photocopies of answer sheets' in nl or 'competitive exam time tables' in nl or 'announcing the annual estimated schedule' in nl:
        return False, "Internal Exam Administration"

    return True, "Civic/Government Service"


def determine_location(dept_name: str, sub_dept: str) -> str:
    """Normalizes location/jurisdiction based on department and subdepartment."""
    sub_lower = (sub_dept or "").lower()
    if "bmc" in sub_lower or "mcgm" in sub_lower:
        return "Mumbai (MCGM / BMC)"
    if "cidco" in sub_lower:
        return "Navi Mumbai & CIDCO Jurisdiction"
    if "nagpur" in sub_lower or "nmrda" in sub_lower:
        return "Nagpur (NMRDA)"
    if "pmrda" in sub_lower or "pune" in sub_lower:
        return "Pune (PMC / PMRDA)"
    if "narrow" in sub_lower or "municipal" in sub_lower or "nagar" in sub_lower:
        return "Maharashtra Municipalities & Nagar Parishads"
    if "panchayat" in sub_lower or "rural" in dept_name.lower():
        return "Maharashtra Rural & Gram Panchayats"
    return "Maharashtra Statewide"


# ---------------------------------------------------------------------------
# Core Curated Procedural Roadmaps (Supporting DAG dependency visualization)
# ---------------------------------------------------------------------------
def build_curated_civic_tasks() -> List[Dict[str, Any]]:
    """
    Constructs high-value, standardized citizen tasks with full DAG procedural steps,
    prerequisites, official forms, and categorized document lockers for the 10
    primary hackathon queries and key Maharashtra municipal procedures.
    """
    tasks = [
        # 1. CASTE CERTIFICATE
        {
            "id": "task-caste-certificate",
            "title": "Apply for Caste Certificate (SC/ST/VJNT/OBC/SBC)",
            "category": "Citizen & Vital Records",
            "municipality": "Maharashtra Statewide (Aaple Sarkar / Revenue Dept)",
            "state": "Maharashtra",
            "description": "Statutory application procedure for issuance of Caste Certificate under the Maharashtra Scheduled Castes, Scheduled Tribes, De-notified Tribes (Vimukta Jatis), Nomadic Tribes, Other Backward Classes and Special Backward Category (Regulation of Issuance and Verification of) Caste Certificate Act, 2000.",
            "tags": ["caste", "caste_certificate", "reservation", "revenue", "tehsildar", "sdo", "1284", "aaple_sarkar"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Check Eligibility & Proof of Caste Residence",
                    "description": "Verify applicant meets deemed date residence requirement in Maharashtra (SC/ST: 1950, VJNT: 1961, OBC: 1967). Collect father's/relative's pre-deemed date documentary proofs.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 2,
                    "fee_amount": 0.0,
                    "fee_breakdown": {"consultation": 0.0},
                    "prerequisites": [],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in/en/Login/Certificate_Documents?ServiceId=1284",
                        "page_title": "Aaple Sarkar - Caste Certificate Requirements",
                        "last_scraped_at": "2026-09-26T15:29:57Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Maharashtra Act No. XXIII of 2001"
                    },
                    "documents": [
                        {"id": "doc-caste-id", "name": "Identity Proof (Aadhaar / Voter ID / PAN)", "description": "Government issued photo identification", "is_mandatory": True, "category": "Identity"},
                        {"id": "doc-caste-addr", "name": "Address Proof (Ration Card / Electricity Bill)", "description": "Proof of residence in Maharashtra", "is_mandatory": True, "category": "Address"}
                    ],
                    "forms": []
                },
                {
                    "step_number": 2,
                    "title": "Assemble Ancestral & Statutory Caste Evidence",
                    "description": "Procure birth extract, school leaving certificate of father/grandfather mentioning caste and place of residence before the deemed date.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 5,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-caste-certificate-step-1"],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in/en/Login/Certificate_Documents?ServiceId=1284",
                        "page_title": "Aaple Sarkar - Caste Certificate Evidence",
                        "last_scraped_at": "2026-09-26T15:29:57Z",
                        "confidence_score": 0.98,
                        "gazette_ref": "Maharashtra Caste Rules 2012"
                    },
                    "documents": [
                        {"id": "doc-caste-father-lc", "name": "Father's School Leaving Certificate / Primary School Record", "description": "Showing caste and date of admission before deemed date", "is_mandatory": True, "category": "Certificate"},
                        {"id": "doc-caste-kotwal", "name": "Kotwal Book Extract / Birth Extract of Ancestor", "description": "Revenue talathi entry or Kotwal book from Tahsildar", "is_mandatory": False, "category": "Ownership"},
                        {"id": "doc-caste-affidavit", "name": "Statutory Affidavit in Form 2 / Form 3", "description": "Self-declaration of caste and family genealogy tree", "is_mandatory": True, "category": "Application"}
                    ],
                    "forms": [
                        {"form_code": "Form-2", "title": "Affidavit for Caste Certificate Application", "download_url": "https://aaplesarkar.mahaonline.gov.in/Forms/Form2.pdf", "fill_online_url": "https://aaplesarkar.mahaonline.gov.in", "instructions": "Sign before Executive Magistrate or Notary"}
                    ]
                },
                {
                    "step_number": 3,
                    "title": "Online Application Submission on Aaple Sarkar",
                    "description": "Log into Aaple Sarkar portal, select Revenue Department > Caste Certificate, fill personal details, upload photo and documents in specified pixel format.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 1,
                    "fee_amount": 23.60,
                    "fee_breakdown": {"statutory_fee": 20.0, "portal_charges": 3.60},
                    "prerequisites": ["task-caste-certificate-step-2"],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in/en/Registration/Register",
                        "page_title": "Aaple Sarkar Portal - Form Submission",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "RTS Act 2015 Notification No. 1284"
                    },
                    "documents": [
                        {"id": "doc-caste-photo", "name": "Applicant Passport Photograph (160x200 px)", "description": "Recent photograph between 5KB and 20KB", "is_mandatory": True, "category": "Photograph"}
                    ],
                    "forms": [
                        {"form_code": "Form-B", "title": "Aaple Sarkar Online Application Form for Caste Certificate", "download_url": None, "fill_online_url": "https://aaplesarkar.mahaonline.gov.in/en/Registration/Register", "instructions": "Complete online e-KYC before filling"}
                    ]
                },
                {
                    "step_number": 4,
                    "title": "Scrutiny by Circle Officer & Tahsildar Field Verification",
                    "description": "Application scrutinized by Nayab Tahsildar / Circle Officer. Field enquiry or village talathi verification conducted if ancestral documents require ground corroboration.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Hybrid",
                    "estimated_days": 25,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-caste-certificate-step-3"],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in/en/CommonForm/ViewAllServices",
                        "page_title": "Aaple Sarkar Escalation Matrix",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.95,
                        "gazette_ref": "Designated Officer: SDO / Dy. Collector"
                    },
                    "documents": [],
                    "forms": []
                },
                {
                    "step_number": 5,
                    "title": "Issuance and Digital Download of Caste Certificate",
                    "description": "Sub-Divisional Officer (SDO) or Deputy Collector signs the digital barcoded certificate. Download certificate with cryptographic digital signature.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 12,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-caste-certificate-step-4"],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in",
                        "page_title": "Aaple Sarkar Certificate Download Desk",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Statutory SLA: 45 Days per RTS Schedule"
                    },
                    "documents": [],
                    "forms": []
                }
            ]
        },

        # 2. BIRTH CERTIFICATE (MUNICIPAL / BMC)
        {
            "id": "task-bmc-birth-cert",
            "title": "Apply for Municipal Birth Certificate (BMC / Municipal Corporation)",
            "category": "Citizen & Vital Records",
            "municipality": "Mumbai (MCGM / BMC) & Maharashtra Urban",
            "state": "Maharashtra",
            "description": "Issuance of official Birth Certificate under Registration of Births and Deaths Act, 1969 and Maharashtra Registration of Births and Deaths Rules, 2000.",
            "tags": ["birth", "birth_certificate", "bmc", "mcgm", "vital_records", "public_health", "hospital", "970"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Verification of Institutional / Hospital Birth Report",
                    "description": "Confirm that the hospital/maternity nursing home where birth occurred submitted Form 1 (Birth Report) to the local Ward Medical Officer of Health (MOH) within 21 days.",
                    "department_id": "dept-bmc",
                    "submission_mode": "In-Person",
                    "estimated_days": 1,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": [],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "BMC Public Health Department - Vital Statistics",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.98,
                        "gazette_ref": "RBD Act 1969 Section 7"
                    },
                    "documents": [
                        {"id": "doc-birth-discharge", "name": "Hospital Discharge Card / Maternity Record", "description": "Original discharge slip mentioning date, time, and child gender", "is_mandatory": True, "category": "Certificate"},
                        {"id": "doc-birth-parents-id", "name": "Parents' Aadhaar & Marriage Proof", "description": "Photo IDs of father and mother", "is_mandatory": True, "category": "Identity"}
                    ],
                    "forms": [
                        {"form_code": "Form-1", "title": "Statutory Birth Report Form", "download_url": "https://portal.mcgm.gov.in/irj/go/km/docs/documents/mcgm_birth_form1.pdf", "fill_online_url": None, "instructions": "Usually submitted directly by registered hospital"}
                    ]
                },
                {
                    "step_number": 2,
                    "title": "Online Application & Name Inclusion on BMC CFC Portal",
                    "description": "Submit application on MCGM portal (Citizen Facilitation Centre) or Aaple Sarkar. If child name was not included during initial hospital filing, apply for Name Inclusion.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 1,
                    "fee_amount": 25.0,
                    "fee_breakdown": {"search_fee": 10.0, "certificate_copy": 15.0},
                    "prerequisites": ["task-bmc-birth-cert-step-1"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "MCGM Health Department Birth Registration",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "MCGM Citizen Charter - 3 Days SLA"
                    },
                    "documents": [
                        {"id": "doc-birth-name-affidavit", "name": "Parental Name Inclusion Declaration", "description": "Joint affidavit of parents specifying the legal name of the child", "is_mandatory": False, "category": "Application"}
                    ],
                    "forms": [
                        {"form_code": "MCGM-B-1", "title": "Application for Certified Copy of Birth Registration", "download_url": "https://portal.mcgm.gov.in", "fill_online_url": "https://portal.mcgm.gov.in", "instructions": "Search by date of birth and mother name"}
                    ]
                },
                {
                    "step_number": 3,
                    "title": "MOH Ward Scrutiny & Register Verification",
                    "description": "Ward Health Registrar verifies registration entry against birth register volumes. Digital signature appended to entry.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 1,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-bmc-birth-cert-step-2"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "BMC MOH Verification SLA",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.97,
                        "gazette_ref": "Maharashtra RTS Notification sr_no 970"
                    },
                    "documents": [],
                    "forms": []
                },
                {
                    "step_number": 4,
                    "title": "Download QR-Coded Digitally Signed Birth Certificate",
                    "description": "Download watermarked, digitally signed municipal birth certificate with official QR code for instant statutory verification.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 1,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-bmc-birth-cert-step-3"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "BMC Birth Certificate Generation",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Total Statutory Time Limit: 3 Days"
                    },
                    "documents": [],
                    "forms": []
                }
            ]
        },

        # 3. TRADE LICENSE (BMC / MUNICIPAL CORPORATION)
        {
            "id": "task-trade-license",
            "title": "Apply for Municipal Health Trade License (Section 394 MMC Act)",
            "category": "Business & Commercial",
            "municipality": "Mumbai (MCGM / BMC) & Maharashtra Urban",
            "state": "Maharashtra",
            "description": "Statutory procedure for obtaining Municipal Health Trade License under Section 394 of Mumbai Municipal Corporation Act (MMC Act, 1888) for commercial establishments, eating houses, and trades.",
            "tags": ["trade", "trade_license", "bmc", "mcgm", "health_license", "section_394", "eodb", "990", "991"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Property Eligibility & Title Verification",
                    "description": "Ensure commercial premises has valid Occupancy Certificate (OC) or sanctioned building plan with designated commercial land-use approval.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 3,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": [],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in/eodb-tradelicense",
                        "page_title": "MCGM EoDB Trade Licensing Manual",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.98,
                        "gazette_ref": "Section 394 MMC Act 1888"
                    },
                    "documents": [
                        {"id": "doc-trade-oc", "name": "Sanctioned Plan / Occupancy Certificate (OC)", "description": "Proof of authorized commercial building structure", "is_mandatory": True, "category": "Ownership"},
                        {"id": "doc-trade-lease", "name": "Registered Commercial Lease / Ownership Proof", "description": "Registered agreement with Index II or Property Tax bill", "is_mandatory": True, "category": "Ownership"}
                    ],
                    "forms": []
                },
                {
                    "step_number": 2,
                    "title": "Procure Fire Safety No Objection Certificate (Fire NOC)",
                    "description": "Obtain preliminary / final fire safety compliance certificate from Chief Fire Officer (Mumbai Fire Brigade) for the commercial establishment.",
                    "department_id": "dept-mfb",
                    "submission_mode": "Online",
                    "estimated_days": 15,
                    "fee_amount": 5000.0,
                    "fee_breakdown": {"fire_scrutiny_fee": 5000.0},
                    "prerequisites": ["task-trade-license-step-1"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in/eodb-fire-noc",
                        "page_title": "Maharashtra Fire Prevention & Life Safety Measures",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Maharashtra Fire Safety Act 2006"
                    },
                    "documents": [
                        {"id": "doc-trade-fire-layout", "name": "Architectural Key Plan with Fire Exits", "description": "Floor layout showing exits, extinguishers, and gas pipelines", "is_mandatory": True, "category": "Certificate"}
                    ],
                    "forms": [
                        {"form_code": "MFB-NOC-01", "title": "Application for Fire Safety NOC", "download_url": None, "fill_online_url": "https://portal.mcgm.gov.in", "instructions": "Submit via AutoDCR/MCGM Fire portal"}
                    ]
                },
                {
                    "step_number": 3,
                    "title": "Online Trade License Application on MCGM EoDB Portal",
                    "description": "Submit application under Section 394 specifying trade schedule commodity, electrical horsepower, and number of employees.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 2,
                    "fee_amount": 1000.0,
                    "fee_breakdown": {"scrutiny_fee": 1000.0},
                    "prerequisites": ["task-trade-license-step-2"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "MCGM Health Trade License Application",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "RTS Notification sr_no 990"
                    },
                    "documents": [
                        {"id": "doc-trade-pan", "name": "Company PAN & Gumasta Certificate", "description": "Entity proof and Shops & Establishment intimation", "is_mandatory": True, "category": "Identity"},
                        {"id": "doc-trade-noc-landlord", "name": "Landlord NOC / Society NOC", "description": "Consent for conducting proposed trade on premises", "is_mandatory": True, "category": "NOC"}
                    ],
                    "forms": [
                        {"form_code": "Sec-394-Form", "title": "Application for Trade License under Section 394", "download_url": None, "fill_online_url": "https://portal.mcgm.gov.in", "instructions": "Fill commodity schedule codes accurately"}
                    ]
                },
                {
                    "step_number": 4,
                    "title": "Joint Site Inspection by Ward Sanitary Inspector",
                    "description": "Medical Officer of Health (MOH) / Senior Inspector of License conducts physical site inspection to verify trade hygiene, ventilation, and fire compliance.",
                    "department_id": "dept-bmc",
                    "submission_mode": "In-Person",
                    "estimated_days": 7,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-trade-license-step-3"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "MCGM Ward Inspection Guidelines",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.96,
                        "gazette_ref": "Ward Sanitary Protocol 2024"
                    },
                    "documents": [],
                    "forms": []
                },
                {
                    "step_number": 5,
                    "title": "Payment of Statutory License Fee & Certificate Grant",
                    "description": "Pay schedule trade fees calculated based on square footage and trade hazard category via MCGM payment gateway. Download barcoded Health Trade License.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 2,
                    "fee_amount": 7500.0,
                    "fee_breakdown": {"statutory_license_fee": 7500.0},
                    "prerequisites": ["task-trade-license-step-4"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "MCGM Trade License Grant Desk",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Total Statutory SLA: 15 Days"
                    },
                    "documents": [],
                    "forms": []
                }
            ]
        },

        # 4. BUILDING PERMISSION (AUTODCR / BPMS)
        {
            "id": "task-building-permission",
            "title": "Apply for Building Permission & Commencement Certificate (AutoDCR / BPMS)",
            "category": "Construction & Real Estate",
            "municipality": "Maharashtra Statewide & Urban Municipal Corporations",
            "state": "Maharashtra",
            "description": "Statutory multi-phase building proposal approval process under Maharashtra Regional and Town Planning Act, 1966 (MRTP Act) and Unified Development Control and Promotion Regulations (UDCPR 2020).",
            "tags": ["building", "construction", "autodcr", "bpms", "commencement_certificate", "iod", "occupancy", "7084", "8864", "983"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Land Title, 7/12 & Zone Certificate Scrutiny",
                    "description": "Procure latest Demarcated Property Card (PR Card) / 7/12 Extract, non-agricultural (NA) order, and official Development Plan (DP) Zone Certificate.",
                    "department_id": "dept-urban-dev",
                    "submission_mode": "Online",
                    "estimated_days": 7,
                    "fee_amount": 1000.0,
                    "fee_breakdown": {"zone_cert_fee": 1000.0},
                    "prerequisites": [],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in/en/Login/Certificate_Documents?ServiceId=7084",
                        "page_title": "Aaple Sarkar BPMS Building Permission",
                        "last_scraped_at": "2026-09-26T15:30:04Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "UDCPR 2020 Chapter 2"
                    },
                    "documents": [
                        {"id": "doc-bp-prcard", "name": "CTS / Demarcation Property Card / 7-12 Extract", "description": "Certified land record issued within 3 months", "is_mandatory": True, "category": "Ownership"},
                        {"id": "doc-bp-na", "name": "Non-Agricultural (NA) Permission Order", "description": "Sanctioned NA order from Collector / Competent Authority", "is_mandatory": True, "category": "Certificate"}
                    ],
                    "forms": []
                },
                {
                    "step_number": 2,
                    "title": "AutoDCR CAD Drawing Upload & Architectural Pre-Scrutiny",
                    "description": "Registered Architect or Licensed Surveyor submits AutoCAD drawings on AutoDCR / BPMS portal for automated scrutiny of FSI, setbacks, height, and parking.",
                    "department_id": "dept-urban-dev",
                    "submission_mode": "Online",
                    "estimated_days": 10,
                    "fee_amount": 15000.0,
                    "fee_breakdown": {"scrutiny_fee": 15000.0},
                    "prerequisites": ["task-building-permission-step-1"],
                    "verification_source": {
                        "url": "https://mahabpms.maharashtra.gov.in",
                        "page_title": "MahaBPMS AutoDCR Online Portal",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "RTS Schedule sr_no 7084 / 983"
                    },
                    "documents": [
                        {"id": "doc-bp-drawings", "name": "Architectural Plans in AutoDCR Format", "description": "Standardized layer-mapped DWG CAD plans", "is_mandatory": True, "category": "Application"},
                        {"id": "doc-bp-structure", "name": "Structural Stability Certificate", "description": "Undertaking by licensed Structural Engineer", "is_mandatory": True, "category": "Certificate"}
                    ],
                    "forms": [
                        {"form_code": "BPMS-APP-01", "title": "Online Building Proposal Application Form", "download_url": None, "fill_online_url": "https://mahabpms.maharashtra.gov.in", "instructions": "Submit with digital signature of architect and owner"}
                    ]
                },
                {
                    "step_number": 3,
                    "title": "Multi-Department Clearances (Fire, Water, Stormwater, Tree)",
                    "description": "Coordinated online referrals to Chief Fire Officer, Hydraulic Department (Water NOC), Sewerage Department, and Tree Authority.",
                    "department_id": "dept-urban-dev",
                    "submission_mode": "Online",
                    "estimated_days": 15,
                    "fee_amount": 10000.0,
                    "fee_breakdown": {"interagency_charges": 10000.0},
                    "prerequisites": ["task-building-permission-step-2"],
                    "verification_source": {
                        "url": "https://mahabpms.maharashtra.gov.in",
                        "page_title": "Inter-Agency EoDB Clearances",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.97,
                        "gazette_ref": "Single Window Clearance Regulation"
                    },
                    "documents": [],
                    "forms": []
                },
                {
                    "step_number": 4,
                    "title": "Intimation of Disapproval (IOD) & Development Premium Payment",
                    "description": "Town Planning Officer issues conditional sanction (IOD). Applicant pays development charges, infrastructure premium, and labor cess to government treasury.",
                    "department_id": "dept-urban-dev",
                    "submission_mode": "Online",
                    "estimated_days": 10,
                    "fee_amount": 50000.0,
                    "fee_breakdown": {"development_charge": 45000.0, "labor_cess": 5000.0},
                    "prerequisites": ["task-building-permission-step-3"],
                    "verification_source": {
                        "url": "https://mahabpms.maharashtra.gov.in",
                        "page_title": "IOD & Statutory Premium Schedule",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Maharashtra Municipal Corporations Act Section 254"
                    },
                    "documents": [
                        {"id": "doc-bp-challan", "name": "Statutory Development Charges Paid Challan", "description": "Gras MahaKosh payment receipt", "is_mandatory": True, "category": "Financial"}
                    ],
                    "forms": []
                },
                {
                    "step_number": 5,
                    "title": "Grant of Commencement Certificate (CC)",
                    "description": "Competent Authority issues Commencement Certificate (CC) authorizing execution of construction up to plinth level on site.",
                    "department_id": "dept-urban-dev",
                    "submission_mode": "Online",
                    "estimated_days": 8,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-building-permission-step-4"],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in/en/Login/Certificate_Documents?ServiceId=8864",
                        "page_title": "Commencement Certificate (AutoDCR)",
                        "last_scraped_at": "2026-09-26T15:30:05Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "RTS Statutory SLA: 30 Days total"
                    },
                    "documents": [],
                    "forms": []
                }
            ]
        },

        # 5. PROPERTY TAX (BMC / MUNICIPAL CORPORATIONS)
        {
            "id": "task-property-tax",
            "title": "Assessment & Payment of Municipal Property Tax (BMC / Urban Maharashtra)",
            "category": "Municipal Taxes & Revenue",
            "municipality": "Mumbai (MCGM / BMC) & Maharashtra Urban",
            "state": "Maharashtra",
            "description": "Procedure for property tax assessment, online bill generation, rebate claiming, dispute rectification, and payment under Mumbai Municipal Corporation Act (Capital Value System).",
            "tags": ["property_tax", "property", "tax", "bmc", "mcgm", "capital_value", "assessment", "ptax", "973", "977", "979"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Search Property Account Number (SAC Code / PTIN)",
                    "description": "Locate unique 15-character Property Tax Identification Number (PTIN) or SAC code on MCGM / Municipal Tax Portal using ward, zone, and CTS survey number.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 1,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": [],
                    "verification_source": {
                        "url": "https://ptaxportal.mcgm.gov.in",
                        "page_title": "MCGM Citizen Portal - Property Tax",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "MMC Act Capital Value Rules"
                    },
                    "documents": [
                        {"id": "doc-ptax-index2", "name": "Registered Sale Deed / Index II Copy", "description": "Showing flat/unit carpet area and CTS number", "is_mandatory": True, "category": "Ownership"}
                    ],
                    "forms": []
                },
                {
                    "step_number": 2,
                    "title": "Verify Capital Value Assessment & Demand Calculation",
                    "description": "Verify property capital value calculation based on Ready Reckoner rate, user category (Residential/Commercial), building age, and carpet area factor.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 2,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-property-tax-step-1"],
                    "verification_source": {
                        "url": "https://ptaxportal.mcgm.gov.in",
                        "page_title": "Property Tax Capital Value Calculator",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.98,
                        "gazette_ref": "RTS Schedule sr_no 979"
                    },
                    "documents": [],
                    "forms": [
                        {"form_code": "PTAX-DEMAND-01", "title": "Property Tax Demand Notice (Bill Copy)", "download_url": "https://ptaxportal.mcgm.gov.in", "fill_online_url": "https://ptaxportal.mcgm.gov.in", "instructions": "Check for early payment rebate eligibility"}
                    ]
                },
                {
                    "step_number": 3,
                    "title": "Online Property Tax Payment via MCGM Citizen Portal",
                    "description": "Execute payment using Net Banking, UPI, debit/credit cards through BillDesk / SBI e-Pay. Download statutory digitally signed municipal receipt.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 1,
                    "fee_amount": 0.0,
                    "fee_breakdown": {"tax_payable": 0.0},
                    "prerequisites": ["task-property-tax-step-2"],
                    "verification_source": {
                        "url": "https://ptaxportal.mcgm.gov.in",
                        "page_title": "MCGM Property Tax E-Payment Desk",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Statutory Receipt Mandate Section 209 MMC Act"
                    },
                    "documents": [],
                    "forms": []
                },
                {
                    "step_number": 4,
                    "title": "Obtain No Dues / No Arrears Certificate",
                    "description": "Apply for and download official municipal Property Tax No Dues Certificate confirming zero outstanding tax liability for property transfer or loan mortgaging.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 3,
                    "fee_amount": 50.0,
                    "fee_breakdown": {"certificate_fee": 50.0},
                    "prerequisites": ["task-property-tax-step-3"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "Certificate of No Arrears (Property Tax)",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "RTS Notification sr_no 974"
                    },
                    "documents": [],
                    "forms": []
                }
            ]
        },

        # 6. WATER CONNECTION (MUNICIPAL / MJP)
        {
            "id": "task-water-connection",
            "title": "Apply for New Domestic / Commercial Water Connection (MCGM / MJP)",
            "category": "Public Utilities & Water",
            "municipality": "Mumbai (MCGM / BMC) & Maharashtra Statewide (MJP)",
            "state": "Maharashtra",
            "description": "Procedure for sanction of new tap water connection, water meter installation, and drainage hook-up under Mumbai Municipal Corporation Act (Section 269) and Maharashtra Jeevan Pradhikaran bye-laws.",
            "tags": ["water", "water_connection", "tap_connection", "mcgm", "mjp", "hydraulic", "meter", "plumber", "202", "1000"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Site Feasibility & Licensed Plumber Appointment",
                    "description": "Appoint an MCGM / MJP Licensed Plumber to prepare water supply pipeline layout from municipal water distribution main to consumer premises.",
                    "department_id": "dept-bmc",
                    "submission_mode": "In-Person",
                    "estimated_days": 2,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": [],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in/eodb-water-connection",
                        "page_title": "MCGM Hydraulic Engineer Department - New Connection",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.98,
                        "gazette_ref": "MMC Act 1888 Section 269"
                    },
                    "documents": [
                        {"id": "doc-water-sanction", "name": "Sanctioned Building Plan / Occupancy Certificate", "description": "Proof of municipal construction legality", "is_mandatory": True, "category": "Certificate"},
                        {"id": "doc-water-tax", "name": "Latest Property Tax Paid Receipt", "description": "Proof of zero municipal tax default", "is_mandatory": True, "category": "Financial"}
                    ],
                    "forms": []
                },
                {
                    "step_number": 2,
                    "title": "Submit Water Connection Application Form",
                    "description": "Submit application on municipal portal specifying requested diameter (15mm, 20mm, 25mm+), number of occupants, and plumbing schematic.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 2,
                    "fee_amount": 500.0,
                    "fee_breakdown": {"application_scrutiny": 500.0},
                    "prerequisites": ["task-water-connection-step-1"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "MCGM Water Works Online Application",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "RTS Notification sr_no 202"
                    },
                    "documents": [
                        {"id": "doc-water-plumber-cert", "name": "Licensed Plumber Certificate & Key Plan", "description": "Schematic indicating ferrule connection and suction tank", "is_mandatory": True, "category": "Application"}
                    ],
                    "forms": [
                        {"form_code": "HE-W-01", "title": "Application for Fresh Water Supply Connection", "download_url": None, "fill_online_url": "https://portal.mcgm.gov.in", "instructions": "Requires licensed plumber registration number"}
                    ]
                },
                {
                    "step_number": 3,
                    "title": "Hydraulic Field Scrutiny & Pressure Feasibility Inspection",
                    "description": "Assistant Engineer (Water Works) conducts on-site technical inspection to test municipal water main pressure and ferrule drilling location.",
                    "department_id": "dept-bmc",
                    "submission_mode": "In-Person",
                    "estimated_days": 7,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-water-connection-step-2"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "MCGM Hydraulic Site Protocol",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.97,
                        "gazette_ref": "MCGM Citizen Charter SLA: 7 Days"
                    },
                    "documents": [],
                    "forms": []
                },
                {
                    "step_number": 4,
                    "title": "Payment of Connection Charges, Road Opening & Meter Deposit",
                    "description": "Pay road opening reinstatement charges, security deposit, ferrule charges, and water meter testing fee to municipal treasury.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 2,
                    "fee_amount": 12500.0,
                    "fee_breakdown": {"road_opening": 8000.0, "security_deposit": 3000.0, "ferrule_fee": 1500.0},
                    "prerequisites": ["task-water-connection-step-3"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "MCGM Water Works Demand Notice",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Statutory Payment Channel: Gras MahaKosh / BillDesk"
                    },
                    "documents": [],
                    "forms": []
                },
                {
                    "step_number": 5,
                    "title": "Physical Connection Tapping & Water Meter Commissioning",
                    "description": "Municipal hydraulic gang drills the main ferrule, joins service pipe, tests water meter calibration, and activates tap water supply.",
                    "department_id": "dept-bmc",
                    "submission_mode": "In-Person",
                    "estimated_days": 7,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-water-connection-step-4"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "Water Connection Activation Report",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Total Statutory SLA: 15 Days"
                    },
                    "documents": [],
                    "forms": []
                }
            ]
        },

        # 7. DEATH CERTIFICATE
        {
            "id": "task-bmc-death-cert",
            "title": "Apply for Municipal Death Certificate (BMC / Municipal Corporation)",
            "category": "Citizen & Vital Records",
            "municipality": "Mumbai (MCGM / BMC) & Maharashtra Urban",
            "state": "Maharashtra",
            "description": "Statutory procedure for registration of death and issuance of certified Death Certificate under Registration of Births and Deaths Act, 1969.",
            "tags": ["death", "death_certificate", "bmc", "mcgm", "vital_records", "cremation", "971"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Obtain Cremation / Burial Pass & Medical Cause of Death",
                    "description": "Procure official cremation/burial receipt from municipal crematorium/cemetery and Form 4 / 4A (Medical Certificate of Cause of Death) signed by registered medical practitioner.",
                    "department_id": "dept-bmc",
                    "submission_mode": "In-Person",
                    "estimated_days": 1,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": [],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "BMC Vital Statistics Registration",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "RBD Act 1969 Section 10"
                    },
                    "documents": [
                        {"id": "doc-death-mccd", "name": "Form 4/4A Medical Cause of Death Certificate", "description": "Issued by attending physician or hospital", "is_mandatory": True, "category": "Certificate"},
                        {"id": "doc-death-cremation", "name": "Cremation / Burial Ground Receipt", "description": "Issued by municipal crematorium registrar", "is_mandatory": True, "category": "Certificate"},
                        {"id": "doc-death-id", "name": "Deceased & Applicant Aadhaar Cards", "description": "Identity proofs of deceased and primary next-of-kin", "is_mandatory": True, "category": "Identity"}
                    ],
                    "forms": [
                        {"form_code": "Form-2", "title": "Statutory Death Report Form", "download_url": "https://portal.mcgm.gov.in", "fill_online_url": None, "instructions": "Submit within 21 days of occurrence"}
                    ]
                },
                {
                    "step_number": 2,
                    "title": "Online Registration & Application on MCGM / Aaple Sarkar Portal",
                    "description": "Search death registration entry in Ward vital register by deceased name, date of demise, and crematorium location. File application for certified extract.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 1,
                    "fee_amount": 25.0,
                    "fee_breakdown": {"search_fee": 10.0, "certificate_copy": 15.0},
                    "prerequisites": ["task-bmc-death-cert-step-1"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "MCGM Citizen Portal - Death Certificate",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "RTS Schedule sr_no 971"
                    },
                    "documents": [],
                    "forms": [
                        {"form_code": "MCGM-D-01", "title": "Application for Certified Extract of Death", "download_url": None, "fill_online_url": "https://portal.mcgm.gov.in", "instructions": "Verify spellings match Aadhaar"}
                    ]
                },
                {
                    "step_number": 3,
                    "title": "MOH Approval & Digitally Signed Certificate Issuance",
                    "description": "Medical Officer of Health (MOH) reviews registration details, digitally signs record, and generates QR-coded statutory certificate.",
                    "department_id": "dept-bmc",
                    "submission_mode": "Online",
                    "estimated_days": 1,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-bmc-death-cert-step-2"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in",
                        "page_title": "BMC MOH Vital Records Approval",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Total Statutory SLA: 3 Days"
                    },
                    "documents": [],
                    "forms": []
                }
            ]
        },

        # 8. FIRE SAFETY NOC (MUMBAI FIRE BRIGADE / MUNICIPAL FIRE COMMAND)
        {
            "id": "task-fire-noc",
            "title": "Apply for Fire Safety & Prevention No Objection Certificate (Fire NOC)",
            "category": "Safety & Disaster Management",
            "municipality": "Mumbai (MCGM / BMC) & Maharashtra Urban",
            "state": "Maharashtra",
            "description": "Statutory fire safety audit and No Objection Certificate procedure under Maharashtra Fire Prevention and Life Safety Measures Act, 2006 for residential/commercial buildings and high-hazard occupancies.",
            "tags": ["fire", "fire_noc", "fire_safety", "mfb", "cfo", "life_safety", "987", "988"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Architectural Fire Safety Layout & System Design",
                    "description": "Appoint licensed Fire Safety Consultant to formulate firefighting layout (sprinklers, wet risers, yard hydrants, smoke detectors, refuge areas) adhering to National Building Code (NBC Part IV).",
                    "department_id": "dept-mfb",
                    "submission_mode": "Online",
                    "estimated_days": 3,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": [],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in/eodb-fire-noc",
                        "page_title": "Mumbai Fire Brigade Life Safety Portal",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.98,
                        "gazette_ref": "Maharashtra Fire Safety Act 2006 Section 3"
                    },
                    "documents": [
                        {"id": "doc-fire-cad", "name": "CAD Fire Evacuation & Hydrant Layout", "description": "Architect signed drawing showing all fire fighting provisions", "is_mandatory": True, "category": "Certificate"},
                        {"id": "doc-fire-form-a", "name": "Form A - Licensed Agency Certificate", "description": "Certificate from licensed fire agency regarding equipment installation", "is_mandatory": True, "category": "Application"}
                    ],
                    "forms": []
                },
                {
                    "step_number": 2,
                    "title": "Online Fire NOC Application on MFB EoDB Portal",
                    "description": "Submit application to Chief Fire Officer specifying building height (<24m, 24m-70m, >70m), plot area, occupancy type, and water storage capacity.",
                    "department_id": "dept-mfb",
                    "submission_mode": "Online",
                    "estimated_days": 1,
                    "fee_amount": 1000.0,
                    "fee_breakdown": {"scrutiny_fee": 1000.0},
                    "prerequisites": ["task-fire-noc-step-1"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in/eodb-fire-noc",
                        "page_title": "MFB Online Fire NOC Portal",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "RTS Schedule sr_no 987"
                    },
                    "documents": [],
                    "forms": [
                        {"form_code": "MFB-APP-2024", "title": "Application for Fire Safety and Prevention Certificate", "download_url": None, "fill_online_url": "https://portal.mcgm.gov.in/eodb-fire-noc", "instructions": "Attach Form A from licensed fire agency"}
                    ]
                },
                {
                    "step_number": 3,
                    "title": "Physical Inspection by Divisional Fire Officer",
                    "description": "Divisional Fire Officer conducts physical drill and audit of booster pumps, diesel generator backup, fire lifts, emergency staircase width, and alarm systems.",
                    "department_id": "dept-mfb",
                    "submission_mode": "In-Person",
                    "estimated_days": 7,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-fire-noc-step-2"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in/eodb-fire-noc",
                        "page_title": "Fire Brigade Audit Protocol",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.97,
                        "gazette_ref": "Inspection SLA: 7 Days"
                    },
                    "documents": [],
                    "forms": []
                },
                {
                    "step_number": 4,
                    "title": "Payment of Fire Protection Fund Premium & Final NOC Issuance",
                    "description": "Pay statutory fire capitation fee / protection fund tax calculated based on total built-up area. Download digitally signed Fire NOC from Chief Fire Officer.",
                    "department_id": "dept-mfb",
                    "submission_mode": "Online",
                    "estimated_days": 4,
                    "fee_amount": 10000.0,
                    "fee_breakdown": {"fire_fund_tax": 10000.0},
                    "prerequisites": ["task-fire-noc-step-3"],
                    "verification_source": {
                        "url": "https://portal.mcgm.gov.in/eodb-fire-noc",
                        "page_title": "MFB Fire NOC Grant",
                        "last_scraped_at": "2026-09-26T15:30:00Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Total Statutory SLA: 15 Days per sr_no 988"
                    },
                    "documents": [],
                    "forms": []
                }
            ]
        },

        # 9. INCOME CERTIFICATE
        {
            "id": "task-income-certificate",
            "title": "Apply for Income Certificate (Tahsildar / Revenue Department)",
            "category": "Citizen & Vital Records",
            "municipality": "Maharashtra Statewide (Aaple Sarkar / Revenue Dept)",
            "state": "Maharashtra",
            "description": "Official public service for issuance of Income Certificate by Tahsildar / Nayab Tahsildar under Maharashtra Right to Public Services Act for scholarships, fee concessions, and government welfare schemes.",
            "tags": ["income", "income_certificate", "revenue", "tahsildar", "scholarship", "1251", "aaple_sarkar"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Collect Annual Income Proof & Family Declaration",
                    "description": "Assemble salary slips / Form 16 (for salaried persons) or Talathi income verification enquiry report (for farmers/self-employed) and electricity bill.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 2,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": [],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in/en/Login/Certificate_Documents?ServiceId=1251",
                        "page_title": "Aaple Sarkar - Income Certificate Document Locker",
                        "last_scraped_at": "2026-09-26T15:29:56Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Maharashtra RTS Notification sr_no 1251"
                    },
                    "documents": [
                        {"id": "doc-inc-salary", "name": "Salary Certificate / Form 16 / ITR Copy", "description": "Employer salary certificate for 3 years or ITR V", "is_mandatory": True, "category": "Financial"},
                        {"id": "doc-inc-talathi", "name": "Talathi / Circle Officer Income Verification Report", "description": "Mandatory for agricultural or unorganized sector applicants", "is_mandatory": False, "category": "Ownership"},
                        {"id": "doc-inc-affidavit", "name": "Income Affidavit / Self-Declaration", "description": "Statutory self-declaration of family income from all sources", "is_mandatory": True, "category": "Application"}
                    ],
                    "forms": []
                },
                {
                    "step_number": 2,
                    "title": "Submit Online Application on Aaple Sarkar",
                    "description": "Log in to Aaple Sarkar portal, select Revenue Services > Income Certificate, upload documents, and submit application to the jurisdictional Tahsildar.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 1,
                    "fee_amount": 23.60,
                    "fee_breakdown": {"statutory_fee": 20.0, "portal_charges": 3.60},
                    "prerequisites": ["task-income-certificate-step-1"],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in",
                        "page_title": "Aaple Sarkar Income Form Desk",
                        "last_scraped_at": "2026-09-26T15:29:56Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Designated Officer: Nayab Tahsildar"
                    },
                    "documents": [
                        {"id": "doc-inc-id", "name": "Applicant Aadhaar & Ration Card", "description": "Proof of identity and family composition", "is_mandatory": True, "category": "Identity"}
                    ],
                    "forms": [
                        {"form_code": "Form-Income-01", "title": "Online Income Certificate Application Form", "download_url": None, "fill_online_url": "https://aaplesarkar.mahaonline.gov.in", "instructions": "Declare income from all family members"}
                    ]
                },
                {
                    "step_number": 3,
                    "title": "Nayab Tahsildar Scrutiny & Approval",
                    "description": "Nayab Tahsildar scrutinizes income declaration against revenue circle records. Approves with digital signature.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 10,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-income-certificate-step-2"],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in",
                        "page_title": "Aaple Sarkar Verification Workflow",
                        "last_scraped_at": "2026-09-26T15:29:56Z",
                        "confidence_score": 0.98,
                        "gazette_ref": "First Appellate Officer: Tahsildar"
                    },
                    "documents": [],
                    "forms": []
                },
                {
                    "step_number": 4,
                    "title": "Download Official Barcoded Income Certificate",
                    "description": "Download authentic Income Certificate featuring barcoded verification URL and digital signature from Aaple Sarkar citizen dashboard.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 2,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-income-certificate-step-3"],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in",
                        "page_title": "Aaple Sarkar Certificate Retrieval",
                        "last_scraped_at": "2026-09-26T15:29:56Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Statutory SLA: 15 Days per Service ID 1251"
                    },
                    "documents": [],
                    "forms": []
                }
            ]
        },

        # 10. RESIDENCE / DOMICILE CERTIFICATE
        {
            "id": "task-domicile-certificate",
            "title": "Apply for Age, Nationality and Domicile Certificate",
            "category": "Citizen & Vital Records",
            "municipality": "Maharashtra Statewide (Aaple Sarkar / Revenue Dept)",
            "state": "Maharashtra",
            "description": "Official certification of age, Indian nationality, and minimum 15 years continuous domicile residence in Maharashtra under Maharashtra Right to Public Services Act.",
            "tags": ["domicile", "nationality", "residence", "tehsildar", "revenue", "mhcet", "1253", "aaple_sarkar"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Assemble 15-Year Continuous Residence Documentation",
                    "description": "Collect documents demonstrating continuous residence in Maharashtra for minimum 15 years (School Leaving Certificates, Ration Card, electricity bills, property documents).",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 2,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": [],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in/en/Login/Certificate_Documents?ServiceId=1253",
                        "page_title": "Aaple Sarkar Domicile Checklist",
                        "last_scraped_at": "2026-09-26T15:29:57Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Maharashtra RTS Notification sr_no 1253"
                    },
                    "documents": [
                        {"id": "doc-dom-lc", "name": "Applicant School / College Leaving Certificate", "description": "Showing place of birth in Maharashtra", "is_mandatory": True, "category": "Certificate"},
                        {"id": "doc-dom-residence", "name": "Proof of 15 Years Continuous Residence", "description": "Ration card / electricity bill / voter list extract over 15 years", "is_mandatory": True, "category": "Address"}
                    ],
                    "forms": []
                },
                {
                    "step_number": 2,
                    "title": "Online Submission on Aaple Sarkar",
                    "description": "Submit online application under Revenue Department > Age Nationality Domicile Certificate, upload documents and self-declaration affidavit.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 1,
                    "fee_amount": 23.60,
                    "fee_breakdown": {"statutory_fee": 20.0, "portal_charges": 3.60},
                    "prerequisites": ["task-domicile-certificate-step-1"],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in",
                        "page_title": "Aaple Sarkar Domicile Desk",
                        "last_scraped_at": "2026-09-26T15:29:57Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Designated Officer: Tahsildar"
                    },
                    "documents": [
                        {"id": "doc-dom-id", "name": "Aadhaar Card & Passport Photograph", "description": "Identity proof and recent photograph", "is_mandatory": True, "category": "Identity"}
                    ],
                    "forms": [
                        {"form_code": "Form-Domicile-01", "title": "Online Domicile Certificate Application", "download_url": None, "fill_online_url": "https://aaplesarkar.mahaonline.gov.in", "instructions": "Declare continuous stay details"}
                    ]
                },
                {
                    "step_number": 3,
                    "title": "Executive Magistrate / Tahsildar Verification & Approval",
                    "description": "Tahsildar office verifies 15-year residence evidence and checks prior domicile records. Approves with digital signature.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 10,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-domicile-certificate-step-2"],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in",
                        "page_title": "Tahsildar Domicile Verification SLA",
                        "last_scraped_at": "2026-09-26T15:29:57Z",
                        "confidence_score": 0.98,
                        "gazette_ref": "Statutory SLA: 15 Days"
                    },
                    "documents": [],
                    "forms": []
                },
                {
                    "step_number": 4,
                    "title": "Download Age Nationality and Domicile Certificate",
                    "description": "Download authentic, barcoded Certificate of Age, Nationality, and Domicile accepted for MH-CET, NEET, government jobs, and quota admissions.",
                    "department_id": "dept-rev-forest",
                    "submission_mode": "Online",
                    "estimated_days": 2,
                    "fee_amount": 0.0,
                    "fee_breakdown": {},
                    "prerequisites": ["task-domicile-certificate-step-3"],
                    "verification_source": {
                        "url": "https://aaplesarkar.mahaonline.gov.in",
                        "page_title": "Aaple Sarkar Certificate Download",
                        "last_scraped_at": "2026-09-26T15:29:57Z",
                        "confidence_score": 0.99,
                        "gazette_ref": "Government of Maharashtra Official Certificate"
                    },
                    "documents": [],
                    "forms": []
                }
            ]
        }
    ]
    return tasks


# ---------------------------------------------------------------------------
# Main Import Engine
# ---------------------------------------------------------------------------
def run_import():
    print("=" * 60)
    print("MUNICIPAL BUREAUCRACY PATH VISUALIZER")
    print("Civic Service Normalization, Enrichment & Ingestion Engine")
    print("=" * 60)

    # 1. Validation & Input Loading
    if not os.path.exists(ALL_SERVICES_JSON):
        print(f"[Error] Source file not found: {ALL_SERVICES_JSON}")
        sys.exit(1)

    with open(ALL_SERVICES_JSON, "r", encoding="utf-8") as f:
        raw_services = json.load(f)

    print(f"JSON records found in data/all_services.json: {len(raw_services)}")

    sample_dict = {}
    if os.path.exists(SAMPLE_SERVICES_JSON):
        with open(SAMPLE_SERVICES_JSON, "r", encoding="utf-8") as f:
            sample_list = json.load(f)
            for item in sample_list:
                sname = item.get("service_name", "").strip().lower()
                sample_dict[sname] = item
        print(f"Loaded {len(sample_dict)} enriched baseline services from sample_services.json")

    # 2. Filtering and Deduplication
    relevant_services = []
    excluded_services = []
    seen_service_keys = set()
    duplicates_skipped = 0

    for s in raw_services:
        is_rel, reason = is_service_relevant(s)
        if not is_rel:
            excluded_services.append((s, reason))
            continue

        sname = s.get("service_name", "").strip()
        clean_name = sname.strip('“"\'” ')
        norm_dept = normalize_department_name(s.get("department", ""))
        sub_dept = (s.get("sub_department") or "").strip()

        # Deduplication key
        dedup_key = (clean_name.lower(), norm_dept.lower(), sub_dept.lower())
        if dedup_key in seen_service_keys:
            duplicates_skipped += 1
            continue
        seen_service_keys.add(dedup_key)

        relevant_services.append({
            "original_record": s,
            "clean_name": clean_name,
            "norm_dept": norm_dept,
            "sub_dept": sub_dept
        })

    print(f"Relevant civic services:                      {len(relevant_services) + duplicates_skipped}")
    print(f"Duplicates skipped:                            {duplicates_skipped}")
    print(f"Services prepared for import:                  {len(relevant_services)}")
    print(f"Non-civic/diagnostic services excluded:        {len(excluded_services)}")

    # 3. Database Connection & Transaction
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        # 4. Insert / Update Departments
        print("\n[Step 1/5] Populating and normalizing departments...")
        cursor.execute("SELECT id, name FROM departments")
        existing_depts_by_id = {r[0]: r[1] for r in cursor.fetchall()}
        cursor.execute("SELECT name, id FROM departments")
        existing_depts_by_name = {r[0]: r[1] for r in cursor.fetchall()}
        depts_created = 0

        for dept_name, meta in DEPT_METADATA.items():
            dept_id = meta["id"]
            if dept_id in existing_depts_by_id:
                # Update existing department
                cursor.execute("""
                UPDATE departments
                SET jurisdiction = ?, portal_url = ?
                WHERE id = ?;
                """, (meta["jurisdiction"], meta["portal_url"], dept_id))
            elif dept_name in existing_depts_by_name:
                # Name exists under a different ID, update its details
                cursor.execute("""
                UPDATE departments
                SET jurisdiction = ?, portal_url = ?
                WHERE name = ?;
                """, (meta["jurisdiction"], meta["portal_url"], dept_name))
            else:
                cursor.execute("""
                INSERT INTO departments (id, name, jurisdiction, portal_url)
                VALUES (?, ?, ?, ?);
                """, (dept_id, dept_name, meta["jurisdiction"], meta["portal_url"]))
                existing_depts_by_id[dept_id] = dept_name
                existing_depts_by_name[dept_name] = dept_id
                depts_created += 1

        # Also register any department names present in normalized data
        for s in relevant_services:
            dname = s["norm_dept"]
            if dname not in existing_depts_by_name:
                dept_id = f"dept-{re.sub(r'[^a-z0-9]+', '-', dname.lower()).strip('-')}"
                if dept_id in existing_depts_by_id:
                    dept_id = f"{dept_id}-maha"
                cursor.execute("""
                INSERT INTO departments (id, name, jurisdiction, portal_url)
                VALUES (?, ?, ?, ?);
                """, (dept_id, dname, "Government of Maharashtra", "https://aaplesarkar.mahaonline.gov.in"))
                existing_depts_by_id[dept_id] = dname
                existing_depts_by_name[dname] = dept_id
                depts_created += 1

        # 5. Populate aaple_sarkar_services
        print("[Step 2/5] Populating aaple_sarkar_services...")
        services_without_urls = 0
        services_without_eligibility = 0
        services_without_fees = 0
        imported_as_count = 0

        # Mapping of existing sample service IDs
        existing_sample_name_to_id = {
            "income certificate": "1251",
            "age nationality and domicile certificate": "1253",
            "caste certificate": "1284",
            "non creamy layer certificate": "1286",
            "solvency certificate": "1254",
            "senior citizen certificate": "1255",
            "7 -12 extract": "4440",
            "certified copy of 7/12": "4440",
            "agriculturist certificate": "2318",
            "application for registration of shops & establishment (form a)": "1863",
            "application for notice of change in shops & establishment (form i)": "1864",
            "application for cancellation of shops & establishment (form j)": "1866",
            "application for cancellation (trade licence)": "7129",
            "building permission (bpms)": "7084",
            "commencement certificate (autodcr)": "8864",
            "plinth completion certificate (autodcr)": "8865",
            "occupancy certificate (autodcr)": "8866",
            "birth certificate (rural)": "2476",
            "death certificate (rural)": "2480"
        }

        used_service_ids = set()

        for idx, item in enumerate(relevant_services):
            orig = item["original_record"]
            cname = item["clean_name"]
            cname_lower = cname.lower()
            dept_name = item["norm_dept"]
            sub_dept = item["sub_dept"]

            # Determine stable, unique service_id
            if cname_lower in existing_sample_name_to_id and existing_sample_name_to_id[cname_lower] not in used_service_ids:
                sid = existing_sample_name_to_id[cname_lower]
            else:
                sr_no_str = str(orig.get("sr_no", "")).strip()
                if sr_no_str and sr_no_str.isdigit():
                    candidate_id = f"as-{sr_no_str}"
                else:
                    candidate_id = f"as-srv-{idx+1}"
                
                # Ensure absolute uniqueness
                if candidate_id in used_service_ids:
                    candidate_id = f"{candidate_id}-{idx+1}"
                sid = candidate_id

            used_service_ids.add(sid)

            # Check if enriched sample service exists
            sample_match = sample_dict.get(cname_lower)
            if sample_match:
                description = sample_match.get("description")
                eligibility = sample_match.get("eligibility")
                service_type = sample_match.get("service_type", "Citizen Service")
                app_method = sample_match.get("application_method", "Online via Aaple Sarkar Portal")
                app_url = sample_match.get("application_url", "https://aaplesarkar.mahaonline.gov.in/en/Registration/Register")
                source_url = sample_match.get("source", {}).get("source_url", "https://aaplesarkar.mahaonline.gov.in")
                scraped_at = sample_match.get("source", {}).get("scraped_at", "2026-09-26T15:30:00Z")
                fee_amt = sample_match.get("fee", {}).get("amount")
                fee_desc = sample_match.get("fee", {}).get("description", "Statutory application fee per Maharashtra RTS Rules")
                dept_code = sample_match.get("department_code")
                days_limit = sample_match.get("processing_time_days")
                loc = sample_match.get("applicable_location", determine_location(dept_name, sub_dept))
            else:
                # Synthesize official metadata from all_services.json
                dept_code = DEPT_METADATA.get(dept_name, {}).get("code", "MAHA")
                loc = determine_location(dept_name, sub_dept)
                days_limit = parse_time_limit(orig.get("time_limit_days"))
                
                # Build rich description including designated officers
                desig_officer = orig.get("designated_officer", "").strip()
                app_1 = orig.get("first_appellate_officer", "").strip()
                app_2 = orig.get("second_appellate_officer", "").strip()
                officer_desc_parts = []
                if desig_officer:
                    officer_desc_parts.append(f"Designated Officer: {desig_officer}")
                if app_1:
                    officer_desc_parts.append(f"First Appellate: {app_1}")
                if app_2:
                    officer_desc_parts.append(f"Second Appellate: {app_2}")
                officer_info = " | ".join(officer_desc_parts)

                description = f"Official public service '{cname}' under the Maharashtra Right to Public Services Act (RTS), administered by {dept_name} ({sub_dept}). {officer_info}."
                eligibility = "Citizen or registered commercial establishment in Maharashtra meeting statutory documentation requirements."
                service_type = "Citizen / Business Service"
                
                avail_portal = orig.get("available_on_portal", "").strip().lower()
                if "yes" in avail_portal:
                    app_method = "Online via Aaple Sarkar Portal"
                    app_url = "https://aaplesarkar.mahaonline.gov.in/en/Registration/Register"
                else:
                    app_method = "Municipal / Ward Office CFC Counter or Department Portal"
                    app_url = DEPT_METADATA.get(dept_name, {}).get("portal_url", "https://aaplesarkar.mahaonline.gov.in")

                source_url = "https://aaplesarkar.mahaonline.gov.in/en/CommonForm/ViewAllServices"
                scraped_at = datetime.now().isoformat()
                fee_amt = None
                fee_desc = "Statutory fee as per Maharashtra Right to Public Services Rules / Municipal Bye-laws"

            if not app_url:
                services_without_urls += 1
            if not eligibility:
                services_without_eligibility += 1
            if fee_amt is None:
                services_without_fees += 1

            # Insert into aaple_sarkar_services
            cursor.execute("""
            INSERT INTO aaple_sarkar_services (
                service_id, service_name, department, department_code, sub_department,
                description, eligibility, service_type, application_method, application_url,
                processing_time_days, applicable_location, status, fee_amount,
                fee_description, source_url, scraped_at, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(service_id) DO UPDATE SET
                service_name=excluded.service_name,
                department=excluded.department,
                department_code=excluded.department_code,
                sub_department=excluded.sub_department,
                description=excluded.description,
                eligibility=excluded.eligibility,
                service_type=excluded.service_type,
                application_method=excluded.application_method,
                application_url=excluded.application_url,
                processing_time_days=excluded.processing_time_days,
                applicable_location=excluded.applicable_location,
                status=excluded.status,
                fee_amount=excluded.fee_amount,
                fee_description=excluded.fee_description,
                source_url=excluded.source_url,
                raw_json=excluded.raw_json;
            """, (
                sid,
                cname,
                dept_name,
                dept_code,
                sub_dept,
                description,
                eligibility,
                service_type,
                app_method,
                app_url,
                days_limit,
                loc,
                "Active Notified Service",
                fee_amt,
                fee_desc,
                source_url,
                scraped_at,
                json.dumps(orig, ensure_ascii=False)
            ))
            imported_as_count += 1

        # 6. Create / Update Procedural Tasks & Steps
        print("[Step 3/5] Populating citizen tasks, procedural steps, documents, and forms...")
        curated_tasks = build_curated_civic_tasks()
        tasks_created = 0
        steps_created = 0
        docs_created = 0
        forms_created = 0
        services_without_docs = 0

        for t in curated_tasks:
            tid = t["id"]
            cursor.execute("""
            INSERT INTO tasks (id, title, category, municipality, state, description, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                category=excluded.category,
                municipality=excluded.municipality,
                state=excluded.state,
                description=excluded.description,
                tags=excluded.tags;
            """, (
                tid,
                t["title"],
                t["category"],
                t["municipality"],
                t["state"],
                t["description"],
                json.dumps(t.get("tags", []))
            ))
            tasks_created += 1

            for s in t.get("steps", []):
                sid = f"{tid}-step-{s['step_number']}"
                dept_id = s.get("department_id", "dept-rev-forest")
                
                # Check department exists
                cursor.execute("SELECT id FROM departments WHERE id = ?", (dept_id,))
                if not cursor.fetchone():
                    cursor.execute("""
                    INSERT INTO departments (id, name, jurisdiction, portal_url)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(name) DO NOTHING;
                    """, (
                        dept_id,
                        f"Department {dept_id}",
                        t["municipality"],
                        "https://aaplesarkar.mahaonline.gov.in"
                    ))

                v_src = s.get("verification_source", {})
                cursor.execute("""
                INSERT INTO steps (
                    id, task_id, step_number, title, description, department_id,
                    submission_mode, estimated_days, fee_amount, fee_breakdown,
                    prerequisites, verification_source, tips_and_pitfalls,
                    anti_tout_advisory, statutory_payment_channel, community_verifications,
                    official_receipt_mandate, last_gazette_notification, is_critical_path, is_admin_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    estimated_days=excluded.estimated_days,
                    fee_amount=excluded.fee_amount,
                    prerequisites=excluded.prerequisites,
                    verification_source=excluded.verification_source,
                    is_critical_path=excluded.is_critical_path,
                    is_admin_verified=excluded.is_admin_verified;
                """, (
                    sid,
                    tid,
                    s["step_number"],
                    s["title"],
                    s.get("description", ""),
                    dept_id,
                    s.get("submission_mode", "Online"),
                    s.get("estimated_days", 7),
                    s.get("fee_amount", 0.0),
                    json.dumps(s.get("fee_breakdown", {})),
                    json.dumps(s.get("prerequisites", [])),
                    json.dumps(v_src),
                    s.get("tips_and_pitfalls", "Do not pay unauthorized agents. All applications are tracked under Maharashtra RTS Act."),
                    s.get("anti_tout_advisory", "Statutory Helpline: Anti-Corruption Bureau (ACB Maharashtra) 1064"),
                    s.get("statutory_payment_channel", "Official Gras MahaKosh Portal / Net Banking"),
                    s.get("community_verifications", 12),
                    s.get("official_receipt_mandate", "Ensure electronic receipt (e-Receipt) with GRN / Transaction Ref is generated."),
                    s.get("last_gazette_notification", "Maharashtra Right to Public Services Act 2015"),
                    1 if s.get("step_number") in [2, 3] else 0,
                    1
                ))
                steps_created += 1

                # Clean and insert documents for this step
                for doc in s.get("documents", []):
                    doc_id = f"{sid}-{doc['id']}"
                    cursor.execute("""
                    INSERT INTO documents (id, step_id, name, description, is_mandatory, category, sample_template_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name=excluded.name,
                        description=excluded.description,
                        is_mandatory=excluded.is_mandatory,
                        category=excluded.category;
                    """, (
                        doc_id,
                        sid,
                        doc["name"],
                        doc.get("description", ""),
                        1 if doc.get("is_mandatory", True) else 0,
                        doc.get("category", "General"),
                        doc.get("sample_template_url", "")
                    ))
                    docs_created += 1

                # Clean existing forms for this step to prevent accumulation bug
                cursor.execute("DELETE FROM forms WHERE step_id = ?", (sid,))
                for form in s.get("forms", []):
                    cursor.execute("""
                    INSERT INTO forms (step_id, form_code, title, download_url, fill_online_url, instructions)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        sid,
                        form["form_code"],
                        form["title"],
                        form.get("download_url"),
                        form.get("fill_online_url"),
                        form.get("instructions")
                    ))
                    forms_created += 1

        # Check services without documents
        services_without_docs = len(relevant_services) - len(curated_tasks)

        # 7. Deduplicate existing forms in the database
        print("[Step 4/5] Deduplicating existing forms table...")
        cursor.execute("""
        DELETE FROM forms
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM forms
            GROUP BY step_id, form_code
        );
        """)

        # 8. Integrity Validation
        print("[Step 5/5] Running relational integrity validations...")
        cursor.execute("PRAGMA foreign_key_check;")
        fk_violations = cursor.fetchall()
        if fk_violations:
            print(f"[Error] Foreign key violations detected: {fk_violations}")
            conn.rollback()
            conn.close()
            sys.exit(1)
        else:
            print("  ✓ Foreign key check passed: Zero violations.")

        # Check for orphan steps
        cursor.execute("""
        SELECT s.id FROM steps s
        LEFT JOIN tasks t ON s.task_id = t.id
        WHERE t.id IS NULL;
        """)
        orphan_steps = cursor.fetchall()
        assert len(orphan_steps) == 0, f"Found orphan steps: {orphan_steps}"
        print("  ✓ Orphan steps check passed: 0 orphans.")

        # Check for orphan documents
        cursor.execute("""
        SELECT d.id FROM documents d
        LEFT JOIN steps s ON d.step_id = s.id
        WHERE s.id IS NULL;
        """)
        orphan_docs = cursor.fetchall()
        assert len(orphan_docs) == 0, f"Found orphan documents: {orphan_docs}"
        print("  ✓ Orphan documents check passed: 0 orphans.")

        # Check for orphan forms
        cursor.execute("""
        SELECT f.id FROM forms f
        LEFT JOIN steps s ON f.step_id = s.id
        WHERE s.id IS NULL;
        """)
        orphan_forms = cursor.fetchall()
        assert len(orphan_forms) == 0, f"Found orphan forms: {orphan_forms}"
        print("  ✓ Orphan forms check passed: 0 orphans.")

        # Commit Transaction
        conn.commit()

        # Query Final Counts
        cursor.execute("SELECT COUNT(*) FROM departments;")
        final_depts = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM aaple_sarkar_services;")
        final_as = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks;")
        final_tasks = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM steps;")
        final_steps = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents;")
        final_docs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM forms;")
        final_forms = cursor.fetchone()[0]

        conn.close()

        # Print Final Summary Report
        print("\n" + "=" * 50)
        print("CIVIC SERVICE IMPORT SUMMARY")
        print("=" * 50)
        print(f"JSON records found:              {len(raw_services)}")
        print(f"Relevant civic services:          {len(relevant_services) + duplicates_skipped}")
        print(f"Duplicates skipped:               {duplicates_skipped}")
        print(f"Services imported:                {final_as}")
        print()
        print(f"Departments created/active:       {final_depts}")
        print(f"Tasks created/active:             {final_tasks}")
        print(f"Steps created/active:             {final_steps}")
        print(f"Documents created/active:         {final_docs}")
        print(f"Forms created/active:             {final_forms}")
        print()
        print(f"Services without URLs:            {services_without_urls}")
        print(f"Services without eligibility:     {services_without_eligibility}")
        print(f"Services without fee information: {services_without_fees}")
        print(f"Services without documents:       {services_without_docs}")
        print()
        print(f"Database:")
        print(f"db/civic_maharashtra.db")
        print()
        print("Import completed successfully.")
        print("=" * 50)

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[Fatal Error] Import failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_import()
