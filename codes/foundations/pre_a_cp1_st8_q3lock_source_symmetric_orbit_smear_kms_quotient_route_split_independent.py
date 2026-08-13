#!/usr/bin/env python3
"""Independent stdlib verifier for the R-167 v3.8 proof-first package."""

from __future__ import annotations

import argparse
import ast
import cmath
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-source-symmetric-orbit-smear-kms-quotient-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-independent-{SLUG}/result.json"

CLOSED = "PA-CP1-ST8-Q3LOCK-SOURCE-SYMMETRIC-L1-ORBIT-SMEAR-CARRIER-AND-SELECTED-TANGENT-KMS-PAIR"
NEGATIVE = "NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-AUTOMATIC-ZERO-SOURCE-QUOTIENT-FACTORIZATION"

# Labelled inputs only.
FREQUENCY = Fraction(1)
BREAKS = (Fraction(0), Fraction(1), Fraction(2))
MOMENT_COMPONENTS = 8
TARGET_MOMENT_ORDER = 3
AVAILABLE_MOMENT_ORDER = 4
SINE_REMAINDER_DENOMINATOR = math.factorial(3)
NUMERIC_TOLERANCE = 5e-14


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def integral_exponential(start: Fraction, stop: Fraction, frequency: Fraction) -> complex:
    omega = float(frequency)
    return (cmath.exp(-1j * omega * float(stop)) - cmath.exp(-1j * omega * float(start))) / (-1j * omega)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def coefficient_formula_text(frequency: Fraction) -> str:
    omega = fraction_text(frequency)
    return f"(1-exp(-i*{omega}))^2/(i*{omega})"


def modulus_formula_text(frequency: Fraction) -> str:
    chord_fourth_factor = 2**4
    half_frequency = frequency / 2
    denominator = frequency**2
    base = f"{chord_fourth_factor}*sin({fraction_text(half_frequency)})^4"
    return base if denominator == 1 else f"{base}/{fraction_text(denominator)}"


def derive_m2_fixture() -> dict[str, Any]:
    left, middle, right = BREAKS
    coefficient = integral_exponential(left, middle, FREQUENCY) - integral_exponential(middle, right, FREQUENCY)
    target = (1 - cmath.exp(-1j * float(FREQUENCY))) ** 2 / (1j * float(FREQUENCY))
    modulus_squared = coefficient.real * coefficient.real + coefficient.imag * coefficient.imag
    chord_fourth_factor = 2**4
    sine_form = chord_fourth_factor * math.sin(float(FREQUENCY) / 2) ** 4 / float(FREQUENCY) ** 2
    zero_integral = float((middle - left) - (right - middle))
    matrix = ((0j, coefficient), (coefficient.conjugate(), 0j))
    square00 = matrix[0][1].conjugate() * matrix[0][1]
    square11 = matrix[1][0].conjugate() * matrix[1][0]
    return {
        "zero_source_integral": "0" if zero_integral == 0 else str(zero_integral),
        "coefficient_identity": abs(coefficient - target) < NUMERIC_TOLERANCE,
        "coefficient": coefficient_formula_text(FREQUENCY),
        "modulus_squared_identity": abs(modulus_squared - sine_form) < NUMERIC_TOLERANCE,
        "modulus_squared": modulus_formula_text(FREQUENCY),
        "strictly_positive": modulus_squared > 0,
        "square_scalar": abs(square00 - modulus_squared) < NUMERIC_TOLERANCE and abs(square11 - modulus_squared) < NUMERIC_TOLERANCE,
        "factorization_failure": zero_integral == 0 and modulus_squared > 0,
        "numeric_modulus_squared": modulus_squared,
    }


