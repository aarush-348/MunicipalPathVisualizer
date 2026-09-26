"""
PostgreSQL Seed and Ingestion Script.
Reads scraped data from data/sample_services.json and ingests into normalized PostgreSQL tables.
Also generates standalone seed_data.sql for direct psql execution.
"""
import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PostgresSeeder")

def escape_sql(val: Any) -> str:
    """Escapes string values for SQL literals."""
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    # String escaping
    s = str(val).replace("'", "''")
    return f"'{s}'"

def generate_sql_statements(data: List[Dict[str, Any]]) -> str:
    """Generates idempotent PostgreSQL INSERT / UPSERT SQL script."""
    sql_lines = [
        "-- ====================================================================",
        "-- Auto-generated PostgreSQL Seed Data from Official Aaple Sarkar Scrape",
        f"-- Total Services: {len(data)}",
        "-- ====================================================================\n",
        "BEGIN;\n"
    ]

    # 1. Insert Departments
    sql_lines.append("-- 1. Ingest Departments")
    departments = {}
    for r in data:
        dept_name = r["department"]
        dept_code = r.get("department_code", "")
        source_url = r["source"]["source_url"]
        if dept_name not in departments:
            departments[dept_name] = {
                "name": dept_name,
                "code": dept_code,
                "source_url": source_url
            }

    for d in departments.values():
        sql_lines.append(
            f"INSERT INTO departments (name, department_code, source_url) "
            f"VALUES ({escape_sql(d['name'])}, {escape_sql(d['code'])}, {escape_sql(d['source_url'])}) "
            f"ON CONFLICT (name) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;"
        )

    # 2. Insert Services
    sql_lines.append("\n-- 2. Ingest Services")
    for r in data:
        dept_name = r["department"]
        sql_lines.append(
            f"INSERT INTO services (id, service_name, department_id, sub_department, description, eligibility, "
            f"service_type, application_method, application_url, processing_time_days, processing_time_raw, "
            f"applicable_location, status, source_url, source_title, last_scraped_at, last_verified_at) "
            f"VALUES ({escape_sql(r['service_id'])}, {escape_sql(r['service_name'])}, "
            f"(SELECT id FROM departments WHERE name = {escape_sql(dept_name)}), "
            f"{escape_sql(r['sub_department'])}, {escape_sql(r['description'])}, {escape_sql(r['eligibility'])}, "
            f"{escape_sql(r['service_type'])}, {escape_sql(r['application_method'])}, {escape_sql(r['application_url'])}, "
            f"{escape_sql(r['processing_time_days'])}, {escape_sql(r['processing_time_raw'])}, "
            f"{escape_sql(r['applicable_location'])}, {escape_sql(r['status'])}, {escape_sql(r['source']['source_url'])}, "
            f"{escape_sql(r['source']['source_title'])}, {escape_sql(r['source']['scraped_at'])}::timestamptz, "
            f"{escape_sql(r['source']['last_verified_at'])}::timestamptz) "
            f"ON CONFLICT (id) DO UPDATE SET "
            f"service_name = EXCLUDED.service_name, "
            f"processing_time_days = EXCLUDED.processing_time_days, "
            f"last_verified_at = EXCLUDED.last_verified_at;"
        )

    # 3. Ingest Documents & Service Documents
    sql_lines.append("\n-- 3. Ingest Documents & Service Documents")
    for r in data:
        sid = r["service_id"]
        for doc in r.get("documents", []):
            doc_name = doc["document_name"]
            category = doc.get("category", "General")
            code = doc.get("document_code")
            url = doc.get("source_url")
            mandatory = doc.get("is_mandatory", True)
            group_rule = doc.get("group_rule")

            sql_lines.append(
                f"INSERT INTO documents (document_code, document_name, category) "
                f"VALUES ({escape_sql(code)}, {escape_sql(doc_name)}, {escape_sql(category)}) "
                f"ON CONFLICT (document_name, category) DO NOTHING;"
            )

            sql_lines.append(
                f"INSERT INTO service_documents (service_id, document_id, mandatory, group_rule, source_url) "
                f"VALUES ({escape_sql(sid)}, "
                f"(SELECT id FROM documents WHERE document_name = {escape_sql(doc_name)} AND category = {escape_sql(category)} LIMIT 1), "
                f"{escape_sql(mandatory)}, {escape_sql(group_rule)}, {escape_sql(url)}) "
                f"ON CONFLICT (service_id, document_id) DO NOTHING;"
            )

    # 4. Ingest Officers
    sql_lines.append("\n-- 4. Ingest Statutory Officers Escalation Matrix")
    for r in data:
        sid = r["service_id"]
        url = r["source"]["source_url"]
        for off in r.get("officers", []):
            sql_lines.append(
                f"INSERT INTO officers (service_id, officer_type, officer_name, designation, contact_information, source_url) "
                f"VALUES ({escape_sql(sid)}, {escape_sql(off['officer_type'])}, {escape_sql(off['officer_name'])}, "
                f"{escape_sql(off['designation'])}, {escape_sql(off['contact_information'])}, {escape_sql(url)}) "
                f"ON CONFLICT (service_id, officer_type) DO UPDATE SET "
                f"designation = EXCLUDED.designation;"
            )

    # 5. Ingest Fees
    sql_lines.append("\n-- 5. Ingest Fees")
    for r in data:
        sid = r["service_id"]
        fee = r.get("fee", {})
        if fee:
            sql_lines.append(
                f"INSERT INTO fees (service_id, amount, currency, description, conditions, source_url) "
                f"VALUES ({escape_sql(sid)}, {escape_sql(fee.get('amount'))}, {escape_sql(fee.get('currency', 'INR'))}, "
                f"{escape_sql(fee.get('description'))}, NULL, {escape_sql(fee.get('source_url'))});"
            )

    # 6. Ingest Sources
    sql_lines.append("\n-- 6. Ingest Sources")
    for r in data:
        sid = r["service_id"]
        src = r.get("source", {})
        sql_lines.append(
            f"INSERT INTO sources (service_id, source_url, source_title, source_type, scraped_at, verified_at) "
            f"VALUES ({escape_sql(sid)}, {escape_sql(src.get('source_url'))}, {escape_sql(src.get('source_title'))}, "
            f"{escape_sql(src.get('source_type'))}, {escape_sql(src.get('scraped_at'))}::timestamptz, "
            f"{escape_sql(src.get('last_verified_at'))}::timestamptz);"
        )

    # 7. Ingest Service Dependencies (Only Explicit Official Provenance)
    sql_lines.append("\n-- 7. Ingest Explicit Dependencies (Verified Provenance Only)")
    for r in data:
        sid = r["service_id"]
        for dep in r.get("dependencies", []):
            dep_sid = dep.get("depends_on_service_id")
            dep_name = dep.get("depends_on_service_name")
            dep_type = dep.get("dependency_type")
            dep_desc = dep.get("description")
            dep_url = dep.get("source_url")

            sql_lines.append(
                f"INSERT INTO service_dependencies (service_id, depends_on_service_id, depends_on_service_name, "
                f"dependency_type, dependency_description, source_url) "
                f"VALUES ({escape_sql(sid)}, {escape_sql(dep_sid)}, {escape_sql(dep_name)}, "
                f"{escape_sql(dep_type)}, {escape_sql(dep_desc)}, {escape_sql(dep_url)}) "
                f"ON CONFLICT (service_id, depends_on_service_name) DO UPDATE SET "
                f"dependency_description = EXCLUDED.dependency_description;"
            )

    sql_lines.append("\nCOMMIT;")
    return "\n".join(sql_lines)

