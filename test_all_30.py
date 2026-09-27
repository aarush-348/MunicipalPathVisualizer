import sys
import json
import networkx as nx

from app.database import db as civic_db
from app.nlp_engine import nlp_engine as civic_nlp
from app.graph_engine import CivicGraphEngine

QUERIES = [
    # State Layer
    (1, "How to get caste certificate?", None),
    (2, "How to get income certificate?", None),
    (3, "How to get domicile certificate?", None),
    (4, "How to get non-creamy layer certificate?", None),
    (5, "How to get residence certificate?", None),
    (6, "How to get senior citizen certificate?", None),
    (7, "How to get birth certificate?", None),
    (8, "How to get death certificate?", None),
    (9, "How to register marriage?", None),
    (10, "How to get a certified copy?", None),
    (11, "How to get solvency certificate?", None),
    (12, "How to get temporary residence certificate?", None),
    (13, "How to get living certificate?", None),
    (14, "How to get BPL residence certificate?", None),
    (15, "How to register a shop or establishment?", None),
    (16, "How to register a business?", None),
    (17, "How to get a trade licence?", None),
    # Municipal Layer
    (18, "How to pay property tax in Pune?", "pune"),
    (19, "How to get a water connection in Pune?", "pune"),
    (20, "How to get building permission in Pune?", "pune"),
    (21, "How to pay property tax?", "mumbai"),
    (22, "How to get a water connection?", "mumbai"),
    (23, "How to get building permission?", "mumbai"),
    (24, "How to get a trade licence?", "mumbai"),
    (25, "How to register a birth with the municipality?", "mumbai"),
    (26, "How to register a death with the municipality?", "mumbai"),
    (27, "How to register a marriage with the municipality?", "mumbai"),
    (28, "How to get a no-objection certificate (NOC)?", "mumbai"),
    (29, "How to get a property assessment?", "mumbai"),
    (30, "How to file a municipal complaint?", "mumbai"),
]

def run_tests():
    results = []
    
    for idx, query, jur in QUERIES:
        res = civic_nlp.resolve_intent(query=query, municipality_hint=jur or "")
        task_id = res.matched_task_id
        is_missing = getattr(res, 'is_missing_data', False)
        needs_disambig = getattr(res, 'needs_disambiguation', False)
        
        info = {
            "index": idx,
            "query": query,
            "jurisdiction": jur or "Statewide",
            "matched_task_id": task_id,
            "confidence": res.confidence,
            "department": "",
            "source": "",
            "service_name": "",
            "steps_count": 0,
            "docs_count": 0,
            "dag_nodes": 0,
            "dag_edges": 0,
            "is_dag": False,
            "verified_db": False,
            "status": "OK",
            "notes": ""
        }
        
        if is_missing:
            info["status"] = "MISSING_DATA"
            info["notes"] = res.intent_summary
            results.append(info)
            continue
            
        if needs_disambig:
            info["status"] = "DISAMBIGUATION"
            info["notes"] = f"Ambiguous service; offered options: {[opt['service_name'] for opt in res.disambiguation_options]}"
            results.append(info)
            continue
            
        if not task_id:
            info["status"] = "NO_MATCH"
            results.append(info)
            continue
            
        task = civic_db.get_task_by_id(task_id)
        if not task:
            info["status"] = "TASK_NOT_IN_DB"
            results.append(info)
            continue
            
        info["service_name"] = task.title
        dept = task.steps[0].department.name if task.steps else ""
        info["department"] = dept
        info["source"] = getattr(task, 'source', '') or ("Aaple Sarkar" if getattr(task, 'aaple_sarkar_service_id', None) else (task.municipality or "Statewide"))
        info["steps_count"] = len(task.steps)
        unique_docs = {doc.name for s in task.steps for doc in s.documents}
        info["docs_count"] = len(unique_docs)
        info["verified_db"] = True
        
        # Build DAG
        engine = CivicGraphEngine(task=task)
        roadmap = engine.resolve_roadmap()
        nodes = roadmap.nodes
        edges = roadmap.edges
        info["dag_nodes"] = len(nodes)
        info["dag_edges"] = len(edges)
        info["is_dag"] = not engine.has_cycles()
        results.append(info)

    print("\n" + "="*120)
    print(f"{'#':<3} | {'Query':<45} | {'Matched Task ID':<24} | {'Status':<14} | {'Nodes':<5} | {'Edges':<5} | {'DAG?'}")
    print("="*120)
    for r in results:
        t_id = r['matched_task_id'] or '-'
        status = r['status']
        print(f"{r['index']:<3} | {r['query'][:45]:<45} | {t_id:<24} | {status:<14} | {r['dag_nodes']:<5} | {r['dag_edges']:<5} | {r['is_dag']}")
    print("="*120)
    return results

if __name__ == "__main__":
    run_tests()
