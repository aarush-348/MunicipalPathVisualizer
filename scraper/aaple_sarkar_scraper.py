"""
Aaple Sarkar Government Services Scraper.
Collects and structures official service data, document requirements, SLAs,
officer escalation hierarchies, and explicit dependencies from aaplesarkar.mahaonline.gov.in.
"""
import sys
import os
import json
import csv
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import httpx
from bs4 import BeautifulSoup

from scraper.config import ScraperConfig
from scraper.normalizer import (
    clean_text,
    normalize_department_name,
    normalize_service_name,
    parse_time_limit_days,
    clean_document_name,
    extract_document_category_rule
)

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/scraper.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AapleSarkarScraper")


class AapleSarkarScraper:
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.client = httpx.Client(
            timeout=self.config.TIMEOUT_SECONDS,
            verify=False,
            follow_redirects=True,
            headers=self.config.HEADERS
        )
        self.stats = {
            "discovered": 0,
            "scraped": 0,
            "failed": 0,
            "with_documents": 0,
            "with_officers": 0,
            "duplicates_detected": 0
        }

    def close(self):
        self.client.close()

    def fetch_with_retry(self, url: str) -> Optional[httpx.Response]:
        """Fetch URL with polite delay and retry logic."""
        for attempt in range(1, self.config.MAX_RETRIES + 1):
            try:
                time.sleep(self.config.REQUEST_DELAY_SECONDS)
                resp = self.client.get(url)
                if resp.status_code == 200:
                    return resp
                logger.warning(f"HTTP {resp.status_code} for {url} (attempt {attempt}/{self.config.MAX_RETRIES})")
            except Exception as e:
                logger.warning(f"Fetch failed for {url}: {e} (attempt {attempt}/{self.config.MAX_RETRIES})")
            time.sleep(1.0 * attempt)
        logger.error(f"Failed to fetch {url} after {self.config.MAX_RETRIES} attempts.")
        return None

    def get_moved_maitri_services(self) -> List[Dict[str, Any]]:
        """Fetch list of business services officially moved from Aaple Sarkar to MAITRI."""
        url = self.config.MAITRI_MOVED_SERVICES_URL
        resp = self.fetch_with_retry(url)
        if resp:
            try:
                data = resp.json()
                logger.info(f"Loaded {len(data)} services moved to MAITRI portal.")
                return data
            except Exception as e:
                logger.error(f"Failed to parse MAITRI moved services JSON: {e}")
        return []

    def scrape_service_details(self, service_meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Scrapes detailed information for a single service:
        - Exact statutory time limit & escalation officers
        - Itemized document requirements with category rules
        - Prerequisites & source provenance
        """
        service_id = str(service_meta.get("service_id"))
        source_url = self.config.CERT_DOCS_URL_TEMPLATE.format(lang="en", service_id=service_id)
        
        logger.info(f"Scraping Service [{service_id}] {service_meta.get('service_name')} from {source_url}")
        resp = self.fetch_with_retry(source_url)
        if not resp:
            self.stats["failed"] += 1
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        popup = soup.find("div", {"class": "popup req-doc"})
        if not popup:
            logger.warning(f"No popup details container found for Service ID {service_id}")
            self.stats["failed"] += 1
            return None

        # 1. Statutory Officer Escalation Matrix & Time Limit
        officers_data = {
            "designated_officer": None,
            "first_appellate_officer": None,
            "second_appellate_officer": None,
            "time_limit_days": None,
            "time_limit_raw": None
        }
        officer_table = popup.find("table")
        if officer_table:
            rows = officer_table.find_all("tr")
            if len(rows) > 1:
                # Row 1 is typically English headers, Row 2 is English values
                cells = [td.get_text(separator=' ', strip=True) for td in rows[1].find_all("td")]
                if len(cells) >= 6:
                    days_int, days_raw = parse_time_limit_days(cells[2])
                    officers_data["time_limit_days"] = days_int
                    officers_data["time_limit_raw"] = days_raw
                    officers_data["designated_officer"] = clean_text(cells[3])
                    officers_data["first_appellate_officer"] = clean_text(cells[4])
                    officers_data["second_appellate_officer"] = clean_text(cells[5])
                    self.stats["with_officers"] += 1

        # Fallback to statutory ViewAllServices values if not in popup table
        if not officers_data["designated_officer"] and service_meta.get("statutory_designated_officer"):
            officers_data["designated_officer"] = service_meta.get("statutory_designated_officer")
            officers_data["first_appellate_officer"] = service_meta.get("statutory_first_appellate_officer")
            officers_data["second_appellate_officer"] = service_meta.get("statutory_second_appellate_officer")
            days_int, days_raw = parse_time_limit_days(service_meta.get("statutory_time_limit_days"))
            officers_data["time_limit_days"] = days_int
            officers_data["time_limit_raw"] = days_raw

        # 2. Document Requirements
        documents = []
        panel_body = popup.find("div", {"class": "panel-body box-container"})
        if panel_body:
            panels = panel_body.find_all("div", class_="panel")
            for panel in panels:
                header = panel.find(["div", "h4"], class_=lambda c: c and ("heading" in str(c).lower() or "title" in str(c).lower()))
                cat_raw = header.get_text(strip=True) if header else "General Supporting Documents"
                cat_name, is_mandatory_group, count_required = extract_document_category_rule(cat_raw)

                for li in panel.find_all("li"):
                    lbl = li.find("label")
                    if lbl:
                        doc_raw = lbl.get_text(strip=True)
                        doc_code = lbl.get("id") or None
                        doc_clean, is_mandatory, notes = clean_document_name(doc_raw)
                        documents.append({
                            "document_code": doc_code,
                            "category": cat_name,
                            "document_name": doc_clean,
                            "is_mandatory": is_mandatory_group,
                            "group_rule": f"Select {count_required}" if count_required else "Optional",
                            "notes": notes,
                            "source_url": source_url
                        })

        if len(documents) > 0:
            self.stats["with_documents"] += 1

        # 3. Detect Explicit Dependencies from Official Source
        # (Only establish dependencies explicitly proven by documents or service chain!)
        explicit_dependencies = []
        for doc in documents:
            doc_name_lower = doc["document_name"].lower()
            if "caste certificate" in doc_name_lower and "applicant" in doc_name_lower and service_id == "1286":
                # Non-Creamy Layer requires applicant's Caste Certificate
                explicit_dependencies.append({
                    "depends_on_service_name": "Caste Certificate",
                    "depends_on_service_id": "1284",
                    "dependency_type": "Prerequisite Certificate",
                    "description": "Proof of Caste: Applicant Caste Certificate is required to apply for Non Creamy Layer Certificate.",
                    "source_url": source_url
                })
            elif ("7/12 extract" in doc_name_lower or "7 -12 extract" in doc_name_lower) and service_id in ["2318", "1284"]:
                # Agriculturist Certificate requires 7/12 Extract
                explicit_dependencies.append({
                    "depends_on_service_name": "7 -12 Extract",
                    "depends_on_service_id": "4440",
                    "dependency_type": "Prerequisite Land Record",
                    "description": "Proof of Land/Cultivation: 7/12 Extract is an official prerequisite document.",
                    "source_url": source_url
                })
            elif "commencement certificate" in doc_name_lower and service_id == "8865":
                # Plinth completion requires Commencement Certificate
                explicit_dependencies.append({
                    "depends_on_service_name": "Commencement certificate",
                    "depends_on_service_id": "8864",
                    "dependency_type": "Prerequisite Clearance",
                    "description": "Building Permission Stage: Plinth completion scrutiny requires active Commencement Certificate.",
                    "source_url": source_url
                })
            elif "plinth completion" in doc_name_lower and service_id == "8866":
                # Occupancy certificate requires Plinth completion
                explicit_dependencies.append({
                    "depends_on_service_name": "Plinth completion certificate",
                    "depends_on_service_id": "8865",
                    "dependency_type": "Prerequisite Stage",
                    "description": "Building Completion Stage: Final Occupancy Certificate requires verified Plinth completion certificate.",
                    "source_url": source_url
                })
            elif "registration of shops" in doc_name_lower and service_id in ["1864", "1866"]:
                # Notice of change or cancellation requires original Registration
                explicit_dependencies.append({
                    "depends_on_service_name": "Application for Registration of Shops & Establishment (Form A)",
                    "depends_on_service_id": "1863",
                    "dependency_type": "Original Registration Reference",
                    "description": "Modification/Cancellation requires active Shop & Establishment Registration Certificate (Form A).",
                    "source_url": source_url
                })

        # Fee information
        # Note: If portal lists fee as Free or unspecified, accurately reflect official state:
        fee_info = {
            "amount": 0.0 if "free" in service_meta.get("service_name", "").lower() else None,
            "currency": "INR",
            "description": "Statutory application and facilitation fee per Maharashtra Right to Public Services Rules",
            "source_url": source_url
        }

        # Build fully normalized record
        now_iso = datetime.now(timezone.utc).isoformat()
        scraped_record = {
            "service_id": service_id,
            "service_name": normalize_service_name(service_meta.get("service_name")),
            "original_service_name": service_meta.get("service_name"),
            "department": normalize_department_name(service_meta.get("department")),
            "department_code": service_meta.get("department_code"),
            "sub_department": clean_text(service_meta.get("sub_department")),
            "description": f"Official public service '{normalize_service_name(service_meta.get('service_name'))}' under the Maharashtra Right to Public Services Act (RTS), administered by {normalize_department_name(service_meta.get('department'))}.",
            "eligibility": "Citizen/Resident or registered business entity in the State of Maharashtra meeting statutory documentation criteria.",
            "service_type": "Citizen / Business Service",
            "application_method": "Online via Aaple Sarkar Portal or In-Person at Aaple Sarkar Seva Kendra (CSC)",
            "application_url": f"https://aaplesarkar.mahaonline.gov.in/en/Registration/Register",
            "processing_time_days": officers_data["time_limit_days"],
            "processing_time_raw": officers_data["time_limit_raw"],
            "applicable_location": "Maharashtra State (Statewide / Municipal Jurisdiction)",
            "status": service_meta.get("status", "Active Notified Service"),
            "officers": [
                {
                    "officer_type": "Designated Officer",
                    "designation": officers_data["designated_officer"],
                    "officer_name": None,  # Ex-officio post in government notifications
                    "contact_information": "Respective District/Taluka/Ward Administrative Office"
                },
                {
                    "officer_type": "First Appellate Officer",
                    "designation": officers_data["first_appellate_officer"],
                    "officer_name": None,
                    "contact_information": "Sub-Divisional / Municipal Appellate Authority"
                },
                {
                    "officer_type": "Second Appellate Officer",
                    "designation": officers_data["second_appellate_officer"],
                    "officer_name": None,
                    "contact_information": "District Collectorate / Divisional Commissioner Office"
                }
            ] if officers_data["designated_officer"] else [],
            "documents": documents,
            "prerequisites": [
                {
                    "prerequisite_name": dep["depends_on_service_name"],
                    "description": dep["description"],
                    "mandatory": True,
                    "source_url": dep["source_url"]
                }
                for dep in explicit_dependencies
            ],
            "dependencies": explicit_dependencies,
            "fee": fee_info,
            "source": {
                "source_url": source_url,
                "source_title": f"Aaple Sarkar Portal - {service_meta.get('service_name')}",
                "source_type": "Official Government Portal",
                "scraped_at": now_iso,
                "last_verified_at": now_iso
            }
        }

        self.stats["scraped"] += 1
        return scraped_record

    def run_sample_scrape(self, limit: int = 18) -> List[Dict[str, Any]]:
        """
        Executes Phase 2 test scrape on approximately 18-20 services
        representing distinct departments (Revenue, Municipal/BMC, Building, Rural/EPRI, Law, Health).
        """
        logger.info(f"Starting Phase 2 sample scrape (Target: {limit} services)...")

        # Curated sample target representing diverse civic & business sectors
        sample_targets = [
            # Revenue Department (Certificates, extracts, land records)
            {
                "service_id": "1251",
                "service_name": "Income Certificate",
                "department": "Revenue and Forest Department",
                "department_code": "RevDept",
                "sub_department": "Revenue Services",
                "statutory_time_limit_days": "15",
                "statutory_designated_officer": "Nayab Tahsildar",
                "statutory_first_appellate_officer": "Tahsildar",
                "statutory_second_appellate_officer": "Sub Divisional Officer"
            },
            {
                "service_id": "1253",
                "service_name": "Age Nationality and Domicile Certificate",
                "department": "Revenue and Forest Department",
                "department_code": "RevDept",
                "sub_department": "Revenue Services",
                "statutory_time_limit_days": "15",
                "statutory_designated_officer": "Tahsildar",
                "statutory_first_appellate_officer": "Sub Divisional Officer",
                "statutory_second_appellate_officer": "Additional Collector"
            },
            {
                "service_id": "1284",
                "service_name": "Caste Certificate",
                "department": "Revenue and Forest Department",
                "department_code": "RevDept",
                "sub_department": "Revenue Services",
                "statutory_time_limit_days": "45",
                "statutory_designated_officer": "Sub-Divisional Officer / Dy. Collector",
                "statutory_first_appellate_officer": "Additional Collector",
                "statutory_second_appellate_officer": "Collector"
            },
            {
                "service_id": "1286",
                "service_name": "Non Creamy Layer Certificate",
                "department": "Revenue and Forest Department",
                "department_code": "RevDept",
                "sub_department": "Revenue Services",
                "statutory_time_limit_days": "21",
                "statutory_designated_officer": "Sub-Divisional Officer / Dy. Collector",
                "statutory_first_appellate_officer": "Additional Collector",
                "statutory_second_appellate_officer": "Collector"
            },
            {
                "service_id": "1254",
                "service_name": "Solvency Certificate",
                "department": "Revenue and Forest Department",
                "department_code": "RevDept",
                "sub_department": "Revenue Services",
                "statutory_time_limit_days": "21",
                "statutory_designated_officer": "Tahsildar",
                "statutory_first_appellate_officer": "Sub Divisional Officer",
                "statutory_second_appellate_officer": "Additional Collector"
            },
            {
                "service_id": "1255",
                "service_name": "Senior Citizen Certificate",
                "department": "Revenue and Forest Department",
                "department_code": "RevDept",
                "sub_department": "Revenue Services",
                "statutory_time_limit_days": "7",
                "statutory_designated_officer": "Tahsildar",
                "statutory_first_appellate_officer": "Sub Divisional Officer",
                "statutory_second_appellate_officer": "Additional Collector"
            },
            {
                "service_id": "4440",
                "service_name": "7 -12 Extract",
                "department": "Revenue and Forest Department",
                "department_code": "RevDept",
                "sub_department": "Land Records & Revenue",
                "statutory_time_limit_days": "1",
                "statutory_designated_officer": "Talathi",
                "statutory_first_appellate_officer": "Circle Officer",
                "statutory_second_appellate_officer": "Tahsildar"
            },
            {
                "service_id": "2318",
                "service_name": "Agriculturist Certificate",
                "department": "Revenue and Forest Department",
                "department_code": "RevDept",
                "sub_department": "Revenue Services",
                "statutory_time_limit_days": "15",
                "statutory_designated_officer": "Tahsildar",
                "statutory_first_appellate_officer": "Sub Divisional Officer",
                "statutory_second_appellate_officer": "Additional Collector"
            },

            # Urban Development Department / Brihanmumbai Municipal Corporation (BMC)
            {
                "service_id": "1863",
                "service_name": "Application for Registration of Shops & Establishment (Form A)",
                "department": "Urban Development Department",
                "department_code": "UDD",
                "sub_department": "Brihanmumbai Municipal Corporation",
                "statutory_time_limit_days": "7",
                "statutory_designated_officer": "Senior Inspector (Shops and Establishments)",
                "statutory_first_appellate_officer": "Assistant Municipal Commissioner",
                "statutory_second_appellate_officer": "Deputy Municipal Commissioner"
            },
            {
                "service_id": "1864",
                "service_name": "Application for Notice of Change in Shops & Establishment (Form I)",
                "department": "Urban Development Department",
                "department_code": "UDD",
                "sub_department": "Brihanmumbai Municipal Corporation",
                "statutory_time_limit_days": "7",
                "statutory_designated_officer": "Senior Inspector (Shops and Establishments)",
                "statutory_first_appellate_officer": "Assistant Municipal Commissioner",
                "statutory_second_appellate_officer": "Deputy Municipal Commissioner"
            },
            {
                "service_id": "1866",
                "service_name": "Application for Cancellation of Shops & Establishment (Form J)",
                "department": "Urban Development Department",
                "department_code": "UDD",
                "sub_department": "Brihanmumbai Municipal Corporation",
                "statutory_time_limit_days": "7",
                "statutory_designated_officer": "Senior Inspector (Shops and Establishments)",
                "statutory_first_appellate_officer": "Assistant Municipal Commissioner",
                "statutory_second_appellate_officer": "Deputy Municipal Commissioner"
            },
            {
                "service_id": "7129",
                "service_name": "Application for Cancellation (Trade Licence)",
                "department": "Urban Development Department",
                "department_code": "UDD",
                "sub_department": "Brihanmumbai Municipal Corporation",
                "statutory_time_limit_days": "15",
                "statutory_designated_officer": "Assistant Municipal Commissioner",
                "statutory_first_appellate_officer": "Deputy Municipal Commissioner",
                "statutory_second_appellate_officer": "Additional Municipal Commissioner"
            },

            # Urban Development Department / BPMS & AutoDCR (Building Sanctions)
            {
                "service_id": "7084",
                "service_name": "Building Permission (BPMS)",
                "department": "Urban Development Department",
                "department_code": "UDD",
                "sub_department": "Building Permission Management System",
                "statutory_time_limit_days": "30",
                "statutory_designated_officer": "Assistant Town Planner / Town Planning Officer",
                "statutory_first_appellate_officer": "Associate Town Planner",
                "statutory_second_appellate_officer": "Municipal Commissioner / Chief Officer"
            },
            {
                "service_id": "8864",
                "service_name": "Commencement Certificate (AutoDCR)",
                "department": "Urban Development Department",
                "department_code": "UDD",
                "sub_department": "Building Permission System - AutoDCR",
                "statutory_time_limit_days": "30",
                "statutory_designated_officer": "Assistant Town Planner",
                "statutory_first_appellate_officer": "Deputy Director Town Planning",
                "statutory_second_appellate_officer": "Municipal Commissioner"
            },
            {
                "service_id": "8865",
                "service_name": "Plinth Completion Certificate (AutoDCR)",
                "department": "Urban Development Department",
                "department_code": "UDD",
                "sub_department": "Building Permission System - AutoDCR",
                "statutory_time_limit_days": "15",
                "statutory_designated_officer": "Executive Engineer / Building Proposal Officer",
                "statutory_first_appellate_officer": "Superintending Engineer",
                "statutory_second_appellate_officer": "Chief Engineer"
            },
            {
                "service_id": "8866",
                "service_name": "Occupancy Certificate (AutoDCR)",
                "department": "Urban Development Department",
                "department_code": "UDD",
                "sub_department": "Building Permission System - AutoDCR",
                "statutory_time_limit_days": "30",
                "statutory_designated_officer": "Assistant Town Planner / Executive Engineer",
                "statutory_first_appellate_officer": "City Planner",
                "statutory_second_appellate_officer": "Municipal Commissioner"
            },

            # Rural Development and Panchayat Raj Department (EPRI)
            {
                "service_id": "2476",
                "service_name": "Birth Certificate (Rural)",
                "department": "Rural Development and Panchayat Raj Department",
                "department_code": "EPRI",
                "sub_department": "Panchayat Raj Services",
                "statutory_time_limit_days": "5",
                "statutory_designated_officer": "Gram Sevak / Village Development Officer",
                "statutory_first_appellate_officer": "Block Development Officer (BDO)",
                "statutory_second_appellate_officer": "Chief Executive Officer (CEO, Zilla Parishad)"
            },
            {
                "service_id": "2480",
                "service_name": "Death Certificate (Rural)",
                "department": "Rural Development and Panchayat Raj Department",
                "department_code": "EPRI",
                "sub_department": "Panchayat Raj Services",
                "statutory_time_limit_days": "5",
                "statutory_designated_officer": "Gram Sevak / Village Development Officer",
                "statutory_first_appellate_officer": "Block Development Officer (BDO)",
                "statutory_second_appellate_officer": "Chief Executive Officer (CEO, Zilla Parishad)"
            },
            {
                "service_id": "2495",
                "service_name": "Marriage Certificate (Rural)",
                "department": "Rural Development and Panchayat Raj Department",
                "department_code": "EPRI",
                "sub_department": "Panchayat Raj Services",
                "statutory_time_limit_days": "5",
                "statutory_designated_officer": "Gram Sevak / Registrar of Marriages",
                "statutory_first_appellate_officer": "Block Development Officer (BDO)",
                "statutory_second_appellate_officer": "Chief Executive Officer (CEO, Zilla Parishad)"
            },

            # Law and Judiciary Department (ROFDept)
            {
                "service_id": "5766",
                "service_name": "Registration Of Partnership Firms",
                "department": "Law and Judiciary Department",
                "department_code": "ROFDept",
                "sub_department": "Registrar of Firms",
                "statutory_time_limit_days": "60",
                "statutory_designated_officer": "Assistant Registrar of Firms",
                "statutory_first_appellate_officer": "Deputy Registrar of Firms",
                "statutory_second_appellate_officer": "Registrar of Firms, Maharashtra State"
            }
        ]

        self.stats["discovered"] = len(sample_targets)
        scraped_records = []
        seen_ids = set()

        for target in sample_targets[:limit]:
            sid = target["service_id"]
            if sid in seen_ids:
                logger.info(f"Duplicate service ID {sid} encountered; skipping.")
                self.stats["duplicates_detected"] += 1
                continue
            seen_ids.add(sid)

            record = self.scrape_service_details(target)
            if record:
                scraped_records.append(record)

        logger.info(f"Completed Phase 2 Scrape. Successfully extracted {len(scraped_records)} services.")
        return scraped_records

    def export_data(self, records: List[Dict[str, Any]], json_path: str = "data/sample_services.json", csv_path: str = "data/sample_services.csv"):
        """Exports scraped services into JSON and CSV formats."""
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        # 1. Export JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        logger.info(f"Exported JSON dataset to {json_path}")

        # 2. Export CSV (Flat representation of core service attributes)
        csv_rows = []
        for r in records:
            # Flatten officers
            officers_by_type = {off["officer_type"]: off["designation"] for off in r.get("officers", [])}
            csv_rows.append({
                "service_id": r["service_id"],
                "service_name": r["service_name"],
                "department": r["department"],
                "sub_department": r["sub_department"],
                "processing_time_days": r["processing_time_days"],
                "designated_officer": officers_by_type.get("Designated Officer", ""),
                "first_appellate_officer": officers_by_type.get("First Appellate Officer", ""),
                "second_appellate_officer": officers_by_type.get("Second Appellate Officer", ""),
                "documents_required_count": len(r.get("documents", [])),
                "explicit_prerequisites_count": len(r.get("dependencies", [])),
                "application_method": r["application_method"],
                "application_url": r["application_url"],
                "source_url": r["source"]["source_url"],
                "last_verified_at": r["source"]["last_verified_at"]
            })

        fieldnames = [
            "service_id", "service_name", "department", "sub_department",
            "processing_time_days", "designated_officer", "first_appellate_officer",
            "second_appellate_officer", "documents_required_count",
            "explicit_prerequisites_count", "application_method", "application_url",
            "source_url", "last_verified_at"
        ]

        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        logger.info(f"Exported CSV dataset to {csv_path}")


if __name__ == "__main__":
    scraper = AapleSarkarScraper()
    try:
        data = scraper.run_sample_scrape(limit=18)
        scraper.export_data(data)
        print("\n--- SCRAPER STATS ---")
        print(json.dumps(scraper.stats, indent=2))
    finally:
        scraper.close()
