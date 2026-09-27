from app.database import db
from app.nlp_engine import nlp_engine
from app.graph_engine import CivicGraphEngine
import networkx as nx

def test_caste_certificate():
    q1 = "How to get caste certificate?"
    q2 = "I need a caste certificate"
    
    r1 = nlp_engine.resolve_intent(q1)
    r2 = nlp_engine.resolve_intent(q2)
    
    print(f"Query 1: '{q1}' -> matched_task_id: {r1.matched_task_id}, confidence: {r1.confidence}")
    print(f"Query 2: '{q2}' -> matched_task_id: {r2.matched_task_id}, confidence: {r2.confidence}")
    
    assert r1.matched_task_id == "task-caste-certificate", "Should resolve to task-caste-certificate"
    assert r2.matched_task_id == "task-caste-certificate", "Should resolve to task-caste-certificate"
    
    task1 = db.get_task_by_id(r1.matched_task_id)
    task2 = db.get_task_by_id(r2.matched_task_id)
    
    # Verify no combined package
    assert "income" not in task1.title.lower(), "Must NOT be income certificate"
    assert "domicile" not in task1.title.lower(), "Must NOT be domicile certificate"
    assert "package" not in task1.title.lower(), "Must NOT be a package"
    
    # Generate DAG
    engine1 = CivicGraphEngine(task=task1)
    engine2 = CivicGraphEngine(task=task2)
    
    rm1 = engine1.resolve_roadmap()
    rm2 = engine2.resolve_roadmap()
    
    nodes1 = [(n.id, n.title) for n in rm1.nodes]
    nodes2 = [(n.id, n.title) for n in rm2.nodes]
    
    edges1 = [(e.source, e.target) for e in rm1.edges]
    edges2 = [(e.source, e.target) for e in rm2.edges]
    
    print(f"\nNodes ({len(nodes1)}):")
    for n in nodes1:
        print(f"  - {n[0]}: {n[1]}")
        
    print(f"\nEdges ({len(edges1)}):")
    for e in edges1:
        print(f"  - {e[0]} -> {e[1]}")
        
    assert nodes1 == nodes2, "Both queries must yield identical nodes"
    assert edges1 == edges2, "Both queries must yield identical edges"
    assert not engine1.has_cycles(), "Graph must be acyclic (DAG)"
    
    print("\nALL CASTE CERTIFICATE CHECKS PASSED!")

if __name__ == "__main__":
    test_caste_certificate()
