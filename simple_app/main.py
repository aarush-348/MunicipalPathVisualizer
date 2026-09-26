"""
Civic Task Navigator - Simple Web Application.
Main FastAPI server providing verified government service roadmaps from PostgreSQL.
"""
import os
import sys
from typing import Optional
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader

# Add parent directory to path so imports work cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from simple_app.db import (
    check_db_health,
    fetch_all_services,
    fetch_service_by_id
)
from simple_app.matcher import match_service_from_query

app = FastAPI(
    title="Civic Task Navigator",
    description="Find the steps required to complete a government service backed by verified PostgreSQL records.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Jinja2 templates and static directory
templates_dir = os.path.join(CURRENT_DIR, "templates")
static_dir = os.path.join(CURRENT_DIR, "static")

jinja_env = Environment(loader=FileSystemLoader(templates_dir))
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, q: Optional[str] = None, location: Optional[str] = None):
    """Renders the simple Civic Task Navigator homepage."""
    template = jinja_env.get_template("index.html")
    return template.render(initial_query=q or "", initial_location=location or "")

@app.get("/api/health")
async def health():
    """Health check validating PostgreSQL connectivity."""
    return check_db_health()

@app.get("/api/services")
async def get_services():
    """Returns list of all verified government services in the database."""
    try:
        return fetch_all_services()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/services/{service_id}")
async def get_service(service_id: str, location: Optional[str] = None):
    """Retrieves full details and roadmap for a verified service by ID."""
    service_data = fetch_service_by_id(service_id, location_override=location)
    if not service_data:
        raise HTTPException(status_code=404, detail="Service not found in verified database.")
    return service_data

@app.get("/api/search")
async def search_civic_task(
    q: str = Query(..., description="User civic task query"),
    location: Optional[str] = Query(None, description="User location")
):
    """
    Identifies the government service from natural language, retrieves verified
    data from PostgreSQL, and constructs a step-by-step roadmap.
    If no verified service matches, returns found=False with zero hallucinations.
    """
    if not q or not q.strip():
        return JSONResponse(status_code=400, content={"error": "Query cannot be empty"})

    # 1. Natural Language Matching against PostgreSQL
    service_row, detected_location, confidence = match_service_from_query(
        query=q,
        location_input=location
    )

    if not service_row:
        # Get list of existing verified services to assist the user
        available = fetch_all_services()
        return {
            "found": False,
            "message": "We could not find sufficient verified information for this service in our current database.",
            "query": q,
            "location": detected_location,
            "confidence": 0.0,
            "available_services": [s["service_name"] for s in available[:8]]
        }

    # 2. Retrieve verified records from PostgreSQL
    service_id = service_row["id"]
    service_data = fetch_service_by_id(service_id, location_override=detected_location)

    if not service_data:
        return {
            "found": False,
            "message": "We could not find sufficient verified information for this service in our current database.",
            "query": q,
            "location": detected_location,
            "confidence": 0.0
        }

    return {
        "found": True,
        "query": q,
        "location": detected_location,
        "confidence": confidence,
        "data": service_data
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Civic Task Navigator on http://127.0.0.1:{port}")
    uvicorn.run("simple_app.main:app", host="127.0.0.1", port=port, reload=False)
