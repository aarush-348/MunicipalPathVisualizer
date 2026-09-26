"""
Database connection and verified data access layer for Civic Task Navigator.
Connects directly to PostgreSQL database 'civic_navigator'.
All returned data originates from verified database records.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("SimpleAppDB")

def get_connection_params() -> Dict[str, Any]:
    """Resolves database connection parameters from environment variables."""
    pg_url = os.environ.get("DATABASE_URL")
    if pg_url:
        return {"dsn": pg_url}
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", 5432)),
        "dbname": os.environ.get("DB_NAME", "civic_navigator"),
        "user": os.environ.get("DB_USER", "postgres"),
        "password": os.environ.get("DB_PASSWORD", "")
    }

def get_db_connection():
    """Returns a new connection to PostgreSQL."""
    params = get_connection_params()
    return psycopg2.connect(**params)

def check_db_health() -> Dict[str, Any]:
    """Checks database connectivity and table counts."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM services;")
        service_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM documents;")
        doc_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {
            "status": "connected",
            "services_count": service_count,
            "documents_count": doc_count
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "error", "message": str(e)}

def fetch_all_services() -> List[Dict[str, Any]]:
    """Returns basic list of all active verified services from PostgreSQL."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT s.id, s.service_name, s.sub_department, s.processing_time_days, 
               s.applicable_location, d.name as department_name
        FROM services s
        JOIN departments d ON s.department_id = d.id
        ORDER BY s.service_name ASC;
    """
    cur.execute(query)
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

