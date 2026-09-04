#!/usr/bin/env python3
"""Hostile mutation firewall for PAH-OMC-014 R498.

All mutations are in-memory copies.  No parent, manifest, registry or source
file is modified.  The firewall checks that unauthorized source-law, model,
status, hash and boundary-cancellation mutations are rejected.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-boundary-error-lean-manifest.json"
LEAN = ROOT / "verification/lean/Tect/R498.lean"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-boundary-error-lean/hostile.json"
AUDIT_ID = "PAH-OMC-014-BOUNDARY-ERROR-LEAN-HOSTILE-001"
LEAN_HASH = "fa7cb4d28de1ffd19eb9bc2ddc8a89e24b0f93f6f070204d5872063770773ac5"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def accepts(manifest: dict[str, Any]) -> bool:
    provenance = manifest.get("provenance", {})
    status = manifest.get("status", {})
    treatment = manifest.get("boundary_contract", {}).get("treatment", "").lower()
    lean = manifest.get("lean", {})
    return (
        provenance.get("source_law_present") is False
        and provenance.get("claim_bearing") is False
        and provenance.get("physical_authority") is False
        and provenance.get("model_change") is False
        and provenance.get("parent_mutation") is False
        and status.get("verdict") == "HOLD_FOR_EVIDENCE"
        and status.get("active_gate_change") is False
        and status.get("claim_bearing") is False
        and "not averaged" in treatment
        and "counterterm" in treatment
        and lean.get("sha256") == LEAN_HASH
    )


def main() -> int:
    original = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    check("baseline accepted", accepts(original), True, True)
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("source law injected", lambda m: m["provenance"].__setitem__("source_law_present", True)),
        ("claim-bearing promotion", lambda m: m["provenance"].__setitem__("claim_bearing", True)),
        ("model term changed", lambda m: m["provenance"].__setitem__("model_change", True)),
        ("parent mutation enabled", lambda m: m["provenance"].__setitem__("parent_mutation", True)),
        ("status promoted", lambda m: m["status"].__setitem__("verdict", "MAINLINE_ADVANCE")),
        ("active gate changed", lambda m: m["status"].__setitem__("active_gate_change", True)),
        ("boundary averaged", lambda m: m["boundary_contract"].__setitem__("treatment", "The defect is averaged away and replaced by a counterterm.")),
        ("Lean hash tampered", lambda m: m["lean"].__setitem__("sha256", "0" * 64)),
    ]
    for name, mutate in mutations:
        candidate = copy.deepcopy(original)
        mutate(candidate)
        check(name, not accepts(candidate), accepts(candidate), False)

    check("source file digest unchanged", sha(LEAN) == LEAN_HASH, sha(LEAN), LEAN_HASH)
    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-boundary-error-lean-hostile/1.0",
        "run_kind": "hostile_mutation_firewall",
        "audit_id": AUDIT_ID,
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "result_id": None,
        "exploration_id": None,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "CONDITIONAL_SUPPORT_ONLY",
        "claim_bearing": False,
        "active_gate_change": False,
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "R498": sha(LEAN)},
        "non_claims": [
            "Mutation rejection does not prove a full-Q Gibbs state or a PAH boundary estimate.",
            "No physical Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap or TOE conclusion follows.",
        ],
        "next_question": "Can a source owner prove the actual PAH boundary_error sequence tends to zero without any mutation rejected by this firewall?",
    }
    atomic_json(OUTPUT, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())