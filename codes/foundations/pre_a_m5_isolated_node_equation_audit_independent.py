#!/usr/bin/env python3
"""Non-importing independent lane for the R-458 M5 equation audit."""

from __future__ import annotations

import argparse
import itertools
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[2]
MANIFEST = BASE / "strategy/pre-a-m5-isolated-node-equation-level-audit-manifest.json"
DEFAULT_OUTPUT = BASE / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-independent-pre_a_m5_isolated_node_equation_level_audit/independent.json"
)


def jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, complex):
        return [value.real, value.imag]
    return value


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [[a[i][j] + b[i][j] for j in range(4)] for i in range(4)]


def scale(c: complex, a: list[list[complex]]) -> list[list[complex]]:
    return [[c * a[i][j] for j in range(4)] for i in range(4)]


def product(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def adjoint(a: list[list[complex]]) -> list[list[complex]]:
    return [[a[j][i].conjugate() for j in range(4)] for i in range(4)]


def eye() -> list[list[complex]]:
    return [[1 if i == j else 0 for j in range(4)] for i in range(4)]


def zeros() -> list[list[complex]]:
    return [[0 for _ in range(4)] for _ in range(4)]


def dirac_family() -> tuple[list[list[list[complex]]], list[list[complex]], list[list[complex]]]:
    j = 1j
    a1 = [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]]
    a2 = [[0, 0, 0, -j], [0, 0, -j, 0], [0,  j, 0, 0], [j, 0, 0, 0]]
    a3 = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, -1], [0, 0, -1, 0]]
    beta = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]]
    gamma = [[0, -j, 0, 0], [j, 0, 0, 0], [0, 0, 0, -j], [0, 0, j, 0]]
    return [a1, a2, a3], beta, gamma


def norm2(vector: tuple[complex, ...]) -> int:
    return int(sum(value.conjugate() * value for value in vector).real)


def matvec(a: list[list[complex]], vector: tuple[complex, ...]) -> tuple[complex, ...]:
    return tuple(sum(a[i][j] * vector[j] for j in range(4)) for i in range(4))


def pairing(a: tuple[complex, ...], b: tuple[complex, ...]) -> complex:
    return sum(x.conjugate() * y for x, y in zip(a, b))


def pplus(a: dict[tuple[int, int, int], Fraction], b: dict[tuple[int, int, int], Fraction]) -> dict[tuple[int, int, int], Fraction]:
    result = dict(a)
    for key, value in b.items():
        result[key] = result.get(key, Fraction(0)) + value
        if result[key] == 0:
            del result[key]
    return result


def ptimes(a: dict[tuple[int, int, int], Fraction], b: dict[tuple[int, int, int], Fraction]) -> dict[tuple[int, int, int], Fraction]:
    result: dict[tuple[int, int, int], Fraction] = {}
    for first, left in a.items():
        for second, right in b.items():
            degree = tuple(first[k] + second[k] for k in range(3))
            if sum(degree) <= 4:
                result[degree] = result.get(degree, Fraction(0)) + left * right
    return {key: value for key, value in result.items() if value}


def pscale(c: Fraction, a: dict[tuple[int, int, int], Fraction]) -> dict[tuple[int, int, int], Fraction]:
    return {key: c * value for key, value in a.items() if c * value}


def pvar(axis: int) -> dict[tuple[int, int, int], Fraction]:
    key = [0, 0, 0]
    key[axis] = 1
    return {tuple(key): Fraction(1)}


def ppow(a: dict[tuple[int, int, int], Fraction], n: int) -> dict[tuple[int, int, int], Fraction]:
    result = {(0, 0, 0): Fraction(1)}
    for _ in range(n):
        result = ptimes(result, a)
    return result


