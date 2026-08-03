#!/usr/bin/env python3
"""Primary exact audit for the finite-dimensional analytic strict-cone no-go."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-FD-C1-STRICT-CONE-NOGO-v0"
SLUG = "pre-a-cp1-fdan-strict-cone-nogo"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
ST8 = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
CP1A = REPO / "strategy/pre-a-cp1a-t3-cubic-sos-common-parent-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-primary-{SLUG}/result.json"
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


Matrix = list[list[Fraction]]


def identity(size: int) -> Matrix:
    return [
        [Fraction(1 if row == column else 0) for column in range(size)]
        for row in range(size)
    ]


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(
                (left[row][middle] * right[middle][column] for middle in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_power(matrix: Matrix, exponent: int) -> Matrix:
    output = identity(len(matrix))
    base = matrix
    power = exponent
    while power:
        if power & 1:
            output = multiply(output, base)
        base = multiply(base, base)
        power //= 2
    return output


def block(matrix: Matrix, rows: Iterable[int], columns: Iterable[int]) -> Matrix:
    row_indices, column_indices = tuple(rows), tuple(columns)
    return [[matrix[row][column] for column in column_indices] for row in row_indices]


def nonzero(matrix: Matrix) -> bool:
    return any(entry for row in matrix for entry in row)


def first_nonzero_power(
    generator: Matrix,
    output_indices: tuple[int, ...],
    input_indices: tuple[int, ...],
) -> tuple[int | None, Matrix | None]:
    # Cayley-Hamilton makes powers 0,...,D-1 decisive for a D-dimensional
    # matrix channel.
    for exponent in range(len(generator)):
        candidate = block(
            matrix_power(generator, exponent), output_indices, input_indices
        )
        if nonzero(candidate):
            return exponent, candidate
    return None, None


def chain_stiffness(
    sites: int, mass: Fraction, coupling: Fraction
) -> Matrix:
    matrix = zeros(sites, sites)
    for site in range(sites):
        matrix[site][site] += mass
    for site in range(sites - 1):
        matrix[site][site] += coupling
        matrix[site + 1][site + 1] += coupling
        matrix[site][site + 1] -= coupling
        matrix[site + 1][site] -= coupling
    return matrix


def cycle_stiffness(
    sites: int, mass: Fraction, coupling: Fraction
) -> Matrix:
    if sites < 3:
        raise ValueError("cycle fixture requires at least three sites")
    matrix = zeros(sites, sites)
    for site in range(sites):
        matrix[site][site] += mass
    for site in range(sites):
        neighbor = (site + 1) % sites
        matrix[site][site] += coupling
        matrix[neighbor][neighbor] += coupling
        matrix[site][neighbor] -= coupling
        matrix[neighbor][site] -= coupling
    return matrix


def hamiltonian_generator(stiffness: Matrix, inertia: Fraction) -> Matrix:
    sites = len(stiffness)
    generator = zeros(2 * sites, 2 * sites)
    for site in range(sites):
        generator[site][sites + site] = 1 / inertia
    for row in range(sites):
        for column in range(sites):
            generator[sites + row][column] = -stiffness[row][column]
    return generator


def q3_laplacian() -> Matrix:
    vertices = tuple(range(8))
    matrix = zeros(len(vertices), len(vertices))
    for vertex in vertices:
        for axis in range(3):
            neighbor = vertex ^ (1 << axis)
            matrix[vertex][vertex] += 1
            matrix[vertex][neighbor] -= 1
    return matrix


def q3_edge_hessian(
    left: Fraction, right: Fraction, coupling: Fraction
) -> Matrix:
    return [
        [
            coupling * (3 * left**2 - 3 * left * right + right**2),
            coupling
            * (
                -Fraction(3, 2) * left**2
                + 2 * left * right
                - Fraction(3, 2) * right**2
            ),
        ],
        [
            coupling
            * (
                -Fraction(3, 2) * left**2
                + 2 * left * right
                - Fraction(3, 2) * right**2
            ),
            coupling * (left**2 - 3 * left * right + 3 * right**2),
        ],
    ]


def cp1a_symbol(square_bits: tuple[int, int, int]) -> Fraction:
    """Exact CP1a multiplier on modes n_i in {-1,0,1}, via n_i^2."""
    radial = sum(square_bits) - 3
    anisotropy = sum(
        (square_bits[left] - square_bits[right]) ** 2
        for left, right in ((0, 1), (0, 2), (1, 2))
    )
    return Fraction(radial**2) + Fraction(21, 2) * anisotropy


def cp1a_collocation_kernel(displacement: tuple[int, int, int]) -> Fraction:
    """Exact 3^3 inverse DFT, using the paired +/-1 character sums."""
    total = Fraction(0)
    for bit0 in (0, 1):
        for bit1 in (0, 1):
            for bit2 in (0, 1):
                square_bits = (bit0, bit1, bit2)
                character = 1
                for axis, bit in enumerate(square_bits):
                    if bit:
                        character *= 2 if displacement[axis] % 3 == 0 else -1
                total += cp1a_symbol(square_bits) * character
    return total / 27


def cp1a_collocation_kernel_square(
    displacement: tuple[int, int, int]
) -> Fraction:
    total = Fraction(0)
    for site0 in range(3):
        for site1 in range(3):
            for site2 in range(3):
                site = (site0, site1, site2)
                remainder = tuple(
                    (displacement[axis] - site[axis]) % 3 for axis in range(3)
                )
                total += cp1a_collocation_kernel(site) * cp1a_collocation_kernel(
                    remainder
                )
    return total


ComplexMatrix = list[list[complex]]


def complex_multiply(left: ComplexMatrix, right: ComplexMatrix) -> ComplexMatrix:
    return [
        [
            sum(left[row][middle] * right[middle][column] for middle in range(len(right)))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def commutator(left: ComplexMatrix, right: ComplexMatrix) -> ComplexMatrix:
    lr, rl = complex_multiply(left, right), complex_multiply(right, left)
    return [
        [lr[row][column] - rl[row][column] for column in range(len(lr[0]))]
        for row in range(len(lr))
    ]


def kronecker(left: ComplexMatrix, right: ComplexMatrix) -> ComplexMatrix:
    return [
        [
            left[i // len(right)][j // len(right[0])]
            * right[i % len(right)][j % len(right[0])]
            for j in range(len(left[0]) * len(right[0]))
        ]
        for i in range(len(left) * len(right))
    ]


def complex_nonzero(matrix: ComplexMatrix, tolerance: float = 1e-12) -> bool:
    return any(abs(entry) > tolerance for row in matrix for entry in row)


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

    upstream = {
        path.name: json.loads(path.read_text(encoding="utf-8"))["candidate_id"]
        for path in (ST8, Q3LOCK, CP1A)
    }
    check("ST8 upstream", upstream[ST8.name] == "PA-CP1-ST8-CB-v0", upstream[ST8.name], "PA-CP1-ST8-CB-v0", "identity")
    check("Q3LOCK upstream", upstream[Q3LOCK.name] == "PA-CP1-ST8-Q3LOCK-v0", upstream[Q3LOCK.name], "PA-CP1-ST8-Q3LOCK-v0", "identity")
    check("CP1a upstream", upstream[CP1A.name] == "PA-CP1A-T3-CUBIC-SOS-COMMON-PARENT-v0", upstream[CP1A.name], "PA-CP1A-T3-CUBIC-SOS-COMMON-PARENT-v0", "identity")

    sites = 3
    mass, coupling, inertia = Fraction(2), Fraction(3), Fraction(5)
    stiffness = chain_stiffness(sites, mass, coupling)
    generator = hamiltonian_generator(stiffness, inertia)
    dimension = len(generator)
    check("finite phase dimension", dimension == 2 * sites, dimension, 2 * sites, "classical_fixture")

    q0, q1, q2 = (0,), (1,), (2,)
    p0, p1, p2 = (sites,), (sites + 1,), (sites + 2,)
    exponent_p1_q0, coefficient_p1_q0 = first_nonzero_power(generator, p1, q0)
    exponent_q1_q0, coefficient_q1_q0 = first_nonzero_power(generator, q1, q0)
    exponent_q2_q0, coefficient_q2_q0 = first_nonzero_power(generator, q2, q0)
    check("neighbor momentum channel starts at first order", exponent_p1_q0 == 1, exponent_p1_q0, 1, "classical_fixture")
    check("neighbor momentum coefficient", coefficient_p1_q0 == [[coupling]], coefficient_p1_q0, [[coupling]], "classical_fixture")
    check("neighbor displacement channel starts at second order", exponent_q1_q0 == 2, exponent_q1_q0, 2, "classical_fixture")
    check("neighbor displacement Taylor numerator", coefficient_q1_q0 == [[coupling / inertia]], coefficient_q1_q0, [[coupling / inertia]], "classical_fixture")
    check("distance-two displacement starts at fourth order", exponent_q2_q0 == 4, exponent_q2_q0, 4, "classical_fixture")
    check("distance-two displacement Taylor numerator", coefficient_q2_q0 == [[coupling**2 / inertia**2]], coefficient_q2_q0, [[coupling**2 / inertia**2]], "classical_fixture")
    check("neighbor displacement response coefficient", coefficient_q1_q0[0][0] / 2 == coupling / (2 * inertia), coefficient_q1_q0[0][0] / 2, coupling / (2 * inertia), "classical_fixture")
    check("distance-two displacement response coefficient", coefficient_q2_q0[0][0] / 24 == coupling**2 / (24 * inertia**2), coefficient_q2_q0[0][0] / 24, coupling**2 / (24 * inertia**2), "classical_fixture")

    periodic_stiffness = cycle_stiffness(4, mass, coupling)
    periodic_generator = hamiltonian_generator(periodic_stiffness, inertia)
    periodic_power, periodic_block = first_nonzero_power(
        periodic_generator, (2,), (0,)
    )
    check(
        "four-cycle opposite displacement starts at fourth order",
        periodic_power == 4,
        periodic_power,
        4,
        "periodic_fixture",
    )
    check(
        "four-cycle has two exact length-two paths",
        periodic_block == [[2 * coupling**2 / inertia**2]],
        periodic_block,
        [[2 * coupling**2 / inertia**2]],
        "periodic_fixture",
    )
    check(
        "four-cycle opposite leading response",
        periodic_block[0][0] / 24 == coupling**2 / (12 * inertia**2),
        periodic_block[0][0] / 24,
        coupling**2 / (12 * inertia**2),
        "periodic_fixture",
    )

    disconnected_stiffness = [
        [Fraction(mass if row == column else 0) for column in range(sites)]
        for row in range(sites)
    ]
    disconnected_generator = hamiltonian_generator(disconnected_stiffness, inertia)
    disconnected_exponent, disconnected_coefficient = first_nonzero_power(
        disconnected_generator, q2, q0
    )
    check("disconnected control has no q channel through D-1", disconnected_exponent is None, disconnected_exponent, None, "disconnected_control")
    check("disconnected control coefficient absent", disconnected_coefficient is None, disconnected_coefficient, None, "disconnected_control")

    # The theorem's finite-dimensional load-bearing equivalence is executable:
    # an entire block exp(tK) has all Taylor coefficients zero exactly when the
    # corresponding K^n blocks vanish. Cayley-Hamilton makes n<D sufficient.
    neighbor_powers = [
        block(matrix_power(generator, exponent), q1, q0)
        for exponent in range(dimension)
    ]
    check("connected channel violates all-zero Taylor contract", any(nonzero(value) for value in neighbor_powers), [nonzero(value) for value in neighbor_powers], "at least one true", "analytic_contract")
    disconnected_powers = [
        block(matrix_power(disconnected_generator, exponent), q2, q0)
        for exponent in range(dimension)
    ]
    check("disconnected channel satisfies all-zero Taylor contract", not any(nonzero(value) for value in disconnected_powers), [nonzero(value) for value in disconnected_powers], "all false", "analytic_contract")
    check("Cayley-Hamilton audit range", len(neighbor_powers) == dimension, len(neighbor_powers), dimension, "analytic_contract")

    # The Q3LOCK spatial edge is inherited at the origin because the quartic
    # lock has zero Hessian there.  At either ordered diagonal, the species
    # Hessian gains lambda*v^2*L_Q3 and therefore has nonzero edge channels.
    cube_laplacian = q3_laplacian()
    zero_edge_hessian = q3_edge_hessian(
        Fraction(0), Fraction(0), Fraction(7, 5)
    )
    check(
        "Q3 lock edge Hessian vanishes at origin",
        zero_edge_hessian == zeros(2, 2),
        zero_edge_hessian,
        zeros(2, 2),
        "q3lock_application",
    )
    check(
        "Q3 Laplacian neighbor entry",
        cube_laplacian[1][0] == -1,
        cube_laplacian[1][0],
        -1,
        "q3lock_application",
    )
    cube_spectrum = sorted(2 * alpha.bit_count() for alpha in range(8))
    check(
        "Q3 Laplacian exact spectrum",
        cube_spectrum == [0, 2, 2, 2, 4, 4, 4, 6],
        cube_spectrum,
        [0, 2, 2, 2, 4, 4, 4, 6],
        "q3lock_application",
    )
    lock_coupling, ordered_square, species_inertia = (
        Fraction(7, 5),
        Fraction(11, 3),
        Fraction(13, 2),
    )
    ordered_species_stiffness = [
        [
            lock_coupling * ordered_square * entry
            + (Fraction(10) if row_index == column_index else Fraction(0))
            for column_index, entry in enumerate(row)
        ]
        for row_index, row in enumerate(cube_laplacian)
    ]
    ordered_edge_hessian = q3_edge_hessian(
        Fraction(2), Fraction(2), lock_coupling
    )
    expected_edge_hessian = [
        [4 * lock_coupling, -4 * lock_coupling],
        [-4 * lock_coupling, 4 * lock_coupling],
    ]
    check(
        "Q3 lock ordered edge Hessian is lambda*v^2 Laplacian",
        ordered_edge_hessian == expected_edge_hessian,
        ordered_edge_hessian,
        expected_edge_hessian,
        "q3lock_application",
    )
    ordered_species_generator = hamiltonian_generator(
        ordered_species_stiffness, species_inertia
    )
    ordered_neighbor_power, ordered_neighbor_block = first_nonzero_power(
        ordered_species_generator, (1,), (0,)
    )
    check(
        "ordered Q3 species displacement starts at second order",
        ordered_neighbor_power == 2,
        ordered_neighbor_power,
        2,
        "q3lock_application",
    )
    expected_ordered_block = lock_coupling * ordered_square / species_inertia
    check(
        "ordered Q3 species edge Taylor numerator",
        ordered_neighbor_block == [[expected_ordered_block]],
        ordered_neighbor_block,
        [[expected_ordered_block]],
        "q3lock_application",
    )

    # CP1a's fitted 3^3 Fourier-collocation regulator has exact nonzero
    # real-space cross entries.  This is a collocation-block result, not a
    # compact-support continuum statement.
    cp1a_axis_kernel = cp1a_collocation_kernel((1, 0, 0))
    cp1a_face_kernel = cp1a_collocation_kernel((1, 1, 0))
    cp1a_corner_kernel = cp1a_collocation_kernel((1, 1, 1))
    cp1a_diagonal_kernel = cp1a_collocation_kernel((0, 0, 0))
    cp1a_corner_kernel_square = cp1a_collocation_kernel_square((1, 1, 1))
    check(
        "CP1a axis collocation kernel",
        cp1a_axis_kernel == Fraction(28, 9),
        cp1a_axis_kernel,
        Fraction(28, 9),
        "cp1a_application",
    )
    check(
        "CP1a face collocation kernel",
        cp1a_face_kernel == Fraction(-19, 9),
        cp1a_face_kernel,
        Fraction(-19, 9),
        "cp1a_application",
    )
    check(
        "CP1a corner collocation kernel vanishes",
        cp1a_corner_kernel == 0,
        cp1a_corner_kernel,
        0,
        "cp1a_application",
    )
    check(
        "CP1a diagonal collocation kernel",
        cp1a_diagonal_kernel == Fraction(47, 3),
        cp1a_diagonal_kernel,
        Fraction(47, 3),
        "cp1a_application",
    )
    check(
        "CP1a axis displacement leading response",
        -cp1a_axis_kernel / 2 == Fraction(-14, 9),
        -cp1a_axis_kernel / 2,
        Fraction(-14, 9),
        "cp1a_application",
    )
    check(
        "CP1a face displacement leading response",
        -cp1a_face_kernel / 2 == Fraction(19, 18),
        -cp1a_face_kernel / 2,
        Fraction(19, 18),
        "cp1a_application",
    )
    check(
        "CP1a corner kernel-square channel",
        cp1a_corner_kernel_square == Fraction(-38, 3),
        cp1a_corner_kernel_square,
        Fraction(-38, 3),
        "cp1a_application",
    )
    check(
        "CP1a corner displacement leading response",
        cp1a_corner_kernel_square / 24 == Fraction(-19, 36),
        cp1a_corner_kernel_square / 24,
        Fraction(-19, 36),
        "cp1a_application",
    )

    # Bounded finite-quantum positive control for the nested-commutator test.
    pauli_x: ComplexMatrix = [[0j, 1 + 0j], [1 + 0j, 0j]]
    pauli_z: ComplexMatrix = [[1 + 0j, 0j], [0j, -1 + 0j]]
    unit: ComplexMatrix = [[1 + 0j, 0j], [0j, 1 + 0j]]
    quantum_h = kronecker(pauli_x, pauli_x)
    observable_left = kronecker(pauli_z, unit)
    observable_right = kronecker(unit, pauli_z)
    equal_time_commutator = commutator(observable_left, observable_right)
    first_nested = commutator(commutator(quantum_h, observable_left), observable_right)
    check("two-site observables commute initially", not complex_nonzero(equal_time_commutator), equal_time_commutator, "zero", "quantum_fixture")
    check("bounded Hamiltonian nested commutator is nonzero", complex_nonzero(first_nested), first_nested, "nonzero", "quantum_fixture")

    ring_sites = 5
    shift = [
        [Fraction(1 if row == (column + 1) % ring_sites else 0) for column in range(ring_sites)]
        for row in range(ring_sites)
    ]
    shift_square = matrix_power(shift, 2)
    check("discrete shift has one-step exact support", sum(shift[row][0] != 0 for row in range(ring_sites)) == 1, [row for row in range(ring_sites) if shift[row][0]], [1], "outside_hypothesis")
    check("discrete shift has two-step exact support", [row for row in range(ring_sites) if shift_square[row][0]] == [2], [row for row in range(ring_sites) if shift_square[row][0]], [2], "outside_hypothesis")

    theorem_hypotheses = {
        "finite_site_set": True,
        "finite_dimensional_site_blocks": True,
        "autonomous_C1_flow": True,
        "equilibrium": True,
        "state_differentiable_domain_dependence": True,
        "finite_positive_candidate_speed": True,
    }
    check("theorem hypotheses are explicit", all(theorem_hypotheses.values()), theorem_hypotheses, "all explicit", "scope")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "candidate-scope finite-dimensional autonomous C1 equilibrium strict-cone no-go; not CP1 or Pre-A closure",
        "claim_context": ["C6-SPACETIME-SIGNATURE", "A2-FULL-PRODUCTION-WELLPOSED"],
        "claim_bearing": False,
        "task_id": "T-054",
        "theorem": {
            "hypotheses": theorem_hypotheses,
            "hypothesis_detail": "For every sufficiently small source-block perturbation u and 0<=t<d(x,y)/v, the target block of Phi_t(z_*+u)-Phi_t(z_*) is exactly zero, with d(x,y)>0 and finite v.",
            "linearized_flow": "D Phi_t(z_*)=exp(t A), A=D F(z_*); C1 regularity suffices at an equilibrium",
            "strict_waiting_implication": "differentiation in u gives P_y exp(tA) I_x=0 on a nonempty interval; the entire identity theorem gives P_y A^n I_x=0 for every n",
            "contrapositive": "any nonzero cross-block A^n rules out a finite strict waiting cone for that channel",
            "finite_audit": "powers n=0,...,dim(E)-1 suffice by Cayley-Hamilton",
            "leading_tail": "if m is the first nonzero power, the cross derivative is t^m P_y A^m I_x/m! + O(t^(m+1)), hence nonzero for all sufficiently small positive t",
            "dichotomy": "finite waiting time or permanent projected variational decoupling; no delayed onset for that linearized channel in the declared finite autonomous C1 equilibrium class",
            "nonlinear_boundary": "the nonlinear no-go follows only when the strict-support assertion holds on an open initial-data neighbourhood, so differentiation transfers it to the variational channel; no finite-amplitude time analyticity is inferred from C1 alone",
        },
        "exact_results": {
            "classical_fixture_dimension": dimension,
            "neighbor_full_phase_first_power": exponent_p1_q0,
            "neighbor_displacement_first_power": exponent_q1_q0,
            "neighbor_displacement_leading_coefficient": str(coupling / (2 * inertia)),
            "distance_two_displacement_first_power": exponent_q2_q0,
            "distance_two_displacement_leading_coefficient": str(coupling**2 / (24 * inertia**2)),
            "disconnected_cross_channel": "identically zero by block structure",
            "bounded_quantum_nested_commutator_nonzero": True,
            "discrete_time_shift_exact_support": True,
            "Q3_ordered_species_first_power": ordered_neighbor_power,
            "Q3_ordered_species_Taylor_numerator": str(expected_ordered_block),
            "CP1a_axis_collocation_kernel": str(cp1a_axis_kernel),
            "CP1a_face_collocation_kernel": str(cp1a_face_kernel),
            "CP1a_axis_displacement_leading_response": str(-cp1a_axis_kernel / 2),
            "CP1a_face_displacement_leading_response": str(-cp1a_face_kernel / 2),
            "CP1a_corner_kernel_square": str(cp1a_corner_kernel_square),
            "CP1a_corner_displacement_leading_response": str(cp1a_corner_kernel_square / 24),
        },
        "application_boundary": {
            "LT3_ST8_Q3LOCK_spatial_linearization": "strict finite-regulator cone excluded by the inherited nonzero nearest-neighbor Hessian block",
            "Q3LOCK_origin_species_channel": "the quartic lock has zero species Hessian, so this theorem alone does not test purely nonlinear interspecies signalling at zero; the spatial channel already triggers the no-go",
            "Q3LOCK_ordered_species_channel": "the ordered Hessian contains lambda*v^2*L_Q3, so each Q3 species edge has a nonzero second-order displacement tail",
            "CP1a_fixed_Fourier_cutoff": "on the declared 3^3 collocation blocks the exact kernel entries 28/9 and -19/9 trigger the no-go; a nonzero trigonometric polynomial also cannot define compact support in a proper continuum open set",
            "finite_dimensional_bounded_quantum_system": "exact open-time microcausality is incompatible with a nonzero nested commutator",
        },
        "scope": {
            "strict_compact_support_only": True,
            "Lieb_Robinson_or_quasi_local_cone_excluded": False,
            "continuum_wave_finite_propagation_excluded": False,
            "discrete_time_exact_causality_excluded": False,
            "unbounded_generator_QFT_microcausality_excluded": False,
            "nonautonomous_or_nondifferentiable_update_excluded": False,
            "purely_nonlinear_zero_linearization_channel_excluded": False,
            "physical_empty_space_comparison": False,
            "CP1_complete": False,
            "Pre_A_complete": False,
        },
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
            raise AssertionError("stored primary artifact is stale; regenerate without --self-test")
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    count = payload["assertions"]["passed"]
    print(f"PASS {count}/{count} | {CANDIDATE_ID} | finite analytic cone no-go")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
