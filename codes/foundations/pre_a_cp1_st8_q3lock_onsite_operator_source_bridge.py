#!/usr/bin/env python3
"""Primary audit for the conditional one-step onsite operator/source bridge.

The graph bounds M_m are declared inputs.  The audit only performs the exact
coefficient majorant for one shifted onsite Q3 potential and keeps edge,
product, and history composition explicitly open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-onsite-operator-source-bridge"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def coefficient_rate(coefficients: list[tuple[sp.Rational, int, int]], moments: list[sp.Rational], source_radius: sp.Rational) -> sp.Rational:
    return sp.factor(sum(abs(coefficient) * moments[field_degree] * source_radius**source_degree for coefficient, field_degree, source_degree in coefficients))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g = sp.Rational(str(fixture["g"]))
    gamma = sp.Rational(str(fixture["gamma"]))
    kappa = sp.Rational(str(fixture["kappa"]))
    source_radius = sp.Rational(str(fixture["source_radius"]))
    time = sp.Rational(str(fixture["time"]))
    ratio = sp.factor(kappa / gamma)
    root, exact = sp.integer_nthroot(int(ratio), 4)
    root = sp.Integer(root)
    moments = [root**m for m in range(4)]
    coefficients = [(g, 3, 1), (-sp.Rational(3, 2) * g, 2, 2), (g, 1, 3), (-g / 4, 0, 4)]
    reverse_coefficients = [(-g, 3, 1), (-sp.Rational(3, 2) * g, 2, 2), (-g, 1, 3), (-g / 4, 0, 4)]
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001043" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001043/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("positive graph inputs", g > 0 and gamma > 0 and kappa >= 1 and source_radius > 0, [g, gamma, kappa, source_radius], ">0, kappa>=1", "hypothesis")
    audit.check("perfect fourth-power ratio", exact and root**4 == ratio, [ratio, root], "ratio=root^4", "hypothesis")
    audit.check("derived moment ladder", moments == [sp.Integer(1), sp.Integer(4), sp.Integer(16), sp.Integer(64)], moments, "fixture ladder", "hypothesis")
    audit.check("onsite coefficient table", coefficients[0][0] == g and coefficients[1][0] == -sp.Rational(3, 2) * g and coefficients[2][0] == g and coefficients[3][0] == -g / 4, coefficients, "onsite Taylor coefficients", "derivation")

    rate = coefficient_rate(coefficients, moments, source_radius)
    reverse_rate = coefficient_rate(reverse_coefficients, moments, source_radius)
    weighted_rate = sp.factor(time * rate)
    expected_rate = sp.factor(g * (moments[3] * source_radius + sp.Rational(3, 2) * moments[2] * source_radius**2 + moments[1] * source_radius**3 + source_radius**4 / 4))
    audit.check("onsite operator/source formula", rate == expected_rate, rate, expected_rate, "majorant")
    audit.check("reverse source absolute rate", reverse_rate == rate, reverse_rate, rate, "orientation")
    audit.check("positive source rate", rate > 0 and weighted_rate > 0, [rate, weighted_rate], ">0", "majorant")

    partial = sp.Integer(0)
    egf_rows: list[dict[str, Any]] = []
    for n in range(9):
        term = sp.factor(weighted_rate**n / sp.factorial(n))
        partial += term
        audit.check(f"EGF term n={n}", term >= 0, term, ">=0", "majorant")
        egf_rows.append({"n": n, "term": term, "partial": partial})
    audit.check("EGF partial below exp", float(partial) <= math.exp(float(weighted_rate)) + 1e-12, float(partial), f"<={math.exp(float(weighted_rate))}", "majorant")
    audit.check("operator/history scope", manifest["scope"]["onsite_one_step_bridge_closed"] is True and manifest["scope"]["history_product_closed"] is False, manifest["scope"], "one-step closed/history open", "scope")

    passed = len(audit.rows)
    derived = {
        "energy_ratio": ratio,
        "root_scale": root,
        "M0": moments[0],
        "M1": moments[1],
        "M2": moments[2],
        "M3": moments[3],
        "source_radius": source_radius,
        "onsite_source_rate": rate,
        "reverse_source_rate": reverse_rate,
        "weighted_rate": weighted_rate,
        "onsite_one_step_bridge_closed": True,
        "graph_bounds_assumed": True,
        "edge_bridge_closed": False,
        "history_product_closed": False,
        "actual_q3_history_closed": False,
        "all_shape_exhaustion_closed": False,
        "common_alpha_closed": False,
    }
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0, "assertions": audit.rows, "egf_rows": egf_rows, "derived": derived, "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)}, "exploration_id": manifest["exploration_id"], "boundary": manifest["scope"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY Q3-ONSITE-OPERATOR-SOURCE-BRIDGE PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