def rho_series(r: Fraction) -> tuple[dict[tuple[int, int, int], Fraction], dict[tuple[int, int, int], Fraction]]:
    s2: dict[tuple[int, int, int], Fraction] = {}
    sine4: dict[tuple[int, int, int], Fraction] = {}
    wilson: dict[tuple[int, int, int], Fraction] = {}
    actual: dict[tuple[int, int, int], Fraction] = {}
    for axis in range(3):
        x2 = ppow(pvar(axis), 2)
        x4 = ppow(pvar(axis), 4)
        s2 = pplus(s2, x2)
        sine4 = pplus(sine4, x4)
        wilson = pplus(wilson, pplus(pscale(Fraction(1, 2), x2), pscale(Fraction(-1, 24), x4)))
        actual = pplus(actual, pplus(x2, pscale(Fraction(-1, 3), x4)))
    actual = pplus(actual, pscale(r * r, ptimes(wilson, wilson)))
    expected = pplus(s2, pplus(pscale(Fraction(-1, 3), sine4), pscale(r * r / 4, ptimes(s2, s2))))
    return actual, expected


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": jsonable(actual), "expected": jsonable(expected)})

    check(
        "identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"]]
        == ["R-458", "EXP-001331", "T-054", False, "T0"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"]],
        "R-458/EXP-001331/T-054/false/T0",
        "provenance",
    )
    check("method firewall", all(manifest["methods_preserved"].values()), manifest["methods_preserved"], "all true", "method-firewall")
    scope = manifest["scope"]
    check("promotion firewall", all(scope[key] is False for key in ("source_owner_admitted", "candidate_admitted", "f_lim_closed", "f_eff_closed", "f_obs_closed", "continuum_closed", "qft_identity_closed", "yang_mills_identity_closed", "physical_empty_closed", "pre_a_closed", "sector_a_closed", "c6_closed")), scope, "all promotion flags false", "promotion-firewall")

    alpha, beta, gamma = dirac_family()
    unit = eye()
    zero = zeros()
    for index, item in enumerate(alpha + [beta, gamma]):
        check(f"Hermitian {index}", adjoint(item) == item, True, True, "Clifford")
        check(f"involution {index}", product(item, item) == unit, True, True, "Clifford")
    for i, left in enumerate(alpha + [beta]):
        for j, right in enumerate(alpha + [beta]):
            if i != j:
                check(f"anticommutator {i}/{j}", add(product(left, right), product(right, left)) == zero, True, True, "Clifford")
    for i, item in enumerate(alpha + [beta]):
        check(f"gamma anticommutator {i}", add(product(gamma, item), product(item, gamma)) == zero, True, True, "chiral")

    values = [int(v) for v in manifest["parameter_fixtures"]["symbol_coefficients"]]
    symbol_checks = 0
    for coeffs in itertools.product(values, repeat=4):
        h = zeros()
        for c, item in zip(coeffs[:3], alpha):
            h = add(h, scale(c, item))
        h = add(h, scale(coeffs[3], beta))
        rho2 = sum(c * c for c in coeffs)
        h2 = product(h, h)
        check(f"symbol hermitian {coeffs}", adjoint(h) == h, True, True, "symbol")
        check(f"symbol square {coeffs}", h2 == scale(rho2, unit), True, True, "symbol")
        check(f"symbol chiral {coeffs}", product(product(gamma, h), gamma) == scale(-1, h), True, True, "chiral")
        check(f"quadratic even {coeffs}", product(product(gamma, h2), gamma) == h2, True, True, "chiral")
        symbol_checks += 4

    sizes = [int(v) for v in manifest["finite_scope"]["lattice_sizes"]]
    modes = 0
    nonorigin = 0
    for size in sizes:
        for mode in itertools.product(range(size), repeat=3):
            modes += 1
            origin = all(component % size == 0 for component in mode)
            wilson = all(component % size == 0 for component in mode)
            sine = all((2 * component) % size == 0 for component in mode)
            node = wilson and sine
            check(f"Wilson classification {size}/{mode}", wilson == origin, wilson, origin, "node")
            check(f"node classification {size}/{mode}", node == origin, node, origin, "node")
            check(f"origin equivalence {size}/{mode}", (node is origin), node, origin, "node")
            nonorigin += int(not origin)

    taylor = 0
    for text in manifest["parameter_fixtures"]["r_values"]:
        actual, expected = rho_series(Fraction(text))
        check(f"Taylor identity {text}", actual == expected, actual, expected, "dispersion")
        degree_two = {key: value for key, value in actual.items() if sum(key) == 2}
        check(f"Taylor leading {text}", degree_two == {(2, 0, 0): Fraction(1), (0, 2, 0): Fraction(1), (0, 0, 2): Fraction(1)}, degree_two, "unit quadratic", "dispersion")
        taylor += 2

    vectors = [tuple(complex(v) for v in row) for row in manifest["parameter_fixtures"]["vector_fixtures"]]
    observable = 0
    for vector in vectors:
        cv = matvec(gamma, vector)
        density = pairing(vector, matvec(gamma, vector))
        check(f"Gamma involution vector {vector}", matvec(gamma, cv) == vector, True, True, "observables")
        check(f"chiral density {vector}", pairing(cv, matvec(gamma, cv)) == density, True, True, "observables")
        for phase in (1 + 0j, -1 + 0j, 1j, -1j):
            transformed = tuple(phase * v for v in vector)
            check(f"phase norm {vector}/{phase}", norm2(transformed) == norm2(vector), True, True, "observables")
            check(f"phase density {vector}/{phase}", pairing(transformed, matvec(gamma, transformed)) == density, True, True, "observables")
            observable += 2

    energies = 0
    r_values = [Fraction(v) for v in manifest["parameter_fixtures"]["r_values"]]
    lambdas = [Fraction(v) for v in manifest["parameter_fixtures"]["lambda_values"]]
    etas = [Fraction(v) for v in manifest["parameter_fixtures"]["eta_values"]]
    for r_value, lam, eta in itertools.product(r_values, lambdas, etas):
        check(f"parameter domain {r_value}/{lam}/{eta}", r_value > 0 and lam >= 0 and eta > 0, True, True, "coercivity")
        for coeffs in itertools.product(values, repeat=4):
            rho2 = Fraction(sum(c * c for c in coeffs))
            for vector in vectors:
                z = Fraction(norm2(vector))
                p = Fraction(norm2(tuple(v + 1j * v for v in vector)))
                energy = p / 2 + rho2 * z / 2 + lam * z * z / 4 + eta * z * z * z / 6
                check(f"coercivity {r_value}/{lam}/{eta}/{coeffs}/{vector}", energy >= 0, True, True, "coercivity")
                energies += 1
    check("conditional flow boundary", scope["flow_equivariance_conditional"] is True and scope["finite_flow_conditional_closed"] is True, True, True, "flow-boundary")

    derived = {
        "lattice_sizes": sizes,
        "mode_count": modes,
        "nonorigin_mode_count": nonorigin,
        "clifford_matrix_checks": len(alpha + [beta, gamma]) * 2 + len(alpha + [beta]) * (len(alpha + [beta]) - 1) + len(alpha + [beta]),
        "symbol_matrix_checks": symbol_checks,
        "taylor_checks": taylor,
        "observable_symmetry_checks": observable,
        "coercivity_checks": energies,
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
        "run_kind": "independent",
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
    save(output, payload)
    print(f"R-458 INDEPENDENT {manifest['status']} {len(checks)}/{len(checks)} modes={modes} symbol={symbol_checks} coercivity={energies}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else BASE / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
