import os
from typing import List, Optional, Set
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.models import (
    CivicTask, TaskStep, RoadmapResponse, UserProgressUpdate,
    ScrapeRequest, ScrapeResult, AdminVerificationUpdate,
    IntentRequest, IntentMatchModel, IntentResolutionResponse
)
from app.database import db
from app.graph_engine import CivicGraphEngine
from app.scraper_service import scraper_service
from app.nlp_engine import nlp_engine

app = FastAPI(
    title="Municipal Bureaucracy Path Visualizer API",
    description="Intelligent civic task navigation, government portal scraper, and DAG dependency graph resolver.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize NLP index with catalog tasks
nlp_engine.index_tasks(db.get_all_tasks())

# ---------------------------------------------------------------------------
# Citizen Civic Navigation Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/tasks/resolve-intent", response_model=IntentResolutionResponse)
async def resolve_task_intent(payload: IntentRequest):
    """
    Production Dual-Track NLP Intent Resolution & Procedure Engine.
    Accepts natural language queries, Hinglish transliterations, and regional
    dialects, matching them via semantic vectorization or synthesizing zero-shot
    statutory workflows dynamically into the runtime database.
    """
    res = nlp_engine.resolve_intent(query=payload.query, municipality_hint=payload.municipality or "")
    top_id = res.matches[0].task_id if res.matches else None

    return IntentResolutionResponse(
        original_query=res.original_query,
        normalized_query=res.normalized_query,
        hinglish_detected=res.hinglish_detected,
        top_task_id=top_id,
        matches=[
            IntentMatchModel(
                task_id=m.task_id,
                title=m.title,
                municipality=m.municipality,
                state=m.state,
                category=m.category,
                confidence=m.confidence,
                match_type=m.match_type,
                matched_tokens=m.matched_tokens,
                description=m.description
            )
            for m in res.matches
        ],
        synthesis=res.synthesis,
        needs_disambiguation=res.needs_disambiguation
    )


@app.get("/api/tasks", response_model=List[CivicTask])
async def list_tasks(
    q: Optional[str] = Query(None, description="Search query"),
    municipality: Optional[str] = Query(None, description="Filter by municipality")
):
    """
    Search or list available civic tasks across municipalities.
    """
    if q or municipality:
        return db.search_tasks(query=q or "", municipality=municipality)
    return db.get_all_tasks()


@app.get("/api/tasks/{task_id}", response_model=CivicTask)
async def get_task(task_id: str):
    task = db.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Civic task not found")
    return task


@app.post("/api/tasks/{task_id}/roadmap", response_model=RoadmapResponse)
async def get_task_roadmap(
    task_id: str,
    progress: Optional[UserProgressUpdate] = Body(default=None)
):
    """
    Computes the complete Directed Acyclic Graph (DAG) for the task,
    performing topological sorting, critical path analysis, and dynamic
    state resolution based on completed/in-progress steps.
    """
    task = db.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Civic task not found")

    completed_set: Set[str] = set(progress.completed_step_ids) if progress else set()
    in_progress_set: Set[str] = set(progress.in_progress_step_ids) if progress else set()

    engine = CivicGraphEngine(task)
    return engine.resolve_roadmap(
        completed_step_ids=completed_set,
        in_progress_step_ids=in_progress_set
    )


@app.get("/api/tasks/{task_id}/steps/{step_id}", response_model=TaskStep)
async def get_step_detail(task_id: str, step_id: str):
    """
    Retrieve full step details including official verification source,
    prerequisite checklist, required forms, document locker requirements,
    and municipal office contacts.
    """
    task = db.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Civic task not found")

    for step in task.steps:
        if step.id == step_id:
            return step

    raise HTTPException(status_code=404, detail="Step not found in this civic task")


# ---------------------------------------------------------------------------
# Citizen Feedback & Problem Reporting
# ---------------------------------------------------------------------------

@app.post("/api/feedback")
async def submit_feedback(payload: dict = Body(...)):
    step_id = payload.get("step_id", "general")
    issue_type = payload.get("issue_type", "Broken Link / Changed Rule")
    notes = payload.get("notes", "")
    db.add_citizen_feedback(step_id, issue_type, notes)
    return {"status": "success", "message": "Feedback submitted to municipal review queue"}


@app.get("/api/feedback")
async def list_feedback():
    return db.get_feedback()


# ---------------------------------------------------------------------------
# Live Scraper & Ingestion Engine
# ---------------------------------------------------------------------------

@app.post("/api/scrape", response_model=ScrapeResult)
async def scrape_municipal_portal(payload: ScrapeRequest):
    """
    Aggregates fragmented government portals, extracts downloadable forms,
    SLAs, fees, and constructs candidate steps.
    """
    return await scraper_service.scrape_portal(
        url=payload.url,
        task_hint=payload.task_hint,
        municipality=payload.municipality
    )


# ---------------------------------------------------------------------------
# Administrative Validation & Curation Portal
# ---------------------------------------------------------------------------

@app.post("/api/admin/verify-step")
async def admin_verify_step(update: AdminVerificationUpdate, task_id: str = Query(...)):
    """
    Allows municipal officers or system administrators to review, validate,
    and update extracted government information with provenance verification.
    """
    success = db.update_step_verification(
        task_id=task_id,
        step_id=update.step_id,
        is_verified=update.is_verified,
        updated_fee=update.updated_fee,
        updated_sla=update.updated_sla_days,
        source_url=update.updated_source_url
    )
    if not success:
        raise HTTPException(status_code=404, detail="Step or task not found")
    return {"status": "success", "message": f"Step {update.step_id} verification updated."}


@app.get("/api/admin/audit-logs")
async def get_audit_logs():
    return db.get_audit_logs()


@app.get("/api/admin/regulatory-cache")
async def get_regulatory_cache():
    """
    Returns the locally cached audit status, verified gazette citations,
    and fee schedules for the 6 official statutory portals.
    Guarantees < 5ms retrieval without live external blocking.
    """
    return db.get_regulatory_audits()


@app.post("/api/admin/run-audit-daemon")
async def trigger_regulatory_audit():
    """
    Asynchronously triggers the background regulatory audit daemon across
    all official government portals, updating the local high-speed cache.
    """
    results = await scraper_service.run_regulatory_audit()
    return {"status": "success", "message": f"Successfully audited {len(results)} statutory government portals.", "data": results}


# ---------------------------------------------------------------------------
# Database & Knowledge Store Inspection Endpoints (SQLite & Aaple Sarkar)
# ---------------------------------------------------------------------------

@app.get("/api/db/stats")
async def get_db_stats():
    """
    Returns counts and metrics of Maharashtra statutory services, tasks,
    departments, forms, documents, and audit entries stored in SQLite.
    """
    from app.database_sqlite import sqlite_db
    return sqlite_db.get_database_stats()


@app.get("/api/db/aaple-sarkar")
async def search_aaple_sarkar_records(
    q: Optional[str] = Query("", description="Search term for Aaple Sarkar services"),
    limit: int = Query(20, description="Max records to return")
):
    """
    Search official Aaple Sarkar services catalog stored in SQLite.
    """
    from app.database_sqlite import sqlite_db
    return sqlite_db.search_aaple_sarkar(query=q, limit=limit)


@app.post("/api/user/progress")
async def save_user_progress(payload: dict = Body(...)):
    """
    Persists citizen's task progress (completed steps and in-progress steps)
    into SQLite database.
    """
    from app.database_sqlite import sqlite_db
    session_id = payload.get("session_id", "default_citizen")
    task_id = payload.get("task_id")
    completed = payload.get("completed_step_ids", [])
    in_progress = payload.get("in_progress_step_ids", [])
    if not task_id:
        raise HTTPException(status_code=400, detail="task_id is required")
    sqlite_db.save_user_progress(session_id, task_id, completed, in_progress)
    return {"status": "saved", "session_id": session_id, "task_id": task_id}


@app.get("/api/user/progress")
async def load_user_progress(
    session_id: str = Query("default_citizen"),
    task_id: str = Query(...)
):
    """
    Loads saved citizen task progress from SQLite database.
    """
    from app.database_sqlite import sqlite_db
    prog = sqlite_db.get_user_progress(session_id, task_id)
    if not prog:
        return {"completed_step_ids": [], "in_progress_step_ids": []}
    return prog


# ---------------------------------------------------------------------------
# Static Web App Mount
# ---------------------------------------------------------------------------

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Municipal Bureaucracy Path Visualizer API is running. Static files loading."}
