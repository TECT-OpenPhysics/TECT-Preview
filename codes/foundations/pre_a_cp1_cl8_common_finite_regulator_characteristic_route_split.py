#!/usr/bin/env python3
"""Primary exact audit for the CL8 common-regulator characteristic route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-CAUSAL-CAUCHY-FLOQUET-BH-STATE-TRANSPORT-AND-ROUTE-NOGOS"
SLUG = "pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
STRICT_CONE = REPO / "strategy/pre-a-cp1-fdan-strict-cone-nogo-manifest.json"
QUANTUM_STATE = REPO / "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json"
BOUNDARY_SPLIT = REPO / "strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-primary-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[r, c]) for c in range(value.cols)] for r in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
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
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


def canonical_symplectic(dimension: int) -> sp.Matrix:
    identity = sp.eye(dimension)
    zero = sp.zeros(dimension)
    return zero.row_join(identity).col_join((-identity).row_join(zero))


def periodic_distance(left: int, right: int, size: int) -> int:
    separation = abs(left - right)
    return min(separation, size - separation)


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
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    semidiscrete = json.loads(SEMIDISCRETE.read_text(encoding="utf-8"))
    strict_cone = json.loads(STRICT_CONE.read_text(encoding="utf-8"))
    quantum_state = json.loads(QUANTUM_STATE.read_text(encoding="utf-8"))
    boundary_split = json.loads(BOUNDARY_SPLIT.read_text(encoding="utf-8"))
    audit = Audit()

    expected_parents = (
        "PA-CP1-ST8-Q3LOCK-v0",
        "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0",
        "PA-CP1-FD-C1-STRICT-CONE-NOGO-v0",
        "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0",
        "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0",
    )
    loaded_parents = (
        q3lock["candidate_id"],
        semidiscrete["candidate_id"],
        strict_cone["candidate_id"],
        quantum_state["candidate_id"],
        boundary_split["candidate_id"],
    )
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("parent ids exact", tuple(manifest["parent_ids"]) == expected_parents, manifest["parent_ids"], expected_parents, "identity")
    audit.check("loaded parent ids exact", loaded_parents == expected_parents, loaded_parents, expected_parents, "parents")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("task id", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "identity")
    audit.check("Q3 interaction inherited", "twelve undirected edges of Q3" in q3lock["definition"]["species_graph"], q3lock["definition"]["species_graph"], "Q3", "parents")
    audit.check("semidiscrete Hamiltonian inherited", "H_a=(a/8)" in semidiscrete["hamiltonian_structure"]["Hamiltonian"], semidiscrete["hamiltonian_structure"]["Hamiltonian"], "a/8", "parents")
    audit.check("semidiscrete symplectic form inherited", "Omega_a=(a/8)" in semidiscrete["hamiltonian_structure"]["symplectic_form"], semidiscrete["hamiltonian_structure"]["symplectic_form"], "a/8", "parents")
    audit.check("finite strict cone boundary inherited", strict_cone["scope"]["exact_finite_C1_equilibrium_variational_nogo"] is True, strict_cone["scope"]["exact_finite_C1_equilibrium_variational_nogo"], True, "parents")
    audit.check("ground density inherited", quantum_state["scope"]["finite_quantum_unique_ground"] is True, quantum_state["scope"]["finite_quantum_unique_ground"], True, "parents")
    audit.check("Gibbs density inherited", quantum_state["scope"]["finite_quantum_thermal_Gibbs"] is True, quantum_state["scope"]["finite_quantum_thermal_Gibbs"], True, "parents")
    audit.check("common-model gate inherited", boundary_split["gate_resolution"]["next_gate"] == "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-MODEL", boundary_split["gate_resolution"]["next_gate"], "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-MODEL", "parents")

    # Canonical normalization is derived from the one-eighth grid ledger.
    L = sp.pi / 2
    sites = 8
    a = sp.factor(L / sites)
    weight = sp.factor(a / 8)
    chi = sp.Rational(2, 9)
    mu = sp.factor(chi * weight)
    p_symbol, pi_symbol = sp.symbols("p Pi", real=True)
    kinetic_p = sp.factor(p_symbol**2 / (2 * mu))
    kinetic_pi = sp.factor(weight * pi_symbol**2 / (2 * chi))
    audit.check("fixture even regulator", sites % 2 == 0 and sites >= 4, sites, "even M>=4", "normalization")
    audit.check("spacing derived", a == sp.pi / 16, a, sp.pi / 16, "normalization")
    audit.check("weight derived", weight == sp.pi / 128, weight, sp.pi / 128, "normalization")
    audit.check("canonical mass derived", mu == sp.pi / 576, mu, sp.pi / 576, "normalization")
    audit.check("canonical momentum substitution", sp.simplify(kinetic_p.subs(p_symbol, weight * pi_symbol) - kinetic_pi) == 0, kinetic_p.subs(p_symbol, weight * pi_symbol), kinetic_pi, "normalization")
    audit.check("manifest weight", manifest["finite_regulator"]["weight"] == "w=a/8", manifest["finite_regulator"]["weight"], "w=a/8", "normalization")
    audit.check("manifest canonical momentum", "p_(j,e)=w*Pi_(j,e)" in manifest["finite_regulator"]["field_variables"], manifest["finite_regulator"]["field_variables"], "p=w Pi", "normalization")
    audit.check("manifest Hilbert infinite", "infinite-dimensional" in manifest["quantum_circuit"]["Hilbert_space"], manifest["quantum_circuit"]["Hilbert_space"], "infinite-dimensional", "normalization")

    # Exact symbolic shear identities.
    delta, mu_symbol, curvature = sp.symbols("delta mu curvature", nonzero=True, real=True)
    half = delta / 2
    symplectic_two = canonical_symplectic(1)
    drift = sp.Matrix([[1, half / mu_symbol], [0, 1]])
    kick = sp.Matrix([[1, 0], [-delta * curvature, 1]])
    split = sp.simplify(drift * kick * drift)
    drift_defect = sp.simplify(drift.T * symplectic_two * drift - symplectic_two)
    kick_defect = sp.simplify(kick.T * symplectic_two * kick - symplectic_two)
    split_defect = sp.simplify(split.T * symplectic_two * split - symplectic_two)
    reverse = sp.diag(1, -1)
    split_negative = sp.simplify(split.subs(delta, -delta))
    audit.check("drift determinant", sp.factor(drift.det()) == 1, drift.det(), 1, "symplectic")
    audit.check("kick determinant", sp.factor(kick.det()) == 1, kick.det(), 1, "symplectic")
    audit.check("split determinant", sp.factor(split.det()) == 1, split.det(), 1, "symplectic")
    audit.check("drift symplectic", drift_defect == sp.zeros(2), drift_defect, sp.zeros(2), "symplectic")
    audit.check("kick symplectic", kick_defect == sp.zeros(2), kick_defect, sp.zeros(2), "symplectic")
    audit.check("split symplectic", split_defect == sp.zeros(2), split_defect, sp.zeros(2), "symplectic")
    audit.check("inverse step", sp.simplify(split_negative * split) == sp.eye(2), sp.simplify(split_negative * split), sp.eye(2), "symplectic")
    audit.check("momentum reversal", sp.simplify(reverse * split * reverse - split_negative) == sp.zeros(2), sp.simplify(reverse * split * reverse), split_negative, "symplectic")
    audit.check("nonlinear Hessian symmetry declared", "Hess U_a is symmetric" in manifest["classical_circuit"]["symplectic_result"], manifest["classical_circuit"]["symplectic_result"], "symmetric Hessian", "symplectic")
    audit.check("discrete time scope declared", "discrete-time Cauchy circuit" in manifest["classical_circuit"]["scope"], manifest["classical_circuit"]["scope"], "discrete-time Cauchy circuit", "symplectic")

    # A full scalar periodic fixture proves exact radius-one and radius-two support.
    c = sp.Rational(5, 3)
    mass_squared = sp.Integer(9)
    laplacian = sp.zeros(sites)
    for node in range(sites):
        laplacian[node, node] = 2
        laplacian[node, (node - 1) % sites] = -1
        laplacian[node, (node + 1) % sites] = -1
    spring = sp.factor(weight * c / a**2)
    hessian = sp.simplify(mu * mass_squared * sp.eye(sites) + spring * laplacian)
    identity_sites = sp.eye(sites)
    zero_sites = sp.zeros(sites)
    delta_fixture = sp.Rational(1, 10)
    drift_full = identity_sites.row_join((delta_fixture / (2 * mu)) * identity_sites).col_join(zero_sites.row_join(identity_sites))
    kick_full = identity_sites.row_join(zero_sites).col_join((-delta_fixture * hessian).row_join(identity_sites))
    split_full = sp.simplify(drift_full * kick_full * drift_full)
    symplectic_full = canonical_symplectic(sites)
    split_square = sp.simplify(split_full**2)
    radius_one_violations: list[tuple[int, int]] = []
    radius_two_violations: list[tuple[int, int]] = []
    for output_node in range(sites):
        output_rows = (output_node, output_node + sites)
        for input_node in range(sites):
            input_columns = (input_node, input_node + sites)
            block_one = split_full.extract(output_rows, input_columns)
            block_two = split_square.extract(output_rows, input_columns)
            distance = periodic_distance(output_node, input_node, sites)
            if distance > 1 and block_one != sp.zeros(2):
                radius_one_violations.append((output_node, input_node))
            if distance > 2 and block_two != sp.zeros(2):
                radius_two_violations.append((output_node, input_node))
    neighbour_block = sp.simplify(split_full.extract((0, sites), (1, sites + 1)))
    neighbour_eight = sp.kronecker_product(sp.eye(8), neighbour_block)
    audit.check("periodic Laplacian symmetric", laplacian.T == laplacian, laplacian.T - laplacian, sp.zeros(sites), "causality")
    audit.check("full fixture symplectic", sp.simplify(split_full.T * symplectic_full * split_full - symplectic_full) == sp.zeros(2 * sites), "zero defect", "zero defect", "causality")
    audit.check("one-step exact radius one", not radius_one_violations, radius_one_violations, [], "causality")
    audit.check("two-step exact radius two", not radius_two_violations, radius_two_violations, [], "causality")
    audit.check("neighbour block nonzero", neighbour_block != sp.zeros(2), neighbour_block, "nonzero", "sideways")
    audit.check("neighbour block rank one", neighbour_block.rank() == 1, neighbour_block.rank(), 1, "sideways")
    audit.check("neighbour block determinant zero", sp.factor(neighbour_block.det()) == 0, neighbour_block.det(), 0, "sideways")
    audit.check("eight-species neighbour rank", neighbour_eight.rank() == 8, neighbour_eight.rank(), 8, "sideways")
    audit.check("full neighbour dimension", neighbour_eight.cols == 16, neighbour_eight.cols, 16, "sideways")
    audit.check("sideways inverse rejected", manifest["scope"]["locally_sideways_invertible"] is False, manifest["scope"]["locally_sideways_invertible"], False, "sideways")
    audit.check("two-null reconstruction rejected", manifest["scope"]["two_null_side_characteristic_reconstruction"] is False, manifest["scope"]["two_null_side_characteristic_reconstruction"], False, "sideways")

    # Exact quadratic Floquet symbol.
    omega = sp.symbols("omega", positive=True, real=True)
    x_symbol = sp.factor(delta**2 * omega**2)
    symbol = sp.Matrix(
        [
            [1 - x_symbol / 2, (delta / mu_symbol) * (1 - x_symbol / 4)],
            [-delta * mu_symbol * omega**2, 1 - x_symbol / 2],
        ]
    )
    characteristic_variable = sp.symbols("lambda_F")
    characteristic = sp.factor(symbol.charpoly(characteristic_variable).as_expr())
    expected_characteristic = sp.expand(characteristic_variable**2 - (2 - x_symbol) * characteristic_variable + 1)
    theta = sp.symbols("theta", real=True)
    audit.check("symbol determinant", sp.factor(symbol.det()) == 1, symbol.det(), 1, "Floquet")
    audit.check("symbol trace", sp.factor(sp.trace(symbol)) == 2 - x_symbol, sp.trace(symbol), 2 - x_symbol, "Floquet")
    audit.check("symbol characteristic polynomial", sp.expand(characteristic - expected_characteristic) == 0, characteristic, expected_characteristic, "Floquet")
    audit.check("cosine relation", sp.solve(sp.Eq(2 * sp.cos(theta), sp.trace(symbol)), sp.cos(theta))[0] == 1 - x_symbol / 2, sp.solve(sp.Eq(2 * sp.cos(theta), sp.trace(symbol)), sp.cos(theta))[0], 1 - x_symbol / 2, "Floquet")
    stable_delta = sp.Rational(1, 4)
    stable_omega = sp.Integer(3)
    stable_x = sp.factor(stable_delta**2 * stable_omega**2)
    audit.check("stable fixture x derived", stable_x == sp.Rational(9, 16), stable_x, sp.Rational(9, 16), "Floquet")
    audit.check("stable fixture inside CFL", bool(0 < stable_x < 4), stable_x, "0<x<4", "Floquet")
    audit.check("ordered mass derived", sp.factor(-2 * sp.Rational(-1) / chi) == 9, sp.factor(2 / chi), 9, "Floquet")
    first_wave_number = sp.factor(2 * sp.pi / L)
    lattice_frequency_squared = sp.factor(mass_squared + 4 * c * sp.sin(first_wave_number * a / 2) ** 2 / (chi * a**2))
    audit.check("first wave number derived", first_wave_number == 4, first_wave_number, 4, "Floquet")
    audit.check("lattice frequency positive", bool(lattice_frequency_squared > 0), lattice_frequency_squared, ">0", "Floquet")
    audit.check("Floquet frequency formula declared", "asin(delta*omega_a(k)/2)" in manifest["quadratic_tangent_symbol"]["exact_results"], manifest["quadratic_tangent_symbol"]["exact_results"], "2 asin", "Floquet")
    weyl_status = manifest["quadratic_tangent_symbol"]["Weyl_status"]
    audit.check("quadratic Weyl covariance true", manifest["scope"]["quadratic_metaplectic_Weyl_covariance"] is True and "W(S_delta(k)^(-1) z)" in weyl_status, weyl_status, "inverse symplectic label", "Floquet")

    # Exact energy defect, including an actual ordered double-well fixture.
    q, mass = sp.symbols("q mass", nonzero=True, real=True)
    harmonic_energy_initial = sp.factor(mass * omega**2 * q**2 / 2)
    harmonic_p_out = sp.factor(-delta * mass * omega**2 * q)
    harmonic_q_out = sp.factor((1 - delta**2 * omega**2 / 2) * q)
    harmonic_energy_out = sp.factor(harmonic_p_out**2 / (2 * mass) + mass * omega**2 * harmonic_q_out**2 / 2)
    harmonic_ratio = sp.factor(harmonic_energy_out / harmonic_energy_initial)
    audit.check("harmonic energy ratio", sp.simplify(harmonic_ratio - (1 + delta**4 * omega**4 / 4)) == 0, harmonic_ratio, 1 + delta**4 * omega**4 / 4, "energy")
    audit.check("harmonic nonconservation", sp.factor(harmonic_energy_out - harmonic_energy_initial) != 0, sp.factor(harmonic_energy_out - harmonic_energy_initial), "nonzero", "energy")
    epsilon, ordered_weight = sp.symbols("epsilon ordered_weight", positive=True, real=True)
    ordered_variable = sp.symbols("ordered_variable", real=True)
    ordered_q = 1 + epsilon
    ordered_chi = sp.Rational(2, 9)
    ordered_mu = sp.factor(ordered_chi * ordered_weight)
    ordered_potential = lambda value: sp.factor(ordered_weight * (-value**2 / 2 + value**4 / 4))
    ordered_force = sp.diff(ordered_potential(ordered_variable), ordered_variable).subs(ordered_variable, ordered_q)
    ordered_p_out = sp.factor(-delta * ordered_force)
    ordered_q_out = sp.factor(ordered_q + delta * ordered_p_out / (2 * ordered_mu))
    ordered_defect = sp.factor(ordered_p_out**2 / (2 * ordered_mu) + ordered_potential(ordered_q_out) - ordered_potential(ordered_q))
    ordered_quadratic_coefficient = sp.factor(sp.expand(sp.series(ordered_defect, epsilon, 0, 3).removeO()).coeff(epsilon, 2))
    expected_ordered_coefficient = sp.factor(sp.Rational(81, 4) * ordered_weight * delta**4)
    audit.check("ordered equilibrium force zero", sp.simplify(ordered_force.subs(epsilon, 0)) == 0, ordered_force.subs(epsilon, 0), 0, "energy")
    ordered_curvature = sp.diff(ordered_potential(ordered_variable), ordered_variable, 2).subs(ordered_variable, ordered_q).subs(epsilon, 0)
    audit.check("ordered curvature", ordered_curvature == 2 * ordered_weight, ordered_curvature, 2 * ordered_weight, "energy")
    audit.check("ordered energy-defect coefficient", ordered_quadratic_coefficient == expected_ordered_coefficient, ordered_quadratic_coefficient, expected_ordered_coefficient, "energy")
    audit.check("ordered defect positive coefficient", expected_ordered_coefficient.is_positive is True, expected_ordered_coefficient, ">0", "energy")
    audit.check("autonomous energy scope false", manifest["scope"]["inherited_autonomous_H_conserved"] is False, manifest["scope"]["inherited_autonomous_H_conserved"], False, "energy")
    audit.check("stationarity scope false", manifest["scope"]["inherited_ground_or_Gibbs_stationary"] is False, manifest["scope"]["inherited_ground_or_Gibbs_stationary"], False, "energy")

    # Cubic-phase non-uniform-continuity witness for Weyl nonnormalization.
    coordinate = sp.symbols("coordinate", positive=True, real=True)
    phase_polynomial = sp.expand(coordinate**4 - (coordinate - 1) ** 4)
    phase_derivative = sp.diff(phase_polynomial, coordinate)
    shrinking_increment = sp.pi / phase_derivative
    phase_increment = sp.simplify(phase_polynomial.subs(coordinate, coordinate + shrinking_increment) - phase_polynomial)
    audit.check("quartic difference cubic", sp.Poly(phase_polynomial, coordinate).degree() == 3, sp.Poly(phase_polynomial, coordinate).degree(), 3, "Weyl_no_go")
    audit.check("cubic leading coefficient", sp.Poly(phase_polynomial, coordinate).LC() == 4, sp.Poly(phase_polynomial, coordinate).LC(), 4, "Weyl_no_go")
    audit.check("increment tends to zero", sp.limit(shrinking_increment, coordinate, sp.oo) == 0, sp.limit(shrinking_increment, coordinate, sp.oo), 0, "Weyl_no_go")
    audit.check("phase jump tends to pi", sp.limit(phase_increment, coordinate, sp.oo) == sp.pi, sp.limit(phase_increment, coordinate, sp.oo), sp.pi, "Weyl_no_go")
    algebra_boundary = manifest["nonlinear_Weyl_nonnormalizer"]["algebra_boundary"]
    audit.check("full nonlinear Weyl scope false", manifest["scope"]["full_nonlinear_Weyl_Cstar_invariance"] is False and "modulation-average" in algebra_boundary, algebra_boundary, "false scope with modulation-average intersection proof", "Weyl_no_go")
    audit.check("B(H) automorphism scope true", manifest["scope"]["full_interacting_BH_quantum_automorphism"] is True, manifest["scope"]["full_interacting_BH_quantum_automorphism"], True, "Weyl_no_go")

    # State transport is verified independently of stationarity in a finite trace fixture.
    unitary_fixture = sp.Matrix([[0, 1], [1, 0]])
    density_fixture = sp.diag(sp.Rational(1, 3), sp.Rational(2, 3))
    observable_fixture = sp.Matrix([[2, 1], [1, -1]])
    transported_density = unitary_fixture * density_fixture * unitary_fixture.T
    heisenberg_observable = unitary_fixture.T * observable_fixture * unitary_fixture
    audit.check("unitary fixture", unitary_fixture.T * unitary_fixture == sp.eye(2), unitary_fixture.T * unitary_fixture, sp.eye(2), "state")
    audit.check("density trace one", sp.trace(density_fixture) == 1, sp.trace(density_fixture), 1, "state")
    audit.check("transported trace one", sp.trace(transported_density) == 1, sp.trace(transported_density), 1, "state")
    audit.check("transported positivity", transported_density.is_positive_semidefinite is True, transported_density.eigenvals(), "positive", "state")
    audit.check("Heisenberg-Schrodinger identity", sp.trace(transported_density * observable_fixture) == sp.trace(density_fixture * heisenberg_observable), sp.trace(transported_density * observable_fixture), sp.trace(density_fixture * heisenberg_observable), "state")
    audit.check("state transport scope true", manifest["scope"]["exact_density_state_transport"] is True, manifest["scope"]["exact_density_state_transport"], True, "state")
    audit.check("preferred state scope false", manifest["scope"]["preferred_physical_state_selected"] is False, manifest["scope"]["preferred_physical_state_selected"], False, "state")

    # A bounded principal Floquet logarithm cannot have a trace-class Gibbs exponential.
    beta, bound, truncation_dimension = sp.symbols("beta bound truncation_dimension", positive=True)
    trace_lower_bound = truncation_dimension * sp.exp(-beta * bound)
    audit.check("principal Gibbs trace lower bound diverges", sp.limit(trace_lower_bound, truncation_dimension, sp.oo) == sp.oo, sp.limit(trace_lower_bound, truncation_dimension, sp.oo), sp.oo, "Floquet_Gibbs")
    audit.check("principal Gibbs scope false", manifest["scope"]["principal_Floquet_log_trace_class_Gibbs"] is False, manifest["scope"]["principal_Floquet_log_trace_class_Gibbs"], False, "Floquet_Gibbs")
    audit.check("physical energy reference false", manifest["scope"]["physical_energy_reference"] is False, manifest["scope"]["physical_energy_reference"], False, "Floquet_Gibbs")
    audit.check("physical vacuum false", manifest["scope"]["physical_vacuum"] is False, manifest["scope"]["physical_vacuum"], False, "Floquet_Gibbs")
    audit.check("below empty space false", manifest["scope"]["below_empty_space"] is False, manifest["scope"]["below_empty_space"], False, "Floquet_Gibbs")

    expected_negatives = [
        "NG-2026-08-04-PRE-A-CP1-CL8-NONLINEAR-FLOQUET-WEYL-NORMALIZER",
        "NG-2026-08-04-PRE-A-CP1-CL8-CAUSAL-SPLIT-ORIGINAL-H-STATE",
        "NG-2026-08-04-PRE-A-CP1-CL8-PRINCIPAL-FLOQUET-GIBBS-REFERENCE",
        "NG-2026-08-04-PRE-A-CP1-CL8-CAUSAL-SPLIT-SIDEWAYS-CHARACTERISTIC",
    ]
    audit.check("negative ids exact", manifest["negative_ids"] == expected_negatives, manifest["negative_ids"], expected_negatives, "scope")
    audit.check("parent gate split", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "scope")
    audit.check("four closed subgates", len(manifest["gate_resolution"]["closed_subgates"]) == 4, len(manifest["gate_resolution"]["closed_subgates"]), 4, "scope")
    audit.check("four refuted subgates", len(manifest["gate_resolution"]["refuted_subgates"]) == 4, len(manifest["gate_resolution"]["refuted_subgates"]), 4, "scope")
    audit.check("next sideways gate", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-SIDEWAYS-INVERTIBLE-TWO-ARM-CHARACTERISTIC-CIRCUIT", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-SIDEWAYS-INVERTIBLE-TWO-ARM-CHARACTERISTIC-CIRCUIT", "scope")

    required_true = (
        "fixed_regulator_exact_symplectic_Cauchy_circuit",
        "fixed_regulator_exact_reversibility",
        "fixed_regulator_exact_radius_one_cone",
        "full_interacting_BH_quantum_automorphism",
        "exact_density_state_transport",
        "quadratic_metaplectic_Weyl_covariance",
        "exact_Floquet_symbol_and_CFL",
    )
    for key in required_true:
        audit.check(f"scope true: {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    required_false = (
        "full_nonlinear_Weyl_Cstar_invariance",
        "inherited_autonomous_H_conserved",
        "inherited_ground_or_Gibbs_stationary",
        "principal_Floquet_log_trace_class_Gibbs",
        "two_null_side_characteristic_reconstruction",
        "locally_sideways_invertible",
        "common_characteristic_model_gate_closed",
        "preferred_physical_state_selected",
        "physical_energy_reference",
        "physical_vacuum",
        "below_empty_space",
        "regulator_compatible_state_family",
        "continuum_quantum_state",
        "Hadamard_state",
        "hbar_origin_derived",
        "Lorentzian_or_null_structure_derived",
        "C0_closed",
        "N1_closed",
        "N2_closed",
        "N3_closed",
        "N4_closed",
        "N5_closed",
        "full_3_plus_1_dependence",
        "gravity",
        "cooling",
        "cycle",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in required_false:
        audit.check(f"scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    derived = {
        "fixture": {
            "L": serial(L),
            "M": sites,
            "a": serial(a),
            "w": serial(weight),
            "chi": serial(chi),
            "mu": serial(mu),
            "c": serial(c),
            "delta": serial(delta_fixture),
        },
        "shear_split": serial(split),
        "radius_one_violations": radius_one_violations,
        "radius_two_violations": radius_two_violations,
        "neighbour_block": serial(neighbour_block),
        "neighbour_rank_one_species": neighbour_block.rank(),
        "neighbour_rank_eight_species": neighbour_eight.rank(),
        "Floquet_symbol": serial(symbol),
        "Floquet_characteristic": serial(characteristic),
        "stable_x": serial(stable_x),
        "first_wave_number": serial(first_wave_number),
        "lattice_frequency_squared": serial(lattice_frequency_squared),
        "harmonic_energy_ratio": serial(harmonic_ratio),
        "ordered_energy_defect_quadratic": serial(ordered_quadratic_coefficient),
        "quartic_difference": serial(phase_polynomial),
        "cubic_phase_increment_limit": serial(sp.limit(phase_increment, coordinate, sp.oo)),
        "principal_Gibbs_trace_limit": serial(sp.limit(trace_lower_bound, truncation_dimension, sp.oo)),
        "next_gate": manifest["gate_resolution"]["next_gate"],
    }
    cross_invariants = {
        "canonical_weight_rule": "a/8",
        "canonical_mass_rule": "chi*a/8",
        "split_determinant": 1,
        "radius_one_exact": True,
        "radius_two_exact": True,
        "neighbour_rank_one_species": 1,
        "neighbour_rank_eight_species": 8,
        "Floquet_determinant": 1,
        "Floquet_trace_rule": "2-x",
        "harmonic_energy_ratio": "1+(delta*omega)^4/4",
        "ordered_energy_defect_rule": "mu*omega^6*delta^4/8",
        "quartic_translation_phase_degree": 3,
        "principal_Gibbs_trace": "infinity",
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
        "cross_invariants": cross_invariants,
        "scope": manifest["scope"],
        "negative_ids": expected_negatives,
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "q3lock_manifest": sha256(Q3LOCK),
            "semidiscrete_manifest": sha256(SEMIDISCRETE),
            "strict_cone_manifest": sha256(STRICT_CONE),
            "quantum_state_manifest": sha256(QUANTUM_STATE),
            "boundary_split_manifest": sha256(BOUNDARY_SPLIT),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} primary: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
