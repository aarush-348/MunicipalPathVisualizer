"""
Natural Language Query Matcher for Civic Task Navigator.
Matches user search queries to verified PostgreSQL service records.
Ensures zero hallucinations: if no verified service matches, returns None.
"""
import re
from typing import Tuple, Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from simple_app.db import get_connection_params

KNOWN_LOCATIONS = [
    "Thane", "Pune", "Mumbai", "Nagpur", "Nashik", "Aurangabad",
    "Chhatrapati Sambhajinagar", "Navi Mumbai", "Solapur", "Kolhapur",
    "Amravati", "Nanded", "Jalgaon", "Akola", "Latur", "Dhule", "Ahmednagar",
    "Chandrapur", "Parbhani", "Satara", "Palghar", "Raigad", "Ratnagiri",
    "Sindhudurg", "Sangli", "Beed", "Bhandara", "Gondia", "Gadchiroli",
    "Hingoli", "Jalna", "Osmanabad", "Dharashiv", "Wardha", "Washim",
    "Yavatmal", "Maharashtra"
]

# Canonical civic aliases mapping to official service names
SYNONYM_MAP = {
    "income": "Income Certificate",
    "income certificate": "Income Certificate",
    "income cert": "Income Certificate",
    "aavak": "Income Certificate",
    "salary certificate": "Income Certificate",
    
    "caste": "Caste Certificate",
    "caste certificate": "Caste Certificate",
    "caste cert": "Caste Certificate",
    "jaat": "Caste Certificate",
    
    "domicile": "Age Nationality and Domicile Certificate",
    "nationality": "Age Nationality and Domicile Certificate",
    "age nationality": "Age Nationality and Domicile Certificate",
    "residence certificate": "Residence Certificate",
    "domicile certificate": "Age Nationality and Domicile Certificate",
    
    "non creamy layer": "Non Creamy Layer Certificate",
    "non-creamy layer": "Non Creamy Layer Certificate",
    "creamy layer": "Non Creamy Layer Certificate",
    "ncl": "Non Creamy Layer Certificate",
    
    "small business": "Application for Registration of Shops & Establishment (Form A)",
    "business": "Application for Registration of Shops & Establishment (Form A)",
    "register business": "Application for Registration of Shops & Establishment (Form A)",
    "shop": "Application for Registration of Shops & Establishment (Form A)",
    "shops": "Application for Registration of Shops & Establishment (Form A)",
    "shops and establishment": "Application for Registration of Shops & Establishment (Form A)",
    "gumasta": "Application for Registration of Shops & Establishment (Form A)",
    "trade licence": "Application for Cancellation (Trade Licence)",
    "trade license": "Application for Cancellation (Trade Licence)",
    
    "7 12": "7 -12 Extract",
    "7/12": "7 -12 Extract",
    "7-12": "7 -12 Extract",
    "satbara": "7 -12 Extract",
    "land extract": "7 -12 Extract",
    
    "birth": "Birth Certificate (Rural)",
    "birth certificate": "Birth Certificate (Rural)",
    "janma": "Birth Certificate (Rural)",
    
    "death": "Death Certificate (Rural)",
    "death certificate": "Death Certificate (Rural)",
    "mrityu": "Death Certificate (Rural)",
    
    "senior citizen": "Senior Citizen Certificate",
    "senior citizen certificate": "Senior Citizen Certificate",
    
    "solvency": "Solvency Certificate",
    "solvency certificate": "Solvency Certificate",
    
    "agriculturist": "Agriculturist Certificate",
    "farmer certificate": "Agriculturist Certificate",
    
    "building permission": "Building Permission (BPMS)",
    "bpms": "Building Permission (BPMS)",
    
    "commencement": "Commencement Certificate (AutoDCR)",
    "commencement certificate": "Commencement Certificate (AutoDCR)",
    "plinth": "Plinth Completion Certificate (AutoDCR)",
    "occupancy": "Occupancy Certificate (AutoDCR)",
    "occupancy certificate": "Occupancy Certificate (AutoDCR)"
}

# Stopwords to clean user queries
STOPWORDS = {
    "steps", "step", "to", "register", "for", "an", "a", "the", "how", "can",
    "i", "get", "need", "do", "apply", "in", "of", "please", "want", "require",
    "process", "procedure", "application", "form", "me", "my", "give", "show",
    "what", "is", "are", "certificate", "tell", "way", "guide", "roadmap"
}

def extract_location(text: str) -> Optional[str]:
    """Extracts known Maharashtra administrative locations from text."""
    if not text:
        return None
    for loc in KNOWN_LOCATIONS:
        pattern = r'\b' + re.escape(loc) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            return loc
    return None

def clean_query_text(text: str) -> str:
    """Removes punctuation and common conversational stopwords."""
    cleaned = re.sub(r'[^\w\s\/-]', ' ', text.lower())
    words = cleaned.split()
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 1]
    return " ".join(filtered)

def match_service_from_query(query: str, location_input: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], str, float]:
    """
    Intelligently matches a natural language query against verified PostgreSQL services.
    
    Returns:
        (service_row, detected_location, confidence_score)
        If no verified match found, service_row will be None.
    """
    if not query or not query.strip():
        return None, location_input or "Maharashtra State", 0.0

    raw_query = query.strip()
    query_lower = raw_query.lower()

    # Determine location: explicit input takes precedence over extracted
    detected_loc = location_input.strip() if (location_input and location_input.strip()) else extract_location(raw_query)
    final_location = detected_loc if detected_loc else "Maharashtra State"

    conn = psycopg2.connect(**get_connection_params())
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Step 1: Direct Alias / Synonym Intent Matching
        matched_target = None
        for key in sorted(SYNONYM_MAP.keys(), key=lambda x: -len(x)):
            pattern = r'\b' + re.escape(key) + r'\b'
            if re.search(pattern, query_lower):
                matched_target = SYNONYM_MAP[key]
                break

        if matched_target:
            cur.execute(
                "SELECT * FROM services WHERE service_name ILIKE %s LIMIT 1;",
                (f"%{matched_target}%",)
            )
            row = cur.fetchone()
            if row:
                return dict(row), final_location, 1.0

        # Step 2: PostgreSQL Full-Text Search
        cleaned = clean_query_text(raw_query)
        if cleaned:
            cur.execute("""
                SELECT s.*, 
                       ts_rank(to_tsvector('english', s.service_name || ' ' || COALESCE(s.description, '')), 
                               plainto_tsquery('english', %s)) as rank
                FROM services s
                WHERE to_tsvector('english', s.service_name || ' ' || COALESCE(s.description, '')) @@ plainto_tsquery('english', %s)
                ORDER BY rank DESC
                LIMIT 1;
            """, (cleaned, cleaned))
            row = cur.fetchone()
            if row and row["rank"] > 0.03:
                return dict(row), final_location, float(row["rank"])

        # Step 3: Exact Word Boundary Substring Match
        keywords = [w for w in cleaned.split() if len(w) >= 4]
        for kw in keywords:
            cur.execute("""
                SELECT * FROM services 
                WHERE service_name ~* %s
                LIMIT 1;
            """, (r'\y' + re.escape(kw) + r'\y',))
            row = cur.fetchone()
            if row:
                return dict(row), final_location, 0.75

        # No verified match found in PostgreSQL
        return None, final_location, 0.0

    finally:
        cur.close()
        conn.close()