def run_seed(json_path: str = "data/sample_services.json", sql_output_path: str = "db/seed_data.sql"):
    """Reads JSON data, generates seed_data.sql, and attempts PostgreSQL connection if configured."""
    if not os.path.exists(json_path):
        logger.error(f"Data file {json_path} does not exist. Run scraper first.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"Loaded {len(data)} services from {json_path}")
    sql_content = generate_sql_statements(data)

    with open(sql_output_path, "w", encoding="utf-8") as f:
        f.write(sql_content)
    logger.info(f"Generated standalone PostgreSQL seed script: {sql_output_path}")

    # Check for DATABASE_URL or PostgreSQL environment
    pg_url = os.environ.get("DATABASE_URL")
    if pg_url:
        logger.info(f"Connecting to PostgreSQL database at {pg_url}...")
        try:
            import psycopg2
            conn = psycopg2.connect(pg_url)
            cur = conn.cursor()
            cur.execute(sql_content)
            conn.commit()
            cur.close()
            conn.close()
            logger.info("Successfully executed seed SQL directly on PostgreSQL database!")
        except ImportError:
            logger.info("psycopg2 not installed. Database seed script is ready in db/seed_data.sql")
        except Exception as e:
            logger.error(f"PostgreSQL direct execution failed: {e}")
    else:
        logger.info("Note: DATABASE_URL environment variable not set. Generated standalone db/seed_data.sql for execution with psql.")

if __name__ == "__main__":
    run_seed()
