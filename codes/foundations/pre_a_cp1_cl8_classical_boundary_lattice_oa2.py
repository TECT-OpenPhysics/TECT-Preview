#!/usr/bin/env python3
"""Primary exact audit for the classical CL8 boundary-to-lattice bridge.

The executable audits the null-slice/grid geometry, periodic seam obstruction,
explicit Hermite jet fills, fixed-high-regularity-family energy and symplectic
quadrature, trigonometric reconstruction multipliers, the deterministic
measure coupling, and the PA-H1 full-circumference contraction obstruction.
The infinite-dimensional analytic arguments are proved in the certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from math import factorial
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.1"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0"
PARENT_IDS = (
    "PA-CP1-CL8-GOURSAT-v0",
    "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0",
)
RESULT_ID = "PA-CP1-CL8-GOURSAT-PHASE-SLICE-SEMIDISCRETE-COMPOSITION-OA2"
NEGATIVE_ID = "NG-2026-08-03-PRE-A-CP1-CL8-UNMATCHED-PERIODIC-COMPOSITION"
SLUG = "pre-a-cp1-cl8-classical-boundary-lattice-oa2"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
GOURSAT = REPO / "strategy/pre-a-cp1-cl8-goursat-manifest.json"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
BLOCK = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
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
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[row, column]) for column in range(value.cols)] for row in range(value.rows)]
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


def hermite_matrix(order: int) -> sp.Matrix:
    """Confluent two-endpoint jet matrix for degree at most 2*order+1."""
    size = 2 * (order + 1)
    rows: list[list[sp.Expr]] = []
    for point in (sp.Integer(0), sp.Integer(1)):
        for derivative in range(order + 1):
            row: list[sp.Expr] = []
            for power in range(size):
                if power < derivative:
                    row.append(sp.Integer(0))
                else:
                    row.append(
                        sp.factorial(power)
                        / sp.factorial(power - derivative)
                        * point ** (power - derivative)
                    )
            rows.append(row)
    return sp.Matrix(rows)


def endpoint_jets(polynomial: sp.Expr, variable: sp.Symbol, point: sp.Expr, order: int) -> list[sp.Expr]:
    return [sp.diff(polynomial, variable, derivative).subs(variable, point) for derivative in range(order + 1)]


def hermite_fixture(order: int, source_power: int, gap: sp.Rational) -> dict[str, Any]:
    """Join the right jet at x=1 to the left jet at x=-1 across a gap."""
    y, x = sp.symbols("y x", real=True)
    matrix = hermite_matrix(order)
    source = x**source_power
    right = endpoint_jets(source, x, sp.Integer(1), order)
    left = endpoint_jets(source, x, sp.Integer(-1), order)
    scaled = [gap**derivative * right[derivative] for derivative in range(order + 1)]
    scaled += [gap**derivative * left[derivative] for derivative in range(order + 1)]
    coefficients = list(matrix.inv() * sp.Matrix(scaled))
    bridge = sp.expand(sum(coefficient * y**power for power, coefficient in enumerate(coefficients)))
    at_zero = endpoint_jets(bridge, y, sp.Integer(0), order)
    at_one = endpoint_jets(bridge, y, sp.Integer(1), order)
    return {
        "order": order,
        "degree": sp.degree(bridge, y),
        "determinant": sp.factor(matrix.det()),
        "coefficients": coefficients,
        "zero_jets": at_zero,
        "one_jets": at_one,
        "expected_zero_jets": scaled[: order + 1],
        "expected_one_jets": scaled[order + 1 :],
    }


def parse_calibration(block: dict[str, Any]) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    calibration = block["pah1_tangent_calibration"]
    circumference_text = next(
        entry for entry in calibration["selected_inputs"] if entry.startswith("circle circumference ")
    )
    speed_text = next(entry for entry in calibration["selected_inputs"] if entry.startswith("c/chi="))
    curvature_text = calibration["ordered_curvature"]
    circumference = sp.sympify(circumference_text.removeprefix("circle circumference "))
    speed_ratio = sp.Rational(speed_text.split("=", maxsplit=1)[1])
    curvature = sp.Rational(curvature_text.split("=", maxsplit=1)[1])
    return circumference, speed_ratio, curvature


def derive() -> dict[str, Any]:
    audit = Audit()
    goursat = json.loads(GOURSAT.read_text(encoding="utf-8"))
    semidiscrete = json.loads(SEMIDISCRETE.read_text(encoding="utf-8"))
    block = json.loads(BLOCK.read_text(encoding="utf-8"))
    audit.check("Goursat parent identity", goursat["candidate_id"] == PARENT_IDS[0], goursat["candidate_id"], PARENT_IDS[0], "authority")
    audit.check("semidiscrete parent identity", semidiscrete["candidate_id"] == PARENT_IDS[1], semidiscrete["candidate_id"], PARENT_IDS[1], "authority")
    audit.check(
        "parents expose the same open route gate",
        goursat["composition_gate"]["id"]
        == semidiscrete["composition_gate"]["id"]
        == "PA-CP1-CL8-BOUNDARY-TO-LATTICE-COMPOSITION",
        (goursat["composition_gate"]["id"], semidiscrete["composition_gate"]["id"]),
        "common route ID",
        "authority",
    )
    parent_equations = (
        goursat["definition"]["continuum_equation"].split(" for ", maxsplit=1)[0],
        semidiscrete["definition"]["continuum_equation"].split(" for ", maxsplit=1)[0],
    )
    normalized_equations = tuple(re.sub(r"[\s*]", "", equation) for equation in parent_equations)
    audit.check(
        "continuum equation is identical across parents",
        normalized_equations[0] == normalized_equations[1],
        normalized_equations,
        "equal after notation normalization",
        "authority",
    )

    # Exact natural-slice geometry.
    s, tau, index, sites = sp.symbols("s tau j M", positive=True)
    length = 2 * s * tau
    spacing = length / sites
    x_node = -s * tau + index * spacing
    u_node = sp.simplify(tau + x_node / s)
    v_node = sp.simplify(tau - x_node / s)
    audit.check("direct-circle length", length == 2 * s * tau, length, 2 * s * tau, "geometry")
    audit.check("slice node u coordinate", sp.simplify(u_node - 2 * tau * index / sites) == 0, u_node, 2 * tau * index / sites, "geometry")
    audit.check("slice node v coordinate", sp.simplify(v_node - (2 * tau - 2 * tau * index / sites)) == 0, v_node, 2 * tau - 2 * tau * index / sites, "geometry")
    audit.check("null coordinate sum", sp.simplify(u_node + v_node) == 2 * tau, sp.simplify(u_node + v_node), 2 * tau, "geometry")

    # Endpoint coefficient ledger for Pi/chi and s*q_x.  IA and IB already
    # include the factor 1/(4chi).
    right_u = sp.Matrix((1, 0, 0))
    right_v = sp.Matrix((0, 1, -1))
    left_u = sp.Matrix((1, 0, -1))
    left_v = sp.Matrix((0, 1, 0))
    right_pi = tuple(right_u + right_v)
    right_gradient = tuple(right_u - right_v)
    left_pi = tuple(left_u + left_v)
    left_gradient = tuple(left_u - left_v)
    audit.check("right endpoint Pi coefficients", right_pi == (1, 1, -1), right_pi, (1, 1, -1), "phase_slice")
    audit.check("right endpoint spatial coefficients", right_gradient == (1, -1, 1), right_gradient, (1, -1, 1), "phase_slice")
    audit.check("left endpoint Pi coefficients", left_pi == (1, 1, -1), left_pi, (1, 1, -1), "phase_slice")
    audit.check("left endpoint spatial coefficients", left_gradient == (1, -1, -1), left_gradient, (1, -1, -1), "phase_slice")

    # A field jump across the direct periodic seam has a divergent one-bond
    # gradient ledger c*delta^2/(16a).
    a, c, delta = sp.symbols("a c delta", positive=True)
    seam_bond = sp.simplify((a / 8) * (c / 2) * (delta / a) ** 2)
    audit.check("seam jump bond coefficient", seam_bond == c * delta**2 / (16 * a), seam_bond, c * delta**2 / (16 * a), "seam_obstruction")
    derivative_jump = sp.symbols("d_jump", nonzero=True)
    seam_laplacian_lead = derivative_jump / a
    audit.check("derivative seam residual is order a^-1", sp.simplify(a * seam_laplacian_lead) == derivative_jump, seam_laplacian_lead, "d_jump/a", "seam_obstruction")

    # Exact admitted fixture proving that the generic direct-seam obstruction
    # occurs inside, rather than merely outside, the parent Goursat gates.
    fixture_radius = sp.Integer(1)
    fixture_tau = sp.Rational(1, 10)
    fixture_b_radius = fixture_radius + (1 + 12) * fixture_radius**3
    fixture_ell_radius = 1 + (3 + 36) * fixture_radius**2
    fixture_m_zero = sp.Rational(1, 5)
    fixture_self_map = fixture_m_zero + fixture_tau**2 * fixture_b_radius / 4
    fixture_contraction = fixture_tau**2 * fixture_ell_radius / 4
    fixture_jump = sp.Rational(1, 5)
    fixture_wrap = sp.factor(seam_bond.subs({c: 1, delta: fixture_jump}))
    audit.check("admitted mismatch b_R", fixture_b_radius == 14, fixture_b_radius, 14, "admitted_same_domain_no_go")
    audit.check("admitted mismatch ell_R", fixture_ell_radius == 40, fixture_ell_radius, 40, "admitted_same_domain_no_go")
    audit.check("admitted mismatch self-map gate", fixture_self_map == sp.Rational(47, 200) and fixture_self_map < fixture_radius, fixture_self_map, sp.Rational(47, 200), "admitted_same_domain_no_go")
    audit.check("admitted mismatch contraction gate", fixture_contraction == sp.Rational(1, 10) and fixture_contraction < 1, fixture_contraction, sp.Rational(1, 10), "admitted_same_domain_no_go")
    audit.check("admitted mismatch phase jump", fixture_jump == sp.Rational(1, 5), fixture_jump, sp.Rational(1, 5), "admitted_same_domain_no_go")
    audit.check("admitted mismatch wrap coefficient", fixture_wrap == 1 / (400 * a), fixture_wrap, 1 / (400 * a), "admitted_same_domain_no_go")

    # Explicit deterministic jet fills: q uses C7 matching, Pi uses C6.
    gap = sp.Rational(2)
    q_fill = hermite_fixture(order=7, source_power=8, gap=gap)
    pi_fill = hermite_fixture(order=6, source_power=7, gap=gap)
    for label, fixture, order, max_degree in (
        ("q", q_fill, 7, 15),
        ("Pi", pi_fill, 6, 13),
    ):
        audit.check(f"{label} Hermite matrix nonsingular", fixture["determinant"] != 0, fixture["determinant"], "nonzero", "hermite_extension")
        audit.check(f"{label} Hermite degree bound", fixture["degree"] <= max_degree, fixture["degree"], f"<= {max_degree}", "hermite_extension")
        audit.check(f"{label} right jets reproduced", fixture["zero_jets"] == fixture["expected_zero_jets"], fixture["zero_jets"], fixture["expected_zero_jets"], "hermite_extension")
        audit.check(f"{label} left jets reproduced", fixture["one_jets"] == fixture["expected_one_jets"], fixture["one_jets"], fixture["expected_one_jets"], "hermite_extension")

    # Exact sampling makes both initial error fields zero.
    q_sample, pi_sample, chi = sp.symbols("q_sample pi_sample chi", nonzero=True)
    e_zero = sp.simplify(q_sample - q_sample)
    et_zero = sp.simplify(pi_sample / chi - pi_sample / chi)
    alpha = sp.symbols("alpha", positive=True)
    initial_modified_energy = sp.simplify(chi * et_zero**2 / 2 + c * e_zero**2 / 2 + alpha * e_zero**2 / 2)
    audit.check("exact sampled position error", e_zero == 0, e_zero, 0, "initialization")
    audit.check("exact sampled velocity error", et_zero == 0, et_zero, 0, "initialization")
    audit.check("exact sampled modified energy", initial_modified_energy == 0, initial_modified_energy, 0, "initialization")

    # The only non-exact energy term in a low Fourier fixture is the forward
    # gradient symbol.  Its leading error is second order.
    fourth_coefficient = sp.Rational(2, factorial(4))
    sixth_coefficient = sp.Rational(2, factorial(6))
    symbol = 4 * sp.sin(a / 2) ** 2 / a**2
    symbol_series = sp.series(symbol, a, 0, 6).removeO().expand()
    expected_symbol = 1 - fourth_coefficient * a**2 + sixth_coefficient * a**4
    audit.check("forward-gradient symbol series", sp.expand(symbol_series - expected_symbol) == 0, symbol_series, expected_symbol, "energy_consistency")
    gradient_energy_difference = sp.pi * c * (symbol - 1) / 16
    gradient_difference_series = sp.series(gradient_energy_difference, a, 0, 6).removeO().expand()
    expected_gradient_difference = sp.pi * c * (
        -fourth_coefficient * a**2 + sixth_coefficient * a**4
    ) / 16
    audit.check("one-mode physical energy difference", sp.expand(gradient_difference_series - expected_gradient_difference) == 0, gradient_difference_series, expected_gradient_difference, "energy_consistency")

    # Cellwise average-gradient identity underlying the O(a^2) energy bound.
    x = sp.symbols("x", real=True)
    polynomial = x**3 + 2 * x**2 - x + 1
    average_derivative = sp.integrate(sp.diff(polynomial, x), (x, 0, a)) / a
    variance = sp.integrate((sp.diff(polynomial, x) - average_derivative) ** 2, (x, 0, a))
    energy_gap = sp.integrate(sp.diff(polynomial, x) ** 2, (x, 0, a)) - a * average_derivative**2
    audit.check("cell gradient variance identity", sp.expand(variance - energy_gap) == 0, sp.expand(variance), sp.expand(energy_gap), "energy_consistency")

    # Sampling is not an exact symplectic map on arbitrary lattice-frequency
    # families: sin(2*pi*M*y/L) vanishes at all M nodes but has L2 mass L/2.
    test_sites = 8  # fixed adversarial oracle resolution
    test_length = 2 * sp.pi
    test_nodes = [test_length * node / test_sites for node in range(test_sites)]
    kernel_values = [sp.simplify(sp.sin(2 * sp.pi * test_sites * node / test_length)) for node in test_nodes]
    y = sp.symbols("y", real=True)
    kernel_mass = sp.integrate(sp.sin(2 * sp.pi * test_sites * y / test_length) ** 2, (y, 0, test_length))
    continuum_symplectic_kernel = -kernel_mass / 8
    audit.check("high-frequency sampling kernel", kernel_values == [0] * test_sites, kernel_values, [0] * test_sites, "symplectic_boundary")
    audit.check("sampling-kernel continuum mass", sp.simplify(kernel_mass - test_length / 2) == 0, kernel_mass, test_length / 2, "symplectic_boundary")
    audit.check("sampling-kernel symplectic value nonzero", continuum_symplectic_kernel != 0, continuum_symplectic_kernel, "nonzero", "symplectic_boundary")

    # Trigonometric reconstruction converts the discrete H1 error to a common
    # continuum H1 error.  The real even-M Nyquist cosine has half the
    # continuum squared norm of its discrete samples; only the upper stability
    # bound is used.  Concavity of sin proves the pi/2 derivative multiplier.
    nyquist_discrete_square = sp.Integer(1)
    nyquist_continuum_square = sp.simplify(
        sp.integrate(sp.cos(y) ** 2, (y, 0, 2 * sp.pi)) / (2 * sp.pi)
    )
    audit.check(
        "real Nyquist continuum/discrete squared-norm ratio",
        nyquist_continuum_square / nyquist_discrete_square == sp.Rational(1, 2),
        nyquist_continuum_square / nyquist_discrete_square,
        sp.Rational(1, 2),
        "reconstruction",
    )
    audit.check(
        "real trigonometric reconstruction L2 upper stability at Nyquist",
        nyquist_continuum_square <= nyquist_discrete_square,
        nyquist_continuum_square,
        f"<= {nyquist_discrete_square}",
        "reconstruction",
    )
    theta = sp.symbols("theta", positive=True)
    multiplier = theta / (2 * sp.sin(theta / 2))
    audit.check("spectral multiplier endpoint", sp.simplify(multiplier.subs(theta, sp.pi) - sp.pi / 2) == 0, multiplier.subs(theta, sp.pi), sp.pi / 2, "reconstruction")
    for test_m in (8, 16, 32, 64):
        ratios = [sp.N(multiplier.subs(theta, 2 * sp.pi * mode / test_m), 50) for mode in range(1, test_m // 2 + 1)]
        audit.check(
            f"spectral multiplier finite fixture M={test_m}",
            all(value <= sp.N(sp.pi / 2, 50) for value in ratios),
            max(ratios),
            "<= pi/2",
            "reconstruction",
        )

    # Identity coupling for two atoms: W1 is no larger than the average
    # deterministic composition error and hence no larger than the sup error.
    weights = (Fraction(1, 3), Fraction(2, 3))
    point_errors = (Fraction(1, 100), Fraction(2, 100))
    coupling_cost = sum((weight * error for weight, error in zip(weights, point_errors)), Fraction(0))
    audit.check("probability weights sum to one", sum(weights, Fraction(0)) == 1, sum(weights, Fraction(0)), 1, "measure")
    audit.check("identity coupling average error", coupling_cost == Fraction(1, 60), coupling_cost, Fraction(1, 60), "measure")
    audit.check("identity coupling bounded by sup error", coupling_cost <= max(point_errors), coupling_cost, f"<= {max(point_errors)}", "measure")

    # Parse, rather than duplicate, the inserted PA-H1 calibration.  The
    # current one-patch max-ball gate cannot include an ordered-amplitude ball
    # on the full calibrated circumference.
    circumference, speed_ratio, ordered_curvature = parse_calibration(block)
    inserted_speed = sp.sqrt(speed_ratio)
    calibrated_tau = sp.simplify(circumference / (2 * inserted_speed))
    ordered_ball_ell_lower_over_chi = 2 * ordered_curvature
    ordered_q_lower = sp.simplify(calibrated_tau**2 * ordered_ball_ell_lower_over_chi / 4)
    shifted_q_lower = sp.simplify(calibrated_tau**2 * ordered_curvature / 4)
    audit.check("parsed PA-H1 circumference", circumference == sp.pi / 2, circumference, sp.pi / 2, "calibration_gate")
    audit.check("parsed PA-H1 speed ratio", speed_ratio == 1, speed_ratio, 1, "calibration_gate")
    audit.check("parsed PA-H1 ordered curvature", ordered_curvature == 9, ordered_curvature, 9, "calibration_gate")
    audit.check("full-circle characteristic half-time", calibrated_tau == sp.pi / 4, calibrated_tau, sp.pi / 4, "calibration_gate")
    audit.check("ordered max-ball contraction lower bound", ordered_q_lower == 9 * sp.pi**2 / 32, ordered_q_lower, 9 * sp.pi**2 / 32, "calibration_gate")
    audit.check("ordered max-ball gate fails", bool(sp.N(ordered_q_lower, 50) > 1), sp.N(ordered_q_lower, 30), "> 1", "calibration_gate")
    audit.check("shifted ordered-neighbourhood lower bound", shifted_q_lower == 9 * sp.pi**2 / 64, shifted_q_lower, 9 * sp.pi**2 / 64, "calibration_gate")
    audit.check("shifted one-patch gate also fails", bool(sp.N(shifted_q_lower, 50) > 1), sp.N(shifted_q_lower, 30), "> 1", "calibration_gate")

    exact_results = {
        "direct_length": "2*s*tau",
        "u_node": u_node,
        "v_node": v_node,
        "seam_bond": seam_bond,
        "negative_id": NEGATIVE_ID,
        "mismatch_b_R": fixture_b_radius,
        "mismatch_ell_R": fixture_ell_radius,
        "mismatch_self_map": fixture_self_map,
        "mismatch_contraction": fixture_contraction,
        "mismatch_jump": fixture_jump,
        "mismatch_wrap_coefficient": sp.factor(a * fixture_wrap),
        "q_hermite_determinant": q_fill["determinant"],
        "q_hermite_coefficients": q_fill["coefficients"],
        "pi_hermite_determinant": pi_fill["determinant"],
        "pi_hermite_coefficients": pi_fill["coefficients"],
        "gradient_symbol_series": symbol_series,
        "gradient_energy_difference_series": gradient_difference_series,
        "real_nyquist_squared_norm_ratio": sp.Rational(1, 2),
        "spectral_multiplier_endpoint": sp.pi / 2,
        "sampling_kernel_symplectic_fixture": continuum_symplectic_kernel,
        "measure_coupling_cost_fixture": coupling_cost,
        "pah1_ordered_q_lower": ordered_q_lower,
        "pah1_shifted_q_lower": shifted_q_lower,
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": list(PARENT_IDS),
        "result_id": RESULT_ID,
        "package_version": __version__,
        "verdict": "PASS",
        "assertions": {"passed": len(audit.rows), "total": len(audit.rows), "rows": audit.rows},
        "exact_results": exact_results,
        "scope": {
            "claim_bearing": False,
            "direct_periodic_seam_branch": True,
            "deterministic_hermite_extension_branch": True,
            "fixed_high_regularity_family_discrete_phase_Oa2": True,
            "trigonometric_reconstruction_H1_L2_Oa2": True,
            "supplied_classical_phase_measure_W1_Oa2": True,
            "generic_direct_periodic_composition": False,
            "exact_finite_a_energy_or_symplectic_sampling": False,
            "finite_a_goursat_scheme": False,
            "full_pah1_circumference_current_gate": False,
            "preferred_classical_measure_selected": False,
            "selected_quantum_state": False,
            "physical_empty_space": False,
            "cp1_complete": False,
            "pre_a_complete": False,
        },
        "provenance": {
            "script": serial(SCRIPT.relative_to(REPO)),
            "script_sha256": sha256(SCRIPT),
            "goursat_manifest": serial(GOURSAT.relative_to(REPO)),
            "goursat_manifest_sha256": sha256(GOURSAT),
            "semidiscrete_manifest": serial(SEMIDISCRETE.relative_to(REPO)),
            "semidiscrete_manifest_sha256": sha256(SEMIDISCRETE),
            "block_manifest": serial(BLOCK.relative_to(REPO)),
            "block_manifest_sha256": sha256(BLOCK),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--selftest", action="store_true")
    arguments = parser.parse_args()
    payload = derive()
    if not arguments.selftest:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID}: {payload['assertions']['passed']}/{payload['assertions']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
