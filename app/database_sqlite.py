"""
SQLite Database Layer for Maharashtra Civic Services & Procedural Pathways
==========================================================================
Persists:
- Official Aaple Sarkar services (from data/sample_services.json)
- Multi-agency civic tasks and steps
- Document locker requirements and forms
- Officer escalation matrices
- Citizen feedback and administrative verification audit trails
- User progress tracking
"""
import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "civic_maharashtra.db")

class CivicSQLiteDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_schema()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_schema(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Departments table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                jurisdiction TEXT NOT NULL,
                office_address TEXT,
                contact_phone TEXT,
                contact_email TEXT,
                working_hours TEXT,
                portal_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 2. Curated Tasks table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                municipality TEXT NOT NULL,
                state TEXT NOT NULL,
                description TEXT,
                tags TEXT, -- JSON array of tags
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 3. Steps table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                department_id TEXT NOT NULL,
                submission_mode TEXT NOT NULL,
                estimated_days INTEGER DEFAULT 7,
                fee_amount REAL DEFAULT 0.0,
                fee_breakdown TEXT, -- JSON dict
                prerequisites TEXT, -- JSON list of step IDs
                verification_source TEXT, -- JSON dict
                tips_and_pitfalls TEXT,
                anti_tout_advisory TEXT,
                statutory_payment_channel TEXT,
                community_verifications INTEGER DEFAULT 0,
                official_receipt_mandate TEXT,
                last_gazette_notification TEXT,
                is_critical_path INTEGER DEFAULT 0,
                is_admin_verified INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            );
            """)

            # 4. Documents table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                step_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                is_mandatory INTEGER DEFAULT 1,
                category TEXT DEFAULT 'General',
                sample_template_url TEXT,
                FOREIGN KEY (step_id) REFERENCES steps(id) ON DELETE CASCADE
            );
            """)

            # 5. Forms table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                step_id TEXT NOT NULL,
                form_code TEXT NOT NULL,
                title TEXT NOT NULL,
                download_url TEXT,
                fill_online_url TEXT,
                instructions TEXT,
                FOREIGN KEY (step_id) REFERENCES steps(id) ON DELETE CASCADE
            );
            """)

            # 6. Aaple Sarkar Individual Official Services table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS aaple_sarkar_services (
                service_id TEXT PRIMARY KEY,
                service_name TEXT NOT NULL,
                department TEXT NOT NULL,
                department_code TEXT,
                sub_department TEXT,
                description TEXT,
                eligibility TEXT,
                service_type TEXT,
                application_method TEXT,
                application_url TEXT,
                processing_time_days INTEGER,
                applicable_location TEXT,
                status TEXT,
                fee_amount REAL,
                fee_description TEXT,
                source_url TEXT,
                scraped_at TEXT,
                raw_json TEXT
            );
            """)

            # 7. Citizen Feedback table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS citizen_feedback (
                id TEXT PRIMARY KEY,
                step_id TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                notes TEXT,
                status TEXT DEFAULT 'pending_review',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 8. Audit Logs table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                user_name TEXT DEFAULT 'Admin',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 9. User Progress Tracking table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                user_session_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                completed_step_ids TEXT, -- JSON list
                in_progress_step_ids TEXT, -- JSON list
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_session_id, task_id)
            );
            """)

            # Indices for fast lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_steps_task ON steps(task_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_step ON documents(step_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_forms_step ON forms(step_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_as_dept ON aaple_sarkar_services(department);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_as_name ON aaple_sarkar_services(service_name);")

            conn.commit()

    def seed_aaple_sarkar_services(self, json_path: str):
        if not os.path.exists(json_path):
            return 0
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for s in data:
                sid = str(s.get("service_id", ""))
                if not sid:
                    continue
                fee_obj = s.get("fee") or {}
                source_obj = s.get("source") or {}
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
                    processing_time_days=excluded.processing_time_days,
                    application_url=excluded.application_url;
                """, (
                    sid,
                    s.get("service_name"),
                    s.get("department"),
                    s.get("department_code"),
                    s.get("sub_department"),
                    s.get("description"),
                    s.get("eligibility"),
                    s.get("service_type"),
                    s.get("application_method"),
                    s.get("application_url"),
                    s.get("processing_time_days"),
                    s.get("applicable_location"),
                    s.get("status"),
                    fee_obj.get("amount"),
                    fee_obj.get("description"),
                    source_obj.get("source_url"),
                    source_obj.get("scraped_at"),
                    json.dumps(s, ensure_ascii=False)
                ))
                count += 1
            conn.commit()
        return count

    def persist_task(self, task_dict: Dict[str, Any]):
        """Persists a complete CivicTask into SQLite."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Insert task
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
                task_dict["id"],
                task_dict["title"],
                task_dict["category"],
                task_dict["municipality"],
                task_dict["state"],
                task_dict["description"],
                json.dumps(task_dict.get("tags", []))
            ))

            # Insert steps
            for step in task_dict.get("steps", []):
                dept = step.get("department", {})
                dept_id = dept.get("id", f"dept-{step['id']}")
                cursor.execute("""
                INSERT INTO departments (id, name, jurisdiction, office_address, contact_phone, contact_email, working_hours, portal_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    office_address=excluded.office_address,
                    portal_url=excluded.portal_url;
                """, (
                    dept_id,
                    dept.get("name", "Maharashtra Municipal Department"),
                    dept.get("jurisdiction", task_dict.get("municipality", "Maharashtra")),
                    dept.get("office_address", ""),
                    dept.get("contact_phone", ""),
                    dept.get("contact_email", ""),
                    dept.get("working_hours", ""),
                    dept.get("portal_url", "")
                ))

                v_src = step.get("verification_source", {})
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
                    is_critical_path=excluded.is_critical_path,
                    is_admin_verified=excluded.is_admin_verified;
                """, (
                    step["id"],
                    task_dict["id"],
                    step["step_number"],
                    step["title"],
                    step.get("description", ""),
                    dept_id,
                    step.get("submission_mode", "Online"),
                    step.get("estimated_days", 7),
                    step.get("fee_amount", 0.0),
                    json.dumps(step.get("fee_breakdown", {})),
                    json.dumps(step.get("prerequisites", [])),
                    json.dumps(v_src),
                    step.get("tips_and_pitfalls", ""),
                    step.get("anti_tout_advisory", ""),
                    step.get("statutory_payment_channel", ""),
                    step.get("community_verifications", 0),
                    step.get("official_receipt_mandate", ""),
                    step.get("last_gazette_notification", ""),
                    1 if step.get("is_critical_path") else 0,
                    1 if v_src.get("is_admin_verified") else 0
                ))

                # Documents
                for doc in step.get("documents", []):
                    cursor.execute("""
                    INSERT INTO documents (id, step_id, name, description, is_mandatory, category, sample_template_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name=excluded.name,
                        description=excluded.description;
                    """, (
                        doc["id"],
                        step["id"],
                        doc["name"],
                        doc.get("description", ""),
                        1 if doc.get("is_mandatory", True) else 0,
                        doc.get("category", "General"),
                        doc.get("sample_template_url", "")
                    ))

                # Forms
                for form in step.get("forms", []):
                    cursor.execute("""
                    INSERT INTO forms (step_id, form_code, title, download_url, fill_online_url, instructions)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        step["id"],
                        form["form_code"],
                        form["title"],
                        form.get("download_url"),
                        form.get("fill_online_url"),
                        form.get("instructions")
                    ))
            conn.commit()

    def record_feedback(self, fb_id: str, step_id: str, issue_type: str, notes: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO citizen_feedback (id, step_id, issue_type, notes, status)
            VALUES (?, ?, ?, ?, 'pending_review');
            """, (fb_id, step_id, issue_type, notes))
            conn.commit()

    def record_audit(self, action: str, details: str, user_name: str = "Admin"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO audit_logs (action, details, user_name)
            VALUES (?, ?, ?);
            """, (action, details, user_name))
            conn.commit()

    def save_user_progress(self, session_id: str, task_id: str, completed_ids: List[str], in_progress_ids: List[str]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO user_progress (user_session_id, task_id, completed_step_ids, in_progress_step_ids, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_session_id, task_id) DO UPDATE SET
                completed_step_ids=excluded.completed_step_ids,
                in_progress_step_ids=excluded.in_progress_step_ids,
                updated_at=CURRENT_TIMESTAMP;
            """, (session_id, task_id, json.dumps(completed_ids), json.dumps(in_progress_ids)))
            conn.commit()

    def get_user_progress(self, session_id: str, task_id: str) -> Optional[Dict[str, List[str]]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT completed_step_ids, in_progress_step_ids
            FROM user_progress
            WHERE user_session_id = ? AND task_id = ?;
            """, (session_id, task_id))
            row = cursor.fetchone()
            if row:
                return {
                    "completed_step_ids": json.loads(row["completed_step_ids"] or "[]"),
                    "in_progress_step_ids": json.loads(row["in_progress_step_ids"] or "[]")
                }
            return None

    def get_database_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            stats = {}
            for table in ["departments", "tasks", "steps", "documents", "forms", "aaple_sarkar_services", "citizen_feedback", "audit_logs"]:
                cursor.execute(f"SELECT COUNT(*) as c FROM {table};")
                stats[table] = cursor.fetchone()["c"]
            return stats

    def search_aaple_sarkar(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        q = f"%{query.strip()}%"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT service_id, service_name, department, processing_time_days, application_url, source_url
            FROM aaple_sarkar_services
            WHERE service_name LIKE ? OR department LIKE ? OR description LIKE ?
            LIMIT ?;
            """, (q, q, q, limit))
            return [dict(r) for r in cursor.fetchall()]

    def get_aaple_sarkar_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves raw Aaple Sarkar official service record by service_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM aaple_sarkar_services WHERE service_id = ?;
            """, (str(service_id),))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def load_all_tasks(self) -> Dict[str, Any]:
        """Loads and reconstructs all curated CivicTasks with steps, docs, and forms from SQLite."""
        from app.models import (
            CivicTask, TaskStep, DepartmentInfo, DocumentRequirement,
            FormRequirement, VerificationSource, SubmissionMode
        )

        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 1. Load departments
            cursor.execute("SELECT * FROM departments;")
            depts = {}
            for row in cursor.fetchall():
                depts[row["id"]] = DepartmentInfo(
                    id=row["id"],
                    name=row["name"],
                    jurisdiction=row["jurisdiction"],
                    office_address=row["office_address"] or "",
                    contact_phone=row["contact_phone"],
                    contact_email=row["contact_email"],
                    working_hours=row["working_hours"] or "Mon-Fri 10:00 AM - 5:00 PM",
                    portal_url=row["portal_url"]
                )

            # 2. Load tasks
            cursor.execute("SELECT * FROM tasks;")
            task_rows = cursor.fetchall()

            loaded: Dict[str, CivicTask] = {}
            for t in task_rows:
                task_id = t["id"]
                # 3. Load steps for this task
                cursor.execute("SELECT * FROM steps WHERE task_id = ? ORDER BY step_number ASC;", (task_id,))
                step_rows = cursor.fetchall()

                steps = []
                for s in step_rows:
                    step_id = s["id"]
                    # Load documents
                    cursor.execute("SELECT * FROM documents WHERE step_id = ?;", (step_id,))
                    doc_rows = cursor.fetchall()
                    docs = [
                        DocumentRequirement(
                            id=d["id"],
                            name=d["name"],
                            description=d["description"] or "",
                            is_mandatory=bool(d["is_mandatory"]),
                            category=d["category"] or "General",
                            sample_template_url=d["sample_template_url"]
                        )
                        for d in doc_rows
                    ]

                    # Load forms
                    cursor.execute("SELECT * FROM forms WHERE step_id = ?;", (step_id,))
                    form_rows = cursor.fetchall()
                    forms = [
                        FormRequirement(
                            form_code=f["form_code"],
                            title=f["title"],
                            download_url=f["download_url"],
                            fill_online_url=f["fill_online_url"],
                            instructions=f["instructions"]
                        )
                        for f in form_rows
                    ]

                    dept_id = s["department_id"]
                    dept = depts.get(dept_id, DepartmentInfo(
                        id=dept_id,
                        name="Maharashtra Municipal Department",
                        jurisdiction=t["municipality"],
                        office_address=""
                    ))

                    v_src_raw = json.loads(s["verification_source"]) if s["verification_source"] else {}
                    v_src = VerificationSource(
                        url=v_src_raw.get("url", "https://aaplesarkar.mahaonline.gov.in"),
                        page_title=v_src_raw.get("page_title", "Government Portal"),
                        last_scraped_at=v_src_raw.get("last_scraped_at", "2026-09-26T15:30:00Z"),
                        confidence_score=float(v_src_raw.get("confidence_score", 0.95)),
                        is_admin_verified=bool(s["is_admin_verified"]),
                        gazette_ref=v_src_raw.get("gazette_ref"),
                        portal_section=v_src_raw.get("portal_section")
                    )

                    prereqs = json.loads(s["prerequisites"]) if s["prerequisites"] else []
                    fee_breakdown = json.loads(s["fee_breakdown"]) if s["fee_breakdown"] else {}

                    sub_mode = SubmissionMode.ONLINE
                    if s["submission_mode"] in [e.value for e in SubmissionMode]:
                        sub_mode = SubmissionMode(s["submission_mode"])

                    step = TaskStep(
                        id=step_id,
                        task_id=task_id,
                        step_number=s["step_number"],
                        title=s["title"],
                        description=s["description"] or "",
                        department=dept,
                        submission_mode=sub_mode,
                        estimated_days=s["estimated_days"] or 7,
                        fee_amount=float(s["fee_amount"] or 0.0),
                        fee_breakdown=fee_breakdown,
                        prerequisites=prereqs,
                        documents=docs,
                        forms=forms,
                        verification_source=v_src,
                        tips_and_pitfalls=s["tips_and_pitfalls"],
                        anti_tout_advisory=s["anti_tout_advisory"],
                        statutory_payment_channel=s["statutory_payment_channel"],
                        community_verifications=s["community_verifications"] or 0,
                        official_receipt_mandate=s["official_receipt_mandate"],
                        last_gazette_notification=s["last_gazette_notification"],
                        is_critical_path=bool(s["is_critical_path"])
                    )
                    steps.append(step)

                tags = json.loads(t["tags"]) if t["tags"] else []
                loaded[task_id] = CivicTask(
                    id=task_id,
                    title=t["title"],
                    category=t["category"],
                    municipality=t["municipality"],
                    state=t["state"],
                    description=t["description"] or "",
                    tags=tags,
                    steps=steps
                )
            return loaded

sqlite_db = CivicSQLiteDB()
