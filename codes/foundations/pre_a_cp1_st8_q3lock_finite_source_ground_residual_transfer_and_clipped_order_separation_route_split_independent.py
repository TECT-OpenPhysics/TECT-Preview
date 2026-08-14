#!/usr/bin/env python3
"""Independent stdlib verifier for the R-167 v3.9 proof-first package."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-finite-source-ground-residual-transfer-and-clipped-order-separation-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-independent-{SLUG}/result.json"

CLOSED = "PA-CP1-ST8-Q3LOCK-FINITE-SOURCE-GROUND-RESIDUAL-TRANSFER-AND-CLIPPED-ORDER-SEPARATION"
NEGATIVE = "NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-EXACT-TARGET-GENERATOR-AND-SEPARATION-AUTOMATIC-TARGET-GROUNDNESS"
REUSED = "NG-2026-08-13-PRE-A-ST8-Q3LOCK-FINITE-GAPS-PLUS-WEAKSTAR-STATES-AUTOMATIC-TARGET-GENERATOR-AND-GNS-GAP-TRANSFER"

# Independent labelled fixture inputs.
Q_VALUES = (-1, 0, 1)
TARGET_EXPONENT = 2
SELECTOR_FACTOR = 2
AVAILABLE_MOMENT_ORDER = 4
N_SAMPLES = (1, 2, 5, 11)
PHASE_SIGNS = (-1, 1)
HBAR = Fraction(1)
ORDER_LOWER = Fraction(2)
FOURTH_CEILING = Fraction(16)
RADIUS = Fraction(4)
EPSILON_FRACTION = Fraction(1, 2)


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


Gaussian = tuple[Fraction, Fraction]
ZERO: Gaussian = (Fraction(0), Fraction(0))
ONE: Gaussian = (Fraction(1), Fraction(0))
I_UNIT: Gaussian = (Fraction(0), Fraction(1))


def g(value: int | Fraction) -> Gaussian:
    return (Fraction(value), Fraction(0))


def g_add(left: Gaussian, right: Gaussian) -> Gaussian:
    return (left[0] + right[0], left[1] + right[1])


def g_sub(left: Gaussian, right: Gaussian) -> Gaussian:
    return (left[0] - right[0], left[1] - right[1])


def g_mul(left: Gaussian, right: Gaussian) -> Gaussian:
    return (left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0])


def g_conjugate(value: Gaussian) -> Gaussian:
    return (value[0], -value[1])


def matrix_diagonal(values: tuple[int, ...]) -> list[list[Gaussian]]:
    return [[g(value if row == column else 0) for column in range(len(values))] for row, value in enumerate(values)]


def multiply(left: list[list[Gaussian]], right: list[list[Gaussian]]) -> list[list[Gaussian]]:
    dimension = len(left)
    product: list[list[Gaussian]] = []
    for row in range(dimension):
        product_row: list[Gaussian] = []
        for column in range(dimension):
            entry = ZERO
            for inner in range(dimension):
                entry = g_add(entry, g_mul(left[row][inner], right[inner][column]))
            product_row.append(entry)
        product.append(product_row)
    return product


def subtract(left: list[list[Gaussian]], right: list[list[Gaussian]]) -> list[list[Gaussian]]:
    return [[g_sub(a, b) for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def scale(value: Gaussian, matrix: list[list[Gaussian]]) -> list[list[Gaussian]]:
    return [[g_mul(value, entry) for entry in row] for row in matrix]


def adjoint(matrix: list[list[Gaussian]]) -> list[list[Gaussian]]:
    return [[g_conjugate(matrix[column][row]) for column in range(len(matrix))] for row in range(len(matrix))]


def expectation(index: int, observable: list[list[Gaussian]]) -> Gaussian:
    return observable[index][index]


def clean_integer(value: Gaussian) -> str:
    if value[1] != 0:
        raise AssertionError(f"expected real exact fixture value, got {value}")
    if value[0].denominator != 1:
        raise AssertionError(f"expected integer exact fixture value, got {value}")
    return str(value[0].numerator)


def exact_m3_fixture() -> dict[str, Any]:
    q = matrix_diagonal(Q_VALUES)
    k = matrix_diagonal(tuple(value**TARGET_EXPONENT for value in Q_VALUES))
    zero_index = Q_VALUES.index(0)
    rows: list[dict[str, Any]] = []
    for n in N_SAMPLES:
        h = Fraction(1, n)
        selector = scale(g(SELECTOR_FACTOR * n), q)
        scaled_selector = scale(g(h), selector)
        for sigma in PHASE_SIGNS:
            source = subtract(k, scale(g(sigma * h), selector))
            eigenvalues = tuple(source[index][index][0] for index in range(len(Q_VALUES)))
            ground_value = min(eigenvalues)
            ground_index = Q_VALUES.index(sigma)
            ground_unique = eigenvalues.count(ground_value) == 1 and eigenvalues[ground_index] == ground_value
            a = [[ZERO for _ in Q_VALUES] for _ in Q_VALUES]
            a[zero_index][ground_index] = ONE
            a_star = adjoint(a)
            h_zero = k
            generator_factor = g_mul(I_UNIT, g(1 / HBAR))
            delta_n_zero = scale(generator_factor, subtract(multiply(h_zero, a), multiply(a, h_zero)))
            target_delta = scale(generator_factor, subtract(multiply(k, a), multiply(a, k)))
            defect = subtract(delta_n_zero, target_delta)
            target_form = g_mul(g_mul(g(-HBAR), I_UNIT), expectation(ground_index, multiply(a_star, target_delta)))
            source_commutator = subtract(multiply(selector, a), multiply(a, selector))
            source_residual = g_mul(g(sigma * h), expectation(ground_index, multiply(a_star, source_commutator)))
            shifted_source = subtract(source, matrix_diagonal(tuple(int(ground_value) for _ in Q_VALUES)))
            finite_form = expectation(ground_index, multiply(multiply(a_star, shifted_source), a))
            defect_term = g_mul(g_mul(I_UNIT, g(HBAR)), expectation(ground_index, multiply(a_star, defect)))
            combined = g_add(source_residual, defect_term)
            rows.append({
                "n": n,
                "sigma": sigma,
                "h_n": str(h),
                "h_n_S_n_equals": [[clean_integer(entry) for entry in row] for row in scaled_selector],
                "finite_source_ground_eigenvalue": str(ground_value.numerator),
                "source_ground_unique": ground_unique,
                "finite_source_excitation_form": clean_integer(finite_form),
                "target_generator_defect": clean_integer(defect_term),
                "source_scalar_residual": clean_integer(source_residual),
                "combined_residual": clean_integer(combined),
                "target_energy_form": clean_integer(target_form),
                "target_decomposition_rhs": clean_integer(g_add(finite_form, combined)),
                "target_groundness": target_form[1] == 0 and target_form[0] >= 0,
            })
    minus_order, plus_order = Q_VALUES[0], Q_VALUES[-1]
    return {
        "rows": rows,
        "parity_related": plus_order == -minus_order,
        "fixed_order_separated": max(abs(value) for value in Q_VALUES) <= 1 and plus_order - minus_order > 0,
        "order_values": [str(minus_order), str(plus_order)],
    }


def clipped_order_fixture() -> dict[str, Any]:
    radius_fourth = RADIUS**AVAILABLE_MOMENT_ORDER
    d_r = ORDER_LOWER / RADIUS - FOURTH_CEILING / radius_fourth
    epsilon = EPSILON_FRACTION * d_r
    retained = d_r - epsilon
    distance = (1 - (-1)) * retained
    threshold_cubed = FOURTH_CEILING / ORDER_LOWER
    return {
        "radius_fourth_power": str(radius_fourth),
        "d_R": str(d_r),
        "epsilon": str(epsilon),
        "retained_order": str(retained),
        "distance_lower_bound": str(distance),
        "radius_above_threshold": RADIUS**3 > threshold_cubed,
        "positive": d_r > 0 and 0 < epsilon < d_r,
    }


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    fixture = exact_m3_fixture()
    clipped = clipped_order_fixture()
    expected = manifest["exact_m3_fixture"]["derived"]
    audit = Audit()
    audit.check("manifest identity", manifest["package_id"] == SLUG and manifest["version"] == "R-167 v3.9" and manifest["exploration_id"] == "EXP-000843" and manifest["claim_bearing"] is False, (manifest["package_id"], manifest["version"], manifest["exploration_id"]), (SLUG, "R-167 v3.9", "EXP-000843"), "identity")
    audit.check("manifest topology", manifest["closed_gate_ids"] == [CLOSED] and manifest["negative_ids"] == [NEGATIVE] and manifest["reused_negative_ids"] == [REUSED], (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]), ([CLOSED], [NEGATIVE], [REUSED]), "topology")
    theorem = manifest["ground_residual_transfer"]
    audit.check("typed combined residual", all(token in theorem["finite_energy_identity"] + theorem["target_decomposition"] for token in ("hat omega_n", "tilde omega_n", "quadratic-form commutator identity", "+i hbar", "cal E_n(A)+R_n(A)")), theorem, "typed expectation-level theorem", "theorem")
    audit.check("fixed-sign and invariance", "Fix one sign" in theorem["setup"] and "applied separately" in theorem["setup"] and all(token in theorem["conclusion"] for token in ("1+zA", "every complex z", "omega(delta A)=0", "alpha-invariant")), theorem, "fixed sign and positivity-derived invariance", "theorem")
    separation = " ".join(manifest["clipped_order_separation"].values())
    audit.check("carrier separation premise", all(token in separation for token in ("locally normal", "affiliated", "strong-star dense", "odd self-adjoint contraction", "not claimed to belong")), separation, "normal clipped carrier approximation", "separation")
    audit.check("independent clipped arithmetic", clipped["radius_above_threshold"] and clipped["positive"] and Fraction(clipped["distance_lower_bound"]) == 2 * Fraction(clipped["retained_order"]), clipped, "positive exact bound", "separation")
    rows = fixture["rows"]
    audit.check("fixture row count", len(rows) == len(N_SAMPLES) * len(PHASE_SIGNS), len(rows), len(N_SAMPLES) * len(PHASE_SIGNS), "fixture")
    for key in ("finite_source_ground_eigenvalue", "finite_source_excitation_form", "target_generator_defect", "source_scalar_residual", "combined_residual", "target_energy_form", "target_decomposition_rhs"):
        audit.check(f"fixture exact {key}", all(row[key] == expected[key] for row in rows), sorted({row[key] for row in rows}), expected[key], "fixture")
    audit.check("fixture uniqueness and target failure", all(row["source_ground_unique"] is expected["source_ground_unique"] and row["target_groundness"] is expected["target_groundness"] for row in rows), (all(row["source_ground_unique"] for row in rows), any(row["target_groundness"] for row in rows)), (True, False), "fixture")
    audit.check("fixture parity separator", fixture["parity_related"] is expected["parity_related"] and fixture["fixed_order_separated"] is expected["fixed_order_separated"], (fixture["parity_related"], fixture["fixed_order_separated"]), (True, True), "fixture")
    scaled = {json.dumps(row["h_n_S_n_equals"]) for row in rows}
    audit.check("scaled selector nonvanishing and constant", len(scaled) == 1 and next(iter(scaled)) != json.dumps([["0"] * len(Q_VALUES) for _ in Q_VALUES]), scaled, "one nonzero 2Q", "fixture")
    audit.check("certificate tokens", all(token in certificate for token in ("hat omega_n", "tilde omega_n", "quadratic-form commutator identity", "1+zA", "strong-star dense", "-1=1+(-2)", NEGATIVE)), "required tokens present", "required tokens present", "certificate")
    audit.check("scope firewalls", all(token in certificate for token in ("not a Q3LOCK counterexample", "no exact-Q3 common target representation", "positive broken-sector GNS gap", "No v3.9 PDF is issued")), "scope tokens present", "scope tokens present", "scope")
    audit.check("source AST and format", ast.parse(SCRIPT.read_text(encoding="utf-8")) is not None and all(b"\r" not in path.read_bytes() and path.read_bytes().endswith(b"\n") and all(byte < 128 for byte in path.read_bytes()) for path in (MANIFEST, CERTIFICATE, SCRIPT)), "AST ASCII LF final-LF", "AST ASCII LF final-LF", "format")
    if formal:
        formal_paths = (REPO / "claims/GATES.md", REPO / "RESULTS-LEDGER.md", REPO / "negative-results/registry.md", REPO / "explorations/log.jsonl")
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in formal_paths)
        audit.check("formal authority links", all(token in formal_text for token in ("EXP-000843", CLOSED, NEGATIVE, "R-167 v3.9")), "all formal tokens present", "all formal tokens present", "formal")
    return {
        "schema": "tect/pre-a-q3lock-finite-source-ground-residual-transfer-independent-run/1.0",
        "version": "R-167 v3.9",
        "mode": "formal" if formal else "staged",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": {"m3": fixture, "clipped": clipped},
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
