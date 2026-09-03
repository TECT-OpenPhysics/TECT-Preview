#!/usr/bin/env python3
"""Non-importing exact audit of PA-CP1-FD-C1-STRICT-CONE-NOGO-v0."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-FD-C1-STRICT-CONE-NOGO-v0"
SLUG = "pre-a-cp1-fdan-strict-cone-nogo"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
ST8 = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
CP1A = REPO / "strategy/pre-a-cp1a-t3-cubic-sos-common-parent-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-independent-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def canonical(value: Any) -> str:
    return json.dumps(
        serial(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


Matrix = tuple[tuple[Fraction, ...], ...]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(
            sum(
                (left[row][middle] * right[middle][column] for middle in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def eye(size: int) -> Matrix:
    return tuple(
        tuple(Fraction(row == column) for column in range(size))
        for row in range(size)
    )


def powers(generator: Matrix) -> tuple[Matrix, ...]:
    output = [eye(len(generator))]
    for _ in range(1, len(generator)):
        output.append(matmul(output[-1], generator))
    return tuple(output)


def oscillator_generator(
    stiffness: Matrix, inertia: Fraction
) -> Matrix:
    sites = len(stiffness)
    rows = [[Fraction(0) for _ in range(2 * sites)] for _ in range(2 * sites)]
    for site in range(sites):
        rows[site][sites + site] = 1 / inertia
    for row in range(sites):
        for column in range(sites):
            rows[sites + row][column] = -stiffness[row][column]
    return tuple(tuple(row) for row in rows)


def graph_stiffness(
    sites: int,
    edges: tuple[tuple[int, int], ...],
    onsite: Fraction,
    coupling: Fraction,
) -> Matrix:
    rows = [[Fraction(0) for _ in range(sites)] for _ in range(sites)]
    for site in range(sites):
        rows[site][site] += onsite
    for left, right in edges:
        rows[left][left] += coupling
        rows[right][right] += coupling
        rows[left][right] -= coupling
        rows[right][left] -= coupling
    return tuple(tuple(row) for row in rows)


def first_scalar_channel(
    generator: Matrix, target: int, source: int
) -> tuple[int | None, Fraction]:
    for exponent, value in enumerate(powers(generator)):
        if value[target][source]:
            return exponent, value[target][source]
    return None, Fraction(0)


def cp1a_value(
    bits: tuple[int, int, int],
    radial_coefficient: Fraction,
    anisotropy_coefficient: Fraction,
) -> Fraction:
    radial = sum(bits) - 3
    pairs = ((0, 1), (0, 2), (1, 2))
    return radial_coefficient * radial * radial + anisotropy_coefficient * sum(
        (bits[left] - bits[right]) ** 2 for left, right in pairs
    )


def inverse_character(
    displacement: tuple[int, int, int],
    radial_coefficient: Fraction,
    anisotropy_coefficient: Fraction,
) -> Fraction:
    result = Fraction(0)
    for bits in product((0, 1), repeat=3):
        paired_character = 1
        for bit, shift in zip(bits, displacement):
            paired_character *= 1 if bit == 0 else (2 if shift % 3 == 0 else -1)
        result += cp1a_value(
            bits, radial_coefficient, anisotropy_coefficient
        ) * paired_character
    return result / 27


def inverse_character_square(
    displacement: tuple[int, int, int],
    radial_coefficient: Fraction,
    anisotropy_coefficient: Fraction,
) -> Fraction:
    total = Fraction(0)
    for site in product(range(3), repeat=3):
        remainder = tuple(
            (displacement[axis] - site[axis]) % 3 for axis in range(3)
        )
        total += inverse_character(
            site, radial_coefficient, anisotropy_coefficient
        ) * inverse_character(
            remainder, radial_coefficient, anisotropy_coefficient
        )
    return total


def edge_hessian(
    left: Fraction, right: Fraction, coupling: Fraction
) -> Matrix:
    diagonal_left = coupling * (3 * left**2 - 3 * left * right + right**2)
    diagonal_right = coupling * (left**2 - 3 * left * right + 3 * right**2)
    mixed = coupling * (
        -Fraction(3, 2) * left**2
        + 2 * left * right
        - Fraction(3, 2) * right**2
    )
    return ((diagonal_left, mixed), (mixed, diagonal_right))


ComplexMatrix = tuple[tuple[complex, ...], ...]


def cmatmul(left: ComplexMatrix, right: ComplexMatrix) -> ComplexMatrix:
    return tuple(
        tuple(
            sum(left[row][middle] * right[middle][column] for middle in range(len(right)))
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def commutator(left: ComplexMatrix, right: ComplexMatrix) -> ComplexMatrix:
    forward, reverse = cmatmul(left, right), cmatmul(right, left)
    return tuple(
        tuple(forward[row][column] - reverse[row][column] for column in range(len(forward)))
        for row in range(len(forward))
    )


def kron(left: ComplexMatrix, right: ComplexMatrix) -> ComplexMatrix:
    return tuple(
        tuple(
            left[row // len(right)][column // len(right[0])]
            * right[row % len(right)][column % len(right[0])]
            for column in range(len(left[0]) * len(right[0]))
        )
        for row in range(len(left) * len(right))
    )


def verify() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(
                f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}"
            )
        rows.append(
            {
                "name": name,
                "group": group,
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    upstream_payloads = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in (ST8, Q3LOCK, CP1A)
    }
    upstream = {
        name: payload["candidate_id"] for name, payload in upstream_payloads.items()
    }
    check("ST8 identity", upstream[ST8.name] == "PA-CP1-ST8-CB-v0", upstream[ST8.name], "PA-CP1-ST8-CB-v0", "identity")
    check("Q3LOCK identity", upstream[Q3LOCK.name] == "PA-CP1-ST8-Q3LOCK-v0", upstream[Q3LOCK.name], "PA-CP1-ST8-Q3LOCK-v0", "identity")
    check("CP1a identity", upstream[CP1A.name] == "PA-CP1A-T3-CUBIC-SOS-COMMON-PARENT-v0", upstream[CP1A.name], "PA-CP1A-T3-CUBIC-SOS-COMMON-PARENT-v0", "identity")
    cp1a_kernel_definition = upstream_payloads[CP1A.name]["kernel"]
    cp1a_alpha = Fraction(cp1a_kernel_definition["alpha"])
    cp1a_beta = Fraction(cp1a_kernel_definition["beta"])
    cp1a_radial_coefficient = 256 * cp1a_alpha
    cp1a_anisotropy_coefficient = 256 * cp1a_beta
    check("CP1a radial coefficient from manifest", cp1a_radial_coefficient == 1, cp1a_radial_coefficient, 1, "identity")
    check("CP1a anisotropy coefficient from manifest", cp1a_anisotropy_coefficient == Fraction(21, 2), cp1a_anisotropy_coefficient, Fraction(21, 2), "identity")

    onsite, coupling, inertia = Fraction(5, 2), Fraction(7, 3), Fraction(11, 4)
    two_stiffness = graph_stiffness(2, ((0, 1),), onsite, coupling)
    two_generator = oscillator_generator(two_stiffness, inertia)
    neighbor_q = first_scalar_channel(two_generator, 1, 0)
    neighbor_p = first_scalar_channel(two_generator, 3, 0)
    check("two-site q channel first power", neighbor_q[0] == 2, neighbor_q[0], 2, "classical")
    check("two-site q channel coefficient", neighbor_q[1] == coupling / inertia, neighbor_q[1], coupling / inertia, "classical")
    check("two-site p channel first power", neighbor_p[0] == 1, neighbor_p[0], 1, "classical")
    check("two-site p channel coefficient", neighbor_p[1] == coupling, neighbor_p[1], coupling, "classical")
    check("two-site q Taylor coefficient", neighbor_q[1] / 2 == coupling / (2 * inertia), neighbor_q[1] / 2, coupling / (2 * inertia), "classical")

    cycle_edges = ((0, 1), (1, 2), (2, 3), (3, 0))
    cycle_stiffness = graph_stiffness(4, cycle_edges, onsite, coupling)
    cycle_generator = oscillator_generator(cycle_stiffness, inertia)
    opposite_q = first_scalar_channel(cycle_generator, 2, 0)
    check("four-cycle opposite q first power", opposite_q[0] == 4, opposite_q[0], 4, "walk")
    check("four-cycle two-path numerator", opposite_q[1] == 2 * coupling**2 / inertia**2, opposite_q[1], 2 * coupling**2 / inertia**2, "walk")
    check("four-cycle leading response", opposite_q[1] / 24 == coupling**2 / (12 * inertia**2), opposite_q[1] / 24, coupling**2 / (12 * inertia**2), "walk")

    disconnected = graph_stiffness(3, (), onsite, coupling)
    disconnected_generator = oscillator_generator(disconnected, inertia)
    disconnected_channel = first_scalar_channel(disconnected_generator, 2, 0)
    check("disconnected q channel absent through D-1", disconnected_channel[0] is None, disconnected_channel[0], None, "control")
    check("Cayley-Hamilton range has dimension powers", len(powers(disconnected_generator)) == len(disconnected_generator), len(powers(disconnected_generator)), len(disconnected_generator), "control")

    q3_edges = tuple(
        (vertex, vertex ^ (1 << axis))
        for vertex in range(8)
        for axis in range(3)
        if not (vertex & (1 << axis))
    )
    q3_lambda = Fraction(13, 7)
    q3_amplitude = Fraction(3)
    q3_v_squared = q3_amplitude**2
    q3_inertia = Fraction(17, 5)
    q3_effective_coupling = q3_lambda * q3_v_squared
    q3_stiffness = graph_stiffness(
        8, q3_edges, Fraction(0), q3_effective_coupling
    )
    q3_generator = oscillator_generator(q3_stiffness, q3_inertia)
    q3_channel = first_scalar_channel(q3_generator, 1, 0)
    check("Q3 edge count", len(q3_edges) == 12, len(q3_edges), 12, "q3lock")
    check("Q3 origin edge Hessian zero", edge_hessian(Fraction(0), Fraction(0), q3_lambda) == ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(0))), edge_hessian(Fraction(0), Fraction(0), q3_lambda), "zero", "q3lock")
    check("Q3 ordered edge Hessian", edge_hessian(q3_amplitude, q3_amplitude, q3_lambda) == ((q3_effective_coupling, -q3_effective_coupling), (-q3_effective_coupling, q3_effective_coupling)), edge_hessian(q3_amplitude, q3_amplitude, q3_lambda), ((q3_effective_coupling, -q3_effective_coupling), (-q3_effective_coupling, q3_effective_coupling)), "q3lock")
    check("ordered Q3 q first power", q3_channel[0] == 2, q3_channel[0], 2, "q3lock")
    check("ordered Q3 q numerator", q3_channel[1] == q3_effective_coupling / q3_inertia, q3_channel[1], Fraction(585, 119), "q3lock")
    ordered_edge = edge_hessian(q3_amplitude, q3_amplitude, q3_lambda)
    check("ordered Q3 generator matches edge Hessian", -ordered_edge[1][0] / q3_inertia == q3_channel[1], -ordered_edge[1][0] / q3_inertia, q3_channel[1], "q3lock")
    q3_walsh_spectrum = sorted(2 * alpha.bit_count() for alpha in range(8))
    check("Q3 Walsh spectrum", q3_walsh_spectrum == [0, 2, 2, 2, 4, 4, 4, 6], q3_walsh_spectrum, [0, 2, 2, 2, 4, 4, 4, 6], "q3lock")

    cp1a_values = {
        "diagonal": inverse_character((0, 0, 0), cp1a_radial_coefficient, cp1a_anisotropy_coefficient),
        "axis": inverse_character((1, 0, 0), cp1a_radial_coefficient, cp1a_anisotropy_coefficient),
        "face": inverse_character((1, 1, 0), cp1a_radial_coefficient, cp1a_anisotropy_coefficient),
        "corner": inverse_character((1, 1, 1), cp1a_radial_coefficient, cp1a_anisotropy_coefficient),
    }
    check("CP1a diagonal kernel", cp1a_values["diagonal"] == Fraction(47, 3), cp1a_values["diagonal"], Fraction(47, 3), "cp1a")
    check("CP1a axis kernel", cp1a_values["axis"] == Fraction(28, 9), cp1a_values["axis"], Fraction(28, 9), "cp1a")
    check("CP1a face kernel", cp1a_values["face"] == Fraction(-19, 9), cp1a_values["face"], Fraction(-19, 9), "cp1a")
    check("CP1a corner kernel", cp1a_values["corner"] == 0, cp1a_values["corner"], 0, "cp1a")
    check("CP1a axis leading response", -cp1a_values["axis"] / 2 == Fraction(-14, 9), -cp1a_values["axis"] / 2, Fraction(-14, 9), "cp1a")
    check("CP1a face leading response", -cp1a_values["face"] / 2 == Fraction(19, 18), -cp1a_values["face"] / 2, Fraction(19, 18), "cp1a")
    cp1a_corner_square = inverse_character_square(
        (1, 1, 1), cp1a_radial_coefficient, cp1a_anisotropy_coefficient
    )
    check("CP1a corner kernel-square", cp1a_corner_square == Fraction(-38, 3), cp1a_corner_square, Fraction(-38, 3), "cp1a")
    check("CP1a corner fourth-order response", cp1a_corner_square / 24 == Fraction(-19, 36), cp1a_corner_square / 24, Fraction(-19, 36), "cp1a")

    pauli_x: ComplexMatrix = ((0j, 1 + 0j), (1 + 0j, 0j))
    pauli_z: ComplexMatrix = ((1 + 0j, 0j), (0j, -1 + 0j))
    unit: ComplexMatrix = ((1 + 0j, 0j), (0j, 1 + 0j))
    hamiltonian = kron(pauli_x, pauli_x)
    left = kron(pauli_z, unit)
    right = kron(unit, pauli_z)
    equal_time = commutator(left, right)
    nested = commutator(commutator(hamiltonian, left), right)
    check("quantum equal-time commutator zero", all(not value for row in equal_time for value in row), equal_time, "zero", "quantum")
    check("quantum first nested commutator nonzero", any(abs(value) > 0 for row in nested for value in row), nested, "nonzero", "quantum")

    shift = tuple(
        tuple(Fraction(row == (column + 1) % 7) for column in range(7))
        for row in range(7)
    )
    shift_powers = [eye(7)]
    for _ in range(3):
        shift_powers.append(matmul(shift_powers[-1], shift))
    supports = [
        [row for row in range(7) if value[row][0]] for value in shift_powers
    ]
    check("discrete shift exact support", supports == [[0], [1], [2], [3]], supports, [[0], [1], [2], [3]], "outside_hypothesis")

    scope = {
        "requires_positive_block_distance": True,
        "requires_finite_candidate_speed": True,
        "requires_finite_phase_dimension": True,
        "requires_autonomous_C1_flow_near_equilibrium": True,
        "strict_support_not_Lieb_Robinson": True,
        "does_not_exclude_continuum_unbounded_generators": True,
        "does_not_exclude_discrete_time": True,
        "does_not_test_purely_nonlinear_zero_linearization_channel": True,
        "physical_empty_space_comparison": False,
        "CP1_complete": False,
        "Pre_A_complete": False,
    }
    check("all theorem hypotheses declared", all(scope[key] for key in ("requires_positive_block_distance", "requires_finite_candidate_speed", "requires_finite_phase_dimension", "requires_autonomous_C1_flow_near_equilibrium")), scope, "declared", "scope")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "non-importing exact finite C1 equilibrium cone audit; not CP1 or Pre-A closure",
        "claim_context": ["C6-SPACETIME-SIGNATURE", "A2-FULL-PRODUCTION-WELLPOSED"],
        "claim_bearing": False,
        "task_id": "T-054",
        "exact_results": {
            "two_site_neighbor_q_first_power": neighbor_q[0],
            "four_cycle_opposite_q_first_power": opposite_q[0],
            "four_cycle_two_path_leading_response": str(opposite_q[1] / 24),
            "Q3_ordered_edge_first_power": q3_channel[0],
            "Q3_ordered_edge_Taylor_numerator": str(q3_channel[1]),
            "Q3_ordered_fixture": {
                "lambda": str(q3_lambda),
                "v_squared": str(q3_v_squared),
                "chi": str(q3_inertia),
                "lambda_v_squared_over_chi": str(
                    q3_effective_coupling / q3_inertia
                ),
            },
            "CP1a_collocation_kernel": cp1a_values,
            "CP1a_corner_kernel_square": str(cp1a_corner_square),
            "CP1a_corner_fourth_order_response": str(cp1a_corner_square / 24),
            "CP1a_upstream_coefficients": {
                "alpha": str(cp1a_alpha),
                "beta": str(cp1a_beta),
                "radial": str(cp1a_radial_coefficient),
                "anisotropy": str(cp1a_anisotropy_coefficient),
            },
            "bounded_quantum_nested_commutator_nonzero": True,
            "discrete_shift_exact_support": supports,
        },
        "scope": scope,
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "sources": [
            {"path": str(path.relative_to(REPO)).replace("\\", "/"), "sha256": sha256(path)}
            for path in (SCRIPT, ST8, Q3LOCK, CP1A)
        ],
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = verify()
    if arguments.self_test and DEFAULT_OUTPUT.is_file():
        stored = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        if canonical(stored) != canonical(payload):
            raise AssertionError("stored independent artifact is stale; regenerate without --self-test")
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    count = payload["assertions"]["passed"]
    print(f"PASS {count}/{count} | {CANDIDATE_ID} | independent finite-cone audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
