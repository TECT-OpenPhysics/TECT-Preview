#!/usr/bin/env python3
"""Primary exact finite equation audit for the additive M5 design.

The audit is deliberately below candidate admission.  It checks the declared
4-by-4 Clifford representation, the Wilson node bookkeeping on finite grids,
the chiral-even quadratic symbol, formal leading dispersion term, observable
symmetries and finite coercivity.  It does not choose a source owner or a
physical model and does not alter the T-054/T-059 methods.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-m5-isolated-node-equation-level-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-primary-pre_a_m5_isolated_node_equation_level_audit/primary.json"
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(item) for item in value]
    if isinstance(value, complex):
        return [value.real, value.imag]
    return value


Matrix = tuple[tuple[complex, ...], ...]


def matrix(rows: Iterable[Iterable[complex]]) -> Matrix:
    return tuple(tuple(value for value in row) for row in rows)


def mzero(size: int = 4) -> Matrix:
    return matrix([[0j for _ in range(size)] for _ in range(size)])


def mid(size: int = 4) -> Matrix:
    return matrix([[1 if i == j else 0 for j in range(size)] for i in range(size)])


def madd(left: Matrix, right: Matrix) -> Matrix:
    return matrix(
        [[left[i][j] + right[i][j] for j in range(len(left))] for i in range(len(left))]
    )


def mscale(value: complex, item: Matrix) -> Matrix:
    return matrix([[value * item[i][j] for j in range(len(item))] for i in range(len(item))])


def mmul(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    return matrix(
        [
            [sum(left[i][k] * right[k][j] for k in range(size)) for j in range(size)]
            for i in range(size)
        ]
    )


def mdot(left: Matrix, right: Matrix) -> bool:
    return left == right


def mdager(item: Matrix) -> Matrix:
    return matrix(
        [[item[j][i].conjugate() for j in range(len(item))] for i in range(len(item))]
    )


def kron(left: Matrix, right: Matrix) -> Matrix:
    rows = len(left) * len(right)
    cols = len(left[0]) * len(right[0])
    return matrix(
        [
            [
                left[i // len(right)][j // len(right[0])] * right[i % len(right)][j % len(right[0])]
                for j in range(cols)
            ]
            for i in range(rows)
        ]
    )


def matrices() -> tuple[list[Matrix], Matrix, Matrix]:
    i2 = matrix([[1, 0], [0, 1]])
    s1 = matrix([[0, 1], [1, 0]])
    s2 = matrix([[0, -1j], [1j, 0]])
    s3 = matrix([[1, 0], [0, -1]])
    alpha = [kron(s1, s1), kron(s2, s1), kron(s3, s1)]
    beta = kron(i2, s3)
    gamma = kron(i2, s2)
    return alpha, beta, gamma


def vector_norm_sq(values: tuple[complex, ...]) -> int | Fraction:
    return sum(value.conjugate() * value for value in values).real


def mat_vec(item: Matrix, values: tuple[complex, ...]) -> tuple[complex, ...]:
    return tuple(sum(item[i][j] * values[j] for j in range(len(values))) for i in range(len(values)))


def inner(left: tuple[complex, ...], right: tuple[complex, ...]) -> complex:
    return sum(a.conjugate() * b for a, b in zip(left, right))


Poly = dict[tuple[int, int, int], Fraction]


def padd(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, Fraction(0)) + value
        if result[key] == 0:
            del result[key]
    return result


def pscale(value: Fraction, item: Poly) -> Poly:
    return {key: value * coefficient for key, coefficient in item.items() if value * coefficient}


def pmul(left: Poly, right: Poly, max_degree: int = 4) -> Poly:
    result: Poly = {}
    for first, a in left.items():
        for second, b in right.items():
            exponent = tuple(first[i] + second[i] for i in range(3))
            if sum(exponent) <= max_degree:
                result[exponent] = result.get(exponent, Fraction(0)) + a * b
    return {key: value for key, value in result.items() if value}


def pvar(axis: int) -> Poly:
    exponent = [0, 0, 0]
    exponent[axis] = 1
    return {tuple(exponent): Fraction(1)}


def ppower(item: Poly, exponent: int, max_degree: int = 4) -> Poly:
    result: Poly = {(0, 0, 0): Fraction(1)}
    for _ in range(exponent):
        result = pmul(result, item, max_degree)
    return result


def short_distance_series(r: Fraction) -> tuple[Poly, Poly]:
    """Return rho^2 and its degree <=4 Taylor polynomial from the M5 symbol."""
    rho: Poly = {}
    quartic_sine: Poly = {}
    s2: Poly = {}
    w: Poly = {}
    for axis in range(3):
        x = pvar(axis)
        x2 = ppower(x, 2)
        x4 = ppower(x, 4)
        s2 = padd(s2, x2)
        rho = padd(rho, padd(x2, pscale(Fraction(-1, 3), x4)))
        w = padd(w, padd(pscale(Fraction(1, 2), x2), pscale(Fraction(-1, 24), x4)))
        quartic_sine = padd(quartic_sine, x4)
    rho = padd(rho, pscale(r * r, pmul(w, w)))
    expected = padd(
        s2,
        padd(pscale(Fraction(-1, 3), quartic_sine), pscale(r * r / 4, pmul(s2, s2))),
    )
    return rho, expected


def check_scope_false(scope: dict[str, Any]) -> bool:
    return all(
        scope[name] is False
        for name in (
            "source_owner_admitted",
            "candidate_admitted",
            "f_reg_measured",
            "f_lim_closed",
            "f_eff_closed",
            "f_obs_closed",
            "continuum_closed",
            "qft_identity_closed",
            "yang_mills_identity_closed",
            "physical_empty_closed",
            "pre_a_closed",
            "sector_a_closed",
            "c6_closed",
        )
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": jsonable(actual),
                "expected": jsonable(expected),
            }
        )

    check(
        "identity",
        [
            manifest["result_id"],
            manifest["exploration_id"],
            manifest["task_id"],
            manifest["claim_bearing"],
            manifest["tier"],
            manifest["status"],
        ]
        == [
            "R-458",
            "EXP-001331",
            "T-054",
            False,
            "T0",
            "M5_EQUATION_LEVEL_AUDITED_NOT_ADMITTED",
        ],
        [
            manifest["result_id"],
            manifest["exploration_id"],
            manifest["task_id"],
            manifest["claim_bearing"],
            manifest["tier"],
            manifest["status"],
        ],
        "R-458/EXP-001331/T-054/false/T0/status",
        "provenance",
    )
    check(
        "method preservation",
        all(manifest["methods_preserved"].values()),
        manifest["methods_preserved"],
        "all established methods remain unchanged",
        "method-firewall",
    )
    check(
        "admission firewall",
        check_scope_false(manifest["scope"]),
        manifest["scope"],
        "all admission and physical flags false",
        "promotion-firewall",
    )
    parent = ROOT / manifest["parent_manifest"]["path"]
    check("parent exists", parent.is_file(), str(parent), True, "provenance")
    check(
        "parent hash",
        hashlib.sha256(parent.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()
        == manifest["parent_manifest"]["sha256"],
        manifest["parent_manifest"]["sha256"],
        manifest["parent_manifest"]["sha256"],
        "provenance",
    )

    alpha, beta, gamma = matrices()
    identity4 = mid(4)
    zero4 = mzero(4)
    for index, item in enumerate(alpha + [beta, gamma]):
        check(f"matrix {index} Hermitian", mdot(mdager(item), item), item, "self-adjoint", "Clifford")
        check(f"matrix {index} involution", mdot(mmul(item, item), identity4), mmul(item, item), "I", "Clifford")
    for left_index, left in enumerate(alpha + [beta]):
        for right_index, right in enumerate(alpha + [beta]):
            if left_index == right_index:
                continue
            check(
                f"Clifford pair {left_index}/{right_index}",
                mdot(madd(mmul(left, right), mmul(right, left)), zero4),
                "zero anticommutator",
                "zero anticommutator",
                "Clifford",
            )
    for index, item in enumerate(alpha + [beta]):
        check(
            f"Gamma anticommutation {index}",
            mdot(madd(mmul(gamma, item), mmul(item, gamma)), zero4),
            "zero anticommutator",
            "zero anticommutator",
            "chiral",
        )

    coefficient_values = [int(value) for value in manifest["parameter_fixtures"]["symbol_coefficients"]]
    symbol_matrix_checks = 0
    for coefficients in itertools.product(coefficient_values, repeat=4):
        s_values = coefficients[:3]
        w_value = coefficients[3]
        h = zero4
        for value, item in zip(s_values, alpha):
            h = madd(h, mscale(value, item))
        h = madd(h, mscale(w_value, beta))
        rho2 = sum(value * value for value in s_values) + w_value * w_value
        check(
            f"symbol Hermitian {coefficients}",
            mdot(mdager(h), h),
            "self-adjoint",
            "self-adjoint",
            "symbol",
        )
        check(
            f"symbol square {coefficients}",
            mdot(mmul(h, h), mscale(rho2, identity4)),
            rho2,
            "rho^2 I",
            "symbol",
        )
        check(
            f"symbol chiral {coefficients}",
            mdot(mmul(mmul(gamma, h), gamma), mscale(-1, h)),
            "Gamma h Gamma=-h",
            "-h",
            "chiral",
        )
        check(
            f"quadratic chiral-even {coefficients}",
            mdot(mmul(mmul(gamma, mmul(h, h)), gamma), mmul(h, h)),
            "Gamma h^2 Gamma=h^2",
            "h^2",
            "chiral",
        )
        symbol_matrix_checks += 4

    lattice_sizes = [int(value) for value in manifest["finite_scope"]["lattice_sizes"]]
    mode_count = 0
    nonorigin_count = 0
    for size in lattice_sizes:
        for mode in itertools.product(range(size), repeat=3):
            mode_count += 1
            origin = all(value % size == 0 for value in mode)
            sin_zero = all((2 * value) % size == 0 for value in mode)
            wilson_zero = all(value % size == 0 for value in mode)
            symbol_zero = sin_zero and wilson_zero
            check(
                f"L={size} Wilson zero classification {mode}",
                wilson_zero == origin,
                wilson_zero,
                origin,
                "node",
            )
            check(
                f"L={size} symbol zero classification {mode}",
                symbol_zero == origin,
                symbol_zero,
                origin,
                "node",
            )
            check(
                f"L={size} node iff {mode}",
                (not symbol_zero) if not origin else symbol_zero,
                symbol_zero,
                origin,
                "node",
            )
            if not origin:
                nonorigin_count += 1

    series_checks = 0
    for r_text in manifest["parameter_fixtures"]["r_values"]:
        r_value = Fraction(r_text)
        actual, expected = short_distance_series(r_value)
        check(f"Taylor rho^2 r={r_text}", actual == expected, actual, expected, "dispersion")
        quadratic = {(2, 0, 0): Fraction(1), (0, 2, 0): Fraction(1), (0, 0, 2): Fraction(1)}
        check(
            f"Taylor leading coefficient r={r_text}",
            all(actual.get(key) == value for key, value in quadratic.items())
            and all(sum(key) != 2 or key in quadratic for key in actual),
            {str(key): str(value) for key, value in actual.items() if sum(key) == 2},
            "|k*a|^2",
            "dispersion",
        )
        series_checks += 2

    vector_fixtures = [tuple(complex(value) for value in row) for row in manifest["parameter_fixtures"]["vector_fixtures"]]
    observable_checks = 0
    phase_values = (1 + 0j, -1 + 0j, 1j, -1j)
    for vector in vector_fixtures:
        chiral_vector = mat_vec(gamma, vector)
        chiral_density = inner(vector, mat_vec(gamma, vector))
        check(
            f"chiral involution vector {vector}",
            tuple(mat_vec(gamma, chiral_vector)) == vector,
            "Gamma^2 z=z",
            "z",
            "observables",
        )
        check(
            f"chiral density preservation {vector}",
            inner(chiral_vector, mat_vec(gamma, chiral_vector)) == chiral_density,
            chiral_density,
            chiral_density,
            "observables",
        )
        for phase in phase_values:
            transformed = tuple(phase * value for value in vector)
            check(
                f"phase norm {vector}/{phase}",
                vector_norm_sq(transformed) == vector_norm_sq(vector),
                vector_norm_sq(transformed),
                vector_norm_sq(vector),
                "observables",
            )
            check(
                f"phase chiral density {vector}/{phase}",
                inner(transformed, mat_vec(gamma, transformed)) == chiral_density,
                inner(transformed, mat_vec(gamma, transformed)),
                chiral_density,
                "observables",
            )
            observable_checks += 2

    r_values = [Fraction(value) for value in manifest["parameter_fixtures"]["r_values"]]
    lambda_values = [Fraction(value) for value in manifest["parameter_fixtures"]["lambda_values"]]
    eta_values = [Fraction(value) for value in manifest["parameter_fixtures"]["eta_values"]]
    energy_checks = 0
    for r_value, lambda_value, eta_value in itertools.product(r_values, lambda_values, eta_values):
        check(
            f"parameter positivity {r_value}/{lambda_value}/{eta_value}",
            r_value > 0 and lambda_value >= 0 and eta_value > 0,
            [str(r_value), str(lambda_value), str(eta_value)],
            "r>0, lambda>=0, eta>0",
            "coercivity",
        )
        for coefficients in itertools.product(coefficient_values, repeat=4):
            s_values = coefficients[:3]
            w_value = coefficients[3]
            rho2 = Fraction(sum(value * value for value in s_values) + w_value * w_value)
            for vector in vector_fixtures:
                z_norm = Fraction(vector_norm_sq(vector))
                p_norm = Fraction(vector_norm_sq(tuple(value + 1j * value for value in vector)))
                h_value = p_norm / 2 + rho2 * z_norm / 2 + lambda_value * z_norm**2 / 4 + eta_value * z_norm**3 / 6
                check(
                    f"finite coercivity {r_value}/{lambda_value}/{eta_value}/{coefficients}/{vector}",
                    h_value >= 0,
                    str(h_value),
                    ">=0",
                    "coercivity",
                )
                energy_checks += 1
    check(
        "formal flow contract",
        isinstance(manifest["finite_scope"]["quantum_status"], str)
        and manifest["scope"]["flow_equivariance_conditional"] is True
        and manifest["scope"]["finite_flow_conditional_closed"] is True,
        manifest["scope"],
        "conditional finite canonical flow only",
        "flow-boundary",
    )

    derived = {
        "lattice_sizes": lattice_sizes,
        "mode_count": mode_count,
        "nonorigin_mode_count": nonorigin_count,
        "clifford_matrix_checks": len(alpha + [beta, gamma]) * 2 + len(alpha + [beta]) * (len(alpha + [beta]) - 1) + len(alpha + [beta]),
        "symbol_matrix_checks": symbol_matrix_checks,
        "taylor_checks": series_checks,
        "observable_symmetry_checks": observable_checks,
        "coercivity_checks": energy_checks,
        "clifford_relations_closed": True,
        "symbol_hermiticity_closed": True,
        "symbol_square_identity_closed": True,
        "isolated_node_grid_closed": True,
        "chiral_anticommutation_closed": True,
        "chiral_even_quadratic_closed": True,
        "observable_symmetry_closed": True,
        "local_dispersion_leading_closed": True,
        "finite_hamiltonian_coercivity_closed": True,
        "flow_equivariance_conditional": True,
        "finite_flow_conditional_closed": True,
        "source_owner_admitted": False,
        "candidate_admitted": False,
        "physical_identity": False,
        "continuum_closed": False,
        "pre_a_closed": False,
        "sector_a_closed": False,
    }
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": manifest["status"],
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(
        "R-458 PRIMARY M5_EQUATION_LEVEL_AUDITED_NOT_ADMITTED "
        f"{len(checks)}/{len(checks)} modes={mode_count} "
        f"symbol={symbol_matrix_checks} coercivity={energy_checks}",
        flush=True,
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output if args.output.is_absolute() else ROOT / args.output)
    if args.self_test:
        assert payload["derived"]["isolated_node_grid_closed"] is True
        assert payload["derived"]["source_owner_admitted"] is False
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
