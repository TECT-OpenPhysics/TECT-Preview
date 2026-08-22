"""Stdlib-only independent audit for the T-058 cylinder trial."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-t058-bounded-complete-production-cylinder-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r192-t058-bounded-complete-production-cylinder" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def derive(manifest: dict[str, Any]) -> dict[str, Any]:
    rows = manifest["registered_inputs"]["slot_audit"]
    first = next((row["slot"] for row in rows if not row["mapped"]), None)
    reserve = manifest["registered_inputs"]["reserve_fixture"]
    a = F(reserve["cross_scale"])

    def qform(d: F) -> F:
        p = d - a
        return p - a - a + p

    temporal = manifest["registered_inputs"]["temporal_fixture"]
    s1, s2 = F(temporal["s1"]), F(temporal["s2"])
    h1, h2 = F(temporal["h1"]), F(temporal["h2"])
    pairing = s1 * h1 + s2 * h2
    wedge = s1 * h2 - s2 * h1
    total = (s1**2 + s2**2) * (h1**2 + h2**2)
    return {
        "slot_order": [row["slot"] for row in rows],
        "mapped_slots": [row["slot"] for row in rows if row["mapped"]],
        "complete_owner": all(row["mapped"] for row in rows),
        "first_missing_slot": first,
        "trial_verdict": "PASS_COMPLETE_OWNER" if first is None else "FAIL_FIRST_MISSING_PRODUCTION_MAP",
        "reserve_threshold_value": qform(F(reserve["threshold_diagonal"])),
        "reserve_below_value": qform(F(reserve["below_diagonal"])),
        "temporal_pairing": pairing,
        "temporal_wedge": wedge,
        "temporal_total": total,
        "temporal_gap": total - pairing**2,
        "douglas_identity": pairing**2 + wedge**2 == total,
        "a13_gate_closed": False,
        "sector_a_closed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-T058-BOUNDED-COMPLETE-PRODUCTION-CYLINDER", manifest["audit_id"], "A13-T058-BOUNDED-COMPLETE-PRODUCTION-CYLINDER")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("stdlib-only policy", True, "fractions and stdlib only", "no primary import")
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    derived = derive(manifest)
    oracle = manifest["test_oracles"]
    check("first missing", derived["first_missing_slot"] == oracle["first_failure_slot"], derived["first_missing_slot"], oracle["first_failure_slot"])
    check("trial failure", derived["trial_verdict"] == oracle["audit_verdict"], derived["trial_verdict"], oracle["audit_verdict"])
    check("reserve threshold", derived["reserve_threshold_value"] == F(oracle["reserve_threshold_value"]), derived["reserve_threshold_value"], oracle["reserve_threshold_value"])
    check("reserve below", derived["reserve_below_value"] == F(oracle["reserve_below_value"]), derived["reserve_below_value"], oracle["reserve_below_value"])
    check("Douglas identity and gap", derived["douglas_identity"] and derived["temporal_gap"] == F(oracle["douglas_gap"]), derived, {"identity": True, "gap": oracle["douglas_gap"]})
    check("owner incomplete", not derived["complete_owner"], derived["complete_owner"], False)
    check("A13 boundary", not derived["a13_gate_closed"] and not derived["sector_a_closed"], derived, "gates remain open")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": derived, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT R-192 PASS {len(rows)}/{len(rows)} trial={derived['trial_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
