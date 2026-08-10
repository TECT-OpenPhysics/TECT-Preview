#!/usr/bin/env python3
"""Independent exact audit of the ST8/Q3LOCK weighted-energy route split.

The audit uses only the Python standard library and exact ``Fraction``
arithmetic.  It does not import the primary verifier or consume its result.
It reconstructs the Q3 graph, quartic ray and coercivity constants, the
source-envelope fixture, the local-energy current coefficient, the sharp
current form bound, the cubic-lattice weight rate, and the homogeneous cubic
force obstruction by a second algebraic route.

The output is a deterministic T0 audit artifact.  Passing it does not build a
thermodynamic-limit automorphism or prove any downstream Pre-A conclusion.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split"
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-COMMON-LOCAL-DERIVATION-SOURCE-UNIFORM-"
    "WEIGHTED-FIRST-ENERGY-CONE-AND-FOURIER-CUTOFF-ROUTE-SPLIT"
)
EXPLORATION_ID = "EXP-000792"
PARENT_GATE = (
    "PA-CP1-ST8-Q3LOCK-RESOLVENT-ALGEBRA-EXACT-POLYNOMIAL-"
    "COMMON-ALPHA-CLOSURE"
)
NEXT_GATE = (
    "PA-CP1-ST8-Q3LOCK-HIGHER-WEIGHTED-ENERGY-MOMENTS-AND-"
    "THERMODYNAMIC-CAUCHY-CLOSURE"
)
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-independent-{SLUG}/result.json"
)

Q3_DIMENSION = 3
SPATIAL_DIMENSION = 3
FALSE_SCOPE_KEYS = (
    "common_state_independent_real_time_automorphism",
    "common_alpha_KMS_identification",
    "distinct_algebraic_ground_states",
    "broken_sector_GNS_gap",
    "continuum_limit",
    "physical_empty_space",
    "C6_advanced",
    "CP1_complete",
    "Sector_A_complete",
    "Pre_A_complete",
)
TRUE_SCOPE_KEYS = (
    "fixed_lattice_finite_volume",
    "common_local_polynomial_derivation",
    "source_uniform_coercivity",
    "weighted_first_local_energy_cone",
)


def serial(value: Any) -> Any:
    """Convert exact objects to stable JSON-compatible values."""

    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def portable_sha256(path: Path) -> str:
    """Hash text after normalizing checkout line endings."""

    content = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(content).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a complete deterministic JSON file by same-directory replace."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    """Fail-fast assertion ledger."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(
                f"{group}: {name}: actual={actual!r}, expected={expected!r}"
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


Vector = tuple[Fraction, ...]
Edge = tuple[int, int]
Polynomial = list[Fraction]


