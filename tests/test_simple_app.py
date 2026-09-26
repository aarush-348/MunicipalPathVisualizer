"""
Integration tests for Civic Task Navigator (simple_app).
Tests PostgreSQL connection, table schemas, seed records, natural language query matching,
roadmap generation, official URLs, and 404/not-found handling.
"""
import os
import sys

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2.extras import RealDictCursor
import httpx
from simple_app.db import get_connection_params, check_db_health, fetch_service_by_id
from simple_app.matcher import match_service_from_query

def test_postgresql_connection():
    """Verify PostgreSQL connects and database civic_navigator exists."""
    params = get_connection_params()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute("SELECT current_database();")
    db_name = cur.fetchone()[0]
    assert db_name == "civic_navigator"
    cur.close()
    conn.close()

def test_required_tables_exist():
    """Verify all 10 schema tables exist in PostgreSQL."""
    expected_tables = [
        "departments", "services", "documents", "service_documents",
        "prerequisites", "service_prerequisites", "officers", "fees",
        "sources", "service_dependencies"
    ]
    conn = psycopg2.connect(**get_connection_params())
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    existing_tables = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    for table in expected_tables:
        assert table in existing_tables, f"Missing table: {table}"

def test_seed_data_records():
    """Verify seed data has been inserted into PostgreSQL."""
    conn = psycopg2.connect(**get_connection_params())
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM services;")
    services_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM documents;")
    documents_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM departments;")
    dept_count = cur.fetchone()[0]
    cur.close()
    conn.close()

    assert services_count >= 18, f"Expected at least 18 services, got {services_count}"
    assert documents_count > 0, f"Expected documents, got {documents_count}"
    assert dept_count >= 3, f"Expected departments, got {dept_count}"

def test_income_certificate_query_matching():
    """Verify 'Steps to register for an income certificate in Thane' matches Income Certificate."""
    query = "Steps to register for an income certificate in Thane"
    service_row, location, conf = match_service_from_query(query)
    assert service_row is not None
    assert service_row["id"] == "1251"
    assert service_row["service_name"] == "Income Certificate"
    assert location == "Thane"
    assert conf > 0.5

def test_income_certificate_roadmap_and_official_urls():
    """Verify full roadmap and official URLs for Income Certificate."""
    detail = fetch_service_by_id("1251", "Thane, Maharashtra")
    assert detail is not None
    assert detail["service"]["service_name"] == "Income Certificate"
    assert detail["display_location"] == "Thane, Maharashtra"
    assert detail["department_name"] == "Revenue and Forest Department"

    # Verify official URLs
    assert detail["service"]["application_url"].startswith("http")
    assert detail["service"]["source_url"].startswith("http")

    # Verify roadmap has 5 steps
    roadmap = detail["roadmap"]
    assert len(roadmap) == 5
    assert roadmap[0]["title"] == "Check Eligibility"
    assert roadmap[1]["title"] == "Prepare Required Documents"
    assert roadmap[2]["title"] == "Submit Application"
    assert roadmap[3]["title"] == "Verification & Scrutiny"
    assert roadmap[4]["title"] == "Certificate Issued"

    # Verify document groups exist in Step 2
    step2 = roadmap[1]
    assert "doc_groups" in step2
    cat_names = [g["category"] for g in step2["doc_groups"]]
    assert "Proof of Identity" in cat_names
    assert "Proof of Address" in cat_names
    assert "Proof of Income" in cat_names

def test_api_search_endpoint():
    """Verify the running API server /api/search endpoint."""
    with httpx.Client(base_url="http://127.0.0.1:8080") as client:
        # 1. Income Certificate search
        resp = client.get("/api/search", params={"q": "Steps to register for an income certificate in Thane", "location": "Thane"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["found"] is True
        assert data["data"]["service"]["service_name"] == "Income Certificate"
        assert len(data["data"]["roadmap"]) == 5

        # 2. Unknown service query produces not found message
        resp_unknown = client.get("/api/search", params={"q": "How to build a space station"})
        assert resp_unknown.status_code == 200
        data_unknown = resp_unknown.json()
        assert data_unknown["found"] is False
        assert "We could not find sufficient verified information" in data_unknown["message"]
        assert len(data_unknown["available_services"]) > 0

if __name__ == "__main__":
    test_postgresql_connection()
    test_required_tables_exist()
    test_seed_data_records()
    test_income_certificate_query_matching()
    test_income_certificate_roadmap_and_official_urls()
    test_api_search_endpoint()
    print("All tests passed successfully!")
