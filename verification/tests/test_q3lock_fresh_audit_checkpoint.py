"""Regression tests for the non-overwriting Q3LOCK audit checkpoint."""
from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODULE = runpy.run_path(
    str(ROOT / "verification/scripts/q3lock_fresh_audit_checkpoint.py"),
    run_name="q3lock_fresh_audit_checkpoint_test",
)
CURRENT_LABEL = "2026-09-07-q3lock-manuscript-fresh-audit-r8-literature-handoff"


class TestQ3LockFreshAuditCheckpoint(unittest.TestCase):
    def test_checkpoint_validates(self):
        payload = MODULE["validate_checkpoint"](CURRENT_LABEL)
        self.assertEqual(payload["audit_count"], len(MODULE["AUDIT_SPECS"]))
        self.assertGreater(payload["total_assertions"], 0)
        self.assertTrue(payload["protected_records_preserved"])

    def test_existing_checkpoint_rejects_overwrite(self):
        with self.assertRaises(FileExistsError):
            MODULE["build_payload"](CURRENT_LABEL)


if __name__ == "__main__":
    unittest.main()
