#!/usr/bin/env python3
"""Hostile mutation audit for the HOLD-LC-001 rsp2 segment index."""

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
CONTRACT = REPO / "strategy/hold-lc-001-rsp2-segment-index-contract-v0.1.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-hostile-hold-lc-rsp2-segment-index/hostile.json"
import sys
sys.path.insert(0, str(REPO / "codes" / "foundations"))
from hold_lc_001_rsp2_segment_index import digest, run, validate_report  # noqa: E402


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    baseline = run(contract)
    mutations: list[tuple[str, dict[str, Any]]] = []

    def add(name: str, change: Any) -> None:
        candidate = copy.deepcopy(baseline)
        change(candidate)
        mutations.append((name, candidate))

    add("wrong product hash", lambda x: x["products"][0].__setitem__("actual_sha256", "0" * 64))
    add("segment renumbering", lambda x: x["products"][0]["segments"][0].__setitem__("rsp_num", 99))
    add("overlapping interval", lambda x: x["products"][0]["segments"][1].__setitem__("tstart_met", x["products"][0]["segments"][0]["tstart_met"]))
    add("missing covering alternative", lambda x: x["products"][0]["query_selection_alternatives"][0].__setitem__("covering_rsp_nums", []))
    add("missing interpolation bracket", lambda x: x["products"][0]["query_selection_alternatives"][0].__setitem__("interpolation_bracket", None))
    add("matrix coefficient admission", lambda x: x.__setitem__("matrix_coefficients_read", True))
    add("candidate scoring", lambda x: x.__setitem__("candidate_scoring", True))
    add("production response selection", lambda x: x.__setitem__("selection_mode", "nearest"))
    add("candidate-dependent query", lambda x: x["products"][0]["query_selection_alternatives"][0].__setitem__("relative_offset_s", 999))
    add("prospective credit", lambda x: x.__setitem__("prospective_lock", "ADMITTED"))
    rejected = sum(not validate_report(candidate, contract) for _, candidate in mutations)
    if rejected != len(mutations):
        accepted = [name for name, candidate in mutations if validate_report(candidate, contract)]
        raise AssertionError(f"hostile mutation accepted: {accepted}")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "hostile", "audit_id": "HOLD-LC-001-RSP2-SEGMENT-INDEX-HOSTILE", "claim_id": baseline["claim_id"], "task_id": baseline["task_id"], "holdout_id": baseline["holdout_id"], "verdict": "PASS", "mutation_count": len(mutations), "mutations_rejected": rejected, "mutations": [{"name": name, "rejected": not validate_report(candidate, contract)} for name, candidate in mutations], "boundary": baseline["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"contract_sha256": digest(CONTRACT)}}
    if not args.self_test:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOLD-LC-RSP2-INDEX HOSTILE: PASS {rejected}/{len(mutations)} mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
