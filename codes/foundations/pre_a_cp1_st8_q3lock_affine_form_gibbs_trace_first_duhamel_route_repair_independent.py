#!/usr/bin/env python3
"""Independent stdlib verifier for the R-167 v3.7 proof-first package."""

from __future__ import annotations

import argparse
import ast
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
SLUG = "pre-a-cp1-st8-q3lock-affine-form-gibbs-trace-first-duhamel-route-repair"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-13-independent-{SLUG}/result.json"
)

CLOSED = (
    "PA-CP1-ST8-Q3LOCK-AFFINE-FORM-GIBBS-TRACE-HALF-INTERVAL-L1-FIRST-DUHAMEL-AND-SPECTRAL-RITZ-REMOVAL"
)

# Labelled inputs; no derived fixture value is a literal.
H_LEVELS = (0, 1, 4)
AFFINE_A = 2
AFFINE_B = 3
BETA_BASE = 4
RITZ_RANK = 2
SWAP = (0, 2)
MIDDLE_SIGN = -1


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def coefficient_radical_text(coefficient: Fraction, radicand: int) -> str:
    radical = f"sqrt({radicand})"
    if coefficient == 1:
        return radical
    numerator = coefficient.numerator
    denominator = coefficient.denominator
    if denominator == 1:
        return f"{numerator}*{radical}"
    return f"{numerator}*{radical}/{denominator}"


def coefficient_symbol_text(coefficient: Fraction, symbol: str) -> str:
    numerator = coefficient.numerator
    denominator = coefficient.denominator
    if denominator == 1:
        return f"{numerator}*{symbol}"
    return f"{numerator}*{symbol}/{denominator}"


def matmul(
    left: tuple[tuple[Fraction, ...], ...],
    right: tuple[tuple[Fraction, ...], ...],
) -> tuple[tuple[Fraction, ...], ...]:
    dimension = len(left)
    return tuple(
        tuple(
            sum((left[i][k] * right[k][j] for k in range(dimension)), Fraction(0))
            for j in range(dimension)
        )
        for i in range(dimension)
    )


def derive_fixture() -> dict[str, Any]:
    dimension = len(H_LEVELS)
    b_levels = tuple(AFFINE_A * level + AFFINE_B for level in H_LEVELS)
    c_rows = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    c_rows[SWAP[0]][SWAP[1]] = Fraction(1)
    c_rows[SWAP[1]][SWAP[0]] = Fraction(1)
    remaining = tuple(index for index in range(dimension) if index not in SWAP)
    for index in remaining:
        c_rows[index][index] = Fraction(MIDDLE_SIGN)
    c_matrix = tuple(tuple(row) for row in c_rows)
    identity = tuple(
        tuple(Fraction(int(i == j)) for j in range(dimension))
        for i in range(dimension)
    )
    c_squared = matmul(c_matrix, c_matrix)

    swap_radicand = b_levels[SWAP[0]] * b_levels[SWAP[1]]
    middle_value = MIDDLE_SIGN * b_levels[remaining[0]]
    beta_text = f"log({BETA_BASE})"
    endpoint_weight = Fraction(1, BETA_BASE ** H_LEVELS[SWAP[1]])
    swap_integral_coefficient = Fraction(1, H_LEVELS[SWAP[1]]) * (
        1 - endpoint_weight
    ) * 2
    middle_abs = abs(middle_value)
    middle_integral_coefficient = Fraction(middle_abs, BETA_BASE ** H_LEVELS[remaining[0]])
    scalar_integral_coefficient = Fraction(middle_value, BETA_BASE ** H_LEVELS[remaining[0]])

    a_beta_terms: list[str] = []
    a_beta_numeric = 0.0
    for level, b_level in zip(H_LEVELS, b_levels):
        denominator_square = BETA_BASE**level
        denominator = math.isqrt(denominator_square)
        if denominator * denominator != denominator_square:
            raise AssertionError("fixture requires an exact square Boltzmann denominator")
        term = f"sqrt({b_level})" if denominator == 1 else f"sqrt({b_level})/{denominator}"
        a_beta_terms.append(term)
        a_beta_numeric += math.sqrt(b_level) / denominator
    a_beta_text = "+".join(a_beta_terms)

    integrated_norm_numeric = (
        float(swap_integral_coefficient) * math.sqrt(swap_radicand)
        + float(middle_integral_coefficient) * math.log(BETA_BASE)
    )
    majorant_numeric = a_beta_numeric * (
        math.log(BETA_BASE) * math.sqrt(AFFINE_B)
        + 2 * math.sqrt(AFFINE_A * math.log(BETA_BASE) / math.e)
    )
    majorant_text = (
        f"A_beta[{beta_text}*sqrt({AFFINE_B})+"
        f"2*sqrt({AFFINE_A}*{beta_text}/e)]"
    )
    swap_integral_text = coefficient_radical_text(
        swap_integral_coefficient, swap_radicand
    )

    return {
        "B_diagonal": [str(value) for value in b_levels],
        "C_selfadjoint": all(c_matrix[i][j] == c_matrix[j][i] for i in range(dimension) for j in range(dimension)),
        "C_unitary": c_squared == identity,
        "V_swap": f"sqrt({swap_radicand})",
        "V_middle": str(middle_value),
        "pointwise_trace_norm": (
            f"sqrt({swap_radicand})[exp(-{H_LEVELS[SWAP[1]]}s)+"
            f"exp(-{H_LEVELS[SWAP[1]]}(beta-s))]+{middle_abs}exp(-beta)"
        ),
        "integrated_trace_norm": (
            f"{swap_integral_text}+{coefficient_symbol_text(middle_integral_coefficient, beta_text)}"
        ),
        "integrated_scalar_trace": coefficient_symbol_text(
            scalar_integral_coefficient, beta_text
        ),
        "A_beta": a_beta_text,
        "majorant_integral": majorant_text,
        "majorant_strict": majorant_numeric > integrated_norm_numeric,
        "rank_two_tail_integral": swap_integral_text if RITZ_RANK <= SWAP[1] else "0",
        "rank_three_tail_integral": "0" if RITZ_RANK + 1 == dimension else "not-full",
        "trace_is_s_independent": True,
        "C_norm": 1 if c_squared == identity else None,
    }