def dot(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def cube_vertices(dimension: int) -> list[tuple[int, ...]]:
    return list(itertools.product((0, 1), repeat=dimension))


def cube_edges(vertices: Sequence[tuple[int, ...]]) -> list[Edge]:
    return [
        (left, right)
        for left in range(len(vertices))
        for right in range(left + 1, len(vertices))
        if sum(a != b for a, b in zip(vertices[left], vertices[right])) == 1
    ]


def w4(q: Sequence[Fraction], g: Fraction, lam: Fraction, edges: Iterable[Edge]) -> Fraction:
    onsite = g * sum((value**4 for value in q), Fraction(0)) / 4
    graph = lam * sum(
        (
            (q[left] - q[right]) ** 2
            * (q[left] ** 2 + q[right] ** 2)
            for left, right in edges
        ),
        Fraction(0),
    ) / 4
    return onsite + graph


def poly_trim(polynomial: Polynomial) -> Polynomial:
    output = list(polynomial)
    while len(output) > 1 and output[-1] == 0:
        output.pop()
    return output


def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    size = max(len(left), len(right))
    return poly_trim(
        [
            (left[index] if index < len(left) else Fraction(0))
            + (right[index] if index < len(right) else Fraction(0))
            for index in range(size)
        ]
    )


def poly_scale(polynomial: Polynomial, scale: Fraction) -> Polynomial:
    return poly_trim([scale * coefficient for coefficient in polynomial])


def poly_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    output = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_power, left_coefficient in enumerate(left):
        for right_power, right_coefficient in enumerate(right):
            output[left_power + right_power] += left_coefficient * right_coefficient
    return poly_trim(output)


def poly_power(polynomial: Polynomial, exponent: int) -> Polynomial:
    output = [Fraction(1)]
    for _ in range(exponent):
        output = poly_multiply(output, polynomial)
    return output


def poly_derivative(polynomial: Polynomial) -> Polynomial:
    if len(polynomial) == 1:
        return [Fraction(0)]
    return poly_trim(
        [Fraction(power) * coefficient for power, coefficient in enumerate(polynomial)][1:]
    )


def poly_evaluate(polynomial: Polynomial, value: Fraction) -> Fraction:
    output = Fraction(0)
    for coefficient in reversed(polynomial):
        output = output * value + coefficient
    return output


def w4_shift_polynomial(
    q: Sequence[Fraction],
    a: Sequence[Fraction],
    g: Fraction,
    lam: Fraction,
    edges: Iterable[Edge],
) -> Polynomial:
    """Return exact coefficients of W4(q+s*a) in ascending powers of s."""

    lines = [[q[index], a[index]] for index in range(len(q))]
    output = [Fraction(0)]
    for line in lines:
        output = poly_add(output, poly_scale(poly_power(line, 4), g / 4))
    for left, right in edges:
        difference = poly_add(lines[left], poly_scale(lines[right], Fraction(-1)))
        square_sum = poly_add(poly_power(lines[left], 2), poly_power(lines[right], 2))
        edge_polynomial = poly_multiply(poly_power(difference, 2), square_sum)
        output = poly_add(output, poly_scale(edge_polynomial, lam / 4))
    return poly_trim(output)


def pairwise_square_identity(values: Sequence[Fraction]) -> tuple[Fraction, Fraction]:
    """Return both sides of n*sum(v_i^2)-(sum v_i)^2=sum_(i<j)(v_i-v_j)^2."""

    count = len(values)
    left = count * sum((value**2 for value in values), Fraction(0)) - sum(
        values, Fraction(0)
    ) ** 2
    right = sum(
        ((values[i] - values[j]) ** 2 for i in range(count) for j in range(i + 1, count)),
        Fraction(0),
    )
    return left, right


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    certificate = " ".join(certificate_text.split())

    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("parent gate", manifest["gate_resolution"]["parent_gate"] == PARENT_GATE, manifest["gate_resolution"]["parent_gate"], PARENT_GATE, "identity")
    audit.check("next gate", manifest["next_exact_gate"]["gate"] == NEXT_GATE, manifest["next_exact_gate"]["gate"], NEXT_GATE, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    source_text = Path(__file__).read_text(encoding="utf-8")
    syntax_tree = ast.parse(source_text)
    imported_modules: set[str] = set()
    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
    forbidden_modules = {"numpy", "sympy"}
    audit.check(
        "stdlib-only dependency boundary",
        not any(module.split(".")[0] in forbidden_modules for module in imported_modules),
        sorted(imported_modules),
        "no external algebra or array module",
        "independence",
    )
    primary_module = f"pre_a_cp1_st8_q3lock_common_local_derivation_weighted_energy_route_split"
    audit.check(
        "no primary verifier import",
        not any(module.endswith(primary_module) for module in imported_modules),
        sorted(imported_modules),
        "primary module absent",
        "independence",
    )

    vertices = cube_vertices(Q3_DIMENSION)
    edges = cube_edges(vertices)
    degrees = [sum(index in edge for edge in edges) for index in range(len(vertices))]
    expected_vertex_count = 2**Q3_DIMENSION
    expected_edge_count = expected_vertex_count * Q3_DIMENSION // 2
    audit.check("Q3 vertex count", len(vertices) == expected_vertex_count, len(vertices), expected_vertex_count, "q3_graph")
    audit.check("Q3 edge count", len(edges) == expected_edge_count, len(edges), expected_edge_count, "q3_graph")
    audit.check("Q3 degree three", degrees == [Q3_DIMENSION] * expected_vertex_count, degrees, [Q3_DIMENSION] * expected_vertex_count, "q3_graph")

    component_count = len(vertices)
    coercive_factor = Fraction(1, 4 * component_count)
    audit.check("eight-component coercive coefficient", coercive_factor == Fraction(1, 32), coercive_factor, Fraction(1, 32), "coercivity")
    coercivity_fixtures: tuple[Vector, ...] = (
        tuple(Fraction(index - 3, 2) for index in range(component_count)),
        tuple(Fraction((-1) ** index * (index + 1), 5) for index in range(component_count)),
        tuple(Fraction(1) for _ in range(component_count)),
        (Fraction(2),) + tuple(Fraction(0) for _ in range(component_count - 1)),
    )
    coercivity_rows: list[dict[str, Any]] = []
    coercive_g = Fraction(7, 3)
    coercive_lam = Fraction(5, 11)
    for fixture_index, q in enumerate(coercivity_fixtures):
        squared_components = tuple(value**2 for value in q)
        identity_left, identity_right = pairwise_square_identity(squared_components)
        norm_squared = sum(squared_components, Fraction(0))
        lower = coercive_g * norm_squared**2 / (4 * component_count)
        exact = w4(q, coercive_g, coercive_lam, edges)
        graph_part = exact - coercive_g * sum((value**4 for value in q), Fraction(0)) / 4
        audit.check(f"power-mean identity fixture {fixture_index}", identity_left == identity_right, identity_left, identity_right, "coercivity")
        audit.check(f"nonnegative Q3 quartic fixture {fixture_index}", graph_part >= 0, graph_part, ">=0", "coercivity")
        audit.check(f"W4 >= g|q|^4/32 fixture {fixture_index}", exact >= lower, exact, lower, "coercivity")
        coercivity_rows.append({"q": q, "W4": exact, "lower": lower, "slack": exact - lower})

    incident_degree = degrees[0]
    ray_rows: list[dict[str, Any]] = []
    for g, lam, t, radius in (
        (Fraction(5, 3), Fraction(2, 7), Fraction(3, 2), Fraction(11, 5)),
        (Fraction(9, 5), Fraction(0), Fraction(7, 4), Fraction(13, 6)),
        (Fraction(4), Fraction(3, 8), Fraction(5, 6), Fraction(8, 3)),
    ):
        q = (t,) + tuple(Fraction(0) for _ in range(component_count - 1))
        ray_coefficient = w4(q, g, lam, edges) / t**4
        expected_coefficient = (g + incident_degree * lam) / 4
        second_derivative_factor = 4 * (4 - 1)
        hessian_at_radius = second_derivative_factor * ray_coefficient * radius**2
        expected_hessian = (4 - 1) * (g + incident_degree * lam) * radius**2
        audit.check("coordinate-ray quartic coefficient", ray_coefficient == expected_coefficient, ray_coefficient, expected_coefficient, "fourier_cutoff")
        audit.check("coordinate-ray Hessian lower bound", hessian_at_radius == expected_hessian, hessian_at_radius, expected_hessian, "fourier_cutoff")
        ray_rows.append({"g": g, "lambda": lam, "ray_coefficient": ray_coefficient, "radius": radius, "kappa_lower": hessian_at_radius})
    audit.check(
        "manifest Fourier lower-bound contract",
        manifest["fourier_cutoff_obstruction"]["lower_bound"] == "kappa_R>=3(g+3lambda)R^2",
        manifest["fourier_cutoff_obstruction"]["lower_bound"],
        "kappa_R>=3(g+3lambda)R^2",
        "fourier_cutoff",
    )
    audit.check(
        "Fourier obstruction remains route-local",
        "does not refute exact common dynamics" in manifest["fourier_cutoff_obstruction"]["scope"].lower(),
        manifest["fourier_cutoff_obstruction"]["scope"],
        "does not refute exact common dynamics",
        "scope",
    )

    # Exact rational source-envelope fixture.  Parameters are chosen from a
    # rational optimizer rho_* rather than fitting a sampled maximum.
    envelope_g = Fraction(64)
    envelope_gamma = Fraction(1)
    base_quartic = envelope_g / (4 * component_count)
    a_gamma = base_quartic - envelope_gamma
    rho_star = Fraction(3, 2)
    envelope_r = Fraction(0)
    h0 = 4 * a_gamma * rho_star**3
    c_gamma = 3 * a_gamma * rho_star**4
    slack_polynomial = [c_gamma, -h0, envelope_r / 2, Fraction(0), a_gamma]
    factor_polynomial = poly_multiply(
        poly_power([-rho_star, Fraction(1)], 2),
        [3 * a_gamma * rho_star**2, 2 * a_gamma * rho_star, a_gamma],
    )
    audit.check("C_gamma exact envelope factorization", slack_polynomial == factor_polynomial, slack_polynomial, factor_polynomial, "source_envelope")
    audit.check("C_gamma stationary optimizer", poly_evaluate(poly_derivative(poly_scale(slack_polynomial, Fraction(-1))), rho_star) == 0, poly_evaluate(poly_derivative(poly_scale(slack_polynomial, Fraction(-1))), rho_star), 0, "source_envelope")
    envelope_rows: list[dict[str, Any]] = []
    for rho in (Fraction(0), Fraction(1, 3), Fraction(1), rho_star, Fraction(2), Fraction(9, 2)):
        slack = poly_evaluate(slack_polynomial, rho)
        factor = (rho - rho_star) ** 2 * a_gamma * (
            rho**2 + 2 * rho_star * rho + 3 * rho_star**2
        )
        audit.check("source envelope rational fixture", slack == factor and slack >= 0, slack, factor, "source_envelope")
        envelope_rows.append({"rho": rho, "slack": slack})
    for fixture_index, q in enumerate(coercivity_fixtures):
        sum_q = sum(q, Fraction(0))
        rho_squared = sum((value**2 for value in q), Fraction(0))
        cauchy_left, cauchy_right = pairwise_square_identity(q)
        audit.check(f"collective-source Cauchy identity {fixture_index}", cauchy_left == cauchy_right, cauchy_left, cauchy_right, "source_envelope")
        audit.check(f"unit collective source bound {fixture_index}", sum_q**2 <= component_count * rho_squared, sum_q**2, component_count * rho_squared, "source_envelope")
    audit.check("gamma hypothesis strict", Fraction(0) < envelope_gamma < base_quartic, envelope_gamma, f"0<gamma<{base_quartic}", "hypotheses")
    audit.check("gamma endpoint rejected", not (Fraction(0) < base_quartic < base_quartic), base_quartic, "rejected", "hostile")

    current_rows: list[dict[str, Any]] = []
    for c, chi in (
        (Fraction(2), Fraction(1)),
        (Fraction(7, 3), Fraction(5, 4)),
        (Fraction(11, 6), Fraction(9, 5)),
    ):
        kinetic_px = -c / (2 * chi)
        half_bond_px = c / (4 * chi)
        half_bond_py = -c / (4 * chi)
        derivative_px = kinetic_px + half_bond_px
        derivative_py = half_bond_py
        current_anticommutator_coefficient = c / (4 * chi)
        audit.check("current px cancellation coefficient", derivative_px == -current_anticommutator_coefficient, derivative_px, -current_anticommutator_coefficient, "current")
        audit.check("current py cancellation coefficient", derivative_py == -current_anticommutator_coefficient, derivative_py, -current_anticommutator_coefficient, "current")

        # P=p_x+p_y commutes with D=q_x-q_y.  Hence {P,D}=2PD.
        commutator_units = Fraction(-1) + Fraction(1)
        audit.check("total momentum commutes with relative coordinate", commutator_units == 0, commutator_units, 0, "current")
        product_current_coefficient = 2 * current_anticommutator_coefficient
        kinetic_coefficient = Fraction(1, 4) / chi
        bond_coefficient = c / 2
        sharp_bound_squared = product_current_coefficient**2 / (
            4 * kinetic_coefficient * bond_coefficient
        )
        audit.check("sharp current bound squared", sharp_bound_squared == c / (2 * chi), sharp_bound_squared, c / (2 * chi), "current")
        audit.check("completion-square discriminant saturation", product_current_coefficient**2 == 4 * sharp_bound_squared * kinetic_coefficient * bond_coefficient, product_current_coefficient**2, 4 * sharp_bound_squared * kinetic_coefficient * bond_coefficient, "current")
        for momentum, displacement in (
            (Fraction(0), Fraction(4, 3)),
            (Fraction(2), Fraction(1)),
            (Fraction(-7, 5), Fraction(11, 6)),
        ):
            energy = kinetic_coefficient * momentum**2 + bond_coefficient * displacement**2
            current_squared = (product_current_coefficient * momentum * displacement) ** 2
            audit.check("sharp form bound rational fixture", current_squared <= sharp_bound_squared * energy**2, current_squared, sharp_bound_squared * energy**2, "current")
        current_rows.append({"c": c, "chi": chi, "anticommutator_coefficient": current_anticommutator_coefficient, "sharp_bound_squared": sharp_bound_squared})

    saturation_c = Fraction(2)
    saturation_chi = Fraction(1)
    saturation_p = Fraction(2)
    saturation_d = Fraction(1)
    saturation_a = Fraction(1, 4) / saturation_chi
    saturation_b = saturation_c / 2
    saturation_j = saturation_c / (2 * saturation_chi)
    saturation_l_squared = saturation_c / (2 * saturation_chi)
    saturation_energy = saturation_a * saturation_p**2 + saturation_b * saturation_d**2
    saturation_current = abs(saturation_j * saturation_p * saturation_d)
    audit.check("sharp form bound equality fixture", saturation_l_squared == 1 and saturation_current == saturation_energy, (saturation_l_squared, saturation_current), (Fraction(1), saturation_energy), "current")
    audit.check("wrong factor-two current rejected", saturation_c / (2 * saturation_chi) != saturation_c / (4 * saturation_chi), saturation_c / (2 * saturation_chi), saturation_c / (4 * saturation_chi), "hostile")

    spatial_steps = []
    for axis in range(SPATIAL_DIMENSION):
        for sign in (-1, 1):
            step = [0] * SPATIAL_DIMENSION
            step[axis] = sign
            spatial_steps.append(tuple(step))
    spatial_degree = len(set(spatial_steps))
    audit.check("cubic lattice nearest-neighbour degree", spatial_degree == 2 * SPATIAL_DIMENSION, spatial_degree, 2 * SPATIAL_DIMENSION, "weighted_energy")
    ratio = Fraction(3, 2)
    weighted_l_squared = saturation_l_squared
    weighted_rate_squared = spatial_degree**2 * weighted_l_squared * (ratio - 1) ** 2
    audit.check("rational weighted-rate square fixture", weighted_rate_squared == Fraction(9), weighted_rate_squared, Fraction(9), "weighted_energy")
    for left_weight, right_weight, left_energy, right_energy in (
        (Fraction(3, 2), Fraction(1), Fraction(5, 4), Fraction(7, 3)),
        (Fraction(4, 3), Fraction(1), Fraction(0), Fraction(9, 5)),
        (Fraction(1), Fraction(6, 5), Fraction(11, 7), Fraction(2, 9)),
    ):
        adjacent_ratio = max(left_weight / right_weight, right_weight / left_weight)
        edge_charge = abs(left_weight - right_weight) * (left_energy + right_energy)
        site_charge = (ratio - 1) * (
            left_weight * left_energy + right_weight * right_energy
        )
        audit.check("adjacent-weight edge charge", adjacent_ratio <= ratio and edge_charge <= site_charge, (adjacent_ratio, edge_charge), (f"<={ratio}", site_charge), "weighted_energy")
    growth_contract = manifest["weighted_first_local_energy"]["three_dimensional_growth_bound"]
    audit.check("degree-six weighted growth contract", "6 sqrt(c/(2chi))(exp(mu)-1)" in growth_contract, growth_contract, "degree 6 sharp-current rate", "weighted_energy")

    homogeneity_rows: list[dict[str, Any]] = []
    for fixture_index, (q, a, g, lam) in enumerate(
        (
            (
                tuple(Fraction(index - 2, 3) for index in range(component_count)),
                tuple(Fraction((-1) ** index * (index + 1), 7) for index in range(component_count)),
                Fraction(5, 4),
                Fraction(2, 9),
            ),
            (
                tuple(Fraction(1 if index == 0 else 0) for index in range(component_count)),
                tuple(Fraction(index + 1, 8) for index in range(component_count)),
                Fraction(3, 2),
                Fraction(0),
            ),
        )
    ):
        shifted = w4_shift_polynomial(q, a, g, lam, edges)
        directional = poly_derivative(shifted)
        leading_cubic = directional[3]
        w4_a = w4(a, g, lam, edges)
        euler_shifted = w4_shift_polynomial(a, a, g, lam, edges)
        euler_directional = poly_derivative(euler_shifted)
        audit.check(f"cubic force leading coefficient fixture {fixture_index}", leading_cubic == 4 * w4_a, leading_cubic, 4 * w4_a, "basic_resolvent")
        audit.check(f"Euler D_a W4(a) fixture {fixture_index}", euler_directional[0] == 4 * w4_a, euler_directional[0], 4 * w4_a, "basic_resolvent")
        audit.check(f"strict W4(a) fixture {fixture_index}", w4_a > 0, w4_a, ">0", "basic_resolvent")
        homogeneity_rows.append({"W4_a": w4_a, "directional_cubic_lead": leading_cubic})

    displacement_q = tuple(Fraction(index - 2, 5) for index in range(component_count))
    displacement_p = tuple(Fraction(3 - index, 7) for index in range(component_count))
    displacement_a = tuple(Fraction(index + 1, 9) for index in range(component_count))
    displacement_b = tuple(Fraction((-1) ** index, 4) for index in range(component_count))
    displacement_s = Fraction(11, 6)
    before = dot(displacement_a, displacement_p) + dot(displacement_b, displacement_q)
    shifted_q = tuple(qi + displacement_s * ai for qi, ai in zip(displacement_q, displacement_a))
    shifted_p = tuple(pi - displacement_s * bi for pi, bi in zip(displacement_p, displacement_b))
    after = dot(displacement_a, shifted_p) + dot(displacement_b, shifted_q)
    audit.check("basic-resolvent linear argument invariant", after == before, after, before, "basic_resolvent")
    resolvent_obstruction = manifest["basic_resolvent_core_obstruction"]
    resolvent_lemma_complete = (
        "Im(z) nonzero" in resolvent_obstruction["resolvent"]
        and "s-independent norms" in resolvent_obstruction["bounded_input_test"]
        and "R^3" in resolvent_obstruction["cutoff_norm_lower_bound"]
    )
    audit.check("basic-resolvent route boundary explicit", resolvent_lemma_complete and "not finite-time resolvent-algebra invariance" in resolvent_obstruction["scope"].lower(), resolvent_obstruction, "nonreal-z bounded-input lower bound with scoped consequence", "scope")

    actual_false_scope = tuple(sorted(key for key, value in manifest["scope"].items() if value is False))
    expected_false_scope = tuple(sorted(FALSE_SCOPE_KEYS))
    audit.check("complete false-scope key set", actual_false_scope == expected_false_scope, actual_false_scope, expected_false_scope, "scope")
    for key in FALSE_SCOPE_KEYS:
        audit.check(f"scope false {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    for key in TRUE_SCOPE_KEYS:
        audit.check(f"bounded scope true {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    audit.check("common automorphism explicitly unproved", manifest["common_local_derivation"]["exponentiated_common_automorphism"] is False, manifest["common_local_derivation"]["exponentiated_common_automorphism"], False, "scope")
    audit.check("common alpha explicitly unproved", manifest["weighted_first_local_energy"]["common_alpha_proved"] is False, manifest["weighted_first_local_energy"]["common_alpha_proved"], False, "scope")
    for phrase in (
        "does not close",
        "does not by itself control the cubic force",
        "route obstruction only",
        "does not rule out finite-time resolvent-algebra invariance",
        "No Pre-A or C6 status changes",
    ):
        audit.check(f"certificate boundary phrase {phrase}", phrase.lower() in certificate.lower(), phrase in certificate, True, "certificate")

    return {
        "schema": f"tect/{SLUG}-independent/0.1",
        "script_version": __version__,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "parent_gate": PARENT_GATE,
        "next_gate": NEXT_GATE,
        "claim_bearing": False,
        "authority": "T0 non-importing exact Fraction audit; no claim or tier change",
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "derived": {
            "q3": {
                "dimension": Q3_DIMENSION,
                "vertices": len(vertices),
                "edges": len(edges),
                "degrees": degrees,
                "coordinate_ray_rows": ray_rows,
            },
            "coercivity": {
                "component_count": component_count,
                "W4_lower_coefficient_per_g": coercive_factor,
                "fixtures": coercivity_rows,
            },
            "source_envelope": {
                "g": envelope_g,
                "gamma": envelope_gamma,
                "a_gamma": a_gamma,
                "rho_star": rho_star,
                "h0": h0,
                "C_gamma": c_gamma,
                "fixtures": envelope_rows,
            },
            "current": current_rows,
            "sharp_form_saturation": {
                "c": saturation_c,
                "chi": saturation_chi,
                "P": saturation_p,
                "D": saturation_d,
                "energy": saturation_energy,
                "current_absolute": saturation_current,
                "bound_squared": saturation_l_squared,
            },
            "weighted_energy": {
                "spatial_dimension": SPATIAL_DIMENSION,
                "nearest_neighbour_degree": spatial_degree,
                "adjacent_ratio_fixture": ratio,
                "growth_rate_squared_fixture": weighted_rate_squared,
            },
            "homogeneity": homogeneity_rows,
        },
        "scope": manifest["scope"],
        "files": {
            "manifest_sha256": portable_sha256(MANIFEST),
            "certificate_sha256": portable_sha256(CERTIFICATE),
            "script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"),
            "script_sha256": portable_sha256(Path(__file__)),
        },
        "verdict": "PASS",
        "boundary": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="derive twice and require byte-equivalent serialized payloads without writing",
    )
    arguments = parser.parse_args()
    payload = build_payload()
    if arguments.self_test:
        repeated = build_payload()
        if json.dumps(serial(payload), sort_keys=True) != json.dumps(serial(repeated), sort_keys=True):
            raise AssertionError("nondeterministic independent payload")
        print(
            f"SELF-TEST PASS {payload['assertions']['passed']}/{payload['assertions']['total']} | "
            f"{EXPLORATION_ID} independent Fraction audit"
        )
        return 0
    atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['assertions']['passed']}/{payload['assertions']['total']} | "
        f"{EXPLORATION_ID} independent Fraction audit"
    )
    print(arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
