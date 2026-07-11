"""test_report.py — HTML template integrity"""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cli.report import TEMPLATE

class TestTemplatePlaceholders(unittest.TestCase):
    required = [
        "TOTAL_GB_PLACEHOLDER",
        "GPU_STATUS_PLACEHOLDER",
        "TABLE_ROWS_PLACEHOLDER",
        "LABELS_PLACEHOLDER",
        "DATA_GB_PLACEHOLDER",
        "COLORS_PLACEHOLDER",
        "DISK_FREE_PLACEHOLDER",
        "DISK_PCT_PLACEHOLDER",
        "SNAPSHOT_HTML_PLACEHOLDER",
    ]

    def test_all_placeholders_present(self):
        for p in self.required:
            with self.subTest(placeholder=p):
                self.assertIn(p, TEMPLATE)

    def test_html_document_structure(self):
        self.assertIn("<html", TEMPLATE)
        self.assertIn("<head>", TEMPLATE)
        self.assertIn("<body>", TEMPLATE)
        self.assertIn("</html>", TEMPLATE)

    def test_chart_js_loaded(self):
        self.assertIn("chart.js", TEMPLATE)

    def NOT_USED_bilingual_toggle_present(self):
        self.assertIn("setLang", TEMPLATE)
        self.assertIn("btn-zh", TEMPLATE)
        self.assertIn("class=\\\"zh\\\"", TEMPLATE)

    def test_comparison_grid_styles_present(self):
        self.assertIn("comp-grid", TEMPLATE)
        self.assertIn("delta .up", TEMPLATE)
        self.assertIn("delta .down", TEMPLATE)

if __name__ == "__main__":
    unittest.main()
