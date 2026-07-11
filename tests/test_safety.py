"""test_safety.py — Fuse list and path protection"""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cli.cleanup import ABSOLUTE_FUSES

class TestAbsoluteFuses(unittest.TestCase):
    def test_winsxs_is_protected(self):
        self.assertTrue(
            any("WinSxS" in f for f in ABSOLUTE_FUSES),
            "WinSxS must be in absolute fuses"
        )

    def test_pagefile_is_protected(self):
        self.assertTrue(
            any("pagefile" in f for f in ABSOLUTE_FUSES),
            "pagefile.sys must be in absolute fuses"
        )

    def test_temps_not_accidentally_fused(self):
        """Verify TEMP dirs are NOT in the fuse list"""
        fused_lower = [f.lower() for f in ABSOLUTE_FUSES]
        temp_entries = [f for f in fused_lower if "temp" in f]
        # TEMP should not be in fuses (it's safe to clean)
        self.assertEqual(len(temp_entries), 0,
            f"TEMP appears in fuses: {temp_entries}")

    def test_hibernation_protected(self):
        self.assertTrue(
            any("hiberfil" in f for f in ABSOLUTE_FUSES),
            "hiberfil.sys must be protected"
        )

class TestFuseFormat(unittest.TestCase):
    def test_all_fuses_are_paths(self):
        for f in ABSOLUTE_FUSES:
            self.assertIsInstance(f, str)

if __name__ == "__main__":
    unittest.main()
