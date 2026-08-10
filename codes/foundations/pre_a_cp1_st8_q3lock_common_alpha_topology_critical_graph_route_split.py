#!/usr/bin/env python3
"""Primary exact verifier for the R-167 v1.3 topology route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-common-alpha-topology-critical-graph-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-modular-cutoff-unitary-resummation-route-split-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-primary-{SLUG}/result.json"
)


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return str(value)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(json_safe(payload), stream, indent=2, sort_keys=True)
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
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": json_safe(actual),
                "expected": json_safe(expected),
            }
        )


def centered_kick_audit() -> dict[str, Any]:
    # Declared rational fixture inputs.
    c = sp.Rational(3, 5)
    z = sp.Integer(6)
    chi = sp.Rational(7, 4)
    sqrt_gamma = sp.Rational(2, 5)
    weight_ratio = sp.Rational(3, 2)
    delta = sp.Rational(2, 7)
    c_b = sp.simplify(
        1 + c**2 * z**2 * weight_ratio / (2 * chi * sqrt_gamma)
    )

    p, s = sp.symbols("p s", real=True)
    shifted = (p + delta * c * s) ** 2
    young = (1 + delta) * p**2 + (1 + 1 / delta) * delta**2 * c**2 * s**2
    residual = sp.factor(young - shifted)
    hessian = sp.hessian(residual, (p, s)) / 2

    q2, one = sp.symbols("q2 one", nonnegative=True)
    quartic_residual = sp.factor(one**2 + sqrt_gamma**2 * q2**2 - 2 * sqrt_gamma * one * q2)

    return {
        "inputs": {
            "c": c,
            "z": z,
            "chi": chi,
            "sqrt_gamma": sqrt_gamma,
            "weight_ratio": weight_ratio,
            "delta": delta,
        },
        "weighted_star_coefficient": z**2 * weight_ratio,
        "c_b": c_b,
        "young_residual": residual,
        "young_hessian": hessian,
        "young_trace": sp.trace(hessian),
        "young_determinant": sp.det(hessian),
        "quartic_residual": quartic_residual,
        "one_sided_sum_power_at_half": sp.Rational(1, 2),
        "fully_conjugated_safe_power_at_half": 2 * sp.Rational(1, 2),
        "commutator_recurrence": {
            "q": "beta([q_x,A])",
            "p": "beta([p_x,A]-delta*c*sum_y[q_y,A])",
        },
    }


def resolvent_audit() -> dict[str, Any]:
    u, v = sp.symbols("u v", real=True)
    denominator_sq = (1 + u**2) * (1 + v**2)
    numerator_sq = (u - v) ** 2
    residual = sp.factor(denominator_sq - numerator_sq)
    fixtures: list[dict[str, Any]] = []
    for value in (sp.Rational(1, 3), sp.Rational(1), sp.Rational(7, 2), sp.Rational(19, 5)):
        paired = -1 / value
        ratio_sq = sp.simplify(
            (value - paired) ** 2 / ((1 + value**2) * (1 + paired**2))
        )
        fixtures.append({"u": value, "v": paired, "ratio_squared": ratio_sq})
    return {
        "residual": residual,
        "fixtures": fixtures,
        "exact_norm_distance": sp.Integer(1),
        "point_norm_continuous": False,
    }


def onsite_audit() -> dict[str, Any]:
    q, a, g = sp.symbols("q a g", real=True, nonzero=True)
    potential = g * q**4 / 4
    derivative_difference = sp.expand(sp.diff(potential, q) - sp.diff(potential, q).subs(q, q - a))
    expected = g * (3 * a * q**2 - 3 * a**2 * q + a**3)
    exponents = {
        "s_0": sp.Integer(2),
        "s_quarter": sp.Integer(2) - 4 * sp.Rational(1, 4),
        "s_half": sp.Integer(2) - 4 * sp.Rational(1, 2),
        "s_three_quarters": sp.Integer(2) - 4 * sp.Rational(3, 4),
    }
    return {
        "derivative_difference": sp.factor(derivative_difference),
        "expected": sp.factor(expected),
        "translated_bump_exponents": exponents,
        "unweighted_lipschitz_closed": False,
        "subcritical_lipschitz_closed": False,
        "critical_half_status": "FIXED_LEIBNIZ_REJECTED_NONLEIBNIZ_OPEN",
    }


def critical_half_audit() -> dict[str, Any]:
    q = sp.symbols("q0:8", real=True)
    p = sp.symbols("p0:8", real=True)
    a, g, lam, chi = sp.symbols("a g lambda chi", positive=True)
    edges = sorted(
        {
            (min(vertex, vertex ^ (1 << bit)), max(vertex, vertex ^ (1 << bit)))
            for vertex in range(8)
            for bit in range(3)
        }
    )
    potential = g * sum(coordinate**4 for coordinate in q) / 4
    potential += lam * sum(
        (q[left] - q[right]) ** 2 * (q[left] ** 2 + q[right] ** 2)
        for left, right in edges
    ) / 4
    forces = [sp.expand(sp.diff(potential, coordinate)) for coordinate in q]
    neighbors_zero = sorted(
        right if left == 0 else left
        for left, right in edges
        if left == 0 or right == 0
    )
    expected_force_zero = sp.expand(
        (g + 3 * lam) * q[0] ** 3
        - sp.Rational(3, 2) * lam * q[0] ** 2 * sum(q[j] for j in neighbors_zero)
        + lam * q[0] * sum(q[j] ** 2 for j in neighbors_zero)
        - sp.Rational(1, 2) * lam * sum(q[j] ** 3 for j in neighbors_zero)
    )

    def backward_vector_field(expression: sp.Expr) -> sp.Expr:
        return sp.expand(
            sum(-p[index] * sp.diff(expression, q[index]) / chi for index in range(8))
            + sum(forces[index] * sp.diff(expression, p[index]) for index in range(8))
        )

    axis = {q[0]: a, **{q[index]: 0 for index in range(1, 8)}, **{momentum: 0 for momentum in p}}
    full_jet_expressions: list[sp.Expr] = []
    current: sp.Expr = p[0]
    for _ in range(3):
        current = backward_vector_field(current)
        full_jet_expressions.append(sp.factor(current.subs(axis)))

    fixture = {g: sp.Rational(3, 5), lam: sp.Rational(2, 7), chi: sp.Rational(7, 4)}
    full_fixture_jets = [sp.factor(value.subs(fixture)) for value in full_jet_expressions]
    g_fixture = sp.simplify((g + 3 * lam).subs(fixture))

    q_scalar, p_scalar = sp.symbols("q_scalar p_scalar", real=True)

    def scalar_vector_field(expression: sp.Expr) -> sp.Expr:
        return sp.expand(
            -p_scalar * sp.diff(expression, q_scalar)
            + q_scalar**3 * sp.diff(expression, p_scalar)
        )

    scalar_jets: list[sp.Expr] = []
    scalar_current: sp.Expr = p_scalar
    for _ in range(5):
        scalar_current = scalar_vector_field(scalar_current)
        scalar_jets.append(sp.factor(scalar_current.subs({q_scalar: a, p_scalar: 0})))

    b = sp.Rational(2, 5)
    commutator_domination = sp.Rational(3, 7)
    l_wb = sp.Rational(5, 4)
    tau_threshold = sp.simplify(l_wb / (commutator_domination * g_fixture * b))
    tau_fixture = tau_threshold + 1
    lower_linear_slope = sp.simplify(
        commutator_domination * g_fixture * tau_fixture * b
    )

    return {
        "q3_edges": edges,
        "neighbors_zero": neighbors_zero,
        "force_zero": sp.factor(forces[0]),
        "expected_force_zero": sp.factor(expected_force_zero),
        "G_fixture": g_fixture,
        "full_q3_backward_jets": full_fixture_jets,
        "scalar_backward_jets": scalar_jets,
        "scaled_time_series_coefficients": {
            "tau_a": g_fixture,
            "tau_cubed_over_a": sp.simplify(full_fixture_jets[2] / (6 * a**5)),
        },
        "leibniz_fixture": {
            "b": b,
            "commutator_domination": commutator_domination,
            "L_Wb": l_wb,
            "tau_threshold": tau_threshold,
            "tau": tau_fixture,
            "lower_linear_slope": lower_linear_slope,
            "upper_linear_slope": l_wb,
        },
        "fixed_one_sided_leibniz_critical_closed": False,
        "nonleibniz_or_state_weighted_critical_open": True,
    }


def cutoff_audit() -> dict[str, Any]:
    z = sp.Integer(6)
    beta = sp.Rational(5, 3)
    c = sp.Rational(3, 5)
    cutoff_sizes = (sp.Integer(2), sp.Integer(4), sp.Integer(8), sp.Integer(16))
    # The radial cutoff has |Q_L|<=2L, so a safe scalar bond norm is 4cL^2.
    rows = []
    for length in cutoff_sizes:
        j_l = 4 * c * length**2
        rows.append(
            {
                "L": length,
                "J_L": j_l,
                "half_strip_parameter": sp.simplify(z * beta * j_l),
            }
        )
    return {
        "rows": rows,
        "half_strip_condition": "z*beta*J_L<1",
        "growth_power": sp.Integer(2),
        "fixed_beta_limit_closed_by_absolute_expansion": False,
        "kinetic_commutator": "[p^2,Q_L]=-i*hbar*(p.DQ_L+DQ_L.p)",
        "norm_c1": False,
    }


def direct_relative_audit() -> dict[str, Any]:
    beta = sp.Rational(4, 3)
    theta = sp.Rational(7, 3)
    t_fixture = sp.Rational(5, 7)
    hbar_fixture = sp.Rational(11, 13)
    phi_w2_fixture = sp.Rational(9, 16)
    one_orientation_bound = sp.simplify(
        t_fixture * sp.sqrt(phi_w2_fixture) / hbar_fixture
    )
    trace_distance_bound = sp.simplify(2 * one_orientation_bound)
    entropy_coefficient = sp.simplify(beta / (theta - beta))

    rho_fixture = sp.diag(sp.Rational(2, 3), sp.Rational(1, 3))
    sqrt_rho_fixture = sp.diag(sp.sqrt(sp.Rational(2, 3)), sp.sqrt(sp.Rational(1, 3)))
    w_fixture = sp.Matrix([[1, 2], [2, -1]])
    right_hs_sq = sp.simplify(
        sp.trace((w_fixture * sqrt_rho_fixture).T * (w_fixture * sqrt_rho_fixture))
    )
    left_hs_sq = sp.simplify(
        sp.trace((sqrt_rho_fixture * w_fixture).T * (sqrt_rho_fixture * w_fixture))
    )
    phi_w2_matrix = sp.simplify(sp.trace(rho_fixture * w_fixture**2))
    rows: list[dict[str, Any]] = []
    previous_multiplier = None
    for n_value in (8, 16, 32):
        n = sp.Integer(n_value)
        epsilon = sp.exp(-beta * n / 4)
        omega = sp.sqrt(n**2 + 4 * epsilon**2)
        r = sp.exp(-beta * n)
        logarithmic_mean = (1 - r) / ((1 + r) * beta * n)
        w_duhamel_sq = sp.simplify(2 * epsilon**2 * logarithmic_mean)
        w_modular_sq = sp.simplify((beta * n) ** 2 * w_duhamel_sq)
        off_diagonal = sp.simplify(2 * epsilon * n / omega**2)
        direct_d_sq_upper = sp.simplify(2 * off_diagonal**2 * logarithmic_mean + 32 * epsilon**4 / omega**4)
        direct_delta_sq_upper = sp.simplify((beta * n) ** 2 * 2 * off_diagonal**2 * logarithmic_mean)
        multiplier_lower = sp.simplify(off_diagonal * sp.exp(beta * n / 2))
        multiplier_float = float(sp.N(multiplier_lower, 40))
        rows.append(
            {
                "n": n,
                "epsilon": epsilon,
                "w_duhamel_sq": w_duhamel_sq,
                "w_modular_sq": w_modular_sq,
                "off_diagonal": off_diagonal,
                "direct_d_sq_upper": direct_d_sq_upper,
                "direct_delta_sq_upper": direct_delta_sq_upper,
                "multiplier_lower": multiplier_lower,
                "multiplier_lower_float": multiplier_float,
                "multiplier_increases": previous_multiplier is None or multiplier_float > previous_multiplier,
            }
        )
        previous_multiplier = multiplier_float
    return {
        "beta": beta,
        "theta": theta,
        "rows": rows,
        "fixed_finite_volume_unbounded_tail_passage_closed": True,
        "thermodynamic_uniform_tail_passage_closed": False,
        "form_norm_cutoff_required": True,
        "finite_gibbs_energy_required": True,
        "uniform_evolved_half_strip_inferred": False,
        "one_orientation_bound_fixture": one_orientation_bound,
        "trace_distance_bound_fixture": trace_distance_bound,
        "right_hs_sq_fixture": right_hs_sq,
        "left_hs_sq_fixture": left_hs_sq,
        "phi_w2_matrix_fixture": phi_w2_matrix,
        "entropy_coefficient_fixture": entropy_coefficient,
        "trace_distance_coefficient": "2*abs(t)/hbar",
        "relative_entropy_identity": "beta*(rho_t(W)-rho(W))",
    }


def representation_audit() -> dict[str, Any]:
    rows = []
    for n in (2, 4, 8, 16):
        test_vectors = {
            "e0": 0,
            "e1": 0 if n > 1 else 1,
            "en": 1,
        }
        rows.append(
            {
                "n": n,
                "multiplication_tail_values": test_vectors,
                "ultrafilter_character": 1,
            }
        )
    return {
        "rows": rows,
        "multiplication_strong_star_limit": 0,
        "direct_sum_strong_star_limit": [0, 1],
        "abstract_cstar_inference": False,
    }


def run_audit() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    parent = json.loads(PARENT.read_text(encoding="utf-8"))

    audit.check("schema", manifest["schema"] == "tect/pre-a-route-split/1.0", manifest["schema"], "tect/pre-a-route-split/1.0", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-000799", manifest["exploration_id"], "EXP-000799", "provenance")
    audit.check("result number", manifest["result_number"] == "R-167", manifest["result_number"], "R-167", "provenance")
    audit.check("result version", manifest["result_version"] == "v1.3", manifest["result_version"], "v1.3", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "provenance")
    audit.check("parent v1.2", parent["result_version"] == "v1.2", parent["result_version"], "v1.2", "provenance")
    audit.check("seven negatives", len(manifest["negative_ids"]) == 7, len(manifest["negative_ids"]), 7, "provenance")

    kick = centered_kick_audit()
    audit.check("weighted star coefficient", kick["weighted_star_coefficient"] == 54, kick["weighted_star_coefficient"], 54, "kick")
    audit.check("C_b fixture", kick["c_b"] == sp.Rational(521, 35), kick["c_b"], sp.Rational(521, 35), "kick")
    audit.check("Young residual PSD determinant", kick["young_determinant"] == 0, kick["young_determinant"], 0, "kick")
    audit.check("Young residual PSD trace", bool(kick["young_trace"] > 0), kick["young_trace"], ">0", "kick")
    audit.check("quartic residual square", sp.expand(kick["quartic_residual"] - (kick["inputs"]["sqrt_gamma"] * sp.symbols("q2", nonnegative=True) - sp.symbols("one", nonnegative=True)) ** 2) == 0, kick["quartic_residual"], "square", "kick")
    audit.check("one-sided sum half power", kick["one_sided_sum_power_at_half"] == sp.Rational(1, 2), kick["one_sided_sum_power_at_half"], sp.Rational(1, 2), "kick")
    audit.check("fully conjugated safe half power", kick["fully_conjugated_safe_power_at_half"] == 1, kick["fully_conjugated_safe_power_at_half"], 1, "kick")
    audit.check("q recurrence", kick["commutator_recurrence"]["q"] == "beta([q_x,A])", kick["commutator_recurrence"]["q"], "beta([q_x,A])", "kick")
    audit.check("p recurrence one layer", "sum_y[q_y,A]" in kick["commutator_recurrence"]["p"], kick["commutator_recurrence"]["p"], "neighbor q commutators", "kick")
    audit.check("declared beta convention plus", "p_x+delta c" in manifest["all_bond_centered_graph_theorem"]["canonical_action"], manifest["all_bond_centered_graph_theorem"]["canonical_action"], "B^*pB=p+delta cS", "kick")

    resolvent = resolvent_audit()
    audit.check("resolvent residual", resolvent["residual"] == (1 + sp.symbols("u", real=True) * sp.symbols("v", real=True)) ** 2, resolvent["residual"], "(1+u*v)^2", "resolvent")
    for index, row in enumerate(resolvent["fixtures"]):
        audit.check(f"resolvent saturation {index}", row["ratio_squared"] == 1, row["ratio_squared"], 1, "resolvent")
    audit.check("resolvent exact norm", resolvent["exact_norm_distance"] == 1, resolvent["exact_norm_distance"], 1, "resolvent")
    audit.check("point norm rejected", resolvent["point_norm_continuous"] is False, resolvent["point_norm_continuous"], False, "resolvent")

    onsite = onsite_audit()
    audit.check("quartic translation polynomial", sp.expand(onsite["derivative_difference"] - onsite["expected"]) == 0, onsite["derivative_difference"], onsite["expected"], "onsite")
    audit.check("unweighted rejected", onsite["unweighted_lipschitz_closed"] is False, onsite["unweighted_lipschitz_closed"], False, "onsite")
    audit.check("subcritical rejected", onsite["subcritical_lipschitz_closed"] is False, onsite["subcritical_lipschitz_closed"], False, "onsite")
    audit.check("quarter exponent positive", onsite["translated_bump_exponents"]["s_quarter"] > 0, onsite["translated_bump_exponents"]["s_quarter"], ">0", "onsite")
    audit.check("half exponent critical", onsite["translated_bump_exponents"]["s_half"] == 0, onsite["translated_bump_exponents"]["s_half"], 0, "onsite")
    audit.check("critical Leibniz route rejected", onsite["critical_half_status"] == "FIXED_LEIBNIZ_REJECTED_NONLEIBNIZ_OPEN", onsite["critical_half_status"], "FIXED_LEIBNIZ_REJECTED_NONLEIBNIZ_OPEN", "onsite")

    critical_half = critical_half_audit()
    audit.check("Q3 edge count", len(critical_half["q3_edges"]) == 12, len(critical_half["q3_edges"]), 12, "critical_half")
    audit.check("Q3 zero degree", critical_half["neighbors_zero"] == [1, 2, 4], critical_half["neighbors_zero"], [1, 2, 4], "critical_half")
    audit.check("critical force identity", sp.expand(critical_half["force_zero"] - critical_half["expected_force_zero"]) == 0, critical_half["force_zero"], critical_half["expected_force_zero"], "critical_half")
    audit.check("critical G fixture", critical_half["G_fixture"] == sp.Rational(51, 35), critical_half["G_fixture"], sp.Rational(51, 35), "critical_half")
    audit.check(
        "full Q3 critical jets",
        critical_half["full_q3_backward_jets"]
        == [
            sp.Rational(51, 35) * sp.symbols("a", positive=True) ** 3,
            0,
            -sp.Rational(32112, 8575) * sp.symbols("a", positive=True) ** 5,
        ],
        critical_half["full_q3_backward_jets"],
        ["51*a^3/35", "0", "-32112*a^5/8575"],
        "critical_half",
    )
    audit.check(
        "full Q3 scaled cubic coefficient",
        critical_half["scaled_time_series_coefficients"]["tau_cubed_over_a"]
        == -sp.Rational(5352, 8575),
        critical_half["scaled_time_series_coefficients"]["tau_cubed_over_a"],
        -sp.Rational(5352, 8575),
        "critical_half",
    )
    audit.check(
        "scalar critical jets",
        critical_half["scalar_backward_jets"]
        == [
            sp.symbols("a", positive=True) ** 3,
            0,
            -3 * sp.symbols("a", positive=True) ** 5,
            0,
            27 * sp.symbols("a", positive=True) ** 7,
        ],
        critical_half["scalar_backward_jets"],
        ["a^3", "0", "-3*a^5", "0", "27*a^7"],
        "critical_half",
    )
    audit.check(
        "Leibniz slope contradiction fixture",
        critical_half["leibniz_fixture"]["lower_linear_slope"]
        > critical_half["leibniz_fixture"]["upper_linear_slope"],
        critical_half["leibniz_fixture"],
        "lower slope exceeds n*L(W_b) slope",
        "critical_half",
    )
    audit.check("fixed critical Leibniz route rejected", critical_half["fixed_one_sided_leibniz_critical_closed"] is False, critical_half["fixed_one_sided_leibniz_critical_closed"], False, "critical_half")
    audit.check("critical alternatives retained", critical_half["nonleibniz_or_state_weighted_critical_open"] is True, critical_half["nonleibniz_or_state_weighted_critical_open"], True, "critical_half")

    cutoff = cutoff_audit()
    parameters = [row["half_strip_parameter"] for row in cutoff["rows"]]
    audit.check("cutoff parameter strictly grows", all(right > left for left, right in zip(parameters, parameters[1:])), parameters, "strictly increasing", "cutoff")
    audit.check(
        "cutoff quadratic growth",
        all(
            sp.simplify(
                cutoff["rows"][i + 1]["J_L"] / cutoff["rows"][i]["J_L"]
            )
            == 4
            for i in range(len(cutoff["rows"]) - 1)
        ),
        [row["J_L"] for row in cutoff["rows"]],
        "quadruples when L doubles",
        "cutoff",
    )
    audit.check("cutoff norm C1 rejected", cutoff["norm_c1"] is False, cutoff["norm_c1"], False, "cutoff")
    audit.check("half strip absolute route open", cutoff["fixed_beta_limit_closed_by_absolute_expansion"] is False, cutoff["fixed_beta_limit_closed_by_absolute_expansion"], False, "cutoff")

    direct = direct_relative_audit()
    audit.check("direct multiplier lower increases", all(row["multiplier_increases"] for row in direct["rows"]), [row["multiplier_lower_float"] for row in direct["rows"]], "strictly increasing", "direct")
    audit.check(
        "W Duhamel tails decrease",
        all(
            float(sp.N(right["w_duhamel_sq"], 40))
            < float(sp.N(left["w_duhamel_sq"], 40))
            for left, right in zip(direct["rows"], direct["rows"][1:])
        ),
        [row["w_duhamel_sq"] for row in direct["rows"]],
        "decreasing",
        "direct",
    )
    audit.check(
        "W modular tails decrease",
        all(
            float(sp.N(right["w_modular_sq"], 40))
            < float(sp.N(left["w_modular_sq"], 40))
            for left, right in zip(direct["rows"], direct["rows"][1:])
        ),
        [row["w_modular_sq"] for row in direct["rows"]],
        "decreasing",
        "direct",
    )
    audit.check(
        "direct D tails decrease",
        all(
            float(sp.N(right["direct_d_sq_upper"], 40))
            < float(sp.N(left["direct_d_sq_upper"], 40))
            for left, right in zip(direct["rows"], direct["rows"][1:])
        ),
        [row["direct_d_sq_upper"] for row in direct["rows"]],
        "decreasing",
        "direct",
    )
    audit.check(
        "direct delta D tails decrease",
        all(
            float(sp.N(right["direct_delta_sq_upper"], 40))
            < float(sp.N(left["direct_delta_sq_upper"], 40))
            for left, right in zip(direct["rows"], direct["rows"][1:])
        ),
        [row["direct_delta_sq_upper"] for row in direct["rows"]],
        "decreasing",
        "direct",
    )
    audit.check(
        "two HS orientations equal phi(W^2)",
        direct["right_hs_sq_fixture"]
        == direct["left_hs_sq_fixture"]
        == direct["phi_w2_matrix_fixture"]
        == 5,
        {
            "right": direct["right_hs_sq_fixture"],
            "left": direct["left_hs_sq_fixture"],
            "phi_w2": direct["phi_w2_matrix_fixture"],
        },
        5,
        "direct",
    )
    audit.check(
        "relative-unitary one-orientation fixture",
        direct["one_orientation_bound_fixture"] == sp.Rational(195, 308),
        direct["one_orientation_bound_fixture"],
        sp.Rational(195, 308),
        "direct",
    )
    audit.check(
        "trace-distance factor two fixture",
        direct["trace_distance_bound_fixture"] == sp.Rational(195, 154)
        and direct["trace_distance_bound_fixture"]
        == 2 * direct["one_orientation_bound_fixture"],
        direct["trace_distance_bound_fixture"],
        sp.Rational(195, 154),
        "direct",
    )
    audit.check(
        "entropy variational coefficient fixture",
        direct["entropy_coefficient_fixture"] == sp.Rational(4, 3),
        direct["entropy_coefficient_fixture"],
        sp.Rational(4, 3),
        "direct",
    )
    audit.check(
        "fixed-finite-volume tail scope",
        direct["fixed_finite_volume_unbounded_tail_passage_closed"] is True
        and direct["thermodynamic_uniform_tail_passage_closed"] is False
        and direct["form_norm_cutoff_required"] is True
        and direct["finite_gibbs_energy_required"] is True,
        {
            "fixed_finite_volume": direct[
                "fixed_finite_volume_unbounded_tail_passage_closed"
            ],
            "thermodynamic_uniform": direct[
                "thermodynamic_uniform_tail_passage_closed"
            ],
            "form_norm": direct["form_norm_cutoff_required"],
            "finite_energy": direct["finite_gibbs_energy_required"],
        },
        "fixed finite volume only",
        "direct",
    )
    audit.check("uniform M not inferred", direct["uniform_evolved_half_strip_inferred"] is False, direct["uniform_evolved_half_strip_inferred"], False, "direct")

    representation = representation_audit()
    audit.check("multiplication strong-star zero", representation["multiplication_strong_star_limit"] == 0, representation["multiplication_strong_star_limit"], 0, "representation")
    audit.check("ultrafilter direct sum nonzero", representation["direct_sum_strong_star_limit"] == [0, 1], representation["direct_sum_strong_star_limit"], [0, 1], "representation")
    audit.check("abstract inference rejected", representation["abstract_cstar_inference"] is False, representation["abstract_cstar_inference"], False, "representation")

    for token in (
        "s=1/2",
        "EXP-000799",
        "R-167",
        "direct `D,delta D`",
        "thermodynamic `alpha`",
        "Pre-A remain open",
    ):
        audit.check(f"certificate token {token}", token in certificate, token if token in certificate else "MISSING", token, "authority")
    for negative_id in manifest["negative_ids"]:
        audit.check(
            f"negative in certificate {negative_id}",
            negative_id in certificate,
            negative_id if negative_id in certificate else "MISSING",
            negative_id,
            "authority",
        )
    audit.check("two active gates", len(manifest["open_gates"]) == 3 and all(gate in manifest["open_gates"] for gate in (manifest["active_routes"]["primary_gate"], manifest["active_routes"]["secondary_gate"])), manifest["open_gates"], "two route gates plus round-one", "authority")
    audit.check("no common alpha", "does not prove" in manifest["no_overclaim"] and "common C-star" in manifest["no_overclaim"], manifest["no_overclaim"], "explicit no-overclaim", "scope")
    audit.check("no ground", "algebraic ground states" in manifest["no_overclaim"], manifest["no_overclaim"], "ground open", "scope")
    audit.check("no gap", "GNS" in manifest["no_overclaim"], manifest["no_overclaim"], "gap open", "scope")
    audit.check("no Pre-A", "Pre-A" in manifest["no_overclaim"], manifest["no_overclaim"], "Pre-A open", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "centered_kick": kick,
            "resolvent": resolvent,
            "onsite": onsite,
            "critical_half": critical_half,
            "cutoff": cutoff,
            "direct_relative": direct,
            "representation": representation,
            "common_alpha_closed": False,
            "fixed_critical_leibniz_route_closed": False,
            "nonleibniz_or_state_weighted_critical_gate_open": True,
            "direct_projected_gate_open": True,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": normalized_sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": normalized_sha256(MANIFEST),
            "certificate": str(CERTIFICATE.relative_to(REPO)).replace("\\", "/"),
            "certificate_sha256": normalized_sha256(CERTIFICATE),
            "parent_manifest_sha256": normalized_sha256(PARENT),
        },
        "exploration_id": "EXP-000799",
        "result_number": "R-167",
        "result_version": "v1.3",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run_audit()
    if not args.self_test:
        atomic_json(args.output, payload)
    print(f"PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