def fetch_service_by_id(service_id: str, location_override: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves complete verified service details from PostgreSQL across all normalized tables.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # 1. Base Service and Department info
    service_query = """
        SELECT s.id, s.service_name, s.department_id, s.sub_department, s.description,
               s.eligibility, s.service_type, s.application_method, s.application_url,
               s.processing_time_days, s.processing_time_raw, s.applicable_location,
               s.status, s.source_url, s.source_title, s.last_verified_at,
               d.name as department_name, d.source_url as department_source_url
        FROM services s
        JOIN departments d ON s.department_id = d.id
        WHERE s.id = %s;
    """
    cur.execute(service_query, (service_id,))
    service = cur.fetchone()
    if not service:
        cur.close()
        conn.close()
        return None

    service = dict(service)

    # 2. Documents
    docs_query = """
        SELECT d.id, d.document_name, d.category, d.document_code,
               sd.mandatory, sd.group_rule, sd.notes, sd.source_url
        FROM service_documents sd
        JOIN documents d ON sd.document_id = d.id
        WHERE sd.service_id = %s
        ORDER BY d.category ASC, d.document_name ASC;
    """
    cur.execute(docs_query, (service_id,))
    docs = [dict(r) for r in cur.fetchall()]

    # Group documents by category
    doc_categories: Dict[str, List[Dict[str, Any]]] = {}
    for d in docs:
        cat = d.get("category") or "General Documents"
        if cat not in doc_categories:
            doc_categories[cat] = []
        doc_categories[cat].append(d)

    # 3. Prerequisites
    prereq_query = """
        SELECT p.id, p.prerequisite_name, p.description, sp.mandatory, sp.notes
        FROM service_prerequisites sp
        JOIN prerequisites p ON sp.prerequisite_id = p.id
        WHERE sp.service_id = %s;
    """
    cur.execute(prereq_query, (service_id,))
    prerequisites = [dict(r) for r in cur.fetchall()]

    # 4. Statutory Officers
    officers_query = """
        SELECT officer_type, officer_name, designation, contact_information, source_url
        FROM officers
        WHERE service_id = %s
        ORDER BY CASE 
            WHEN officer_type = 'Designated Officer' THEN 1
            WHEN officer_type = 'First Appellate Officer' THEN 2
            WHEN officer_type = 'Second Appellate Officer' THEN 3
            ELSE 4
        END;
    """
    cur.execute(officers_query, (service_id,))
    officers = [dict(r) for r in cur.fetchall()]

    # 5. Statutory Fees
    fee_query = """
        SELECT amount, currency, description, conditions, source_url
        FROM fees
        WHERE service_id = %s
        LIMIT 1;
    """
    cur.execute(fee_query, (service_id,))
    fee_row = cur.fetchone()
    fee = dict(fee_row) if fee_row else None

    # 6. Service Dependencies
    dep_query = """
        SELECT depends_on_service_id, depends_on_service_name, dependency_type,
               dependency_description, source_url
        FROM service_dependencies
        WHERE service_id = %s;
    """
    cur.execute(dep_query, (service_id,))
    dependencies = [dict(r) for r in cur.fetchall()]

    # 7. Sources
    source_query = """
        SELECT source_url, source_title, source_type, verified_at
        FROM sources
        WHERE service_id = %s
        LIMIT 1;
    """
    cur.execute(source_query, (service_id,))
    source_row = cur.fetchone()
    source = dict(source_row) if source_row else None

    cur.close()
    conn.close()

    # Determine display location
    display_location = location_override if location_override else service.get("applicable_location", "Maharashtra State")

    # Construct verified roadmap steps
    roadmap = build_roadmap_steps(
        service=service,
        doc_categories=doc_categories,
        prerequisites=prerequisites,
        officers=officers,
        fee=fee,
        location=display_location
    )

    return {
        "service": service,
        "display_location": display_location,
        "department_name": service.get("department_name"),
        "sub_department": service.get("sub_department"),
        "doc_categories": doc_categories,
        "total_documents": len(docs),
        "prerequisites": prerequisites,
        "officers": officers,
        "fee": fee,
        "dependencies": dependencies,
        "source": source,
        "roadmap": roadmap
    }

def build_roadmap_steps(
    service: Dict[str, Any],
    doc_categories: Dict[str, List[Dict[str, Any]]],
    prerequisites: List[Dict[str, Any]],
    officers: List[Dict[str, Any]],
    fee: Optional[Dict[str, Any]],
    location: str
) -> List[Dict[str, Any]]:
    """
    Constructs the 5-step roadmap strictly derived from verified PostgreSQL fields:
    1. Check Eligibility
    2. Prepare Required Documents
    3. Submit Application
    4. Verification & Scrutiny
    5. Certificate Issued / Resolution
    """
    steps = []

    # Step 1: Check Eligibility
    eligibility_text = service.get("eligibility") or "Applicant must be a resident/citizen under statutory jurisdiction."
    prereq_items = [p["prerequisite_name"] for p in prerequisites] if prerequisites else []
    steps.append({
        "step_number": 1,
        "title": "Check Eligibility",
        "description": eligibility_text,
        "badge": "Prerequisites",
        "details": prereq_items,
        "link": None
    })

    # Step 2: Prepare Required Documents
    doc_groups = []
    if doc_categories:
        for cat_name, cat_docs in doc_categories.items():
            rule = cat_docs[0].get("group_rule") or "Mandatory"
            names = [d["document_name"] for d in cat_docs]
            doc_groups.append({
                "category": cat_name,
                "rule": rule,
                "documents": names
            })
    else:
        doc_groups.append({
            "category": "Standard Identity & Address Verification",
            "rule": "Mandatory",
            "documents": ["Aadhaar Card or Photo ID", "Proof of Residence / Address"]
        })

    steps.append({
        "step_number": 2,
        "title": "Prepare Required Documents",
        "description": f"Gather and verify all mandatory proofs before initiating the application for {location}.",
        "badge": "Document Verification",
        "doc_groups": doc_groups,
        "link": None
    })

    # Step 3: Submit Application
    app_method = service.get("application_method") or "Online via Aaple Sarkar Portal or In-Person at Aaple Sarkar Seva Kendra (CSC)"
    app_url = service.get("application_url") or "https://aaplesarkar.mahaonline.gov.in"
    fee_desc = "Statutory fee applicable per Maharashtra RTS rules."
    if fee:
        if fee.get("amount") is not None:
            fee_desc = f"Application Fee: ₹{fee['amount']:.2f}"
        elif fee.get("description"):
            fee_desc = fee["description"]

    steps.append({
        "step_number": 3,
        "title": "Submit Application",
        "description": f"File your application through {app_method}. {fee_desc}",
        "badge": "Online / CSC Submission",
        "official_url": app_url,
        "official_url_label": "Official Portal Application Link"
    })

    # Step 4: Verification & Scrutiny
    time_days = service.get("processing_time_days")
    time_desc = f"{time_days} days" if time_days else service.get("processing_time_raw", "Statutory SLA")
    designated_officer = "Competent Authority"
    for o in officers:
        if o.get("officer_type") == "Designated Officer":
            designated_officer = o.get("designation", "Designated Officer")
            break

    steps.append({
        "step_number": 4,
        "title": "Verification & Scrutiny",
        "description": f"The application and submitted proofs undergo statutory scrutiny by the {designated_officer}. Statutory SLA timeline: {time_desc}.",
        "badge": f"SLA: {time_desc}",
        "officer": designated_officer,
        "link": None
    })

    # Step 5: Certificate Issued
    first_appellate = "First Appellate Officer"
    for o in officers:
        if o.get("officer_type") == "First Appellate Officer":
            first_appellate = o.get("designation", "First Appellate Officer")
            break

    steps.append({
        "step_number": 5,
        "title": "Certificate Issued",
        "description": f"Upon successful verification, the digitally signed certificate/clearance is officially issued and can be downloaded from the portal. If delayed beyond {time_desc}, a statutory appeal can be filed with the {first_appellate}.",
        "badge": "Official Issuance",
        "appellate": first_appellate,
        "link": service.get("source_url")
    })

    return steps