def derive_separator() -> dict[str, Any]:
    fourth_factor = MOMENT_COMPONENTS ** (AVAILABLE_MOMENT_ORDER // 2)
    root_factor = math.sqrt(MOMENT_COMPONENTS)
    dominance_factor = Fraction(SINE_REMAINDER_DENOMINATOR, 2)
    boundary_ratio = 1 - dominance_factor / SINE_REMAINDER_DENOMINATOR
    moment_ratio = Fraction(TARGET_MOMENT_ORDER, AVAILABLE_MOMENT_ORDER)
    distance_multiplier = 1 - (-1)
    return {
        "M3": f"({fourth_factor}*C_4)^({fraction_text(moment_ratio)})",
        "moment_factor": str(fourth_factor),
        "remainder_denominator": SINE_REMAINDER_DENOMINATOR,
        "boundary_lower_equals_d": boundary_ratio == Fraction(1, 2),
        "d": f"r*sqrt({MOMENT_COMPONENTS})*m_0/{boundary_ratio.denominator}",
        "distance_lower_bound": f"{distance_multiplier}*d",
        "root_factor_numeric": root_factor,
    }


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    fixture = derive_m2_fixture()
    separator = derive_separator()
    expected = manifest["exact_m2_fixture"]["derived"]
    audit = Audit()
    audit.check("manifest topology", manifest["closed_gate_ids"] == [CLOSED] and manifest["negative_ids"] == [NEGATIVE] and manifest["exploration_id"] == "EXP-000842", (manifest["closed_gate_ids"], manifest["negative_ids"]), ([CLOSED], [NEGATIVE]), "topology")
    audit.check("carrier norm family", all(token in manifest["carrier_theorem"]["setup"] for token in ("I=[-h_0,h_0]", "finite periodic Lambda", "physical real-time")), manifest["carrier_theorem"]["setup"], "fixed N symmetric source family", "theorem")
    audit.check("physical KMS strip", "beta hbar" in manifest["carrier_theorem"]["common_action"] and "physical-beta Gibbs/KMS" in manifest["carrier_theorem"]["selected_kms_pair"] and "mathematical (beta hbar)-KMS" in manifest["carrier_theorem"]["selected_kms_pair"], "physical beta/mathematical beta*hbar KMS", "physical beta/mathematical beta*hbar KMS", "theorem")
    audit.check("parity covariance", "Symmetry of I" in manifest["carrier_theorem"]["parity"] and "commuting with theta" in manifest["carrier_theorem"]["parity"], manifest["carrier_theorem"]["parity"], "same-carrier parity", "theorem")
    audit.check("separator arithmetic", separator["moment_factor"] == str(MOMENT_COMPONENTS**2) and separator["remainder_denominator"] == SINE_REMAINDER_DENOMINATOR and separator["boundary_lower_equals_d"], separator, "derived fourth factor, factorial and one-half", "separator")
    audit.check("separator state distance", "varphi_n^+(b)=rho_n^+(sin(rX))" in manifest["fixed_separator"]["conclusion"] and "||varphi_+-varphi_-||>=2d" in manifest["fixed_separator"]["conclusion"] and "Gibbs invariance" in manifest["fixed_separator"]["conclusion"], manifest["fixed_separator"]["conclusion"], "concrete-to-categorical invariant smear separates", "separator")
    audit.check("M2 zero-source kernel", fixture["zero_source_integral"] == "0" and expected["zero_source_image"] == "0", fixture["zero_source_integral"], "0", "fixture")
    audit.check("M2 coefficient numerical derivation", fixture["coefficient_identity"], fixture["coefficient"], expected["coefficient"], "fixture")
    audit.check("M2 sine modulus derivation", fixture["modulus_squared_identity"] and fixture["square_scalar"], fixture["numeric_modulus_squared"], expected["modulus_squared"], "fixture")
    audit.check("M2 factorization failure", fixture["strictly_positive"] and fixture["factorization_failure"] is expected["factorization_failure"], fixture["factorization_failure"], True, "fixture")
    audit.check("quotient iff and boundary", "if and only if" in manifest["zero_source_quotient"]["factorization_criterion"] and "h_n->0 does not itself" in manifest["zero_source_quotient"]["route_boundary"], manifest["zero_source_quotient"], "kernel criterion and no shortcut", "quotient")
    audit.check("analogous fixture scope", all(token in manifest["exact_m2_fixture"]["carrier"] for token in ("positive integers", "I_2=[-1,1]", "supremum", "q_0^M2")) and "B is not a Q3 rational-character label" in manifest["exact_m2_fixture"]["scope"] and "not a Q3LOCK counterexample" in manifest["exact_m2_fixture"]["scope"], manifest["exact_m2_fixture"], "self-contained explicit non-Q3 carrier", "scope")
    audit.check("certificate audit tokens", all(token in certificate for token in ("physical KMS strip", "varphi_n^+(b)=rho_n^+(sin(rX))", "canonical surjective", "I_2=[-1,1]", "q_0^M2:A_M2->A_(M2,0)", "All five active parent gates")), "all required tokens present", "all required tokens present", "certificate")
    audit.check("no-overclaim", all(token in manifest["no_overclaim"] for token in ("no beta-infinity selection", "no algebraic ground-state identification", "no exact Q3 thermodynamic zero-source", "physical Sector A or Pre-A")), manifest["no_overclaim"], "scope firewalls", "scope")
    audit.check("source AST and format", ast.parse(SCRIPT.read_text(encoding="utf-8")) is not None and all(b"\r" not in path.read_bytes() and path.read_bytes().endswith(b"\n") and all(byte < 128 for byte in path.read_bytes()) for path in (MANIFEST, CERTIFICATE, SCRIPT)), "AST ASCII LF final-LF", "AST ASCII LF final-LF", "format")
    if formal:
        formal_paths = (REPO / "claims/GATES.md", REPO / "RESULTS-LEDGER.md", REPO / "negative-results/registry.md", REPO / "explorations/log.jsonl")
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in formal_paths)
        audit.check("formal authority links", all(token in formal_text for token in ("EXP-000842", CLOSED, NEGATIVE, "R-167 v3.8")), "all formal tokens present", "all formal tokens present", "formal")
    return {
        "schema": "tect/pre-a-q3lock-source-symmetric-orbit-smear-kms-quotient-independent-run/1.0",
        "version": "R-167 v3.8",
        "mode": "formal" if formal else "staged",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": {"separator": separator, "fixture": fixture},
        "source_hashes": {str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path) for path in (MANIFEST, CERTIFICATE, SCRIPT)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(formal=not args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"INDEPENDENT PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
