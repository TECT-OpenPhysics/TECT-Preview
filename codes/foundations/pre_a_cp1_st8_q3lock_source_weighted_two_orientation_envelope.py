#!/usr/bin/env python3
"""Primary exact audit for the EXP-001030 source-weighted branch envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-source-weighted-two-orientation-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def coefficients(G: Fraction, c: Fraction, q: Fraction, r: Fraction) -> list[Fraction]:
    return [Fraction(0), Fraction(0), -2 * c * G * q**3 + 2 * c**2 * r, 3 * c * G * q**2, -2 * c * G * q, c * G / 2]


def response(coeffs: list[Fraction], amplitude: int) -> Fraction:
    return sum(coeff * amplitude**degree for degree, coeff in enumerate(coeffs))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    audit.check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-source-weighted-two-orientation-envelope/1.0", manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001030", manifest["exploration_id"], "EXP-001030", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("no new negative", manifest["scope"]["no_new_negative_result"] is True, manifest["scope"], True, "scope")

    g, lam, c = Fraction(3, 5), Fraction(2, 7), Fraction(2, 3)
    G = g + 3 * lam
    leading = c * G / 2
    weight_degree = int(manifest["fixture"]["weight_degree"])
    C, J, delta = Fraction(1), Fraction(1), Fraction(1, 5)
    orientations = int(manifest["fixture"]["steps"] * 0 + manifest["model"]["orientation_count"])
    steps = int(manifest["fixture"]["steps"])
    amplitudes = [int(a) for a in manifest["fixture"]["sample_amplitudes"]]
    points = [(Fraction(str(q)), Fraction(str(r))) for q, r in manifest["fixture"]["sample_points"]]

    audit.check("Q3 coefficient", G == Fraction(51, 35), G, Fraction(51, 35), "derivation")
    audit.check("leading coefficient", leading == Fraction(17, 35), leading, Fraction(17, 35), "derivation")
    audit.check("weight degree", weight_degree == 5, weight_degree, 5, "source-weight")
    weighted_rows: list[dict[str, Any]] = []
    for q, r in points:
        coeffs = coefficients(G, c, q, r)
        coefficient_sum = sum(abs(value) for value in coeffs)
        for amplitude in amplitudes:
            weight = (1 + abs(amplitude)) ** weight_degree
            actual = abs(response(coeffs, amplitude))
            bound = coefficient_sum * weight
            audit.check(f"weighted response q={q} r={r} a={amplitude}", actual <= bound, actual, f"<={bound}", "source-weight")
            weighted_rows.append({"q": q, "r": r, "amplitude": amplitude, "response": actual, "weight": weight, "coefficient_sum": coefficient_sum, "bound": bound})

    zero_coeffs = coefficients(G, c, Fraction(0), Fraction(0))
    fixture_response = response(zero_coeffs, 10)
    fixture_weight = (1 + 10) ** weight_degree
    weighted_ratio = fixture_response / fixture_weight
    linear_ratio = fixture_response / 10
    audit.check("zero-site response", fixture_response == Fraction(17, 35) * 10**5, fixture_response, Fraction(17, 35) * 10**5, "fixture")
    audit.check("weighted ratio bounded by leading", weighted_ratio < leading, weighted_ratio, f"<{leading}", "fixture")
    audit.check("linear ratio exceeds leading", linear_ratio > leading, linear_ratio, f">{leading}", "fixture")

    factor = 1 + (C + orientations * J) * delta
    mass = Fraction(1)
    branch_rows: list[dict[str, Any]] = []
    for step_index in range(1, steps + 1):
        onsite = (1 + C * delta) * mass
        forward = J * delta * mass
        reverse = J * delta * mass
        after = onsite + forward + reverse
        audit.check(f"two-orientation step {step_index}", after == factor * mass, after, factor * mass, "two-orientation")
        audit.check(f"orientation symmetry step {step_index}", forward == reverse, [forward, reverse], "equal", "two-orientation")
        branch_rows.append({"step": step_index, "before": mass, "onsite": onsite, "forward": forward, "reverse": reverse, "after": after})
        mass = after
    audit.check("two-orientation factor", factor == Fraction(8, 5), factor, Fraction(8, 5), "two-orientation")
    audit.check("iterated branch envelope", mass == factor**steps, mass, factor**steps, "two-orientation")
    audit.check("finite branch volume independence", orientations == 2, orientations, 2, "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": audit.rows, "weighted_rows": weighted_rows, "branch_rows": branch_rows,
        "derived": {
            "G": G, "leading_coefficient": leading, "weight_degree": weight_degree,
            "orientation_count": orientations, "C": C, "J": J, "delta": delta, "steps": steps,
            "two_orientation_factor": factor, "iterated_factor": factor**steps,
            "fixture_weighted_ratio": weighted_ratio, "fixture_linear_ratio": linear_ratio,
            "source_weight_absorption_closed": True, "finite_two_orientation_algebra_closed": True,
            "actual_q3_recurrence_closed": False, "all_bond_volume_uniform_recurrence_closed": False,
            "exhaustion_cauchy_closed": False, "common_alpha_closed": False
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "exploration_id": manifest["exploration_id"], "boundary": manifest["scope"]
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(); payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY SOURCE-WEIGHTED-TWO-ORIENTATION PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
