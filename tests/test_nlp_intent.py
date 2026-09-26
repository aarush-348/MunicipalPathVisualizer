import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db
from app.nlp_engine import nlp_engine

class TestNLPIntentEngine(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        nlp_engine.index_tasks(db.get_all_tasks())

    def test_catalog_exact_match(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "Register & Commission a Commercial Bakery in Bandra, Mumbai"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["top_task_id"], "task-mum-bakery")
        self.assertGreater(data["matches"][0]["confidence"], 0.7)

    def test_catalog_semantic_match_construction(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "building permit autodcr mumbai"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["top_task_id"], "task-mum-construction")

    def test_hinglish_shop_intent(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "dukaan shuru karni hai"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["hinglish_detected"])
        self.assertTrue("task-synth-gumasta-trade" in data["top_task_id"])

    def test_devanagari_hindi_intent(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "दुकान शुरू करनी है"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["hinglish_detected"])
        self.assertEqual(data["top_task_id"], "task-synth-gumasta-trade")

    def test_zero_shot_voter_id_synthesis(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "making a new voter id"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        top_id = data["top_task_id"]
        self.assertTrue("voter-id" in top_id)
        self.assertEqual(data["matches"][0]["match_type"], "synthesized")

        # Test roadmap generation for synthesized task
        rm_resp = self.client.post(f"/api/tasks/{top_id}/roadmap", json={})
        self.assertEqual(rm_resp.status_code, 200)
        rm_data = rm_resp.json()
        self.assertGreater(len(rm_data["nodes"]), 0)
        self.assertGreater(len(rm_data["consolidated_documents"]), 0)

    def test_zero_shot_ration_card_synthesis(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "ration card renewal"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue("ration-card" in data["top_task_id"])

    def test_zero_shot_pharmacy_synthesis(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "open a pharmacy"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue("pharmacy" in data["top_task_id"])

if __name__ == "__main__":
    unittest.main()
