from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/q3lock_review_locator_audit.py"
SPEC = spec_from_file_location("q3lock_review_locator_audit", SCRIPT)
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReviewLocatorAuditTests(unittest.TestCase):
    def test_current_coverage_resolves(self):
        payload = MODULE.build_payload()
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["coverage"]["row_count"], 23)
        self.assertGreaterEqual(payload["coverage"]["manuscript_locators_checked"], 23)
        self.assertEqual(len(payload["hostile_checks"]), 3)
        self.assertFalse(payload["claim_bearing"])
        self.assertEqual(payload["pdf_status"], "DEFERRED")

    def test_missing_label_is_rejected(self):
        matrix = MODULE.MATRIX.read_text(encoding="utf-8")
        manuscript = MODULE.MANUSCRIPT.read_text(encoding="utf-8")
        explorations = MODULE.EXPLORATIONS.read_text(encoding="utf-8")
        package = json.loads(MODULE.PACKAGE.read_text(encoding="utf-8"))
        mutated = manuscript.replace("\\label{eq:bounded-phase-witness}",
                                     "\\label{eq:bounded-phase-witness-removed}", 1)
        with self.assertRaises(ValueError):
            MODULE.validate_matrix(matrix, mutated, explorations, package)

    def test_no_overwrite_writer(self):
        with TemporaryDirectory() as folder:
            target = Path(folder) / "result.json"
            MODULE.write_new(target, {"status": "PASS"})
            before = target.read_bytes()
            with self.assertRaises(FileExistsError):
                MODULE.write_new(target, {"status": "REPLACED"})
            self.assertEqual(target.read_bytes(), before)
            self.assertEqual(list(Path(folder).glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