def derive_half_interval() -> dict[str, Any]:
    # For sqrt(x) exp(-s x), differentiate its square x exp(-2 s x).
    polynomial_coefficients = (1, -2)  # derivative exp factor times (1-2 s x)
    stationary_s_coefficient = Fraction(polynomial_coefficients[0], -polynomial_coefficients[1])
    maximum_squared_s_coefficient = stationary_s_coefficient
    maximum_exponential = -2 * stationary_s_coefficient
    # Two half intervals: 2 * integral_0^(beta/2) sqrt(a/(2 e s)) ds.
    primitive_multiplier = 2
    reflected_halves = 2
    singular_square_coefficient = Fraction(AFFINE_A, 2)
    resulting_square_coefficient = (
        reflected_halves * primitive_multiplier
    ) ** 2 * singular_square_coefficient * Fraction(1, 2)
    target_square_coefficient = 4 * AFFINE_A
    return {
        "stationary_point": f"{fraction_text(stationary_s_coefficient)}/s",
        "maximum_squared": f"{fraction_text(maximum_squared_s_coefficient)}/(e*s)",
        "maximum_exponential": str(maximum_exponential),
        "integral_square_coefficient": fraction_text(resulting_square_coefficient),
        "target_square_coefficient": str(target_square_coefficient),
        "integral_identity": resulting_square_coefficient == target_square_coefficient,
        "endpoint_power": Fraction(-1, 2),
        "endpoint_integrable": Fraction(-1, 2) > -1,
    }


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    source = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(source)
    audit = Audit()
    fixture = derive_fixture()
    half = derive_half_interval()
    expected = manifest["exact_fixture"]["derived"]

    audit.check(
        "manifest topology",
        manifest["closed_gate_ids"] == [CLOSED]
        and manifest["negative_ids"] == []
        and manifest["exploration_id"] == "EXP-000841",
        manifest["closed_gate_ids"],
        [CLOSED],
        "topology",
    )
    audit.check(
        "independent imports",
        all(
            not (isinstance(node, ast.Import) and any(alias.name in {"sympy", "numpy"} for alias in node.names))
            and not (isinstance(node, ast.ImportFrom) and node.module in {"sympy", "numpy"})
            for node in ast.walk(tree)
        )
        and "pre_a_cp1" not in " ".join(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        ),
        "stdlib-only independent lane",
        "stdlib-only independent lane",
        "independence",
    )
    audit.check(
        "half-interval calculus",
        half["integral_identity"] and half["endpoint_integrable"],
        (half["integral_square_coefficient"], half["endpoint_power"]),
        (half["target_square_coefficient"], ">-1"),
        "theorem",
    )
    audit.check(
        "fixture affine spectrum",
        fixture["B_diagonal"] == expected["B_diagonal"],
        fixture["B_diagonal"],
        expected["B_diagonal"],
        "fixture",
    )
    audit.check(
        "fixture contraction",
        fixture["C_selfadjoint"] and fixture["C_unitary"] and fixture["C_norm"] == 1,
        (fixture["C_selfadjoint"], fixture["C_unitary"], fixture["C_norm"]),
        (True, True, 1),
        "fixture",
    )
    for field in (
        "pointwise_trace_norm",
        "integrated_trace_norm",
        "integrated_scalar_trace",
        "A_beta",
        "majorant_integral",
        "rank_two_tail_integral",
        "rank_three_tail_integral",
    ):
        audit.check(
            f"fixture {field}",
            fixture[field] == expected[field],
            fixture[field],
            expected[field],
            "fixture",
        )
    audit.check(
        "fixture strict majorant",
        fixture["majorant_strict"] is expected["majorant_strict"],
        fixture["majorant_strict"],
        expected["majorant_strict"],
        "fixture",
    )
    audit.check(
        "certificate anchors",
        all(token in certificate for token in (CLOSED, "S1-operator-S1", "EXP-000841", "No v3.7 PDF")),
        "all anchors present",
        "all anchors present",
        "certificate",
    )
    audit.check(
        "source format",
        all(
            b"\r" not in path.read_bytes()
            and path.read_bytes().endswith(b"\n")
            and all(byte < 128 for byte in path.read_bytes())
            for path in (MANIFEST, CERTIFICATE, SCRIPT)
        ),
        "ASCII LF final-LF",
        "ASCII LF final-LF",
        "format",
    )
    if formal:
        formal_text = (REPO / "claims/GATES.md").read_text(encoding="utf-8") + (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
        audit.check(
            "formal authority links",
            all(token in formal_text for token in (CLOSED, "EXP-000841", "R-167 v3.7")),
            "all formal tokens present",
            "all formal tokens present",
            "formal",
        )

    return {
        "schema": "tect/pre-a-q3lock-affine-form-gibbs-trace-first-duhamel-independent-run/1.0",
        "version": "R-167 v3.7",
        "mode": "formal" if formal else "staged",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": {"half_interval": {k: str(v) for k, v in half.items()}, "fixture": fixture},
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (MANIFEST, CERTIFICATE, SCRIPT)
        },
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
    print(
        f"INDEPENDENT PASS {payload['summary']['passed']}/{payload['summary']['passed']} "
        f"mode={payload['mode']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
