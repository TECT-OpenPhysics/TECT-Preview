from __future__ import annotations

import json
from pathlib import Path
import runpy

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "verification/scripts/q3lock_kp_envelope_audit.py"
OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-q3lock-kp-envelope-audit-v001/result.json"
)


def test_kp_envelope_audit_current_payload() -> None:
    module = runpy.run_path(str(SCRIPT), run_name="test_kp_envelope")
    payload = module["build_payload"]()
    assert payload["status"] == "PASS"
    assert payload["claim_bearing"] is False
    assert payload["tier"] == "T0"
    assert payload["exploration_id"] == "EXP-001662"
    assert payload["assertions_passed"] > 20
    assert len(payload["hostile_checks"]) == 4
    assert json.loads(OUTPUT.read_text(encoding="utf-8")) == payload


def test_kp_envelope_hostile_inputs_reject() -> None:
    module = runpy.run_path(str(SCRIPT), run_name="test_kp_envelope_hostile")
    checks = module["hostile_fixture"](module["derived_constants"]())
    assert all(row["status"] == "PASS" and row["expected"] == "rejected" for row in checks)


def test_kp_envelope_output_is_not_overwritten() -> None:
    module = runpy.run_path(str(SCRIPT), run_name="test_kp_envelope_no_overwrite")
    payload = module["build_payload"]()
    with pytest.raises(FileExistsError):
        module["write_new"](OUTPUT, payload)
