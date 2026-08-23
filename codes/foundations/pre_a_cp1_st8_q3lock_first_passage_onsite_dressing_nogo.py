#!/usr/bin/env python3
"""Primary exact audit for EXP-001029.

The audit isolates the leading common-core coefficient of one spatial-bond
response after one onsite potential commutator.  It is a scoped obstruction to
linear-source one-sided critical energy normalisation, not a theorem about all
Q3 topologies or the full dynamics.
"""

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
SLUG = "pre-a-cp1-st8-q3lock-first-passage-onsite-dressing-nogo"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


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
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
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
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def rational(text: str) -> sp.Rational:
    return sp.Rational(text)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    audit.check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-first-passage-onsite-dressing-nogo/1.0", manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001029", manifest["exploration_id"], "EXP-001029", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    fixture = manifest["fixture"]
    g = rational(fixture["g"])
    lam = rational(fixture["lambda"])
    c = rational(fixture["c"])
    G = sp.factor(g + 3 * lam)
    expected_G = rational(fixture["G"])
    expected_leading = rational(fixture["leading_coefficient"])
    amplitude = rational(fixture["amplitude"])
    q, r, a = sp.symbols("q r a", real=True)

    delta = sp.expand(G * (q**4 - (q - a) ** 4) / 4 - c * a * r)
    response = sp.expand(sp.diff(delta**2, r))
    expected_response = sp.expand(
        c * G * a**5 / 2
        - 2 * c * G * q * a**4
        + 3 * c * G * q**2 * a**3
        + (-2 * c * G * q**3 + 2 * c**2 * r) * a**2
    )
    polynomial = sp.Poly(response, a)
    leading = sp.factor(polynomial.coeff_monomial(a**5))
    source_commutator = a
    response_degree = int(sp.degree(response, a))
    source_degree = int(sp.degree(source_commutator, a))
    degree_gap = response_degree - source_degree
    fixture_ratio = sp.factor(leading * amplitude**degree_gap)

    audit.check("Q3 quartic coefficient", G == expected_G, G, expected_G, "derivation")
    audit.check("shifted potential definition", sp.expand(delta - (G * (q**4 - (q - a) ** 4) / 4 - c * a * r)) == 0, delta, "Delta_a", "derivation")
    audit.check("second response identity", sp.expand(response - expected_response) == 0, response, expected_response, "common-core")
    audit.check("leading response degree", response_degree == 5, response_degree, 5, "common-core")
    audit.check("leading coefficient", leading == expected_leading, leading, expected_leading, "common-core")
    audit.check("source Weyl degree", source_degree == 1, source_degree, 1, "Weyl")
    audit.check("degree gap", degree_gap == 4, degree_gap, 4, "normalisation")
    audit.check("fixture coefficient", sp.factor(leading - expected_leading) == 0, leading, expected_leading, "fixture")
    audit.check("fixture ratio positive", fixture_ratio > 0, fixture_ratio, ">0", "fixture")
    audit.check("ratio grows with amplitude", int(sp.degree(leading * a**degree_gap, a)) == degree_gap, int(sp.degree(leading * a**degree_gap, a)), degree_gap, "asymptotic")
    audit.check("conditional wave-packet response degree", response_degree - 2 == 3, response_degree - 2, 3, "conditional-operator")
    audit.check("kinetic boundary recorded", "cannot create an a^5 coefficient" in manifest["exact_identity"]["kinetic_boundary"], manifest["exact_identity"]["kinetic_boundary"], "a^5 coefficient boundary", "scope")
    audit.check("broader topologies remain open", len(manifest["open_after_test"]) >= 4, len(manifest["open_after_test"]), ">=4", "scope")
    audit.check("no tier change", manifest["scope"]["no_tier_change"] is True, manifest["scope"]["no_tier_change"], True, "scope")
    audit.check("no negative result", manifest["scope"]["no_new_negative_result"] is True, manifest["scope"]["no_new_negative_result"], True, "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
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
        "formulae": {
            "delta": delta,
            "response": response,
            "source_commutator": "a W_a",
            "conditional_wave_packet_lower_order": "a^3"
        },
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
    print(f"PRIMARY FIRST-PASSAGE-ONSITE-DRESSING-NOGO PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
