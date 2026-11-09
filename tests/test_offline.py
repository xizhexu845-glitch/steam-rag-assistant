import json
import unittest
from pathlib import Path
from unittest.mock import patch
from DataProcess.steam_json_process import json_to_docs
from agent.zhipu_fuc import get_qa_history_chain

class OfflineTests(unittest.TestCase):
    def test_synthetic_data_normalization(self):
        payload = json.loads(Path("examples/games.synthetic.json").read_text())
        docs = json_to_docs(payload)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]["id"], "demo-001")
        self.assertIn("Moon Garden", docs[0]["content"])
        self.assertLessEqual(len(docs[0]["content"]), 803)
    def test_empty_input(self):
        self.assertEqual(json_to_docs([]), [])
    def test_missing_key_rejected(self):
        with self.assertRaises(ValueError):
            get_qa_history_chain(api_key=None)

if __name__ == "__main__":
    unittest.main()
