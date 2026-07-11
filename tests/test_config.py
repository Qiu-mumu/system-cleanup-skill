"""test_config.py — Config structure and data integrity"""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cli.cleanup import load_config

class TestConfigStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config()

    def test_entries_have_required_keys(self):
        for key, entry in self.config.items():
            with self.subTest(entry=key):
                self.assertIn("paths", entry)
                self.assertIn("risk", entry)
                self.assertIn("desc", entry)
                self.assertIn("clean_cmd", entry)

    def test_all_risks_are_valid(self):
        valid = {"safe", "low", "medium", "high"}
        for key, entry in self.config.items():
            with self.subTest(entry=key):
                self.assertIn(entry["risk"], valid)

    def test_all_paths_use_env_vars(self):
        # These paths have no env var (system paths, game library paths)
        KNOWN_LITERAL = {"recycle_bin", "steam_shader"}
        for key, entry in self.config.items():
            if key in KNOWN_LITERAL:
                continue
            for path in entry["paths"]:
                with self.subTest(path=path):
                    self.assertIn("%", path, 
                        f"{key}: path uses literal path, not env var: {path}")

    def test_no_duplicate_keys(self):
        keys = list(self.config.keys())
        self.assertEqual(len(keys), len(set(keys)))

class TestConfigCoverage(unittest.TestCase):
    def test_known_software_covered(self):
        config = load_config()
        known = {"pip", "npm", "nvidia", "wechat", "chrome", "temp", "npm"}
        found = set(k for d in known for k in config if d in k.lower())
        self.assertGreaterEqual(len(found), 4,
            f"Expected at least 4 well-known software entries, found {len(found)}")

if __name__ == "__main__":
    unittest.main()
