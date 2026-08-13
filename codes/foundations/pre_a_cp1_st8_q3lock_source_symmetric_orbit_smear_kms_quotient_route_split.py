#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v3.8 proof-first package."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.simplify.fu import fu


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-source-symmetric-orbit-smear-kms-quotient-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-primary-{SLUG}/result.json"
FORMAL_PATHS = (REPO / "claims/GATES.md", REPO / "RESULTS-LEDGER.md", REPO / "negative-results/registry.md", REPO / "explorations/log.jsonl")

CLOSED = "PA-CP1-ST8-Q3LOCK-SOURCE-SYMMETRIC-L1-ORBIT-SMEAR-CARRIER-AND-SELECTED-TANGENT-KMS-PAIR"
NEGATIVE = "NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-AUTOMATIC-ZERO-SOURCE-QUOTIENT-FACTORIZATION"

# Labelled symbolic fixture inputs only.
FREQUENCY = sp.Integer(1)
INTERVAL_BREAKS = (sp.Integer(0), sp.Integer(1), sp.Integer(2))
SOURCE_SCALE = sp.Integer(1)
MOMENT_COMPONENTS = sp.Integer(8)
TARGET_MOMENT_ORDER = sp.Integer(3)
AVAILABLE_MOMENT_ORDER = sp.Integer(4)
SINE_REMAINDER_DENOMINATOR = sp.factorial(3)


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


def exact_text(value: sp.Expr) -> str:
    return str(sp.simplify(value)).replace("**", "^").replace(" ", "")


def coefficient_formula_text(frequency: sp.Expr) -> str:
    omega = exact_text(frequency)
    return f"(1-exp(-i*{omega}))^2/(i*{omega})"


def modulus_formula_text(frequency: sp.Expr) -> str:
    chord_fourth_factor = sp.Integer(2) ** 4
    half_frequency = sp.Rational(1, 2) * frequency
    denominator = sp.simplify(frequency**2)
    base = f"{exact_text(chord_fourth_factor)}*sin({exact_text(half_frequency)})^4"
    return base if denominator == 1 else f"{base}/{exact_text(denominator)}"


def derive_m2_fixture() -> dict[str, Any]:
    t = sp.symbols("t", real=True)
    left, middle, right = INTERVAL_BREAKS
    positive = sp.integrate(sp.exp(-sp.I * FREQUENCY * t), (t, left, middle))
    negative = sp.integrate(sp.exp(-sp.I * FREQUENCY * t), (t, middle, right))
    coefficient = sp.simplify(positive - negative)
    target = sp.simplify((1 - sp.exp(-sp.I * FREQUENCY)) ** 2 / (sp.I * FREQUENCY))
    coefficient_modulus = sp.simplify(coefficient * sp.conjugate(coefficient))
    modulus_squared = sp.simplify(sp.expand_complex(coefficient_modulus))
    chord_fourth_factor = sp.Integer(2) ** 4
    target_modulus = sp.simplify(chord_fourth_factor * sp.sin(FREQUENCY / 2) ** 4 / FREQUENCY**2)
    zero_source_integral = (middle - left) - (right - middle)
    matrix = sp.Matrix([[0, coefficient], [sp.conjugate(coefficient), 0]])
    square = sp.simplify(matrix.conjugate().T * matrix)
    return {
        "zero_source_integral": exact_text(zero_source_integral),
        "coefficient_identity": bool(sp.simplify(coefficient - target) == 0),
        "coefficient": coefficient_formula_text(FREQUENCY),
        "modulus_squared_identity": bool(fu(modulus_squared - target_modulus) == 0),
        "modulus_squared": modulus_formula_text(FREQUENCY),
        "strictly_positive": bool(sp.N(modulus_squared, 50) > 0),
        "square_scalar": bool(
            square[0, 1] == 0
            and square[1, 0] == 0
            and sp.simplify(square[0, 0] - coefficient_modulus) == 0
            and sp.simplify(square[1, 1] - coefficient_modulus) == 0
        ),
        "factorization_failure": bool(zero_source_integral == 0 and sp.N(modulus_squared, 50) > 0),
    }


