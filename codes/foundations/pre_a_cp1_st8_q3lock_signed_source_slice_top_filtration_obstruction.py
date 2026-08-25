#!/usr/bin/env python3
"""Primary exact audit for EXP-001119."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre_a_cp1_st8_q3lock_signed_source_slice_top_filtration_obstruction"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-signed-source-slice-top-filtration-obstruction-manifest.json"
SOURCE_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-actual-source-coefficient-product-manifest.json"
MIXED_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def source_slice() -> tuple[sp.Expr, sp.Expr]:
    rate = json.loads(MIXED_MANIFEST.read_text(encoding="utf-8"))["fixture"]
    lam = sp.Rational(str(rate["lambda"]))
    coupling = sp.Rational(str(rate["spatial_coupling"]))
    onsite = sp.Rational("3/5")
    q, v, a = sp.symbols("q v a")
    edge = lam * (q - v) ** 2 * (q**2 + v**2) / 4
    edge_u = edge - lam * (q - a - v) ** 2 * ((q - a) ** 2 + v**2) / 4
    edge_v = edge - lam * (q - (v - a)) ** 2 * (q**2 + (v - a) ** 2) / 4
    bond = coupling * (q - v) ** 2 / 2
    bond_u = bond - coupling * (q - a - v) ** 2 / 2
    bond_v = bond - coupling * (q - (v - a)) ** 2 / 2
    center = onsite * (q**4 - (q - a) ** 4) / 4 + 3 * edge_u + 6 * bond_u
    reverse = onsite * (v**4 - (v - a) ** 4) / 4 + 3 * edge_v + 6 * bond_v
    return sp.expand(center.subs({q: 0, v: 0})), sp.expand(reverse.subs({q: 0, v: 0}))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001119" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001119/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    center, reverse = source_slice()
    q, v, a = sp.symbols("q v a")
    expected = -sp.Rational(str(fixture["quartic_coefficient_abs"])) * a**4 - sp.Rational(str(fixture["quadratic_coefficient_abs"])) * a**2
    check("center signed slice", center == expected, center, expected, "source slice")
    check("reverse signed slice", reverse == expected, reverse, expected, "orientation")
    check("orientation equality", center == reverse, [center, reverse], "equal", "orientation")

    c = sp.Rational(str(fixture["quartic_coefficient_abs"]))
    source_radius = sp.Rational(str(fixture["source_radius"]))
    reduced_radius = sp.Rational(str(fixture["reduced_source_radius"]))
    branch = int(fixture["comparison_base"])
    polynomial = -c * a**4 - sp.Rational(str(fixture["quadratic_coefficient_abs"])) * a**2
    current = a
    selected = {int(x) for x in fixture["orders"]}
    rows: list[dict[str, Any]] = []
    for step in range(1, max(selected) + 1):
        current = sp.expand(polynomial * sp.diff(current, a))
        degree = 1 + 3 * step
        coefficient = sp.Poly(current, a).coeff_monomial(a**degree)
        expected_coefficient = (-c) ** step * sp.prod(1 + 3 * j for j in range(step))
        check(f"top coefficient m={step}", coefficient == expected_coefficient, coefficient, expected_coefficient, "degree filtration")
        if step in selected:
            ratio = sp.factor(abs(coefficient) * sp.factorial(degree) * reduced_radius**degree / source_radius)
            check(f"top degree m={step}", sp.Poly(current, a).degree() == degree, sp.Poly(current, a).degree(), degree, "degree filtration")
            rows.append({"m": step, "degree": degree, "top_coefficient": coefficient, "top_norm_ratio": ratio, "comparison_base_power": sp.Integer(branch) ** step, "exceeds_comparison_base": ratio > sp.Integer(branch) ** step})

    witness = next(row for row in rows if row["m"] == int(fixture["small_exact_witness_order"]))
    check("order-sixteen signed witness", witness["top_norm_ratio"] > sp.Integer(branch) ** witness["m"], witness["top_norm_ratio"], f">{branch}^{witness['m']}", "boundary")
    check("scope firewall", manifest["scope"]["signed_source_slice_reconstructed"] and manifest["scope"]["top_degree_filtration_closed"] and manifest["scope"]["signed_slice_quartic_cancellation_refuted"] and not manifest["scope"]["actual_q3_common_core_map_proved"], manifest["scope"], "signed slice boundary / Q3 open", "scope")
    passed = len(checks)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": checks,
        "derived": {
            "center_slice": center,
            "reverse_slice": reverse,
            "quartic_coefficient_abs": c,
            "quadratic_coefficient_abs": sp.Rational(str(fixture["quadratic_coefficient_abs"])),
            "source_radius": source_radius,
            "reduced_source_radius": reduced_radius,
            "ratio_rows": rows,
            "order_sixteen_ratio": witness["top_norm_ratio"],
            "signed_slice_quartic_cancellation_refuted": True,
            "actual_q3_common_core_map_proved": False,
            "actual_q3_history_closed": False,
            "common_alpha_closed": False
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
            "source_manifest": str(SOURCE_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "source_manifest_sha256": sha256(SOURCE_MANIFEST)
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY SIGNED-SOURCE-SLICE PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())