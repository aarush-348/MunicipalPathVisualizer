"""
Data cleaning and normalization logic for Aaple Sarkar portal data.
"""
import re
from typing import Optional, Dict, Any, Tuple

# Canonical department name mapping
DEPARTMENT_CANONICAL_MAP = {
    "REVDEPT": "Revenue and Forest Department",
    "REVENUE DEPARTMENT": "Revenue and Forest Department",
    "REVENUE AND FOREST DEPARTMENT": "Revenue and Forest Department",
    "UDD": "Urban Development Department",
    "DEPARTMENT OF URBAN DEVELOPMENT": "Urban Development Department",
    "URBAN DEVELOPMENT DEPARTMENT": "Urban Development Department",
    "LABDEPT": "Industries, Energy and Labour Department",
    "INDUSTRIES, ENERGY AND LABOUR DEPARTMENT": "Industries, Energy and Labour Department",
    "INDUSTRY, ENERGY AND LABOR DEPARTMENT": "Industries, Energy and Labour Department",
    "EPRI": "Rural Development and Panchayat Raj Department",
    "RURAL DEVELOPMENT AND PANCHAYAT RAJ DEPARTMENT": "Rural Development and Panchayat Raj Department",
    "ROFDEPT": "Law and Judiciary Department",
    "LAW AND JUDICIARY DEPARTMENT": "Law and Judiciary Department",
    "PHDDEPT": "Public Health Department",
    "PUBLIC HEALTH DEPARTMENT": "Public Health Department",
    "HDEPT": "Home Department",
    "HOME DEPARTMENT": "Home Department",
    "SJDDEPT": "Social Justice and Special Assistance Department",
    "SOCIAL JUSTICE AND SPECIAL ASSISTANCE DEPARTMENT": "Social Justice and Special Assistance Department",
    "HEDDEPT": "Higher and Technical Education Department",
    "HIGHER AND TECHNICAL EDUCATION DEPARTMENT": "Higher and Technical Education Department",
    "AGRI": "Agriculture Department",
    "AGRICULTURE": "Agriculture Department",
    "AGRICULTURE, ANIMAL HUSBANDRY, DAIRY AND FISHERIES DEPARTMENT": "Agriculture, Animal Husbandry, Dairy and Fisheries Department",
    "DHDEPT": "Department of Animal Husbandry, Dairying and Fisheries",
    "DEPARTMENT OF ANIMAL HUSBANDRY ,DAIRYING & FISHERIES": "Department of Animal Husbandry, Dairying and Fisheries",
    "DOCDEPT": "Department of Co-Operation Marketing and Textiles",
    "DEPARTMENT OF CO-OPERATION MARKETING AND TEXTILES": "Department of Co-Operation Marketing and Textiles",
    "FCCPDEPT": "Food, Civil Supplies and Consumer Protection Department",
    "FOOD, CIVIL SUPPLIES AND CONSUMER PROTECTION DEPARTMENT": "Food, Civil Supplies and Consumer Protection Department",
    "FOOD CIVIL SUPPLIES AND CONSUMER PROTECTION DEPARTMENT": "Food, Civil Supplies and Consumer Protection Department",
    "MHADADEPT": "Maharashtra Housing and Area Development Authority",
    "MAHARASHTRA HOUSING AND AREA DEVELOPMENT AUTHORITY": "Maharashtra Housing and Area Development Authority",
    "MPCBDEPT": "Maharashtra Pollution Control Board",
    "MAHARASHTRA POLLUTION CONTROL BOARD": "Maharashtra Pollution Control Board",
    "MEDDEPT": "Medical Education and Drugs Department",
    "MEDICAL EDUCATION AND DRUG DEPARTMENT": "Medical Education and Drugs Department",
    "DEPARTMENT OF MEDICAL EDUCATION AND DRUGS": "Medical Education and Drugs Department",
    "TOURISMDEPT": "Tourism and Cultural Affairs Department",
    "TOURISM": "Tourism and Cultural Affairs Department",
    "TOURISM AND CULTURAL AFFAIRS DEPARTMENT": "Tourism and Cultural Affairs Department",
    "TDRDEPT": "Transport Department",
    "TRANSPORT": "Transport Department",
    "TRANSPORTATION": "Transport Department",
    "TRANSPORT DEPARTMENT": "Transport Department",
    "WRD": "Water Resources Department",
    "WATER RESOURCES DEPARTMENT": "Water Resources Department",
    "WSSD": "Water Supply and Sanitation Department",
    "WATER SUPPLY AND SANITATION DEPARTMENT": "Water Supply and Sanitation Department",
    "DEPARTMENT OF WATER, SUPPLY AND SANITATION": "Water Supply and Sanitation Department",
    "WCDDEPT": "Women and Child Development Department",
    "WOMEN AND CHILD DEVELOPMENT": "Women and Child Development Department"
}

def clean_text(text: Optional[str]) -> Optional[str]:
    """Clean and normalize whitespace, remove unprintable chars."""
    if not text:
        return None
    # Replace non-breaking spaces and tabs
    cleaned = text.replace('\xa0', ' ').replace('\r', ' ').replace('\n', ' ')
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned if cleaned else None

def normalize_department_name(dept_raw: Optional[str]) -> str:
    """Normalize department name into standard government nomenclature."""
    if not dept_raw:
        return "Unknown Department"
    cleaned = clean_text(dept_raw).upper()
    return DEPARTMENT_CANONICAL_MAP.get(cleaned, clean_text(dept_raw))

def normalize_service_name(service_raw: Optional[str]) -> str:
    """Clean service name, remove unwanted trailing prefixes."""
    cleaned = clean_text(service_raw)
    if not cleaned:
        return "Unknown Service"
    # Remove leading numbering like "1) ", "A) "
    cleaned = re.sub(r'^[0-9A-Za-z]+[\.\)]\s*', '', cleaned)
    # Remove redundant "(Free)" or double spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def parse_time_limit_days(time_raw: Optional[str]) -> Tuple[Optional[int], Optional[str]]:
    """
    Parse statutory SLA days.
    Returns (days_int, raw_text).
    """
    if not time_raw:
        return (None, None)
    raw = clean_text(time_raw)
    # Match digits
    m = re.search(r'(\d+)', raw)
    if m:
        try:
            return (int(m.group(1)), raw)
        except ValueError:
            pass
    return (None, raw)

def clean_document_name(doc_raw: Optional[str]) -> Tuple[str, bool, Optional[str]]:
    """
    Cleans document string.
    Returns (clean_document_name, is_mandatory, notes).
    """
    if not doc_raw:
        return ("Unknown Document", False, None)
    raw = clean_text(doc_raw)
    # Strip leading index like "1) ", "28) "
    doc_name = re.sub(r'^\d+[\)\.]\s*', '', raw).strip()
    return (doc_name, True, None)

def extract_document_category_rule(category_text: str) -> Tuple[str, bool, Optional[int]]:
    """
    Parse category like 'Proof of Identity (Any -1)'
    Returns (category_name, is_mandatory_group, required_count)
    """
    cat_clean = clean_text(category_text) or "General Supporting Documents"
    # Check for (Any -X) pattern
    m = re.search(r'\(any\s*[-–:]?\s*(\d+)\)', cat_clean, re.IGNORECASE)
    if m:
        count = int(m.group(1))
        base_cat = re.sub(r'\(any\s*[-–:]?\s*\d+\)', '', cat_clean, flags=re.IGNORECASE).strip()
        return (base_cat, True, count)
    return (cat_clean, False, 1)
