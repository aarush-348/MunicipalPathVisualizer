# Municipal Bureaucracy Path Visualizer (PSWB 02)

**Department:** Computer Engineering Department  
**Project ID:** PSWB 02  
**Title:** Municipal Bureaucracy Path Visualizer (Civic Task Navigator)

---

## 🌟 Overview
Citizens frequently face labyrinthine bureaucratic hurdles when completing civic tasks such as registering a business, securing construction sanctions, transferring property titles, or obtaining health and trade permits. This critical information is traditionally fragmented across dozens of disconnected `.gov` pages, obsolete PDF gazettes, and unlinked department portals.

The **Municipal Bureaucracy Path Visualizer** solves this by:
1. **Aggregating Fragmented Portals:** Ingesting official `.gov` pages, extracting structured forms, departments, fees, and statutory SLAs.
2. **DAG Dependency Graph Engine:** Utilizing `networkx` to automatically detect topological dependencies, isolate parallel tasks vs sequential bottlenecks, and compute the mathematical critical path.
3. **Interactive Visual Canvas:** Providing citizens with an interactive, zoomable roadmap with status color-coding, dynamic prerequisite unlocking, and verified `.gov` source provenance.
4. **Administrative Curation & Scraper Console:** Equipping municipal moderators with live crawlers, diff inspectors, and verification controls.

---

## 🚀 Key Features

- **Directed Acyclic Graph (DAG) Solver:**
  - Automated topological leveling and cycle prevention.
  - Critical Path Method (CPM) calculation identifying the longest dependency chain.
  - Dynamic status gating: unlocks dependent tasks as prerequisites are completed.
- **Official Source Provenance:**
  - Every step displays its official `.gov` URL, verification timestamp, confidence score, and gazette citations.
- **Interactive Citizen Checklist & Document Locker:**
  - Slide-over drawer with itemized document readiness checklists and downloadable blank forms.
  - Printable PDF export feature with QR codes and procedural summaries.
- **Administrative Portal:**
  - Built-in live crawler to scrape target municipal portals.
  - Moderation queue with fee/SLA adjustments and one-click verification.
  - Immutable audit trail.

---

## 🛠️ Architecture & Tech Stack

- **Backend:** FastAPI (Python 3.9+)
- **Graph & Algorithms:** NetworkX (Topological sort, DAG cycle resolution, Critical Path)
- **Scraping & Ingestion:** HTTPX + BeautifulSoup4 + Schema Extractors
- **Data Validation:** Pydantic v2
- **Frontend:** Vanilla HTML5, Modern CSS (Glassmorphism & dark aesthetic), Interactive SVG Graph Engine, ES6 JavaScript.

---

## 🏃 Running Locally

```bash
cd "C:\Users\aarus\.gemini\antigravity-ide\scratch\municipal-path-visualizer"
python run.py
```

Then open your browser at **`http://127.0.0.1:8000`**.
