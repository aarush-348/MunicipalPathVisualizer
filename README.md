# Municipal Bureaucracy Path Visualizer (PSWB 02)

**Department:** Computer Engineering Department  
**Project ID:** PSWB 02  
**Title:** Municipal Bureaucracy Path Visualizer — Civic Task Navigator

---

## 🌟 Overview

Citizens frequently face labyrinthine bureaucratic hurdles when completing civic tasks such as registering a business, securing construction sanctions, transferring property titles, or obtaining health and trade permits. This information is traditionally fragmented across dozens of disconnected `.gov` pages, obsolete PDF gazettes, and unlinked department portals.

The **Civic Task Navigator** solves this by providing a single, clean interface where a citizen can type what they need — in plain language — and instantly see a verified, step-by-step roadmap pulled directly from a PostgreSQL database of official government service records.

> **Core Principle:** We do NOT invent government procedures. Only services with verified administrative provenance in PostgreSQL are displayed. If a service is missing, the app says so clearly.

---

## 🚀 Key Features

- **Natural Language Search:** Type "income certificate Thane" or "register a business in Pune" — the app understands you.
- **Verified Roadmap:** Every step is pulled directly from PostgreSQL. Zero hallucination.
- **Document Checklists:** Shows exactly which documents are required, organized by category.
- **Official Source Provenance:** Every result displays its official `.gov` URL, department, processing time, and statutory fees.
- **Graceful Fallback:** If a service isn't in the DB, you're shown a list of what *is* available.
- **Aaple Sarkar Scraper:** Background scraper to ingest new services from the official Maharashtra government portal.

---

## 🛠️ Architecture & Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.9+) |
| Database | PostgreSQL 17 (`civic_navigator` database) |
| NLP Matching | Custom synonym map + PostgreSQL Full-Text Search |
| Scraping | HTTPX + BeautifulSoup4 |
| Frontend | Vanilla HTML5, CSS (clean modern design), ES6 JavaScript |
| Data Seeding | `db/seed_postgres.py` (idempotent, schema-aware) |

---

## 📁 Project Structure

```
MunicipalPathVisualizer/
├── simple_app/             # ← The working MVP (Civic Task Navigator)
│   ├── main.py             #   FastAPI routes
│   ├── db.py               #   PostgreSQL data access layer
│   ├── matcher.py          #   NLP matching logic
│   ├── templates/          #   Jinja2 HTML templates
│   └── static/             #   JS, CSS assets
├── db/
│   ├── schema.sql          #   Database schema (10 core tables)
│   ├── seed_postgres.py    #   Idempotent DB seeder
│   └── seed_data.sql       #   SQL seed data
├── data/
│   ├── sample_services.json    #   Verified service definitions
│   └── sample_services.csv
├── scraper/
│   ├── aaple_sarkar_scraper.py #   Aaple Sarkar portal scraper
│   ├── normalizer.py
│   └── config.py
├── tests/
│   └── test_simple_app.py  #   Full integration test suite
├── run_simple.py           #   ← Entry point for the MVP
├── run.py                  #   Entry point for legacy app/
├── .env                    #   DB credentials (not committed)
└── requirements.txt
```

---

## 🏃 Running the MVP Locally

### 1. Prerequisites

- Python 3.9+
- PostgreSQL 17 running locally (default port 5432)
- A `civic_navigator` database (auto-created by the seeder)

### 2. Install Dependencies

```bash
cd "C:\Users\SHRIKANT\Desktop\MunicipalPathVisualizer"
.\env\Scripts\pip install -r requirements.txt
```

### 3. Configure Database Credentials

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=civic_navigator
DB_USER=postgres
DB_PASSWORD=1234
```

### 4. Seed the Database

Run this once (it's idempotent — safe to re-run):

```bash
.\env\Scripts\python db\seed_postgres.py
```

### 5. Start the Application

```bash
.\env\Scripts\python run_simple.py
```

Then open your browser at **`http://127.0.0.1:8080`**

---

## 🧪 Running Tests

```bash
.\env\Scripts\python -m pytest tests/test_simple_app.py -v
```

Tests cover:
- Database connection and schema validation
- Data seeding and record counts
- NLP matching (synonym resolution)
- API endpoint responses (search, not-found, list)

---

## 🔍 Example Searches

| Query | What you get |
|---|---|
| `income certificate` | Step-by-step roadmap for Income Certificate (Revenue Dept, Thane) |
| `register a small business in Pune` | Roadmap for Shop & Establishment registration |
| `caste certificate` | Caste/Tribe Validity Certificate roadmap |
| `7/12 land record` | 7-12 Extract (Satbara) application steps |
| `random unverified query` | "We could not find sufficient verified information..." + available services list |

---

## 🌐 Scraper (Aaple Sarkar)

The `scraper/aaple_sarkar_scraper.py` ingests new services from the Maharashtra Aaple Sarkar portal. To run it:

```bash
.\env\Scripts\python -m scraper.aaple_sarkar_scraper
```

Scraped data is normalized via `scraper/normalizer.py` and can be reviewed before being committed to the database.

---

## 📜 License

Academic project — Computer Engineering Department, PSWB 02.
