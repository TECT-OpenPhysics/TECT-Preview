#!/usr/bin/env python3
"""Exact paper-local coercivity and positivity audit for the A2 manuscript.

The script reads the pinned coefficients from the P1 manifest, derives every
reported quantity with Fraction arithmetic, and emits a compact JSON artifact.
It is an auxiliary paper check: it does not promote the registered A2 claim or
replace the analytic proof audit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
MANIFEST = (
    REPO
    / "claims"
    / "A1-PRODUCTION-FUNCTIONAL-REALISATION"
    / "production_functional_manifest.json"
)
MANUSCRIPT = (
    REPO
    / "publish"
    / "papers"
    / "a2-r157-r158-ensemble-minimizers"
    / "manuscript.tex"
)
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "runs" / "exact-coercivity.json"

# This is a proof-design target, not a fitted or derived physical parameter.
PROOF_TARGET = Fraction(1, 5)
# This is a deliberately hostile test oracle: the true lower bound is below it.
HOSTILE_TARGET = PROOF_TARGET + Fraction(1, 100)


def as_fraction(value: Any) -> Fraction:
    """Interpret a finite-decimal manifest value exactly as written."""
    return Fraction(str(value))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    params = manifest["parameters"]
    y = as_fraction(params["Y"])
    z = as_fraction(params["Z"])
    r = as_fraction(params["r"])
    lam = as_fraction(params["lambda"])
    gamma = as_fraction(params["gamma"])

    # p(x) - t(1+x^2) = A x^2 + B x + C.
    a = y - PROOF_TARGET
    b = z
    c = r - PROOF_TARGET
    discriminant = b * b - 4 * a * c
    vertex_value = c - b * b / (4 * a)
    shell_minimum = r - z * z / (4 * y)
    shell_vertex = -z / (2 * y)

    alpha = as_fraction(params["alpha_X"])
    beta = as_fraction(params["beta_X"])
    mx = as_fraction(params["M_X"])
    eps_m = as_fraction(params["classii_mass_regularizer"])
    c_jj = as_fraction(params["cJJ"])
    c_jk = as_fraction(params["cJK"])
    c_kk = as_fraction(params["cKK"])
    classii_base_det = c_jj * c_kk - c_jk * c_jk
    classii_det = alpha * alpha * beta * beta / (mx * mx + eps_m) ** 2 * classii_base_det
    young = abs(lam) ** 3 / (3 * gamma * gamma)

    assertions: list[dict[str, Any]] = []

    def check(name: str, passed: bool, value: Any) -> None:
        assertions.append({"name": name, "passed": bool(passed), "value": value})

    check("manifest_exists", MANIFEST.is_file(), str(MANIFEST.relative_to(REPO)))
    check("manuscript_exists", MANUSCRIPT.is_file(), str(MANUSCRIPT.relative_to(REPO)))
    check("positive_quadratic_leading_coefficient", a > 0, str(a))
    check("exact_target_discriminant_negative", discriminant < 0, str(discriminant))
    check("exact_target_vertex_value_positive", vertex_value > 0, str(vertex_value))
    check("ratio_lower_bound_is_proved", a > 0 and discriminant < 0, str(PROOF_TARGET))
    check("continuous_shell_vertex_is_admissible", shell_vertex >= 0, str(shell_vertex))
    check("continuous_shell_minimum_positive", shell_minimum > 0, str(shell_minimum))
    check("classii_base_determinant_is_one_over_fifty", classii_base_det == Fraction(1, 50), str(classii_base_det))
    check("classii_exact_determinant_positive", classii_det > 0, str(classii_det))
    check("young_constant_exact", young == Fraction(79507, 7873200), str(young))

    # Hostile mutation: demanding 0.21 would make the quadratic certificate fail.
    hostile_a = y - HOSTILE_TARGET
    hostile_c = r - HOSTILE_TARGET
    hostile_discriminant = z * z - 4 * hostile_a * hostile_c
    hostile_vertex_value = hostile_c - z * z / (4 * hostile_a)
    check(
        "hostile_higher_target_is_rejected",
        hostile_a > 0 and hostile_vertex_value < 0,
        {"target": str(HOSTILE_TARGET), "vertex_value": str(hostile_vertex_value)},
    )

    # Hostile sign mutation: the raw sign reversal moves the continuous vertex
    # outside the admissible x>=0 half-line and must not be silently accepted.
    reversed_z_vertex = -(-z) / (2 * y)
    check("hostile_sign_reversal_is_detected", reversed_z_vertex < 0, str(reversed_z_vertex))

    passed = all(item["passed"] for item in assertions)
    return {
        "schema": "tect/paper-exact-coercivity-audit/1.0",
        "paper_id": "a2-r157-r158-ensemble-minimizers",
        "script": "publish/papers/a2-r157-r158-ensemble-minimizers/verification/exact_coercivity_audit.py",
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": sha256(MANIFEST),
        "manuscript": str(MANUSCRIPT.relative_to(REPO)).replace("\\", "/"),
        "manuscript_sha256": sha256(MANUSCRIPT),
        "inputs": {
            "Y": str(y),
            "Z": str(z),
            "r": str(r),
            "lambda": str(lam),
            "gamma": str(gamma),
        },
        "derived": {
            "proof_target": str(PROOF_TARGET),
            "quadratic_coefficients": {"A": str(a), "B": str(b), "C": str(c)},
            "discriminant": str(discriminant),
            "vertex_value": str(vertex_value),
            "continuous_shell_vertex": str(shell_vertex),
            "continuous_shell_minimum": str(shell_minimum),
            "classii_base_determinant": str(classii_base_det),
            "classii_exact_determinant": str(classii_det),
            "young_constant": str(young),
            "hostile_target": str(HOSTILE_TARGET),
            "hostile_discriminant": str(hostile_discriminant),
        },
        "assertions": assertions,
        "assertion_count": len(assertions),
        "passed_count": sum(item["passed"] for item in assertions),
        "verdict": "PAPER-EXACT-COERCIVITY-AUDIT-PASS" if passed else "FAIL",
        "scope": "Paper-local exact coercivity certificate only; no claim-tier or source-hash change.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"{result['verdict']}: {result['passed_count']}/{result['assertion_count']}")
    print(f"artifact: {args.output}")
    return 0 if result["verdict"].endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())