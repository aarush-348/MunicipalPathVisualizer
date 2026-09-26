# Aaple Sarkar Portal Data Ingestion Pipeline

This component is responsible for collecting, validating, normalizing, and structuring civic service data from Maharashtra's official **Aaple Sarkar Portal** (`https://aaplesarkar.mahaonline.gov.in/`).

---

## 🏛️ Pipeline Overview

The pipeline strictly enforces the **Verifiable Government Ground Truth** principle:
```text
Official Aaple Sarkar Portal
         │
         ▼
[Statutory Catalog] (ViewAllServices - 1,180 Notified Services)
         +
[Dynamic REST API] (TrackApplicationStatus/Select_SubDept & Service_SelectedDept)
         +
[Document & SLA Specification] (Certificate_Documents?ServiceId={id})
         │
         ▼
Data Cleaning & Normalization Engine (scraper/normalizer.py)
         │
         ▼
PostgreSQL Normalized Knowledge Layer (db/schema.sql)
         │
         ▼
Civic Dependency Graph & Visualizer (NetworkX / AI Reasoning)
```

> [!IMPORTANT]
> **Strict Provenance Rule:** The AI is **never** the source of truth. Every service, document requirement, officer escalation tier, statutory SLA, and dependency is stamped with its exact official source URL and verification timestamp. No dependencies are assumed or invented—only explicit statutory requirements established by government sources are recorded.

---

## 📂 Repository Structure

```text
MunicipalPathVisualizer/
├── data/
│   ├── sample_services.json     # Full hierarchical JSON export (18 sample services)
│   └── sample_services.csv      # Flat tabular CSV export for analysis
├── db/
│   ├── schema.sql               # PostgreSQL DDL migrations (10 normalized tables)
│   ├── seed_postgres.py         # Python ingestion script & SQL generator
│   ├── seed_data.sql            # Standalone SQL insert file for psql execution
│   └── example_queries.sql      # Analytical, escalation & recursive graph CTE queries
├── logs/
│   └── scraper.log              # Detailed crawler logs with HTTP codes & timestamps
├── scraper/
│   ├── __init__.py
│   ├── config.py                # Portal endpoints, rate limits, headers, timeouts
│   ├── normalizer.py            # Department aliases, SLA parsing, category cleaners
│   └── aaple_sarkar_scraper.py  # Production scraper engine
└── README_AAPLE_SARKAR.md       # Documentation & setup guide
```

---

## 🗄️ Database Design (PostgreSQL)

The database schema is normalized into 10 relational tables:

1. **`departments`**: Master list of government departments with canonical naming.
2. **`services`**: Core service details (Service ID, Name, Department, SLA days, application URL, provenance).
3. **`documents`**: Master dictionary of required civic documents (Aadhaar, 7/12 Extract, Caste Certificate, etc.).
4. **`service_documents`**: Join table specifying document group rules (e.g. `Proof of Identity (Any -1)`, `Mandatory`).
5. **`prerequisites`**: Master list of explicit pre-conditions.
6. **`service_prerequisites`**: Join table mapping services to prerequisites.
7. **`fees`**: Application and facilitation fees with applicable conditions.
8. **`officers`**: 3-tier statutory escalation matrix:
   - `Designated Officer` (Immediate processing authority)
   - `First Appellate Officer` (First level appeal)
   - `Second Appellate Officer` (Second level appeal)
9. **`sources`**: Audit log recording exact `.gov.in` URLs, scrape timestamps, and verification status.
10. **`service_dependencies`**: Graph edges representing sequential prerequisites (Service B depends on Service A).

---

## 🚀 Quickstart & Setup

### 1. Requirements

Ensure you are using Python 3.9+ with virtual environment activated:

```powershell
pip install httpx beautifulsoup4
```

### 2. Running the Scraper

To run the sample test scrape (18-20 services across diverse departments):

```powershell
.\env\Scripts\python.exe -m scraper.aaple_sarkar_scraper
```

Outputs are automatically saved to `data/sample_services.json`, `data/sample_services.csv`, and `logs/scraper.log`.

### 3. Seeding PostgreSQL

#### Option A: Standalone SQL Execution (No Python DB drivers required)
Run the pre-generated SQL script directly into your PostgreSQL database using `psql`:

```powershell
psql -U postgres -d municipal_db -f db/schema.sql
psql -U postgres -d municipal_db -f db/seed_data.sql
```

#### Option B: Automated Python Ingestion
Set the `DATABASE_URL` environment variable:

```powershell
$env:DATABASE_URL = "postgresql://postgres:password@localhost:5432/municipal_db"
.\env\Scripts\python.exe -m db.seed_postgres
```

### 4. Running Verification Queries

Execute the queries in `db/example_queries.sql` to test the escalation hierarchy, document grouping, and dependency graph traversal:

```powershell
psql -U postgres -d municipal_db -f db/example_queries.sql
```

---

## 🔍 Data Provenance & Safety

- **Robots.txt Compliance**: `robots.txt` on `aaplesarkar.mahaonline.gov.in` allows full site access (`User-agent: * Allow: /`).
- **No CAPTCHA / Authentication Bypass**: All public service catalogues, document specification modals, and statutory notification tables are publicly accessible without authentication.
- **Polite Crawling**: Built-in 0.5s inter-request delay and exponential backoff retry.
