import runpy
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "verification/scripts/q3lock_completion_gate_audit.py"


class CompletionGateAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = runpy.run_path(str(SCRIPT), run_name="q3lock_completion_gate_test")

    def test_current_objective_coverage(self):
        payload = self.module["build_payload"]()
        self.assertEqual(payload["status"], "PASS")
        self.assertFalse(payload["claim_bearing"])
        self.assertEqual(payload["coverage"]["proof_audit_rows"], 23)
        self.assertEqual(payload["coverage"]["paper_pdf_count"], 0)
        self.assertEqual(
            payload["coverage"]["completion_state"],
            "INCOMPLETE_EXTERNAL_REVIEW_AND_FREEZE",
        )

    def test_hostile_mutations_rejected(self):
        payload = self.module["build_payload"]()
        self.assertEqual(
            [item["status"] for item in payload["hostile_checks"]],
            ["PASS", "PASS", "PASS", "PASS"],
        )

    def test_output_is_not_overwritten(self):
        payload = self.module["build_payload"]()
        with self.assertRaises(FileExistsError):
            self.module["write_new"](
                self.module["DEFAULT_OUTPUT"],
                payload,
            )


if __name__ == "__main__":
    unittest.main()