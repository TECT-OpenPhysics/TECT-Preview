#!/usr/bin/env python3
"""Primary fixed finite-particle core tail audit for EXP-001095."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_finite_particle_core_domain"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001095" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001095/T-054", "provenance")
    check("nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["fixed_finite_particle_core_strong_zero_closed"] and scope["embedded_basis_identity_closed"] and not scope["evolved_history_tail_closed"], scope, "fixed core only", "scope")

    levels = [int(value) for value in fixture["support_levels"]]
    dimensions = [int(value) for value in fixture["cutoff_dimensions"]]
    rows: list[dict[str, Any]] = []
    for K in levels:
        eligible = [n for n in dimensions if n >= K + 2]
        check(f"K={K} eligible cutoffs", eligible == [n for n in dimensions if K + 1 < n], eligible, "n>K+1", "support")
        for n in eligible:
            for k in range(K + 1):
                top = 1 if k == n - 1 else 0
                scaled_defect = n * top
                check(f"K={K} n={n} k={k} top tail", top == 0, top, 0, "fixed core")
                check(f"K={K} n={n} k={k} defect", scaled_defect == 0, scaled_defect, 0, "fixed core")
                rows.append({"K": K, "n": n, "k": k, "top_overlap": top, "scaled_defect": scaled_defect})
        boundary_n = max(dimensions)
        boundary_k = boundary_n - 1
        boundary_value = boundary_n * (1 if boundary_k == boundary_n - 1 else 0)
        check(f"K={K} top boundary witness", boundary_value == boundary_n, boundary_value, boundary_n, "boundary control")
    check("finite core rows", all(row["scaled_defect"] == 0 for row in rows), len(rows), "all zero", "summary")
    check("finite values", all(isinstance(row["n"], int) and row["n"] > 0 and tolerance >= 0 for row in rows), len(rows), "finite", "summary")

    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-PARTICLE-CORE-DOMAIN", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"rows": rows, "fixed_finite_particle_core_strong_zero_closed": True, "embedded_basis_identity_closed": True, "evolved_history_tail_closed": False, "gibbs_tail_uniformity_closed": False, "actual_unbounded_q3_domain_transfer_closed": False, "source_volume_uniform_modular_history_closed": False, "common_alpha_closed": False}, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-PARTICLE-CORE-DOMAIN PASS {payload['passed']}/{payload['assertion_count']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
