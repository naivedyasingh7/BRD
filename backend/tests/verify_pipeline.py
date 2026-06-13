import os
import unittest
import sqlite3
import shutil
from fastapi.testclient import TestClient
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.main import app
from backend.services.config import is_groq_configured, is_sarvam_configured
from backend.api.schemas import ClarifyRequest, BRDStateResponse
from backend.graph.workflow import graph
from backend.database import (
    DATABASE_PATH,
    init_db,
    save_brd,
    save_clarification,
    save_audit_log,
    get_all_brds,
    get_brd_by_id,
    get_project_history,
    get_audit_trail
)


class TestBRDGenieBackend(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.db_backup_path = DATABASE_PATH + ".bak"
        if os.path.exists(DATABASE_PATH):
            shutil.copy2(DATABASE_PATH, cls.db_backup_path)
            os.remove(DATABASE_PATH)
        init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)
        if os.path.exists(cls.db_backup_path):
            shutil.copy2(cls.db_backup_path, DATABASE_PATH)
            os.remove(cls.db_backup_path)

    def test_database_versioning_and_auditing(self):
        project_name = "Verification Test Project"
        language = "English"
        raw_input = "Original prompt transcript text"
        cleaned_input = "Cleaned English transcript text"
        english_brd = "# Executive Summary\nTest BRD content v1"
        brd_id_1 = save_brd(
            project_name=project_name,
            raw_input=raw_input,
            cleaned_input=cleaned_input,
            english_brd=english_brd,
            localized_brd=english_brd,
            language=language
        )
        self.assertIsNotNone(brd_id_1)
        brd_id_2 = save_brd(
            project_name=project_name,
            raw_input=raw_input,
            cleaned_input=cleaned_input,
            english_brd="# Executive Summary\nTest BRD content v2",
            localized_brd="# Executive Summary\nTest BRD content v2",
            language=language
        )
        self.assertIsNotNone(brd_id_2)
        self.assertNotEqual(brd_id_1, brd_id_2)
        history = get_project_history(project_name)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["version"], "v1.1.0")
        self.assertEqual(history[1]["version"], "v1.0.0")
        save_clarification(project_name, "Q1: Is security high?", "A1: Yes, very.")
        save_audit_log(
            project_name=project_name,
            request_id="test-req-123",
            step_name="Discovery: Context",
            agent_role="Context Understanding Analyst",
            input_data="Cleaned text",
            output_data="Context summary output text",
            duration=1.452,
            status="Success"
        )
        audit_trail = get_audit_trail(project_name)
        self.assertEqual(len(audit_trail), 1)
        self.assertEqual(audit_trail[0]["agent_role"], "Context Understanding Analyst")
        self.assertEqual(audit_trail[0]["status"], "Success")
        self.assertEqual(audit_trail[0]["duration_seconds"], 1.452)

    def test_graph_compilation(self):
        self.assertIsNotNone(graph)
        nodes = graph.nodes
        self.assertIn("input", nodes)
        self.assertIn("extract", nodes)
        self.assertIn("clarify", nodes)
        self.assertIn("generate", nodes)
        self.assertIn("localize", nodes)

    def test_api_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["status"], "ok")
        self.assertIn("agents_ready", json_data)

    def test_api_history_endpoint(self):
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_schemas_validation(self):
        mock_payload = {
            "state": {
                "raw_input": "Test text",
                "cleaned_input": "Test text",
                "questions": ["Q1?"],
                "answers": [],
                "brd_draft": "",
                "final_brd": "",
                "language": "English",
                "localized_brd": "",
                "request_id": "req-123",
                "project_name": "Test project",
                "db_id": None,
                "context_analysis": "",
                "extracted_requirements": "",
                "stakeholder_analysis": "",
                "ambiguities_analysis": "",
                "risks_analysis": "",
                "structured_outline": "",
                "qa_review": "",
                "agent_traces": []
            },
            "answers": ["A1"]
        }
        
        obj = ClarifyRequest(**mock_payload)
        self.assertEqual(obj.answers, ["A1"])
        self.assertEqual(obj.state["request_id"], "req-123")


if __name__ == "__main__":
    unittest.main()
