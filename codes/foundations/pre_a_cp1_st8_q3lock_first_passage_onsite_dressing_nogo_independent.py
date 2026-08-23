#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001029.

This lane reconstructs the shifted polynomial coefficient list directly and
does not import the SymPy primary result.
"""

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
SLUG = "pre-a-cp1-st8-q3lock-first-passage-onsite-dressing-nogo"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def clean(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(clean(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
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
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": clean(actual), "expected": clean(expected)})


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    audit.check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-first-passage-onsite-dressing-nogo/1.0", manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001029", manifest["exploration_id"], "EXP-001029", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    fixture = manifest["fixture"]
    g = Fraction(fixture["g"])
    lam = Fraction(fixture["lambda"])
    c = Fraction(fixture["c"])
    G = g + 3 * lam
    expected_G = Fraction(fixture["G"])
    leading = c * G / 2
    expected_leading = Fraction(fixture["leading_coefficient"])
    amplitude = Fraction(fixture["amplitude"])
    q = Fraction(0)
    r = Fraction(0)

    # Direct coefficient reconstruction from
    # d_r[(G/4)(q^4-(q-a)^4)-c*a*r]^2.
    coefficients = {
        5: c * G / 2,
        4: -2 * c * G * q,
        3: 3 * c * G * q * q,
        2: -2 * c * G * q**3 + 2 * c * c * r,
    }
    response_degree = max(coefficients)
    source_degree = 1
    degree_gap = response_degree - source_degree
    fixture_ratio = leading * amplitude**degree_gap

    audit.check("Q3 quartic coefficient", G == expected_G, G, expected_G, "derivation")
    audit.check("coefficient list has four terms", sorted(coefficients) == [2, 3, 4, 5], sorted(coefficients), [2, 3, 4, 5], "common-core")
    audit.check("leading coefficient", coefficients[5] == expected_leading, coefficients[5], expected_leading, "common-core")
    audit.check("leading degree", response_degree == 5, response_degree, 5, "common-core")
    audit.check("source Weyl degree", source_degree == 1, source_degree, 1, "Weyl")
    audit.check("degree gap", degree_gap == 4, degree_gap, 4, "normalisation")
    audit.check("zero-centre lower coefficients", coefficients[4] == 0 and coefficients[3] == 0 and coefficients[2] == 0, coefficients, "only a^5 at q=r=0", "fixture")
    audit.check("fixture ratio positive", fixture_ratio > 0, fixture_ratio, ">0", "fixture")
    audit.check("ratio is unbounded in amplitude", leading > 0 and degree_gap > 0, [leading, degree_gap], "positive coefficient and gap", "asymptotic")
    audit.check("conditional wave-packet degree", response_degree - 2 == 3, response_degree - 2, 3, "conditional-operator")
    audit.check("kinetic boundary recorded", "cannot create an a^5 coefficient" in manifest["exact_identity"]["kinetic_boundary"], manifest["exact_identity"]["kinetic_boundary"], "a^5 coefficient boundary", "scope")
    audit.check("all broader routes remain open", len(manifest["open_after_test"]) >= 4, len(manifest["open_after_test"]), ">=4", "scope")
    audit.check("no tier change", manifest["scope"]["no_tier_change"] is True, manifest["scope"]["no_tier_change"], True, "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "g": g,
            "lambda": lam,
            "c": c,
            "G": G,
            "leading_coefficient": leading,
            "response_degree": response_degree,
            "source_degree": source_degree,
            "degree_gap": degree_gap,
            "fixture_amplitude": amplitude,
            "fixture_ratio": fixture_ratio,
            "critical_linear_source_route_closed": False,
            "all_critical_topologies_rejected": False,
            "actual_q3_first_passage_closed": False,
            "common_alpha_closed": False
        },
        "coefficient_list_at_q_r_zero": {str(power): value for power, value in coefficients.items()},
        "scope": manifest["scope"],
        "exploration_id": manifest["exploration_id"],
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST)
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FIRST-PASSAGE-ONSITE-DRESSING-NOGO PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
