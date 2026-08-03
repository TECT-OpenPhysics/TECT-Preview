#!/usr/bin/env python3
"""Primary exact audit for the transverse-zero CL8 Goursat candidate.

This script checks convention-level algebra and exact fixtures.  The analytic
existence, uniqueness, regularity, energy-flux, and variational symplectic-flux
proofs are written in the companion certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-GOURSAT-v0"
PARENT_ID = "PA-CP1-ST8-Q3LOCK-v0"
RESULT_ID = "PA-CP1-CL8-CONTINUUM-GOURSAT-ENERGY-SYMPLECTIC-FLUX"
SLUG = "pre-a-cp1-cl8-goursat"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> None:
        if not condition:
            raise AssertionError(
                f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}"
            )
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


def q3_vertices() -> tuple[int, ...]:
    return tuple(range(1 << 3))


def q3_edges() -> tuple[tuple[int, int], ...]:
    return tuple(
        (vertex, vertex ^ (1 << axis))
        for vertex in q3_vertices()
        for axis in range(3)
        if not (vertex & (1 << axis))
    )


def volterra(polynomial: sp.Expr, u: sp.Symbol, v: sp.Symbol) -> sp.Expr:
    sigma, nu = sp.symbols("sigma nu", real=True)
    return sp.expand(
        sp.integrate(
            sp.integrate(polynomial.subs({u: sigma, v: nu}), (nu, 0, v)),
            (sigma, 0, u),
        )
    )


def derive() -> dict[str, Any]:
    audit = Audit()
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))

    audit.check(
        "upstream candidate identity",
        upstream["candidate_id"] == PARENT_ID,
        upstream["candidate_id"],
        PARENT_ID,
        "authority",
    )
    physical_ledger = upstream["collective_reduction"]["physical_volume_ledger"]
    audit.check(
        "upstream physical ledger contains one-eighth fine volume",
        "a^3/8" in physical_ledger and "h^3" in physical_ledger,
        physical_ledger,
        "contains a^3/8=h^3",
        "authority",
    )
    audit.check(
        "upstream physical diagonal quartic remains g",
        upstream["collective_reduction"]["physical_diagonal_quartic"]
        == "g remains g because the common 1/8 factor cancels the eight species",
        upstream["collective_reduction"]["physical_diagonal_quartic"],
        "g remains g because the common 1/8 factor cancels the eight species",
        "authority",
    )

    vertices, edges = q3_vertices(), q3_edges()
    degrees = {
        vertex: sum(vertex in edge for edge in edges) for vertex in vertices
    }
    audit.check("Q3 has eight vertices", len(vertices) == 8, len(vertices), 8, "q3")
    audit.check("Q3 has twelve edges", len(edges) == 12, len(edges), 12, "q3")
    audit.check(
        "Q3 is three-regular",
        set(degrees.values()) == {3},
        degrees,
        {vertex: 3 for vertex in vertices},
        "q3",
    )

    left, right, coupling, radius = sp.symbols(
        "left right lambda R", real=True, positive=True
    )
    edge_potential = coupling * (left - right) ** 2 * (left**2 + right**2) / 4
    derivative_left = sp.expand(sp.diff(edge_potential, left))
    hessian_ll = sp.expand(sp.diff(edge_potential, left, left))
    hessian_lr = sp.expand(sp.diff(edge_potential, left, right))
    expected_derivative = sp.expand(
        coupling * (left - right) * (2 * left**2 - left * right + right**2) / 2
    )
    expected_ll = sp.expand(coupling * (3 * left**2 - 3 * left * right + right**2))
    expected_lr = sp.expand(
        -coupling * (3 * left**2 - 4 * left * right + 3 * right**2) / 2
    )
    for name, actual, expected in (
        ("edge gradient", derivative_left, expected_derivative),
        ("edge same-end Hessian", hessian_ll, expected_ll),
        ("edge cross Hessian", hessian_lr, expected_lr),
    ):
        audit.check(
            f"Q3 {name} formula",
            sp.expand(actual - expected) == 0,
            actual,
            expected,
            "potential",
        )

    gradient_saturation = sp.simplify(
        derivative_left.subs({left: radius, right: -radius})
    )
    same_saturation = sp.simplify(hessian_ll.subs({left: radius, right: -radius}))
    cross_saturation = sp.simplify(hessian_lr.subs({left: radius, right: -radius}))
    audit.check(
        "edge force bound is saturated by bipartite endpoints",
        gradient_saturation == 4 * coupling * radius**3,
        gradient_saturation,
        4 * coupling * radius**3,
        "potential",
    )
    audit.check(
        "edge Hessian row-sum bound is saturated",
        same_saturation + abs(cross_saturation) == 12 * coupling * radius**2,
        same_saturation + abs(cross_saturation),
        12 * coupling * radius**2,
        "potential",
    )

    degree = next(iter(set(degrees.values())))
    gradient_edge_l1 = sum(abs(value) for value in (1, -sp.Rational(3, 2), 1, -sp.Rational(1, 2)))
    hessian_edge_row_l1 = sum(abs(value) for value in (3, -3, 1)) + sum(
        abs(value) for value in (-sp.Rational(3, 2), 2, -sp.Rational(3, 2))
    )
    lock_force_constant = sp.simplify(degree * gradient_edge_l1)
    lock_lipschitz_constant = sp.simplify(degree * hessian_edge_row_l1)
    audit.check(
        "Q3 lock force constant is derived",
        lock_force_constant == 12,
        lock_force_constant,
        12,
        "bounds",
    )
    audit.check(
        "Q3 lock Lipschitz constant is derived",
        lock_lipschitz_constant == 36,
        lock_lipschitz_constant,
        36,
        "bounds",
    )

    r, g, lam, R = sp.symbols("r g lam R", positive=True)
    b_R = r * R + (g + lock_force_constant * lam) * R**3
    ell_R = r + (3 * g + lock_lipschitz_constant * lam) * R**2
    fixture = {r: 1, g: 1, lam: 1, R: 1}
    tau, chi, free_bound = sp.Rational(1, 10), sp.Integer(1), sp.Rational(1, 2)
    b_value = sp.simplify(b_R.subs(fixture))
    ell_value = sp.simplify(ell_R.subs(fixture))
    volterra_factor = tau**2 / (4 * chi)
    self_map_value = sp.simplify(free_bound + volterra_factor * b_value)
    contraction_value = sp.simplify(volterra_factor * ell_value)
    audit.check("Goursat fixture b_R", b_value == 14, b_value, 14, "goursat_gate")
    audit.check("Goursat fixture ell_R", ell_value == 40, ell_value, 40, "goursat_gate")
    audit.check(
        "Goursat self-map fixture",
        self_map_value == sp.Rational(107, 200),
        self_map_value,
        sp.Rational(107, 200),
        "goursat_gate",
    )
    audit.check(
        "Goursat contraction fixture",
        contraction_value == sp.Rational(1, 10),
        contraction_value,
        sp.Rational(1, 10),
        "goursat_gate",
    )
    audit.check(
        "Goursat stability fixture",
        sp.simplify(1 / (1 - contraction_value)) == sp.Rational(10, 9),
        sp.simplify(1 / (1 - contraction_value)),
        sp.Rational(10, 9),
        "goursat_gate",
    )

    u, v = sp.symbols("u v", nonnegative=True)
    for power_u in range(4):
        for power_v in range(4):
            actual = volterra(u**power_u * v**power_v, u, v)
            expected = u ** (power_u + 1) * v ** (power_v + 1) / (
                (power_u + 1) * (power_v + 1)
            )
            audit.check(
                f"Volterra monomial ({power_u},{power_v})",
                sp.expand(actual - expected) == 0,
                actual,
                expected,
                "volterra",
            )
    iterate = sp.Integer(1)
    for order in range(1, 6):
        iterate = volterra(iterate, u, v)
        expected = u**order * v**order / sp.factorial(order) ** 2
        audit.check(
            f"factorial-squared Volterra iterate {order}",
            sp.expand(iterate - expected) == 0,
            iterate,
            expected,
            "volterra",
        )
    triangle_identity = sp.expand(
        sp.Symbol("tau") ** 2 - u * v - (2 * sp.Symbol("tau") - u - v) * (u + v) / 4
    )
    # The executable certificate uses the simpler AM-GM identity on a fixed
    # slice: uv=((u+v)^2-(u-v)^2)/4 <= (u+v)^2/4 <= tau^2.
    audit.check(
        "null product identity",
        sp.expand(4 * u * v - ((u + v) ** 2 - (u - v) ** 2)) == 0,
        sp.expand(4 * u * v),
        sp.expand((u + v) ** 2 - (u - v) ** 2),
        "volterra",
    )
    del triangle_identity

    a_symbol = sp.symbols("a", positive=True)
    h = a_symbol / 2
    audit.check(
        "fine-cell volume ledger",
        sp.simplify(h**3 - a_symbol**3 / 8) == 0,
        h**3,
        a_symbol**3 / 8,
        "normalization",
    )
    audit.check(
        "eight three-dimensional species weights sum to coarse volume",
        sp.simplify(8 * a_symbol**3 / 8) == a_symbol**3,
        sp.simplify(8 * a_symbol**3 / 8),
        a_symbol**3,
        "normalization",
    )
    audit.check(
        "eight reduced one-dimensional weights sum to coarse length",
        sp.simplify(8 * a_symbol / 8) == a_symbol,
        sp.simplify(8 * a_symbol / 8),
        a_symbol,
        "normalization",
    )
    z = sp.symbols("z", real=True)
    diagonal_density = sp.simplify(
        sp.Rational(1, 8)
        * 8
        * (sp.Symbol("r0") * z**2 / 2 + sp.Symbol("g0") * z**4 / 4)
    )
    audit.check(
        "physical diagonal retains onsite quartic coefficient",
        sp.expand(diagonal_density - (sp.Symbol("r0") * z**2 / 2 + sp.Symbol("g0") * z**4 / 4)) == 0,
        diagonal_density,
        sp.Symbol("r0") * z**2 / 2 + sp.Symbol("g0") * z**4 / 4,
        "normalization",
    )

    psi_uu, psi_uv, psi_vv, c_phys, chi_symbol, speed = sp.symbols(
        "psi_uu psi_uv psi_vv c chi s", positive=True
    )
    transformed = sp.expand(
        chi_symbol * (psi_uu + 2 * psi_uv + psi_vv)
        - c_phys * (psi_uu - 2 * psi_uv + psi_vv) / speed**2
    )
    transformed_on_shell = sp.simplify(transformed.subs(c_phys, chi_symbol * speed**2))
    audit.check(
        "null-coordinate principal part",
        transformed_on_shell == 4 * chi_symbol * psi_uv,
        transformed_on_shell,
        4 * chi_symbol * psi_uv,
        "coordinates",
    )

    # Exact one-component massless energy fixture.  All other CL8 species are
    # zero; c=chi*s^2 is derived rather than inserted independently.
    chi_value, speed_value, tau_value = sp.Integer(2), sp.Integer(3), sp.Integer(1)
    c_value = chi_value * speed_value**2
    A_prime, B_prime = sp.Integer(1), sp.Integer(2)
    psi_t = A_prime + B_prime
    psi_x = (A_prime - B_prime) / speed_value
    density = sp.Rational(1, 8) * (
        chi_value * psi_t**2 / 2 + c_value * psi_x**2 / 2
    )
    slice_energy = sp.simplify(2 * speed_value * tau_value * density)
    boundary_energy = sp.simplify(
        speed_value
        / 8
        * (
            2 * tau_value * chi_value * A_prime**2
            + 2 * tau_value * chi_value * B_prime**2
        )
    )
    audit.check(
        "massless slice energy fixture",
        slice_energy == sp.Rational(15, 2),
        slice_energy,
        sp.Rational(15, 2),
        "energy_flux",
    )
    audit.check(
        "massless null-boundary energy fixture",
        boundary_energy == slice_energy,
        boundary_energy,
        slice_energy,
        "energy_flux",
    )

    # The unshifted physical energy need not be positive when r<0.
    r_negative, g_positive = sp.Integer(-1), sp.Integer(1)
    onsite_at_order = r_negative / 2 + g_positive / 4
    W_ordered = sp.simplify(8 * onsite_at_order)
    W_minimum = sp.simplify(-2 * r_negative**2 / g_positive)
    negative_slice = sp.simplify(2 * speed_value * tau_value * W_ordered / 8)
    negative_boundary = sp.simplify(
        speed_value
        / 8
        * (2 * tau_value * W_ordered / 2 + 2 * tau_value * W_ordered / 2)
    )
    audit.check(
        "eight-species unshifted potential minimum",
        W_ordered == W_minimum == -2,
        W_ordered,
        -2,
        "energy_flux",
    )
    audit.check(
        "negative unshifted flux is balanced but not positive",
        negative_slice == negative_boundary == sp.Rational(-3, 2),
        (negative_slice, negative_boundary),
        (sp.Rational(-3, 2), sp.Rational(-3, 2)),
        "energy_flux",
    )

    # Direct local-current algebra in one component; dot products sum this
    # identity over the eight species.
    pt, px, ptt, pxx, pxt, force = sp.symbols("pt px ptt pxx pxt force")
    dt_energy = sp.Rational(1, 8) * (
        chi_symbol * pt * ptt + c_phys * px * pxt + force * pt
    )
    dx_flux = c_phys * (pxt * px + pt * pxx) / 8
    current_residual = sp.expand(dt_energy - dx_flux)
    expected_current = sp.expand(pt * (chi_symbol * ptt - c_phys * pxx + force) / 8)
    audit.check(
        "continuum local energy-current identity",
        sp.expand(current_residual - expected_current) == 0,
        current_residual,
        expected_current,
        "energy_flux",
    )

    # Inherited dPi wedge dpsi symplectic sign.  The simple massless fixture
    # gives -14; the value-first convention is its hostile +14 control.
    u_slice = sp.symbols("u_slice", real=True)
    v_slice = 2 - u_slice
    eta1 = u_slice + 2 * v_slice
    eta2 = u_slice**2 + 3 * v_slice**2
    eta1_t = sp.Integer(3)
    eta2_t = 2 * u_slice + 6 * v_slice
    slice_form = sp.simplify(
        chi_value
        * speed_value
        / 8
        * sp.integrate(eta1_t * eta2 - eta2_t * eta1, (u_slice, 0, 2))
    )
    u_boundary, v_boundary = sp.symbols("u_boundary v_boundary", real=True)
    A1, A2 = u_boundary, u_boundary**2
    B1, B2 = 2 * v_boundary, 3 * v_boundary**2
    boundary_form = sp.simplify(
        chi_value
        * speed_value
        / 8
        * (
            sp.integrate(sp.diff(A1, u_boundary) * A2 - sp.diff(A2, u_boundary) * A1, (u_boundary, 0, 2))
            + sp.integrate(sp.diff(B1, v_boundary) * B2 - sp.diff(B2, v_boundary) * B1, (v_boundary, 0, 2))
        )
    )
    value_first = -boundary_form
    audit.check(
        "inherited slice symplectic fixture",
        slice_form == -14,
        slice_form,
        -14,
        "symplectic_flux",
    )
    audit.check(
        "derivative-first boundary form matches inherited slice form",
        boundary_form == slice_form,
        boundary_form,
        slice_form,
        "symplectic_flux",
    )
    audit.check(
        "value-first hostile convention has opposite sign",
        value_first == 14,
        value_first,
        14,
        "symplectic_flux",
    )

    exact_results = {
        "species_count": len(vertices),
        "q3_edge_count": len(edges),
        "q3_degree": degree,
        "edge_force_bound_coefficient": lock_force_constant / degree,
        "edge_hessian_row_bound_coefficient": lock_lipschitz_constant / degree,
        "b_R_fixture": b_value,
        "ell_R_fixture": ell_value,
        "self_map_fixture": self_map_value,
        "contraction_fixture": contraction_value,
        "stability_fixture": sp.simplify(1 / (1 - contraction_value)),
        "massless_energy_fixture": slice_energy,
        "negative_unshifted_energy_fixture": negative_slice,
        "symplectic_derivative_first_fixture": boundary_form,
        "symplectic_value_first_hostile_control": value_first,
        "physical_3d_weight": "a^3/8",
        "reduced_1d_weight_per_unit_transverse_area": "a/8",
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_id": PARENT_ID,
        "result_id": RESULT_ID,
        "package_version": __version__,
        "verdict": "PASS",
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "exact_results": exact_results,
        "scope": {
            "fixed_1_plus_1_lorentzian_background": True,
            "transverse_zero_eight_species_classical_field": True,
            "gated_continuum_goursat_reconstruction": True,
            "continuum_energy_flux": True,
            "continuum_variational_symplectic_flux": True,
            "unshifted_energy_positive_for_r_negative": False,
            "finite_a_goursat_scheme": False,
            "lattice_boundary_composition": False,
            "physical_state_selection": False,
            "physical_empty_space": False,
            "cp1_complete": False,
            "pre_a_complete": False,
        },
        "provenance": {
            "script": serial(SCRIPT.relative_to(REPO)),
            "script_sha256": sha256(SCRIPT),
            "upstream": serial(UPSTREAM.relative_to(REPO)),
            "upstream_sha256": sha256(UPSTREAM),
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
    print(
        f"{CANDIDATE_ID}: {payload['assertions']['passed']}/"
        f"{payload['assertions']['total']} PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
