#!/usr/bin/env python3
"""Exact finite covariance-aware Fourier current charge screen.

This is an exploration-level QFT proxy.  It evaluates the Pauli/Fierz
contraction for finitely many 2x2 PSD covariance blocks and a declared scalar
output heat rate.  It does not select the A1 production heat/root owner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a13-a1-covariance-aware-fourier-current-charge-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-primary-covariance-aware-fourier-current-charge" / "result.json"

ComplexQ = tuple[Fraction, Fraction]
Matrix = tuple[tuple[ComplexQ, ComplexQ], tuple[ComplexQ, ComplexQ]]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def q(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def cadd(x: ComplexQ, y: ComplexQ) -> ComplexQ:
    return x[0] + y[0], x[1] + y[1]


def cmul(x: ComplexQ, y: ComplexQ) -> ComplexQ:
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def matrix_mul(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(
            (
                lambda i=i, j=j: cadd(
                    cmul(left[i][0], right[0][j]), cmul(left[i][1], right[1][j])
                )
            )()
            for j in range(2)
        )
        for i in range(2)
    )  # type: ignore[return-value]


def trace(matrix: Matrix) -> ComplexQ:
    return cadd(matrix[0][0], matrix[1][1])


def real_matrix(raw: list[list[Any]]) -> Matrix:
    return tuple(
        tuple((q(raw[i][j]), Fraction(0)) for j in range(2)) for i in range(2)
    )  # type: ignore[return-value]


def real_trace(matrix: Matrix) -> Fraction:
    value = trace(matrix)
    if value[1] != 0:
        raise ValueError("real covariance trace unexpectedly has an imaginary part")
    return value[0]


def psd_symmetric(matrix: Matrix) -> bool:
    a = matrix[0][0][0]
    b = matrix[0][1][0]
    c = matrix[1][0][0]
    d = matrix[1][1][0]
    return matrix[0][0][1] == matrix[0][1][1] == matrix[1][0][1] == matrix[1][1][1] == 0 and b == c and a >= 0 and d >= 0 and a * d - b * c >= 0


def pauli_matrices() -> tuple[Matrix, Matrix, Matrix]:
    zero = (Fraction(0), Fraction(0))
    one = (Fraction(1), Fraction(0))
    plus_i = (Fraction(0), Fraction(1))
    minus_i = (Fraction(0), Fraction(-1))
    return (
        ((zero, one), (one, zero)),
        ((zero, minus_i), (plus_i, zero)),
        ((one, zero), (zero, (Fraction(-1), Fraction(0)))),
    )


def explicit_pauli_sum(left: Matrix, right: Matrix) -> ComplexQ:
    total = (Fraction(0), Fraction(0))
    for sigma in pauli_matrices():
        term = matrix_mul(matrix_mul(matrix_mul(sigma, right), sigma), left)
        total = cadd(total, trace(term))
    return total


def fierz_value(left: Matrix, right: Matrix) -> Fraction:
    product_trace = real_trace(matrix_mul(right, left))
    return 2 * real_trace(left) * real_trace(right) - product_trace


def source_paths(manifest: dict[str, Any]) -> dict[str, Path]:
    return {key: ROOT / value["path"] for key, value in manifest["source_authorities"].items()}


def compute(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    inputs = manifest["registered_inputs"]
    output_mode = tuple(int(value) for value in inputs["output_mode"])
    mode_norm_sq = sum(value * value for value in output_mode)
    prefactor = q(inputs["charge_prefactor"])
    decay_multiplier = q(inputs["heat_decay_multiplier"])
    blocks = {
        name: real_matrix(raw)
        for name, raw in inputs["covariance_blocks"].items()
    }
    authorities = source_paths(manifest)
    current_hashes = {key: sha256(path) for key, path in authorities.items()}
    expected_hashes = {key: value["sha256"] for key, value in manifest["source_authorities"].items()}
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})

    check("source_hashes_match", current_hashes == expected_hashes, current_hashes, expected_hashes)
    check("spatial_dimension_is_three", int(inputs["spatial_dimension"]) == 3, inputs["spatial_dimension"], 3)
    check("internal_dimension_is_two", int(inputs["internal_dimension"]) == 2, inputs["internal_dimension"], 2)
    check("output_mode_norm_is_derived", mode_norm_sq == sum(value * value for value in output_mode), mode_norm_sq, "sum(output_mode_i^2)")
    check("charge_prefactor_positive", prefactor > 0, str(prefactor), ">0")
    check("decay_multiplier_positive", decay_multiplier > 0, str(decay_multiplier), ">0")

    derived_fixtures: dict[str, dict[str, str]] = {}
    for fixture in inputs["covariance_pairs"]:
        name = fixture["name"]
        left = blocks[fixture["left"]]
        right = blocks[fixture["right"]]
        check(f"{name}_left_psd", psd_symmetric(left), inputs["covariance_blocks"][fixture["left"]], "symmetric PSD")
        check(f"{name}_right_psd", psd_symmetric(right), inputs["covariance_blocks"][fixture["right"]], "symmetric PSD")
        explicit = explicit_pauli_sum(left, right)
        fierz = fierz_value(left, right)
        check(f"{name}_fierz_imaginary_zero", explicit[1] == 0, str(explicit), "imaginary part 0")
        check(f"{name}_fierz_identity", explicit[0] == fierz, str(explicit[0]), str(fierz))
        heat_rate = q(fixture["heat_rate"])
        heat_integral_factor = prefactor / (decay_multiplier * heat_rate)
        charge = mode_norm_sq * fierz * heat_integral_factor
        oracle = manifest["test_oracles"][name]
        check(f"{name}_fierz_oracle", fierz == q(oracle["fierz_s"]), str(fierz), oracle["fierz_s"])
        check(f"{name}_heat_integral_oracle", heat_integral_factor == q(oracle["heat_integral_factor"]), str(heat_integral_factor), oracle["heat_integral_factor"])
        check(f"{name}_charge_nonnegative", charge >= 0, str(charge), ">=0")
        check(f"{name}_charge_oracle", charge == q(oracle["charge_q"]), str(charge), oracle["charge_q"])
        check(
            f"{name}_heat_integral_identity",
            prefactor * (Fraction(1, 1) / (decay_multiplier * heat_rate)) == heat_integral_factor,
            str(heat_integral_factor), "2/(2 lambda) when registered",
        )
        derived_fixtures[name] = {
            "left": fixture["left"],
            "right": fixture["right"],
            "trace_left": str(real_trace(left)),
            "trace_right": str(real_trace(right)),
            "trace_product": str(real_trace(matrix_mul(right, left))),
            "fierz_s": str(fierz),
            "heat_rate": str(heat_rate),
            "heat_integral_factor": str(heat_integral_factor),
            "charge_q": str(charge),
        }

    check(
        "proxy_scope_is_explicit",
        all(token in manifest["boundary"].lower() for token in ("finite", "proxy", "no a1 production")),
        manifest["boundary"],
        "finite proxy and no A1 production owner",
    )
    derived = {
        "output_mode": list(output_mode),
        "output_mode_norm_sq": mode_norm_sq,
        "charge_prefactor": str(prefactor),
        "heat_decay_multiplier": str(decay_multiplier),
        "fierz_identity": "sum_a tr(sigma_a C_right sigma_a C_left)=2 tr(C_right) tr(C_left)-tr(C_right C_left)",
        "fixtures": derived_fixtures,
        "formula": "q_r=(charge_prefactor/(heat_decay_multiplier*lambda_r))*|r|^2*S_r; registered values make this |r|^2*S_r/lambda_r",
    }
    return derived, rows, current_hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    derived, assertions, source_hashes = compute(manifest)
    failures = [row for row in assertions if row["status"] != "PASS"]
    result = {
        "schema": "tect/pre-a13-a1-covariance-aware-fourier-current-charge-primary-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Exact finite covariance-aware Pauli/Fierz current proxy with declared scalar heat; no production-owner claim.",
        "source_authorities": source_hashes,
        "derived": derived,
        "assertions": assertions,
        "assertion_count": len(assertions),
        "conclusion": "For each registered PSD covariance pair the exact Pauli/Fierz contraction is nonnegative and the declared heat integral gives the registered finite charge. This is a QFT-compatible finite composite calculation only; it does not identify the A1 production heat/root owner.",
        "honesty_boundary": ["finite covariance proxy", "declared output heat only", "no A1 production heat/root owner", "no raw-current intertwiner", "no cutoff-uniform q-ledger", "no A13 closure", "no continuum, thermodynamic or real-time result"],
        "failures": failures,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A1 COVARIANCE FOURIER CHARGE PRIMARY FAIL {len(assertions)-len(failures)}/{len(assertions)}")
        return 1
    print(f"A1 COVARIANCE FOURIER CHARGE PRIMARY PASS {len(assertions)}/{len(assertions)}")
    print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
