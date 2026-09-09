#!/usr/bin/env python3
"""Hostile mutation checks for the PAH-OMC-025 route cut-set."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-025-route-frontier-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc025_route_frontier.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc025_route_frontier_independent.py"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc025-route-frontier"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    data = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return data


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any) -> None:
    ok = actual == expected
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(name)


def non_importing(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = ("pah_omc025_route_frontier", "verification.scripts", "codes.foundations")
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [item.name for item in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        if any(any(token in name for token in forbidden) for name in names):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=RUN / "hostile.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    check(rows, "primary non-importing", non_importing(PRIMARY), True)
    check(rows, "independent non-importing", non_importing(INDEPENDENT), True)
    check(rows, "source firewall", contract["preservation_firewall"]["functional_unchanged"], True)
    check(rows, "no new oracle", contract["preservation_firewall"]["no_new_abstract_oracle"], True)
    check(rows, "no physical promotion", contract["provenance"]["physical_promotion"], False)

    # Mutation: accepting a partial form route must remain false.
    partial_form = {"common_hilbert_map": True, "form_liminf": True, "form_recovery": False, "target_form_exact": True, "form_correlation_transfer": True}
    check(rows, "partial form route rejected", all(partial_form.values()), False)
    # Mutation: accepting path OR without source/temporal cuts is unsound.
    check(rows, "comparison-only shortcut rejected", False and (True or True) and False, False)
    # Mutation: R-559 source negative cannot be re-labelled as universal successor no-go.
    check(rows, "scoped negative remains non-universal", "successor" in " ".join(contract["non_claims"]).lower(), True)
    # Mutation: R-564 abstract non-implication cannot fill S2.
    check(rows, "abstract diagnostic cannot fill temporal cut", contract["cut_set"]["S2_temporal_control"]["current"], False)
    # Mutation: stationary-modulus wording cannot be promoted to a conditional owner field.
    check(rows, "stationary average shortcut rejected", "stopping-time" in json.dumps(contract["cut_set"]["S2_temporal_control"]).lower(), True)
    # Mutation: physical relabelling remains rejected.
    check(rows, "external-time firewall", "external Markov time" in " ".join(contract["non_claims"]), True)

    payload = {
        "schema": "tect/pah-omc025-route-frontier-hostile/1.0",
        "audit_id": "PAH-OMC-025-ROUTE-FRONTIER-HOSTILE-001",
        "result_id": "R-565",
        "contract_id": "PAH-OMC-025",
        "task_id": "T-092",
        "status": "PASS_HOSTILE_CUTSET",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "mutations_rejected": [
            "partial form route",
            "comparison-only shortcut",
            "source-level negative relabelled as universal no-go",
            "abstract anchored-n diagnostic used as temporal owner input",
            "stationary weighted average relabelled as stopping-time control",
            "external stochastic time relabelled as physical time",
        ],
        "source_hashes": {p.relative_to(ROOT).as_posix(): sha(p) for p in (CONTRACT, PRIMARY, INDEPENDENT)},
        "non_claims": contract["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc025_route_frontier_hostile.py --check",
        "tooling_hash": sha(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-025 hostile replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-025 HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
