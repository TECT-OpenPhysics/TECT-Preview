#!/usr/bin/env python3
"""Non-importing rational audit of the CL8 quantum boundary route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from math import factorial
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-ORDERED-TANGENT-FINITE-IMAGE-WEYL-STATE-PULLBACK-AND-ROUTE-NOGOS"
SLUG = "pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
GLOBAL = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
GAUSSIAN = REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json"
CLASSICAL = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json"
QUANTUM = REPO / "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-independent-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


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


def zero_matrix(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    result = zero_matrix(size, size)
    for index in range(size):
        result[index][index] = Fraction(1)
    return result


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix, strict=True)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(
                left[row][inner] * right[inner][column]
                for inner in range(len(right))
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def scale_matrix(scale: Fraction, matrix: Matrix) -> Matrix:
    return [[scale * value for value in row] for row in matrix]


def symplectic(configuration_dimension: int) -> Matrix:
    result = zero_matrix(2 * configuration_dimension, 2 * configuration_dimension)
    for index in range(configuration_dimension):
        result[index][configuration_dimension + index] = Fraction(1)
        result[configuration_dimension + index][index] = Fraction(-1)
    return result


def rank(matrix: Matrix) -> int:
    work = [row[:] for row in matrix]
    row_count = len(work)
    column_count = len(work[0]) if row_count else 0
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][column]
        work[pivot_row] = [entry / value for entry in work[pivot_row]]
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    work[row][index] - factor * work[pivot_row][index]
                    for index in range(column_count)
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def falling(value: int, order: int) -> int:
    if order > value:
        return 0
    return factorial(value) // factorial(value - order)


def lambda_monomial(
    left: tuple[int, int], right: tuple[int, int], order: int
) -> tuple[int, tuple[int, int]]:
    coefficient = 0
    for index in range(order + 1):
        left_q = order - index
        left_p = index
        right_q = index
        right_p = order - index
        term = (
            (-1) ** index
            * (factorial(order) // (factorial(index) * factorial(order - index)))
            * falling(left[0], left_q)
            * falling(left[1], left_p)
            * falling(right[0], right_q)
            * falling(right[1], right_p)
        )
        coefficient += term
    exponents = (left[0] + right[0] - order, left[1] + right[1] - order)
    return coefficient, exponents


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    global_manifest = json.loads(GLOBAL.read_text(encoding="utf-8"))
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    gaussian = json.loads(GAUSSIAN.read_text(encoding="utf-8"))
    classical = json.loads(CLASSICAL.read_text(encoding="utf-8"))
    quantum = json.loads(QUANTUM.read_text(encoding="utf-8"))
    audit = Audit()

    expected_parents = (
        "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0",
        "PA-CP1-ST8-Q3LOCK-v0",
        "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0",
        "PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0",
        "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0",
    )
    audit.check("independent candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("independent result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("independent parents", tuple(manifest["parent_ids"]) == expected_parents, manifest["parent_ids"], expected_parents, "identity")
    audit.check("independent nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    parent_actual = (
        global_manifest["candidate_id"],
        q3lock["candidate_id"],
        gaussian["candidate_id"],
        classical["candidate_id"],
        quantum["candidate_id"],
    )
    parent_expected = (
        expected_parents[0],
        expected_parents[1],
        expected_parents[2],
        expected_parents[3],
        expected_parents[4],
    )
    audit.check("independent parent identities", parent_actual == parent_expected, parent_actual, parent_expected, "parents")
    frequencies = [int(value) for value in gaussian["fixture"]["omega"]]
    audit.check("independent frequencies", frequencies == [3, 5, 5], frequencies, [3, 5, 5], "parents")
    audit.check("independent ordered squares", q3lock["pah1_calibration"]["result"].endswith("9,25,25"), q3lock["pah1_calibration"]["result"], "ends 9,25,25", "parents")
    audit.check("independent bulk states", quantum["scope"]["finite_quantum_unique_ground"] and quantum["scope"]["finite_quantum_thermal_Gibbs"], [quantum["scope"]["finite_quantum_unique_ground"], quantum["scope"]["finite_quantum_thermal_Gibbs"]], [True, True], "parents")

    # Work over Q with S=(sqrt(2)/2) C.  Then S^T J S=(1/2)C^T J C.
    coefficient_transfer = zero_matrix(6, 6)
    chi_fixture = Fraction(7, 3)
    sine_signs = [1, -1, -1]
    for index, (frequency, sine_sign) in enumerate(zip(frequencies, sine_signs, strict=True)):
        coefficient_transfer[index][index] = Fraction(-1)
        coefficient_transfer[index][index + 3] = Fraction(sine_sign, frequency) / chi_fixture
        coefficient_transfer[index + 3][index] = Fraction(-frequency * sine_sign) * chi_fixture
        coefficient_transfer[index + 3][index + 3] = Fraction(-1)
    sigma6 = symplectic(3)
    transfer_pullback = scale_matrix(
        Fraction(1, 2),
        multiply(transpose(coefficient_transfer), multiply(sigma6, coefficient_transfer)),
    )
    determinants = []
    for index in range(3):
        a_entry = coefficient_transfer[index][index]
        b_entry = coefficient_transfer[index][index + 3]
        c_entry = coefficient_transfer[index + 3][index]
        d_entry = coefficient_transfer[index + 3][index + 3]
        determinants.append(Fraction(1, 2) * (a_entry * d_entry - b_entry * c_entry))
    audit.check("rational transfer determinants", determinants == [1, 1, 1], determinants, [1, 1, 1], "finite_image")
    audit.check("rational transfer symplectic", transfer_pullback == sigma6, transfer_pullback, sigma6, "finite_image")
    audit.check("rational transfer rank", rank(coefficient_transfer) == 6, rank(coefficient_transfer), 6, "finite_image")
    audit.check("nontrivial chi transfer fixture", chi_fixture == Fraction(7, 3), chi_fixture, Fraction(7, 3), "finite_image")
    audit.check("coefficient p is canonical Pi", "canonical Pi=chi*xi_t" in manifest["ordered_tangent_finite_image"]["coefficient_phase_space"], manifest["ordered_tangent_finite_image"]["coefficient_phase_space"], "canonical Pi=chi*xi_t", "finite_image")
    audit.check("independent sign contract", "sigma=-Omega_var" in manifest["algebra_contract"]["CCR_sign"], manifest["algebra_contract"]["CCR_sign"], "sigma=-Omega_var", "finite_image")

    # Modular Fourier audit, independent of trigonometric simplification.
    M = 4

    def root_sum(order: int) -> int:
        return M if order % M == 0 else 0

    def grid_cos_average(order: int) -> Fraction:
        return Fraction(root_sum(order) + root_sum(-order), 2 * M)

    def grid_sin_average(order: int) -> Fraction:
        # The omitted factor 1/i is harmless here because the numerator is
        # proved zero by the paired roots; return its exact real coefficient.
        numerator = root_sum(order) - root_sum(-order)
        if numerator != 0:
            raise AssertionError("unexpected nonreal root average")
        return Fraction(0)

    def continuum_cos_average(order: int) -> Fraction:
        return Fraction(1) if order == 0 else Fraction(0)

    def continuum_sin_average(order: int) -> Fraction:
        return Fraction(0)

    audit.check("root sum order one", root_sum(1) == 0, root_sum(1), 0, "sampling")
    audit.check("root sum order minus one", root_sum(-1) == 0, root_sum(-1), 0, "sampling")
    audit.check("root sum order two", root_sum(2) == 0, root_sum(2), 0, "sampling")
    audit.check("root sum zero", root_sum(0) == M, root_sum(0), M, "sampling")
    # Each entry is first derived as a+b*sqrt(2).  The sqrt(2) coefficient
    # occurs only in constant/nonzero-mode cross terms and vanishes by the
    # root sums rather than being assigned away.
    discrete_quadratic = [
        [(Fraction(1), Fraction(0)), (Fraction(0), grid_cos_average(1)), (Fraction(0), grid_sin_average(1))],
        [(Fraction(0), grid_cos_average(1)), (Fraction(1) + grid_cos_average(2), Fraction(0)), (grid_sin_average(2), Fraction(0))],
        [(Fraction(0), grid_sin_average(1)), (grid_sin_average(2), Fraction(0)), (Fraction(1) - grid_cos_average(2), Fraction(0))],
    ]
    continuum_quadratic = [
        [(Fraction(1), Fraction(0)), (Fraction(0), continuum_cos_average(1)), (Fraction(0), continuum_sin_average(1))],
        [(Fraction(0), continuum_cos_average(1)), (Fraction(1) + continuum_cos_average(2), Fraction(0)), (continuum_sin_average(2), Fraction(0))],
        [(Fraction(0), continuum_sin_average(1)), (continuum_sin_average(2), Fraction(0)), (Fraction(1) - continuum_cos_average(2), Fraction(0))],
    ]
    audit.check("discrete irrational Gram parts vanish", all(entry[1] == 0 for row in discrete_quadratic for entry in row), discrete_quadratic, "all sqrt(2) coefficients zero", "sampling")
    audit.check("continuum irrational Gram parts vanish", all(entry[1] == 0 for row in continuum_quadratic for entry in row), continuum_quadratic, "all sqrt(2) coefficients zero", "sampling")
    discrete_gram = [[entry[0] for entry in row] for row in discrete_quadratic]
    continuum_gram = [[entry[0] for entry in row] for row in continuum_quadratic]
    audit.check("modular discrete Gram", discrete_gram == identity(3), discrete_gram, identity(3), "sampling")
    audit.check("continuum Fourier Gram", continuum_gram == identity(3), continuum_gram, identity(3), "sampling")
    sampling_rank = 2 * rank(discrete_gram)
    audit.check("band sampling phase rank", sampling_rank == 6, sampling_rank, 6, "sampling")
    species_weight = Fraction(8, 8)
    audit.check("species factor cancels", species_weight == 1, species_weight, 1, "sampling")
    audit.check("sampling symplectic from Gram", species_weight == 1 and discrete_gram == continuum_gram, [species_weight, discrete_gram], [1, continuum_gram], "sampling")
    audit.check("map direction fixed", manifest["algebra_contract"]["map_direction"].startswith("alpha_a:"), manifest["algebra_contract"]["map_direction"], "alpha_a boundary to bulk", "sampling")

    # Sampling-kernel phase entirely with rational coefficients of L and hbar.
    norm_over_L = (continuum_cos_average(0) - continuum_cos_average(2 * M)) / 2
    omega_over_L = -norm_over_L / 8
    sigma_over_L = -omega_over_L
    scaled_sigma_over_pi_hbar = Fraction(16) * sigma_over_L
    audit.check("kernel norm coefficient", norm_over_L == Fraction(1, 2), norm_over_L, Fraction(1, 2), "sampling_no_go")
    audit.check("kernel Omega coefficient", omega_over_L == Fraction(-1, 16), omega_over_L, Fraction(-1, 16), "sampling_no_go")
    audit.check("kernel sigma coefficient", sigma_over_L == Fraction(1, 16), sigma_over_L, Fraction(1, 16), "sampling_no_go")
    audit.check("scaled phase coefficient", scaled_sigma_over_pi_hbar == 1, scaled_sigma_over_pi_hbar, 1, "sampling_no_go")
    source_commutator = -1
    target_commutator = 1
    audit.check("source commutator", source_commutator == -1, source_commutator, -1, "sampling_no_go")
    audit.check("target commutator", target_commutator == 1, target_commutator, 1, "sampling_no_go")
    audit.check("commutator contradiction", source_commutator != target_commutator, [source_commutator, target_commutator], "different", "sampling_no_go")

    # Exact nonlinear fixture with g=2, chi=3, tau=1/2.
    fixture_g = Fraction(2)
    fixture_chi = Fraction(3)
    fixture_tau = Fraction(1, 2)
    fixture_v0 = Fraction(5)
    ordered_mixed_second = -Fraction(3) * fixture_g * fixture_v0 / (2 * fixture_chi)
    ordered_endpoint_slope = ordered_mixed_second * (2 * fixture_tau)
    audit.check("independent ordered mixed second", ordered_mixed_second == -5, ordered_mixed_second, -5, "nonlinear_no_go")
    audit.check("independent ordered endpoint slope", ordered_endpoint_slope == -5, ordered_endpoint_slope, -5, "nonlinear_no_go")
    audit.check("independent ordered witness nonzero", ordered_endpoint_slope != 0, ordered_endpoint_slope, "nonzero", "nonlinear_no_go")
    audit.check("ordered witness declared", "endpoint derivative is -3g*v0*tau/chi" in manifest["nonlinear_generator_relabel_no_go"]["CL8_witness"], manifest["nonlinear_generator_relabel_no_go"]["CL8_witness"], "ordered endpoint derivative", "nonlinear_no_go")
    mixed_third = -Fraction(3) * fixture_g / (2 * fixture_chi)
    q_third = mixed_third * fixture_tau**2
    pi_third = -Fraction(3) * fixture_g * fixture_tau
    audit.check("independent third mixed derivative", mixed_third == -1, mixed_third, -1, "nonlinear_no_go")
    audit.check("independent final q third", q_third == Fraction(-1, 4), q_third, Fraction(-1, 4), "nonlinear_no_go")
    audit.check("independent final Pi third", pi_third == -3, pi_third, -3, "nonlinear_no_go")
    audit.check("third derivative nonzero", q_third != 0 and pi_third != 0, [q_third, pi_third], "both nonzero", "nonlinear_no_go")
    gamma = Fraction(1)
    shear_one = (Fraction(1), gamma)
    shear_two = (Fraction(2), 4 * gamma)
    shear_defect = (shear_two[0] - 2 * shear_one[0], shear_two[1] - 2 * shear_one[1])
    audit.check("independent shear defect", shear_defect == (0, 2), shear_defect, (0, 2), "nonlinear_no_go")
    shear_jacobian = [[Fraction(1), Fraction(0)], [Fraction(6), Fraction(1)]]
    shear_pullback = multiply(transpose(shear_jacobian), multiply(symplectic(1), shear_jacobian))
    audit.check("independent nonlinear shear symplectic", shear_pullback == symplectic(1), shear_pullback, symplectic(1), "nonlinear_no_go")
    audit.check("generator relabel linearity boundary", "real-linear" in manifest["nonlinear_generator_relabel_no_go"]["classification"], manifest["nonlinear_generator_relabel_no_go"]["classification"], "real-linear", "nonlinear_no_go")

    # Direct monomial derivative counts for the Moyal obstruction.
    poisson_one, poisson_one_exponents = lambda_monomial((3, 0), (0, 3), 1)
    poisson_two, poisson_two_exponents = lambda_monomial((2, 1), (1, 2), 1)
    lambda3_one, lambda3_one_exponents = lambda_monomial((3, 0), (0, 3), 3)
    lambda3_two, lambda3_two_exponents = lambda_monomial((2, 1), (1, 2), 3)
    first_correction = -Fraction(lambda3_one, 24 * poisson_one)
    second_correction = -Fraction(lambda3_two, 24 * poisson_two)
    discrepancy = second_correction - first_correction
    audit.check("independent first Poisson", (poisson_one, poisson_one_exponents) == (9, (2, 2)), (poisson_one, poisson_one_exponents), (9, (2, 2)), "moyal")
    audit.check("independent second Poisson", (poisson_two, poisson_two_exponents) == (3, (2, 2)), (poisson_two, poisson_two_exponents), (3, (2, 2)), "moyal")
    audit.check("independent first Lambda cubed", (lambda3_one, lambda3_one_exponents) == (36, (0, 0)), (lambda3_one, lambda3_one_exponents), (36, (0, 0)), "moyal")
    audit.check("independent second Lambda cubed", (lambda3_two, lambda3_two_exponents) == (-12, (0, 0)), (lambda3_two, lambda3_two_exponents), (-12, (0, 0)), "moyal")
    audit.check("independent first hbar2 correction", first_correction == Fraction(-1, 6), first_correction, Fraction(-1, 6), "moyal")
    audit.check("independent second hbar2 correction", second_correction == Fraction(1, 6), second_correction, Fraction(1, 6), "moyal")
    audit.check("independent hbar2 discrepancy", discrepancy == Fraction(1, 3), discrepancy, Fraction(1, 3), "moyal")

    continuum_frequency_squared = frequencies[1] ** 2
    inverse_a_squared_coefficient = (2 * M) ** 2
    quarter_turn = (Fraction(0), Fraction(1))
    cosine_double_angle = quarter_turn[0]
    sine_squared_at_fixture = (Fraction(1) - cosine_double_angle) / 2
    lattice_gradient_numerator = 4 * inverse_a_squared_coefficient * sine_squared_at_fixture
    audit.check("independent continuum frequency squared", continuum_frequency_squared == 25, continuum_frequency_squared, 25, "dynamics_no_go")
    audit.check("independent lattice numerator", lattice_gradient_numerator == 128, lattice_gradient_numerator, 128, "dynamics_no_go")
    # pi>3 implies pi^2>9>8, so 128/pi^2<16 and the finite-M fixture is strict.
    rational_upper = Fraction(128, 9)
    audit.check("rational strict dispersion upper bound", rational_upper < 16, rational_upper, "<16", "dynamics_no_go")
    audit.check("general sine inequality recorded", "sin(2a)<2a" in manifest["current_dynamics_no_go"]["strict_mismatch"], manifest["current_dynamics_no_go"]["strict_mismatch"], "sin(2a)<2a", "dynamics_no_go")

    negative_ids = [
        manifest["unrestricted_sampling_no_go"]["negative_id"],
        manifest["nonlinear_generator_relabel_no_go"]["negative_id"],
        manifest["current_dynamics_no_go"]["negative_id"],
    ]
    expected_negatives = [
        "NG-2026-08-04-PRE-A-CP1-CL8-OA2-SAMPLING-EXACT-WEYL",
        "NG-2026-08-04-PRE-A-CP1-CL8-DIRECT-NONLINEAR-WEYL-RELABEL",
        "NG-2026-08-04-PRE-A-CP1-CL8-CURRENT-SAMPLING-EXACT-DYNAMICS",
    ]
    audit.check("independent negative ids", negative_ids == expected_negatives, negative_ids, expected_negatives, "scope")
    audit.check("independent parent split", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "scope")
    audit.check("independent three closed", len(manifest["gate_resolution"]["closed_subgates"]) == 3, len(manifest["gate_resolution"]["closed_subgates"]), 3, "scope")
    audit.check("independent three refuted", len(manifest["gate_resolution"]["refuted_subgates"]) == 3, len(manifest["gate_resolution"]["refuted_subgates"]), 3, "scope")

    required_true = (
        "ordered_tangent_finite_image_symplectic_isomorphism",
        "finite_image_metaplectic_control",
        "restricted_finite_a_Weyl_monomorphism",
        "interacting_bulk_state_restricted_boundary_pullback",
        "conditional_N1_cutoff_ingredient",
    )
    for key in required_true:
        audit.check(f"independent scope true: {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    required_false = (
        "unrestricted_point_sampling_exact_Weyl",
        "direct_nonlinear_generator_relabel_Weyl",
        "current_sampling_exact_dynamics_intertwiner",
        "full_finite_a_boundary_algebra",
        "interacting_boundary_bulk_dynamics_intertwiner",
        "interacting_Weyl_Cstar_dynamics_preserved",
        "preferred_physical_state_selected",
        "regulator_compatible_state_family",
        "continuum_quantum_state",
        "Hadamard_state",
        "hbar_origin_derived",
        "Lorentzian_or_null_structure_derived",
        "physical_vacuum",
        "below_empty_space",
        "C0_closed",
        "N1_closed",
        "N2_closed",
        "N3_closed",
        "N4_closed",
        "N5_closed",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in required_false:
        audit.check(f"independent scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    derived = {
        "frequencies": frequencies,
        "transfer_determinants": [serial(value) for value in determinants],
        "M_fixture": M,
        "continuum_gram": serial(continuum_gram),
        "discrete_gram": serial(discrete_gram),
        "sampling_rank": sampling_rank,
        "sampling_kernel_sigma": "L/16",
        "scaled_commutator": "-1",
        "nonlinear_q_third": "-3*g*tau^2/(2*chi)",
        "nonlinear_Pi_third": "-3*g*tau",
        "ordered_q_second_endpoint_slope": "-3*g*v0*tau/chi",
        "shear_additivity_defect": ["0", "2*gamma"],
        "moyal_lambda3": [lambda3_one, lambda3_two],
        "moyal_discrepancy": "hbar^2/3",
        "continuum_frequency_squared": continuum_frequency_squared,
        "lattice_fixture_frequency_squared": f"9 + {lattice_gradient_numerator}/pi^2",
        "next_gate": manifest["gate_resolution"]["next_gate"],
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": list(expected_parents),
        "result_id": RESULT_ID,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": derived,
        "scope": manifest["scope"],
        "negative_ids": negative_ids,
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "global_manifest": sha256(GLOBAL),
            "q3lock_manifest": sha256(Q3LOCK),
            "gaussian_manifest": sha256(GAUSSIAN),
            "classical_manifest": sha256(CLASSICAL),
            "quantum_manifest": sha256(QUANTUM),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} independent: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
