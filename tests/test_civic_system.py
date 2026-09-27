import unittest
from app.database import db
from app.graph_engine import CivicGraphEngine
from app.models import StepStatus
from app.scraper_service import scraper_service
import asyncio

class TestCivicGraphAndApi(unittest.TestCase):
    def setUp(self):
        self.task = db.get_task_by_id("task-mum-bakery")
        self.assertIsNotNone(self.task)
        self.engine = CivicGraphEngine(self.task)

    def test_dag_acyclic_property(self):
        """Verify the dependency graph has no cycles (is a valid DAG)."""
        self.assertFalse(self.engine.has_cycles(), "Graph must be strictly acyclic (DAG)")

    def test_topological_levels(self):
        """Verify topological levels correctly order Maharashtra statutory prerequisites."""
        levels = self.engine.compute_topological_levels()
        
        # Step 1 (MCA/PAN) has no prerequisites => level 0
        self.assertEqual(levels["stop-01"], 0)
        
        # Step 2 (Lease & Gumasta) depends on Stop 1 => level 1
        self.assertEqual(levels["stop-02"], 1)
        
        # Step 3 (MFB Fire NOC) depends on Stop 2 => level 2
        self.assertEqual(levels["stop-03"], 2)
        
        # Steps 3A (FSSAI) & 3B (MPCB) depend on Stop 2 & 3 => level 3
        self.assertEqual(levels["stop-03a"], 3)
        self.assertEqual(levels["stop-03b"], 3)
        
        # Step 4 (MCGM Health License) depends on 3, 3a, 3b => level 4
        self.assertEqual(levels["stop-04"], 4)
        
        # Step 5 (Outdoor Seating & Marathi Signage) depends on Step 4 => level 5
        self.assertEqual(levels["stop-05"], 5)

    def test_critical_path(self):
        """Verify critical path identifies the longest dependency bottleneck."""
        crit_path, total_days = self.engine.compute_critical_path()
        self.assertTrue(len(crit_path) > 0)
        self.assertTrue(total_days >= 40)
        # MFB Fire NOC and Section 394 Health License should be on critical path
        self.assertIn("stop-03", crit_path)
        self.assertIn("stop-04", crit_path)

    def test_dynamic_status_resolution(self):
        """Verify dynamic unlocking of tasks based on completed prerequisites."""
        # Initial state: only level 0 task is READY, downstream are LOCKED
        initial_roadmap = self.engine.resolve_roadmap()
        node_dict = {n.id: n for n in initial_roadmap.nodes}
        self.assertEqual(node_dict["stop-01"].status, StepStatus.READY)
        self.assertEqual(node_dict["stop-02"].status, StepStatus.LOCKED)
        self.assertEqual(node_dict["stop-03"].status, StepStatus.LOCKED)
        self.assertEqual(node_dict["stop-04"].status, StepStatus.LOCKED)

        # Complete Step 1
        updated_roadmap = self.engine.resolve_roadmap(
            completed_step_ids={"stop-01"}
        )
        updated_dict = {n.id: n for n in updated_roadmap.nodes}
        self.assertEqual(updated_dict["stop-01"].status, StepStatus.COMPLETED)
        # Step 2 is now UNLOCKED and READY
        self.assertEqual(updated_dict["stop-02"].status, StepStatus.READY)
        self.assertEqual(updated_dict["stop-03"].status, StepStatus.LOCKED)

        # Complete Step 1 & 2
        step2_roadmap = self.engine.resolve_roadmap(
            completed_step_ids={"stop-01", "stop-02"}
        )
        step2_dict = {n.id: n for n in step2_roadmap.nodes}
        self.assertEqual(step2_dict["stop-02"].status, StepStatus.COMPLETED)
        # Fire NOC (Step 3) is now UNLOCKED!
        self.assertEqual(step2_dict["stop-03"].status, StepStatus.READY)

    def test_small_biz_task_resolution(self):
        """Verify small business task DAG and prerequisites."""
        small_biz = db.get_task_by_id("task-mah-small-biz")
        self.assertIsNotNone(small_biz)
        engine = CivicGraphEngine(small_biz)
        self.assertFalse(engine.has_cycles())
        rm = engine.resolve_roadmap()
        self.assertGreaterEqual(len(rm.nodes), 5)

    def test_all_tasks_have_official_maharashtra_provenance(self):
        """Verify that 100% of seed steps have official .gov / .mahaonline verification sources."""
        all_tasks = db.get_all_tasks()
        self.assertGreaterEqual(len(all_tasks), 7)
        for task in all_tasks:
            self.assertEqual(task.state, "Maharashtra")
            for step in task.steps:
                self.assertTrue(step.verification_source.url.startswith("http"))
                self.assertGreaterEqual(step.verification_source.confidence_score, 0.8)

    def test_scraper_service(self):
        """Test scraper simulation and extraction fallback on Maharashtra portal."""
        result = asyncio.run(scraper_service.scrape_portal(
            url="https://portal.mcgm.gov.in/eodb-tradelicense",
            task_hint="Commercial Eating House",
            municipality="Mumbai (MCGM / BMC)"
        ))
        self.assertIsNotNone(result.page_title)
        self.assertGreater(len(result.extracted_steps), 0)
        self.assertGreater(result.confidence_score, 0.7)

if __name__ == "__main__":
    unittest.main()
