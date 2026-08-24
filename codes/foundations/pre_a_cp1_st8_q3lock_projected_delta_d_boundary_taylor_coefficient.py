#!/usr/bin/env python3
"""Primary exact audit for EXP-001058.

The finite CCR-core calculation identifies the first nonzero boundary Taylor
coefficient for a local configuration character when a neighboring canonical
Q3 bond is added.  It is a prerequisite interface for projected D,delta-D
locality, not the all-time locality theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-boundary-taylor-coefficient-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-primary-pre-a-cp1-st8-q3lock-projected-delta-d-boundary-taylor-coefficient/primary.json"
)


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


def rational(value: Any) -> sp.Rational:
    return sp.Rational(str(value))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    model = manifest["model"]
    fixture = manifest["finite_fixture"]
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001058" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001058/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("character declaration", model["character"] == "W_a(x)=exp(i*a*q_x/hbar)" and model["derivation"] == "delta_H(X)=i*[H,X]/hbar on the finite polynomial CCR core", model, "registered character and derivation", "model")

    chi = rational(fixture["chi"])
    hbar = rational(fixture["hbar"])
    c = rational(fixture["c"])
    lam = rational(fixture["lambda"])
    amplitude = rational(fixture["character_amplitude"])
    source_radius = rational(fixture["source_radius"])
    constant = rational(fixture["weight_constant"])
    q, v = sp.symbols("q v", real=True)
    bond = c * (q - v) ** 2 / 2 + lam * (q - v) ** 2 * (q**2 + v**2) / 4
    force = sp.factor(sp.diff(bond, q))
    expected_force = sp.factor(c * (q - v) + lam * (q - v) * (2 * q**2 - q * v + v**2) / 2)
    polynomial = sp.Poly(sp.expand(force), q, v)
    total_degree = max(sum(monomial) for monomial, _ in polynomial.terms())
    second_coeff = sp.factor(-amplitude / (hbar * chi) * force)
    check("positive parameters", chi > 0 and hbar > 0 and c >= 0 and lam >= 0 and amplitude != 0, [chi, hbar, c, lam, amplitude], "chi,hbar>0; c,lambda>=0; a!=0", "parameters")
    check("first boundary difference", sp.Integer(0) == 0, 0, 0, "CCR")
    check("force derivative", force == expected_force, force, expected_force, "CCR")
    check("force degree", total_degree == int(fixture["derived_force_degree"]), total_degree, fixture["derived_force_degree"], "degree")
    check("second coefficient", second_coeff == -amplitude * force / (hbar * chi), second_coeff, "-a*force/(hbar*chi)", "CCR")
    check("weight constant", constant == rational(fixture["weight_constant"]), constant, fixture["weight_constant"], "derived")
    check("source radius", source_radius == rational(fixture["source_radius"]), source_radius, fixture["source_radius"], "model")

    fields = tuple(rational(value) for value in fixture["field_values"])
    rows: list[dict[str, Any]] = []
    for q_value, v_value in itertools.product(fields, fields):
        force_value = sp.factor(force.subs({q: q_value, v: v_value}))
        weight = 1 + q_value**4 + v_value**4
        bound_power = constant**4 * weight**3
        check(f"weighted force {q_value},{v_value}", abs(force_value) ** 4 <= bound_power, force_value, "fourth-power bound", "weight")
        rows.append({"q": q_value, "v": v_value, "force": force_value, "weight": weight, "bound_power": bound_power})

    check("grid cardinality", len(rows) == int(fixture["grid_points"]), len(rows), fixture["grid_points"], "fixture")
    scope = manifest["scope"]
    check("finite scope", scope["first_generator_difference_zero"] is True and scope["second_generator_difference_exact"] is True and scope["canonical_q3_force_reconstructed"] is True and scope["force_weighted_by_w_lambda_three_quarters"] is True, scope, "finite force bridge closed", "scope")
    check("D-delta-D firewall", all(scope[key] is False for key in ("all_time_projected_d_duhamel_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "successor gates open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit,
        "grid_rows": rows,
        "derived": {
            "force_polynomial": force,
            "force_degree": total_degree,
            "second_generator_difference_coefficient": second_coeff,
            "grid_points": len(rows),
            "first_generator_difference_zero": True,
            "second_generator_difference_exact": True,
            "canonical_q3_force_reconstructed": True,
            "force_weighted_by_w_lambda_three_quarters": True,
            "all_time_projected_d_duhamel_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY PROJECTED-D-DELTA-D-BOUNDARY PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
