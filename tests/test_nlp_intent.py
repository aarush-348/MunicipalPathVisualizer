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

    def test_small_business_natural_language_query(self):
        """Test user request primary query: 'I want to register a small business'"""
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "I want to register a small business"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["top_task_id"], "task-mah-small-biz")
        self.assertGreaterEqual(data["matches"][0]["confidence"], 0.8)

    def test_catalog_semantic_match_construction(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "building permit autodcr mumbai"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["top_task_id"], "task-mum-construction")

    def test_land_mutation_712_match(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "7/12 extract transfer ferfar"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["top_task_id"], "task-mah-712-mutation")

    def test_water_connection_match(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "new water connection BMC"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["top_task_id"], "task-mum-water-connection")

    def test_pune_restaurant_match(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "Open a restaurant in Pune"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["top_task_id"], "task-pune-restaurant")

    def test_hinglish_shop_intent(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "dukaan shuru karni hai"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["hinglish_detected"])
        self.assertTrue(data["top_task_id"] in ["task-mah-small-biz", "task-synth-gumasta-trade"])

    def test_devanagari_marathi_shop_intent(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "दुकान नोंदणी गुमास्ता"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["hinglish_detected"])
        self.assertEqual(data["top_task_id"], "task-mah-small-biz")

    def test_romanized_marathi_shop_intent(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "mala dukan suru karayche ahe"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["hinglish_detected"])
        self.assertEqual(data["top_task_id"], "task-mah-small-biz")

    def test_devanagari_satbara_intent(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "सातबारा फेरफार नोंदणी"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["top_task_id"], "task-mah-712-mutation")

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

    def test_regional_birth_certificate_not_bakery(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "How to get birth certificate correction done in BMC K-West Andheri ward?"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertNotEqual(data["top_task_id"], "task-mum-bakery")
        self.assertTrue("birth" in data["top_task_id"] or "vital" in data["top_task_id"])

    def test_regional_pune_property_tax_not_restaurant(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "PMC Pune peth area property tax assessment and rebate claim"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertNotEqual(data["top_task_id"], "task-pune-restaurant")
        self.assertTrue("property" in data["top_task_id"] or "mutation" in data["top_task_id"])

    def test_regional_haveli_domicile_rts(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "Apply for Domicile and Nationality certificate in Haveli Taluka, Pune"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertNotEqual(data["top_task_id"], "task-pune-restaurant")
        self.assertTrue(data["top_task_id"] in ["task-mah-rts-certificates", "task-synth-domicile-cert", "task-synth-rts-dakhla"])

    def test_regional_baramati_non_creamy_layer_not_pet_clinic(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "Non-creamy layer certificate application Baramati sub-division"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertNotEqual(data["top_task_id"], "task-synth-bmc-pet-clinic")
        self.assertTrue("pet" not in data["top_task_id"])
        self.assertTrue("ncl" in data["top_task_id"] or "rts" in data["top_task_id"] or "caste" in data["top_task_id"])

    def test_regional_thane_property_tax_mutation_not_712(self):
        resp = self.client.post("/api/tasks/resolve-intent", json={
            "query": "Thane municipal corporation property tax name transfer mutation"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertNotEqual(data["top_task_id"], "task-mah-712-mutation")
        self.assertTrue("property" in data["top_task_id"] or "mutation" in data["top_task_id"])

if __name__ == "__main__":
    unittest.main()


