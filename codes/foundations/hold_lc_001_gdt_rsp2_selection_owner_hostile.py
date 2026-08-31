#!/usr/bin/env python3
"""Hostile mutation audit for the R-469 source-semantic firewall."""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "strategy/hold-lc-001-gdt-rsp2-selection-owner-v0.1.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-hostile-hold-lc-gdt-selection-owner/hostile.json"
import sys
sys.path.insert(0, str(REPO / "codes" / "foundations"))
from hold_lc_001_gdt_rsp2_selection_owner import digest, run, validate_report  # noqa: E402


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    baseline = run(contract)
    mutations: list[tuple[str, dict[str, Any]]] = []

    def add(name: str, change: Any) -> None:
        candidate = copy.deepcopy(baseline)
        change(candidate)
        mutations.append((name, candidate))

    add("wrong source commit", lambda x: x["source_pin"].__setitem__("commit", "0" * 40))
    add("wrong source hash", lambda x: x["source_pin"].__setitem__("source_sha256", "0" * 64))
    add("wrong parent hash", lambda x: x["parent_index"].__setitem__("sha256", "0" * 64))
    add("closed-overlap substitution", lambda x: x["source_checks"].__setitem__("implementation_doc_mismatch", False))
    add("center-distance promotion", lambda x: x["synthetic_probe"].__setitem__("doc_implementation_mismatch", False))
    add("endpoint selection admitted", lambda x: x["products"][0]["edge_probes"][0].__setitem__("selection_admitted", True))
    add("production selection", lambda x: x.__setitem__("selection_mode", "nearest"))
    add("matrix coefficient read", lambda x: x.__setitem__("matrix_coefficients_read", True))
    add("calibration admission", lambda x: x["admission"].__setitem__("calibration_interpolation_admitted", True))
    add("method overhaul", lambda x: x.__setitem__("methods_unchanged", False))
    add("prospective credit", lambda x: x.__setitem__("prospective_lock", "ADMITTED"))
    add("source owner admission", lambda x: x.__setitem__("source_owner_semantics_admitted", True))
    rejected = sum(not validate_report(candidate, contract) for _, candidate in mutations)
    if rejected != len(mutations):
        accepted = [name for name, candidate in mutations if validate_report(candidate, contract)]
        raise AssertionError(f"hostile mutation accepted: {accepted}")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "hostile", "audit_id": "HOLD-LC-001-GDT-RSP2-SELECTION-OWNER-HOSTILE", "claim_id": baseline["claim_id"], "task_id": baseline["task_id"], "holdout_id": baseline["holdout_id"], "verdict": "PASS", "claim_bearing": False, "methods_unchanged": True, "selection_mode": "NONE_SELECTED", "candidate_scoring": False, "prospective_lock": "EMPTY", "matrix_coefficients_read": False, "source_owner_semantics_admitted": False, "mutation_count": len(mutations), "mutations_rejected": rejected, "mutations": [{"name": name, "rejected": not validate_report(candidate, contract)} for name, candidate in mutations], "boundary": baseline["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"contract_sha256": digest(CONTRACT)}}
    if not args.self_test:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOLD-LC-GDT-RSP2-SELECTION OWNER HOSTILE: PASS {rejected}/{len(mutations)} mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
