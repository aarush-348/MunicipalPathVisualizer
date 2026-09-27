import os
import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database_sqlite import sqlite_db

class TestSQLitePersistence(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_database_stats_endpoint(self):
        resp = self.client.get("/api/db/stats")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("aaple_sarkar_services", data)
        self.assertGreaterEqual(data["aaple_sarkar_services"], 18)
        self.assertGreaterEqual(data["tasks"], 7)
        self.assertGreaterEqual(data["steps"], 25)

    def test_aaple_sarkar_search_endpoint(self):
        resp = self.client.get("/api/db/aaple-sarkar?q=Income")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(len(data) > 0)
        self.assertIn("Income", data[0]["service_name"])

    def test_user_progress_save_and_load(self):
        session_id = "test_user_session_42"
        task_id = "task-mah-small-biz"
        payload = {
            "session_id": session_id,
            "task_id": task_id,
            "completed_step_ids": ["mah-biz-1"],
            "in_progress_step_ids": ["mah-biz-2"]
        }
        post_resp = self.client.post("/api/user/progress", json=payload)
        self.assertEqual(post_resp.status_code, 200)

        get_resp = self.client.get(f"/api/user/progress?session_id={session_id}&task_id={task_id}")
        self.assertEqual(get_resp.status_code, 200)
        saved = get_resp.json()
        self.assertEqual(saved["completed_step_ids"], ["mah-biz-1"])
        self.assertEqual(saved["in_progress_step_ids"], ["mah-biz-2"])

if __name__ == "__main__":
    unittest.main()
