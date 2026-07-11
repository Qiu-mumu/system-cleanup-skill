"""test_scan.py — Scan logic in isolated environments"""
import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cli.cleanup import load_config, scan

class TestScanIsolated(unittest.TestCase):
    def test_scan_returns_list(self):
        config = load_config()
        results = scan(config)
        self.assertIsInstance(results, list)

    def test_scan_entry_has_required_fields(self):
        config = load_config()
        results = scan(config)
        if results:
            r = results[0]
            for field in ("key", "path", "size_mb", "risk", "symlink", "locked", "fuse"):
                self.assertIn(field, r, f"Missing field: {field}")

class TestScanEmptyConfig(unittest.TestCase):
    def test_empty_config_returns_empty(self):
        results = scan({})
        self.assertEqual(len(results), 0)

if __name__ == "__main__":
    unittest.main()
