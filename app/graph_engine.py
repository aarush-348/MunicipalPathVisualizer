from typing import List, Dict, Set, Tuple
import networkx as nx
from app.models import (
    TaskStep, StepStatus, GraphNode, GraphEdge, GraphPhase,
    RoadmapResponse, CivicTask, ConsolidatedDocument
)

class CivicGraphEngine:
    def __init__(self, task: CivicTask):
        self.task = task
        self.steps_dict: Dict[str, TaskStep] = {s.id: s for s in task.steps}
        self.g = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        for step in self.task.steps:
            self.g.add_node(
                step.id,
                title=step.title,
                days=step.estimated_days,
                fee=step.fee_amount,
                department=step.department.name,
                mode=step.submission_mode.value,
                confidence=step.verification_source.confidence_score
            )
        for step in self.task.steps:
            for prereq_id in step.prerequisites:
                if prereq_id in self.steps_dict:
                    # Edge goes from prereq -> step (prereq must happen before step)
                    self.g.add_edge(prereq_id, step.id)

    def has_cycles(self) -> bool:
        return not nx.is_directed_acyclic_graph(self.g)

    def get_cycles(self) -> List[List[str]]:
        try:
            return list(nx.simple_cycles(self.g))
        except Exception:
            return []

    def compute_topological_levels(self) -> Dict[str, int]:
        """
        Assigns each node to a topological level (phase).
        Level 0 has no prerequisites. Level N depends only on levels < N.
        """
        if self.has_cycles():
            # Fallback if circular
            return {s.id: 0 for s in self.task.steps}

        levels: Dict[str, int] = {}
        for node in nx.topological_sort(self.g):
            preds = list(self.g.predecessors(node))
            if not preds:
                levels[node] = 0
            else:
                levels[node] = max(levels[p] for p in preds) + 1
        return levels

    def compute_critical_path(self) -> Tuple[List[str], int]:
        """
        Calculates the critical path (longest path through DAG based on estimated_days).
        Returns: (list_of_critical_step_ids, total_critical_days)
        """
        if self.has_cycles() or len(self.g) == 0:
            return [], 0

        # We construct a weighted graph where weight is estimated_days
        # Longest path in DAG can be solved by negating weights or standard topological dynamic programming
        topo_order = list(nx.topological_sort(self.g))
        
        # dist[u] = max days to reach and finish node u from an entry point
        dist: Dict[str, int] = {}
        parent: Dict[str, Optional[str]] = {}

        for node in topo_order:
            node_days = self.steps_dict[node].estimated_days
            preds = list(self.g.predecessors(node))
            if not preds:
                dist[node] = node_days
                parent[node] = None
            else:
                best_pred = max(preds, key=lambda p: dist[p])
                dist[node] = dist[best_pred] + node_days
                parent[node] = best_pred

        if not dist:
            return [], 0

        # Find the terminal node with max distance
        terminal_nodes = [n for n in self.g.nodes() if self.g.out_degree(n) == 0]
        if not terminal_nodes:
            terminal_nodes = list(self.g.nodes())

        end_node = max(terminal_nodes, key=lambda n: dist.get(n, 0))
        total_critical_days = dist[end_node]

        # Reconstruct path backwards
        curr: Optional[str] = end_node
        path: List[str] = []
        while curr:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

        return path, total_critical_days

    def resolve_roadmap(
        self,
        completed_step_ids: Set[str] = None,
        in_progress_step_ids: Set[str] = None
    ) -> RoadmapResponse:
        completed = completed_step_ids or set()
        in_progress = in_progress_step_ids or set()

        levels = self.compute_topological_levels()
        critical_path, total_crit_days = self.compute_critical_path()
        critical_set = set(critical_path)

        # Calculate phase titles
        phase_names = {
            0: ("Phase 1: Legal Identity & Primary Clearances", "Core prerequisite registrations, identity verification, and base statutory filings."),
            1: ("Phase 2: Premise Inspections & Department Clearances", "Parallel departmental clearances such as Fire, Health, Environment, and Zoning."),
            2: ("Phase 3: Formal Municipal Licensing", "Consolidated civic applications, scrutiny, fee disbursement, and biometric/site visits."),
            3: ("Phase 4: Operational Sanction & Signage", "Final sanction certificates, commercial occupancy, and public display permits."),
            4: ("Phase 5: Compliance Maintenance & Renewal", "Periodic audits, compliance filings, and annual renewal scheduling.")
        }

        # Level buckets for coordinate positioning
        level_buckets: Dict[int, List[str]] = {}
        for s in self.task.steps:
            lvl = levels.get(s.id, 0)
            level_buckets.setdefault(lvl, []).append(s.id)

        # Coordinate calculation: X corresponds to Level, Y distributed vertically
        x_spacing = 380
        y_spacing = 210
        nodes: List[GraphNode] = []

        unlocked_count = 0
        completed_count = len(completed)

        for lvl, step_ids in sorted(level_buckets.items()):
            n_in_lvl = len(step_ids)
            total_height = (n_in_lvl - 1) * y_spacing
            start_y = -total_height / 2.0

            for i, sid in enumerate(step_ids):
                step = self.steps_dict[sid]
                # Determine dynamic status
                if sid in completed:
                    status = StepStatus.COMPLETED
                elif sid in in_progress:
                    status = StepStatus.IN_PROGRESS
                else:
                    # Check if all prerequisites are completed
                    prereqs_done = all(p in completed for p in step.prerequisites)
                    if prereqs_done:
                        status = StepStatus.READY
                        unlocked_count += 1
                    else:
                        status = StepStatus.LOCKED

                x = lvl * x_spacing + 80
                y = start_y + (i * y_spacing) + 260

                nodes.append(GraphNode(
                    id=step.id,
                    step_number=step.step_number,
                    title=step.title,
                    department_name=step.department.name,
                    submission_mode=step.submission_mode.value,
                    estimated_days=step.estimated_days,
                    fee_amount=step.fee_amount,
                    status=status,
                    is_critical_path=(sid in critical_set),
                    phase_index=lvl,
                    x=round(x, 1),
                    y=round(y, 1),
                    prerequisites=step.prerequisites,
                    has_official_source=bool(step.verification_source.url),
                    confidence_score=step.verification_source.confidence_score
                ))

        # Build Edges
        edges: List[GraphEdge] = []
        for step in self.task.steps:
            for p in step.prerequisites:
                if p in self.steps_dict:
                    is_crit_edge = (p in critical_set and step.id in critical_set)
                    edges.append(GraphEdge(
                        id=f"edge-{p}-{step.id}",
                        source=p,
                        target=step.id,
                        is_critical=is_crit_edge,
                        dependency_type="Mandatory"
                    ))

        # Build Phases
        phases: List[GraphPhase] = []
        for lvl in sorted(level_buckets.keys()):
            title, desc = phase_names.get(lvl, (f"Phase {lvl+1}: Statutory Step", "Departmental procedure sequence."))
            phases.append(GraphPhase(
                phase_index=lvl,
                title=title,
                description=desc,
                step_ids=level_buckets[lvl]
            ))

        total_days = total_crit_days if total_crit_days > 0 else sum(s.estimated_days for s in self.task.steps)
        total_fees = sum(s.fee_amount for s in self.task.steps)

        # Build consolidated document inventory across all steps
        doc_map: Dict[str, ConsolidatedDocument] = {}
        for s in self.task.steps:
            for d in s.documents:
                doc_key = d.name.strip().lower()
                if doc_key not in doc_map:
                    doc_map[doc_key] = ConsolidatedDocument(
                        id=d.id,
                        name=d.name,
                        category=d.category or "General",
                        description=d.description,
                        validity_rule=d.validity_rule,
                        issuing_authority=d.issuing_authority,
                        is_mandatory=d.is_mandatory,
                        required_in_step_ids=[s.id],
                        required_in_step_numbers=[s.step_number]
                    )
                else:
                    if s.id not in doc_map[doc_key].required_in_step_ids:
                        doc_map[doc_key].required_in_step_ids.append(s.id)
                    if s.step_number not in doc_map[doc_key].required_in_step_numbers:
                        doc_map[doc_key].required_in_step_numbers.append(s.step_number)

        consolidated_docs = sorted(list(doc_map.values()), key=lambda doc: doc.category)

        return RoadmapResponse(
            task=self.task,
            nodes=nodes,
            edges=edges,
            phases=phases,
            total_estimated_days=total_days,
            total_estimated_fees=total_fees,
            critical_path_step_ids=critical_path,
            unlocked_count=unlocked_count,
            completed_count=completed_count,
            consolidated_documents=consolidated_docs
        )
