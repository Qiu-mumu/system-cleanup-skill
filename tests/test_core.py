"""tests/test_core.py -- Core functionality tests"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cli import cleanup

class TestConfig(unittest.TestCase):
    def test_config_exists(self):
        config = cleanup.load_config()
        self.assertGreater(len(config), 0)

    def test_config_has_required_keys(self):
        config = cleanup.load_config()
        for key, entry in config.items():
            self.assertIn("paths", entry)
            self.assertIn("risk", entry)
            self.assertIn("desc", entry)

class TestSafety(unittest.TestCase):
    def test_absolute_fuses_not_empty(self):
        self.assertGreater(len(cleanup.ABSOLUTE_FUSES), 0)

class TestScan(unittest.TestCase):
    def test_scan_returns_list(self):
        config = cleanup.load_config()
        results = cleanup.scan(config)
        self.assertIsInstance(results, list)

if __name__ == "__main__":
    unittest.main()

