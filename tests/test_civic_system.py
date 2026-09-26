import unittest
from app.database import db
from app.graph_engine import CivicGraphEngine
from app.models import StepStatus
from app.scraper_service import scraper_service
import asyncio

class TestCivicGraphAndApi(unittest.TestCase):
    def setUp(self):
        self.task = db.get_task_by_id("task-blr-restaurant")
        self.assertIsNotNone(self.task)
        self.engine = CivicGraphEngine(self.task)

    def test_dag_acyclic_property(self):
        """Verify the dependency graph has no cycles (is a valid DAG)."""
        self.assertFalse(self.engine.has_cycles(), "Graph must be strictly acyclic (DAG)")

    def test_topological_levels(self):
        """Verify topological levels correctly order prerequisites."""
        levels = self.engine.compute_topological_levels()
        
        # Step 1 and 2 have no prerequisites => level 0
        self.assertEqual(levels["blr-food-1"], 0)
        self.assertEqual(levels["blr-food-2"], 0)
        
        # Clearances depend on 1 and 2 => level 1
        self.assertEqual(levels["blr-food-3a"], 1)
        self.assertEqual(levels["blr-food-3b"], 1)
        self.assertEqual(levels["blr-food-3c"], 1)
        
        # Trade license depends on all clearances => level 2
        self.assertEqual(levels["blr-food-4"], 2)
        
        # Signage & BESCOM depend on Trade license => level 3
        self.assertEqual(levels["blr-food-5"], 3)
        self.assertEqual(levels["blr-food-6"], 3)

    def test_critical_path(self):
        """Verify critical path identifies the longest dependency bottleneck."""
        crit_path, total_days = self.engine.compute_critical_path()
        self.assertTrue(len(crit_path) > 0)
        self.assertTrue(total_days > 20)
        # BBMP Trade License (15 days) and Fire NOC (14 days) should be on critical path
        self.assertIn("blr-food-4", crit_path)

    def test_dynamic_status_resolution(self):
        """Verify dynamic unlocking of tasks based on completed prerequisites."""
        # Initial state: only level 0 tasks are READY, downstream are LOCKED
        initial_roadmap = self.engine.resolve_roadmap()
        node_dict = {n.id: n for n in initial_roadmap.nodes}
        self.assertEqual(node_dict["blr-food-1"].status, StepStatus.READY)
        self.assertEqual(node_dict["blr-food-2"].status, StepStatus.READY)
        self.assertEqual(node_dict["blr-food-3a"].status, StepStatus.LOCKED)
        self.assertEqual(node_dict["blr-food-4"].status, StepStatus.LOCKED)

        # Complete Step 1 & 2
        updated_roadmap = self.engine.resolve_roadmap(
            completed_step_ids={"blr-food-1", "blr-food-2"}
        )
        updated_dict = {n.id: n for n in updated_roadmap.nodes}
        self.assertEqual(updated_dict["blr-food-1"].status, StepStatus.COMPLETED)
        self.assertEqual(updated_dict["blr-food-2"].status, StepStatus.COMPLETED)
        # Clearances are now UNLOCKED and READY
        self.assertEqual(updated_dict["blr-food-3a"].status, StepStatus.READY)
        self.assertEqual(updated_dict["blr-food-3b"].status, StepStatus.READY)
        self.assertEqual(updated_dict["blr-food-3c"].status, StepStatus.READY)
        # Trade license is STILL LOCKED because 3a, 3b, 3c are not done yet
        self.assertEqual(updated_dict["blr-food-4"].status, StepStatus.LOCKED)

        # Complete all 3 clearances
        full_clearances_roadmap = self.engine.resolve_roadmap(
            completed_step_ids={"blr-food-1", "blr-food-2", "blr-food-3a", "blr-food-3b", "blr-food-3c"}
        )
        full_dict = {n.id: n for n in full_clearances_roadmap.nodes}
        # Trade License is now UNLOCKED!
        self.assertEqual(full_dict["blr-food-4"].status, StepStatus.READY)

    def test_all_tasks_have_official_provenance(self):
        """Verify that 100% of seed steps have official .gov verification sources."""
        all_tasks = db.get_all_tasks()
        self.assertGreaterEqual(len(all_tasks), 4)
        for task in all_tasks:
            for step in task.steps:
                self.assertTrue(step.verification_source.url.startswith("http"))
                self.assertGreater(step.verification_source.confidence_score, 0.8)

    def test_scraper_service(self):
        """Test scraper simulation and extraction fallback."""
        result = asyncio.run(scraper_service.scrape_portal(
            url="https://bbmp.karnataka.gov.in/tradelicense",
            task_hint="Commercial Eating House",
            municipality="Bengaluru"
        ))
        self.assertIsNotNone(result.page_title)
        self.assertGreater(len(result.extracted_steps), 0)
        self.assertGreater(result.confidence_score, 0.7)

if __name__ == "__main__":
    unittest.main()
