#!/usr/bin/env python3
"""Non-importing independent reconstruction for R-451.

The implementation deliberately rebuilds the scalar shell recurrence and the
conditional fourth-power Cauchy factor without importing the primary audit.
It does not instantiate a Q3 history or a common operator domain.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
PARENT_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"
PARENT_MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-two-orientation-shell-transfer-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-pre_a_cp1_st8_q3lock_two_sided_history_cauchy_transfer/independent.json"


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def poly(n: int) -> int:
    return 4 * n * n + 8 * n + 14


def tail(n: int) -> Fraction:
    return Fraction(3 * poly(n), 2 ** (n - 1))


def step_ratio(n: int) -> Fraction:
    return Fraction(poly(n + 1), 2 * poly(n))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent_manifest = json.loads(PARENT_MANIFEST.read_text(encoding="utf-8"))
    parent_run = json.loads(PARENT_RUN.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("independent identity", manifest["result_id"] == "R-451" and manifest["exploration_id"] == "EXP-001324", [manifest["result_id"], manifest["exploration_id"]], ["R-451", "EXP-001324"])
    check("parent identity", parent_manifest["result_id"] == "R-450" and parent_run["result_id"] == "R-450", [parent_manifest["result_id"], parent_run["result_id"]], ["R-450", "R-450"])
    check("parent history remains open", parent_manifest["scope"]["actual_q3_history_identification_closed"] is False, parent_manifest["scope"]["actual_q3_history_identification_closed"], False)
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_modules = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imported_modules.extend(alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names)
    check("no primary import", not any(module.endswith("two_sided_history_cauchy_transfer") for module in imported_modules), imported_modules, "primary module absent")
    check("method preservation", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true")

    r0 = int(manifest["finite_fixture"]["radius_min"])
    r1 = int(manifest["finite_fixture"]["radius_max"])
    orientations = int(manifest["finite_fixture"]["orientation_count"])
    q = step_ratio(r0)
    c4 = Fraction(parent_run["derived"]["C4_edge"])
    factor = (2 ** (4 - 1)) * orientations
    check("radius range", [r0, r1] == [1, 64], [r0, r1], [1, 64])
    check("base tail", tail(r0) == Fraction(78), tail(r0), 78)
    check("ratio q", q == Fraction(23, 26) and q < 1, q, Fraction(23, 26))
    check("fourth-power factor", factor == 16, factor, 16)
    check("positive C4", c4 > 0, c4, ">0")

    rows: list[dict[str, Any]] = []
    previous = tail(r0)
    max_ratio = Fraction(0)
    for n in range(r0, r1 + 1):
        tn = tail(n)
        rn = step_ratio(n)
        bound = tail(r0) * q ** (n - r0)
        check(f"tail positive {n}", tn > 0, tn, ">0")
        check(f"ratio monotone bound {n}", rn <= q, rn, f"<={q}")
        check(f"geometric bound {n}", tn <= bound, tn, bound)
        if n < r1:
            check(f"exact next-step {n}", tail(n + 1) == tn * rn, tail(n + 1), tn * rn)
        if n > r0:
            check(f"bound induction {n}", bound == previous * q, bound, previous * q)
        previous = bound
        max_ratio = max(max_ratio, rn)
        rows.append({"radius": n, "tail": str(tn), "ratio": str(rn), "geometric_bound": str(bound), "cauchy_fourth_bound": str(Fraction(factor) * c4 * tn ** 4)})

    check("maximum ratio", max_ratio == q, max_ratio, q)
    check("history contract is conditional", "common L4" in manifest["theorem"]["history_contract"] and "actual" in manifest["missing_assumptions"][0], True, True)
    check("shape condition is abstract", "No new finite grid" in manifest["finite_fixture"]["shape_statement"], True, True)
    check("downstream flags closed", all(value is False for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in {"parent_two_orientation_shell_envelope_reused", "tail_ratio_closed", "geometric_vanishing_envelope_closed", "conditional_two_sided_recurrence_transfer_closed", "conditional_all_shape_cauchy_implication_closed"}), True, True)

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": manifest["candidate_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": manifest["status"],
        "assertion_count": len(assertions),
        "assertions": assertions,
        "derived": {
            "base_tail": str(tail(r0)),
            "ratio_q": str(q),
            "maximum_ratio": str(max_ratio),
            "orientation_count": orientations,
            "fourth_power_cauchy_factor": factor,
            "C4_edge": str(c4),
            "ratio_rows": len(rows),
            "conditional_all_shape_cauchy_implication_closed": True,
            "actual_q3_history_closed": False,
            "common_weighted_operator_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "rows": rows,
        "source_hashes": {"script": digest(Path(__file__)), "manifest": digest(MANIFEST), "parent_manifest": digest(PARENT_MANIFEST), "parent_run": digest(PARENT_RUN)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    save(output if output.is_absolute() else ROOT / output, payload)
    print(f"R-451 INDEPENDENT {payload['verdict']} {len(assertions)}/{len(assertions)} ratio_rows={len(rows)} q={q}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
