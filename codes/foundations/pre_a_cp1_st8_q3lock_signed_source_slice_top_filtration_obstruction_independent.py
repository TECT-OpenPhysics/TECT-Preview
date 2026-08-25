#!/usr/bin/env python3
"""Independent fraction/dictionary lane for EXP-001119."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre_a_cp1_st8_q3lock_signed_source_slice_top_filtration_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-signed-source-slice-top-filtration-obstruction-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"
Poly = dict[int, Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def add(left: Poly, right: Poly) -> Poly:
    out = dict(left)
    for degree, value in right.items():
        out[degree] = out.get(degree, Fraction(0)) + value
    return {degree: value for degree, value in out.items() if value}


def multiply(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for a, av in left.items():
        for b, bv in right.items():
            out[a + b] = out.get(a + b, Fraction(0)) + av * bv
    return {degree: value for degree, value in out.items() if value}


def derivative(poly: Poly) -> Poly:
    return {degree - 1: degree * value for degree, value in poly.items() if degree and degree * value}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture = manifest["fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    c = Fraction(str(fixture["quartic_coefficient_abs"])); lower = Fraction(str(fixture["quadratic_coefficient_abs"]))
    S = Fraction(str(fixture["source_radius"])); S_prime = Fraction(str(fixture["reduced_source_radius"])); branch = int(fixture["comparison_base"])
    check("identity", manifest["exploration_id"] == "EXP-001119" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001119/T-054", "provenance")
    source_slice = {4: -c, 2: -lower}
    check("signed slice fixture", source_slice == {4: Fraction(-51, 140), 2: Fraction(-2)}, source_slice, {4: Fraction(-51, 140), 2: Fraction(-2)}, "source slice")
    check("radius order", 0 < S_prime < S, [S_prime, S], "0<S'<S", "radius")
    current: Poly = {1: Fraction(1)}; rows: list[dict[str, Any]] = []
    for m in range(1, max(int(x) for x in fixture["orders"]) + 1):
        current = multiply(source_slice, derivative(current))
        degree = 1 + 3 * m
        expected = (-c) ** m
        for j in range(m):
            expected *= 1 + 3 * j
        check(f"top coefficient m={m}", current.get(degree) == expected, current.get(degree), expected, "degree filtration")
        if m in [int(x) for x in fixture["orders"]]:
            ratio = abs(expected) * math.factorial(degree) * S_prime**degree / S
            check(f"top degree m={m}", max(current) == degree, max(current), degree, "degree filtration")
            rows.append({"m": m, "degree": degree, "top_coefficient": str(expected), "top_norm_ratio": str(ratio), "comparison_base_power": branch**m, "exceeds_comparison_base": ratio > branch**m})
    witness = next(row for row in rows if row["m"] == int(fixture["small_exact_witness_order"]))
    check("order-sixteen signed witness", Fraction(witness["top_norm_ratio"]) > branch**16, witness["top_norm_ratio"], f">{branch}^16", "boundary")
    check("scope firewall", manifest["scope"]["signed_source_slice_reconstructed"] and manifest["scope"]["top_degree_filtration_closed"] and not manifest["scope"]["actual_q3_history_closed"], manifest["scope"], "signed slice boundary / Q3 open", "scope")
    passed = len(checks)
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0, "assertions": checks, "derived": {"center_slice": "-51/140*a^4-2*a^2", "reverse_slice": "-51/140*a^4-2*a^2", "quartic_coefficient_abs": str(c), "quadratic_coefficient_abs": str(lower), "source_radius": str(S), "reduced_source_radius": str(S_prime), "ratio_rows": rows, "order_sixteen_ratio": witness["top_norm_ratio"], "signed_slice_quartic_cancellation_refuted": True, "actual_q3_common_core_map_proved": False, "actual_q3_history_closed": False, "common_alpha_closed": False}, "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)}, "exploration_id": manifest["exploration_id"], "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test:
        payload["provenance"]["independent_lane"] = True; path = args.output if args.output.is_absolute() else REPO / args.output; path.parent.mkdir(parents=True, exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent); os.close(fd); Path(tmp).write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8"); os.replace(tmp,path)
    print(f"INDEPENDENT SIGNED-SOURCE-SLICE PASS {payload['passed']}/{payload['total']}"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
