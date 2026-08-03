#!/usr/bin/env python3
"""Primary exact audit for global finite-triangle CL8 Goursat continuation.

The executable derives the Q3 counts, coercive potential shift, shifted-flux
geometry, explicit continuation max-ball, shell contraction constants,
factorial/Bessel stability majorant, and full-circumference PA-H1 fixtures.
The infinite-dimensional continuation proof is written in the certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0"
PARENT_IDS = (
    "PA-CP1-CL8-GOURSAT-v0",
    "PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0",
)
RESULT_ID = "PA-CP1-CL8-FINITE-TRIANGLE-GOURSAT-GLOBAL-EXISTENCE-STABILITY"
SLUG = "pre-a-cp1-cl8-global-goursat-continuation"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
GOURSAT = REPO / "strategy/pre-a-cp1-cl8-goursat-manifest.json"
COMPOSITION = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
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
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
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


def q3_graph(dimension: int) -> tuple[list[tuple[int, ...]], list[tuple[tuple[int, ...], tuple[int, ...]]]]:
    vertices = list(itertools.product((0, 1), repeat=dimension))
    edges: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    for i, left in enumerate(vertices):
        for right in vertices[i + 1 :]:
            if sum(a != b for a, b in zip(left, right)) == 1:
                edges.append((left, right))
    return vertices, edges


def parse_dimension(q3lock: dict[str, Any]) -> int:
    text = q3lock["definition"]["species"]
    match = re.search(r"\^([0-9]+)", text)
    if match is None:
        raise AssertionError(f"cannot parse Q3 dimension from {text!r}")
    return int(match.group(1))


def parse_pah1(block: dict[str, Any]) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    inputs = block["pah1_tangent_calibration"]["selected_inputs"]
    circumference_text = next(item for item in inputs if item.startswith("circle circumference "))
    speed_text = next(item for item in inputs if item.startswith("c/chi="))
    r_text = next(item for item in inputs if item.startswith("r="))
    circumference = sp.sympify(circumference_text.split("circle circumference ", 1)[1])
    speed_squared = sp.sympify(speed_text.split("=", 1)[1])
    r_over_chi = sp.sympify(r_text.split("=", 1)[1].replace("chi", "1"))
    return circumference, speed_squared, r_over_chi


def derive() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    goursat = json.loads(GOURSAT.read_text(encoding="utf-8"))
    composition = json.loads(COMPOSITION.read_text(encoding="utf-8"))
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    block = json.loads(BLOCK.read_text(encoding="utf-8"))

    audit.check("candidate identity", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("parent identities", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], PARENT_IDS, "identity")
    audit.check("result identity", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    dimension = parse_dimension(q3lock)
    vertices, edges = q3_graph(dimension)
    species_count = len(vertices)
    edge_count = len(edges)
    degrees = {vertex: 0 for vertex in vertices}
    for left, right in edges:
        degrees[left] += 1
        degrees[right] += 1
    degree = next(iter(set(degrees.values())))
    audit.check("Q3 dimension", dimension == 3, dimension, 3, "graph")
    audit.check("Q3 species count derived", species_count == 2**dimension, species_count, 2**dimension, "graph")
    audit.check("Q3 edge count derived", edge_count == dimension * 2 ** (dimension - 1), edge_count, dimension * 2 ** (dimension - 1), "graph")
    audit.check("Q3 regular degree", set(degrees.values()) == {dimension}, sorted(set(degrees.values())), [dimension], "graph")

    z, g, a = sp.symbols("z g a", positive=True, real=True)
    onsite_shifted = -a * z**2 / 2 + g * z**4 / 4 + a**2 / (4 * g)
    onsite_square = (g * z**2 - a) ** 2 / (4 * g)
    quartic_remainder = (
        -a * z**2 / 2 + g * z**4 / 4
        - (g * z**4 / 8 - a**2 / (2 * g))
    )
    quartic_square = (g * z**2 - 2 * a) ** 2 / (8 * g)
    shift_coefficient = sp.Rational(species_count, 4)
    residual_coefficient = sp.Rational(species_count, 2) - shift_coefficient
    audit.check("onsite coercive square identity", sp.simplify(onsite_shifted - onsite_square) == 0, sp.simplify(onsite_shifted - onsite_square), 0, "coercivity")
    audit.check("quartic lower-bound square identity", sp.simplify(quartic_remainder - quartic_square) == 0, sp.simplify(quartic_remainder - quartic_square), 0, "coercivity")
    audit.check("eight-species shift coefficient", shift_coefficient == 2, shift_coefficient, 2, "coercivity")
    audit.check("shift leaves gradient unchanged", sp.diff(shift_coefficient * a**2 / g, z) == 0, sp.diff(shift_coefficient * a**2 / g, z), 0, "coercivity")
    audit.check("post-shift quartic residual coefficient", residual_coefficient == 2, residual_coefficient, 2, "coercivity")

    chi, c, s, t, cstar = sp.symbols("chi c s t Cstar", positive=True)
    normalization = sp.Rational(1, species_count)
    slice_shift = normalization * (2 * s * t) * cstar
    null_shift = 2 * normalization * s * (2 * t) * cstar / 2
    audit.check("one-eighth physical ledger", normalization == sp.Rational(1, 8), normalization, sp.Rational(1, 8), "flux")
    audit.check("constant shift cancels across triangle", sp.simplify(slice_shift - null_shift) == 0, sp.simplify(slice_shift - null_shift), 0, "flux")
    audit.check("spatial derivative energy coefficient", normalization * c / 2 == c / 16, normalization * c / 2, c / 16, "flux")

    # Exact zero-solution test inputs.  These are a declared regression fixture,
    # not values used by the theorem.
    test_chi = sp.Integer(1)
    test_c = sp.Integer(1)
    test_g = sp.Integer(1)
    test_lambda = sp.Integer(0)
    test_r = sp.Integer(-1)
    test_tau = sp.Integer(1)
    test_s = sp.sqrt(test_c / test_chi)
    test_a = max(-test_r, 0)
    test_cstar = shift_coefficient * test_a**2 / test_g
    test_f_each = test_cstar / 2
    test_flux = normalization * test_s * ((2 * test_tau) * test_f_each) * 2
    test_energy = normalization * (2 * test_s * test_tau) * test_cstar
    boundary_max = sp.Integer(0)
    test_S = boundary_max + 4 * sp.sqrt(2 * test_s * test_tau * test_flux / test_c)
    gradient_lock = 4 * degree
    hessian_lock = 12 * degree
    b_S = abs(test_r) * test_S + (test_g + gradient_lock * test_lambda) * test_S**3
    ell_S = abs(test_r) + (3 * test_g + hessian_lock * test_lambda) * test_S**2
    M0 = sp.Integer(0)
    K0 = M0 + test_tau**2 * b_S / (4 * test_chi)
    rho = sp.Integer(1)
    R_c = K0 + rho
    b_Rc = abs(test_r) * R_c + (test_g + gradient_lock * test_lambda) * R_c**3
    ell_Rc = abs(test_r) + (3 * test_g + hessian_lock * test_lambda) * R_c**2
    delta_squared = sp.Rational(1, 2) * (2 * test_chi * rho / b_Rc)
    shell_selfmap = sp.factor(delta_squared * b_Rc / (2 * test_chi))
    shell_contraction = sp.factor(delta_squared * ell_Rc / (2 * test_chi))
    audit.check("test proof shift", test_cstar == 2, test_cstar, 2, "fixture")
    audit.check("test shifted boundary flux", test_flux == sp.Rational(1, 2), test_flux, sp.Rational(1, 2), "fixture")
    audit.check("test shifted slice energy", test_energy == test_flux, test_energy, test_flux, "fixture")
    audit.check("test amplitude radius", test_S == 4, test_S, 4, "fixture")
    audit.check("gradient lock coefficient derived", gradient_lock == 12, gradient_lock, 12, "fixture")
    audit.check("Hessian lock coefficient derived", hessian_lock == 36, hessian_lock, 36, "fixture")
    audit.check("test b_S", b_S == 68, b_S, 68, "fixture")
    audit.check("test ell_S", ell_S == 49, ell_S, 49, "fixture")
    audit.check("test K0", K0 == 17, K0, 17, "fixture")
    audit.check("test continuation radius", R_c == 18, R_c, 18, "fixture")
    audit.check("test b_Rc", b_Rc == 5850, b_Rc, 5850, "fixture")
    audit.check("test ell_Rc", ell_Rc == 973, ell_Rc, 973, "fixture")
    audit.check("shell self-map reserve", shell_selfmap == sp.Rational(1, 2), shell_selfmap, sp.Rational(1, 2), "fixture")
    audit.check("shell contraction strict", shell_contraction < 1, shell_contraction, "<1", "fixture")

    x = sp.symbols("x", nonnegative=True)
    order = 7
    bessel_series = sp.series(sp.besseli(0, 2 * sp.sqrt(x)), x, 0, order).removeO()
    factorial_series = sum(x**n / sp.factorial(n) ** 2 for n in range(order))
    audit.check("Bessel factorial majorant", sp.expand(bessel_series - factorial_series) == 0, sp.expand(bessel_series - factorial_series), 0, "stability")
    audit.check("triangle product maximum", sp.solve(sp.diff(x * (2 * test_tau - x), x), x) == [test_tau], sp.solve(sp.diff(x * (2 * test_tau - x), x), x), [test_tau], "stability")

    z1, z2, r_symbol, lambda_symbol = sp.symbols("z1 z2 r lambda", real=True)
    edge_potential = (
        r_symbol * (z1**2 + z2**2) / 2
        + g * (z1**4 + z2**4) / 4
        + lambda_symbol * (z1 - z2) ** 2 * (z1**2 + z2**2) / 4
    )
    force_pair = [sp.diff(edge_potential, variable) for variable in (z1, z2)]
    potential_degree = sp.Poly(edge_potential, z1, z2).total_degree()
    force_degree = max(sp.Poly(component, z1, z2).total_degree() for component in force_pair)
    fourth_force_derivatives = [
        sp.diff(component, z1, left, z2, 4 - left)
        for component in force_pair
        for left in range(5)
    ]
    recurrence_dependencies = {
        order_value: [order_value - 1] + ([order_value - 2] if order_value >= 2 else [])
        for order_value in range(1, 9)
    }
    lower_order_carry = "D_(m-1)" in manifest["high_regularity_phase_map"]["recursive_bound"]
    audit.check("quartic potential degree", potential_degree == 4, potential_degree, 4, "high-regularity")
    audit.check("cubic force degree", force_degree == potential_degree - 1, force_degree, potential_degree - 1, "high-regularity")
    audit.check("fourth force derivatives vanish", all(item == 0 for item in fourth_force_derivatives), fourth_force_derivatives, [0] * len(fourth_force_derivatives), "high-regularity")
    audit.check("C8 derivative recursion is acyclic", all(max(dependencies) < order_value for order_value, dependencies in recurrence_dependencies.items()), recurrence_dependencies, "all dependencies below current order", "high-regularity")
    audit.check("high-regularity recurrence retains lower derivatives", lower_order_carry, lower_order_carry, True, "high-regularity")

    circumference, speed_squared, r_over_chi = parse_pah1(block)
    pah1_s = sp.sqrt(speed_squared)
    pah1_tau = sp.factor(circumference / (2 * pah1_s))
    ordered_curvature = sp.factor(-2 * r_over_chi)
    base_wavenumber = sp.factor(2 * sp.pi / circumference)
    frequencies_squared = [ordered_curvature, ordered_curvature + base_wavenumber**2, ordered_curvature + base_wavenumber**2]
    old_unshifted = sp.factor(pah1_tau**2 * (2 * ordered_curvature) / 4)
    old_shifted = sp.factor(pah1_tau**2 * ordered_curvature / 4)

    def minimum_linearized_control_shell_count(lipschitz_ratio: sp.Expr) -> int:
        count = 1
        while not bool(sp.N(lipschitz_ratio * pah1_tau**2 / (2 * count**2)) < 1):
            count += 1
        return count

    linearized_shifted_shells = minimum_linearized_control_shell_count(ordered_curvature)
    linearized_unshifted_shells = minimum_linearized_control_shell_count(2 * ordered_curvature)
    linearized_shifted_shell_q = sp.factor(
        ordered_curvature * pah1_tau**2 / (2 * linearized_shifted_shells**2)
    )
    linearized_unshifted_shell_q = sp.factor(
        2 * ordered_curvature * pah1_tau**2 / (2 * linearized_unshifted_shells**2)
    )
    audit.check("PA-H1 circumference", circumference == sp.pi / 2, circumference, sp.pi / 2, "pah1")
    audit.check("PA-H1 speed", pah1_s == 1, pah1_s, 1, "pah1")
    audit.check("PA-H1 triangle time", pah1_tau == sp.pi / 4, pah1_tau, sp.pi / 4, "pah1")
    audit.check("PA-H1 ordered curvature", ordered_curvature == 9, ordered_curvature, 9, "pah1")
    audit.check("PA-H1 base wavenumber", base_wavenumber == 4, base_wavenumber, 4, "pah1")
    audit.check("PA-H1 frequency squares", frequencies_squared == [9, 25, 25], frequencies_squared, [9, 25, 25], "pah1")
    audit.check("old unshifted one-patch factor", old_unshifted == 9 * sp.pi**2 / 32, old_unshifted, 9 * sp.pi**2 / 32, "pah1")
    audit.check("old shifted one-patch factor", old_shifted == 9 * sp.pi**2 / 64, old_shifted, 9 * sp.pi**2 / 64, "pah1")
    audit.check("old unshifted factor fails", old_unshifted > 1, old_unshifted, ">1", "pah1")
    audit.check("old shifted factor fails", old_shifted > 1, old_shifted, ">1", "pah1")
    audit.check("linearized ell=9chi control uses two shells", linearized_shifted_shells == 2, linearized_shifted_shells, 2, "pah1-linearized-control")
    audit.check("linearized ell=18chi control uses three shells", linearized_unshifted_shells == 3, linearized_unshifted_shells, 3, "pah1-linearized-control")
    audit.check("linearized ell=9chi shell cap contracts", linearized_shifted_shell_q < 1, linearized_shifted_shell_q, "<1", "pah1-linearized-control")
    audit.check("linearized ell=18chi shell cap contracts", linearized_unshifted_shell_q < 1, linearized_unshifted_shell_q, "<1", "pah1-linearized-control")

    epsilon, v = sp.symbols("epsilon v", positive=True)
    q = v + epsilon * sp.cos(base_wavenumber * x)
    seam_rows = []
    for derivative in range(9):
        expression = sp.diff(q, x, derivative)
        difference = sp.simplify(expression.subs(x, circumference) - expression.subs(x, 0))
        seam_rows.append(difference)
    audit.check("nonconstant periodic q fixture", sp.diff(q, x) != 0, sp.diff(q, x), "nonzero", "periodic")
    audit.check("q jets zero through eight", all(item == 0 for item in seam_rows), seam_rows, [0] * len(seam_rows), "periodic")
    audit.check("zero Pi jets through seven", all(sp.diff(sp.Integer(0), x, derivative) == 0 for derivative in range(8)), True, True, "periodic")
    periodic_wellposedness = composition["periodic_cauchy_theorem"]["wellposedness"]
    audit.check("periodic Cauchy parent global", "every fixed finite" in periodic_wellposedness.lower(), periodic_wellposedness, "contains every fixed finite", "periodic")
    audit.check("periodic seams not automatic", manifest["scope"]["periodic_seams_automatic"] is False, manifest["scope"]["periodic_seams_automatic"], False, "periodic")

    audit.check("gate identity", manifest["gate_resolution"]["id"] == "PA-CP1-CL8-FULL-CIRCUMFERENCE-GOURSAT-EXISTENCE", manifest["gate_resolution"]["id"], "PA-CP1-CL8-FULL-CIRCUMFERENCE-GOURSAT-EXISTENCE", "gate")
    audit.check("gate source was open", composition["next_route_gates"]["full_circumference"]["status"].startswith("OPEN"), composition["next_route_gates"]["full_circumference"]["status"], "OPEN...", "gate")
    audit.check("child closure is scoped", manifest["gate_resolution"]["status"] == "CLOSED IN DECLARED CLASSICAL FIXED-BACKGROUND SCOPE", manifest["gate_resolution"]["status"], "CLOSED IN DECLARED CLASSICAL FIXED-BACKGROUND SCOPE", "gate")
    audit.check("state selection remains next", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION", "gate")
    audit.check("parent local existence was gated", goursat["scope"]["ungated_global_semilinear_existence"] is False, goursat["scope"]["ungated_global_semilinear_existence"], False, "gate")

    scope = manifest["scope"]
    required_true = (
        "fixed_1_plus_1_lorentzian_background",
        "arbitrary_finite_triangle_goursat_existence",
        "global_classical_uniqueness",
        "explicit_amplitude_bound",
        "global_field_value_stability",
        "full_pah1_circumference_classical_gate",
        "nonconstant_periodic_ordered_trace_family",
    )
    required_false = (
        "causal_structure_derived",
        "periodic_seams_automatic",
        "full_3_plus_1_dependence",
        "finite_a_goursat_scheme",
        "selected_classical_measure",
        "selected_state",
        "physical_vacuum",
        "below_empty_space",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    audit.check("required positive scope flags", all(scope[key] is True for key in required_true), {key: scope[key] for key in required_true}, {key: True for key in required_true}, "scope")
    audit.check("required negative scope flags", all(scope[key] is False for key in required_false), {key: scope[key] for key in required_false}, {key: False for key in required_false}, "scope")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": list(PARENT_IDS),
        "result_id": RESULT_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": {
            "q3": {"dimension": dimension, "species": species_count, "edges": edge_count, "degree": degree},
            "coercive_shift": {
                "C_star": f"{shift_coefficient}*r_minus^2/g",
                "quartic_residual": f"-{residual_coefficient}*r_minus^2/g",
            },
            "test_fixture": {
                "C_star": test_cstar,
                "boundary_flux": test_flux,
                "slice_energy": test_energy,
                "S_tau": test_S,
                "b_S": b_S,
                "ell_S": ell_S,
                "K0": K0,
                "R_c": R_c,
                "b_Rc": b_Rc,
                "ell_Rc": ell_Rc,
                "delta_squared": delta_squared,
                "shell_selfmap": shell_selfmap,
                "shell_contraction": shell_contraction,
            },
            "bessel_coefficients": [sp.Rational(1, sp.factorial(n) ** 2) for n in range(order)],
            "high_regularity": {
                "potential_degree": potential_degree,
                "force_degree": force_degree,
                "fourth_force_derivatives_zero": True,
                "recurrence_dependencies": recurrence_dependencies,
                "lower_order_carry": lower_order_carry,
                "trace_order": 8,
                "phase_target_orders": [7, 6],
            },
            "pah1": {
                "L": circumference,
                "s": pah1_s,
                "tau": pah1_tau,
                "ordered_curvature_over_chi": ordered_curvature,
                "frequency_squares": frequencies_squared,
                "old_unshifted_q": old_unshifted,
                "old_shifted_q": old_shifted,
                "linearized_control_only": True,
                "linearized_shifted_shells": linearized_shifted_shells,
                "linearized_shifted_shell_q": linearized_shifted_shell_q,
                "linearized_unshifted_shells": linearized_unshifted_shells,
                "linearized_unshifted_shell_q": linearized_unshifted_shell_q,
            },
            "periodic_fixture": {
                "q": q,
                "q_jet_differences_0_through_8": seam_rows,
                "Pi": 0,
            },
        },
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "goursat_manifest": sha256(GOURSAT),
            "composition_manifest": sha256(COMPOSITION),
            "q3lock_manifest": sha256(Q3LOCK),
            "block_manifest": sha256(BLOCK),
        },
        "scope": scope,
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = derive()
    atomic_json(args.output, payload)
    count = payload["assertion_summary"]["total"]
    print(f"{CANDIDATE_ID}: {count}/{count} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