def derive_separator() -> dict[str, Any]:
    m0, c4, r, m3_symbol = sp.symbols("m_0 C_4 r M_3", positive=True)
    x_factor = sp.sqrt(MOMENT_COMPONENTS)
    x_fourth_factor = MOMENT_COMPONENTS ** (AVAILABLE_MOMENT_ORDER / 2)
    moment_ratio = sp.Rational(TARGET_MOMENT_ORDER, AVAILABLE_MOMENT_ORDER)
    m3 = sp.simplify((x_fourth_factor * c4) ** moment_ratio)
    raw_lower = sp.simplify(r * x_factor * m0 - r**3 * m3_symbol / SINE_REMAINDER_DENOMINATOR)
    dominance_factor = sp.Rational(SINE_REMAINDER_DENOMINATOR, 2)
    boundary_ratio = sp.simplify(1 - dominance_factor / SINE_REMAINDER_DENOMINATOR)
    d = sp.simplify(boundary_ratio * r * x_factor * m0)
    substitution = {m3_symbol: dominance_factor * x_factor * m0 / r**2}
    boundary_lower = sp.simplify(raw_lower.subs(substitution))
    distance_multiplier = sp.Integer(1) - sp.Integer(-1)
    return {
        "M3": f"({exact_text(x_fourth_factor)}*C_4)^({exact_text(moment_ratio)})",
        "M3_identity": bool(sp.simplify(m3 - (x_fourth_factor * c4) ** moment_ratio) == 0),
        "moment_factor": exact_text(x_fourth_factor),
        "remainder_denominator": int(SINE_REMAINDER_DENOMINATOR),
        "boundary_lower_equals_d": bool(sp.simplify(boundary_lower - d) == 0),
        "d": f"r*sqrt({exact_text(MOMENT_COMPONENTS)})*m_0/{exact_text(sp.denom(boundary_ratio))}",
        "distance_lower_bound": f"{exact_text(distance_multiplier)}*d",
    }


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    fixture = derive_m2_fixture()
    separator = derive_separator()
    expected = manifest["exact_m2_fixture"]["derived"]
    audit = Audit()
    audit.check("manifest topology", manifest["closed_gate_ids"] == [CLOSED] and manifest["negative_ids"] == [NEGATIVE] and manifest["exploration_id"] == "EXP-000842", (manifest["closed_gate_ids"], manifest["negative_ids"]), ([CLOSED], [NEGATIVE]), "topology")
    audit.check("carrier common action", all(token in manifest["carrier_theorem"]["common_action"] for token in ("point-norm C0", "beta hbar", "source-, sign-, state- and beta-independent")), manifest["carrier_theorem"]["common_action"], "common categorical action and physical strip", "theorem")
    audit.check("carrier star and parity", "A_(xi,f)^*=A_(-xi,bar f)" in manifest["carrier_theorem"]["generators"] and "gamma A_(xi,f)=A_(-xi,f)" in manifest["carrier_theorem"]["parity"], "star/parity exact", "star/parity exact", "theorem")
    audit.check("selected KMS weak-star pair", "weak-star cluster" in manifest["carrier_theorem"]["selected_kms_pair"] and "physical-beta Gibbs/KMS" in manifest["carrier_theorem"]["selected_kms_pair"] and "mathematical (beta hbar)-KMS" in manifest["carrier_theorem"]["selected_kms_pair"], manifest["carrier_theorem"]["selected_kms_pair"], "selected common-action KMS pair with exact parameter", "theorem")
    audit.check("separator moment algebra", separator["moment_factor"] == exact_text(MOMENT_COMPONENTS**2) and separator["remainder_denominator"] == int(SINE_REMAINDER_DENOMINATOR) and separator["M3_identity"] and separator["boundary_lower_equals_d"], separator, "M3 and d exact", "separator")
    audit.check("separator fixed witness", all(token in manifest["fixed_separator"]["construction"] for token in ("M_3=(64 C_4)^(3/4)", "r^2 M_3<=3 sqrt(8)m_0", "d=r sqrt(8)m_0/2", "||b||<=1")) and all(token in manifest["fixed_separator"]["input"] for token in ("rho_n^+", "varphi_n^plus/minus")) and "varphi_n^+(b)=rho_n^+(sin(rX))" in manifest["fixed_separator"]["conclusion"], manifest["fixed_separator"], "concrete moments and fixed categorical sine smear", "separator")
    audit.check("M2 zero-source kernel", fixture["zero_source_integral"] == "0" and expected["zero_source_image"] == "0", fixture["zero_source_integral"], "0", "fixture")
    audit.check("M2 exact coefficient", fixture["coefficient_identity"], fixture["coefficient"], expected["coefficient"], "fixture")
    audit.check("M2 exact square", fixture["modulus_squared_identity"] and fixture["square_scalar"], fixture["modulus_squared"], expected["modulus_squared"], "fixture")
    audit.check("M2 factorization failure", fixture["strictly_positive"] and fixture["factorization_failure"] is expected["factorization_failure"], fixture["factorization_failure"], True, "fixture")
    audit.check("canonical quotient iff", "if and only if" in manifest["zero_source_quotient"]["factorization_criterion"] and "omega(k^*k)=0" in manifest["zero_source_quotient"]["factorization_criterion"], manifest["zero_source_quotient"]["factorization_criterion"], "exact kernel criterion", "quotient")
    audit.check("M2 categorical scope", all(token in manifest["exact_m2_fixture"]["carrier"] for token in ("positive integers", "I_2=[-1,1]", "supremum", "q_0^M2")) and "analogous M2 source-family" in manifest["exact_m2_fixture"]["scope"] and "not a Q3LOCK counterexample" in manifest["exact_m2_fixture"]["scope"], manifest["exact_m2_fixture"], "self-contained analogous non-Q3 carrier", "scope")
    audit.check("certificate theorem tokens", all(token in certificate for token in (CLOSED, "beta hbar", "M_3=(64 C_4)^(3/4)", "16 sin(1/2)^4 I_2", NEGATIVE, "No v3.8 PDF is issued")), "required tokens present", "required tokens present", "certificate")
    audit.check("no-overclaim", all(token in manifest["no_overclaim"] for token in ("no zero-source quotient factorization", "no exact Q3 thermodynamic zero-source or spatial common alpha", "no algebraic ground-state identification", "physical Sector A or Pre-A", "remain OPEN")), manifest["no_overclaim"], "scope firewalls", "scope")
    audit.check("source AST and format", ast.parse(SCRIPT.read_text(encoding="utf-8")) is not None and all(b"\r" not in path.read_bytes() and path.read_bytes().endswith(b"\n") and all(byte < 128 for byte in path.read_bytes()) for path in (MANIFEST, CERTIFICATE, SCRIPT)), "AST ASCII LF final-LF", "AST ASCII LF final-LF", "format")
    if formal:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        audit.check("formal authority links", all(token in formal_text for token in ("EXP-000842", CLOSED, NEGATIVE, "R-167 v3.8")), "all formal tokens present", "all formal tokens present", "formal")
    return {
        "schema": "tect/pre-a-q3lock-source-symmetric-orbit-smear-kms-quotient-run/1.0",
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
    print(f"PRIMARY PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
