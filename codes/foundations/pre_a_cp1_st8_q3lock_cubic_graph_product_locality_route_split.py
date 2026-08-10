#!/usr/bin/env python3
"""Primary exact verifier for the Q3LOCK cubic-graph/product-locality split."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from itertools import combinations, product
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-cubic-graph-product-locality-route-split-manifest.json"
CERTIFICATE = REPO / "strategy/pre-a-cp1-st8-q3lock-cubic-graph-product-locality-route-split-certificate-260810.md"
PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-second-weighted-energy-cauchy-gate-manifest.json"
SLUG = "pre-a-cp1-st8-q3lock-cubic-graph-product-locality-route-split"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-10-primary-{SLUG}/result.json"


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return str(value)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
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


def q3_edges() -> list[tuple[int, int]]:
    vertices = list(product((0, 1), repeat=3))
    return [
        (left, right)
        for left, right in combinations(range(8), 2)
        if sum(a != b for a, b in zip(vertices[left], vertices[right])) == 1
    ]


def q3_force_audit() -> dict[str, Any]:
    a, b, g, lam = sp.symbols("a b g lambda", nonnegative=True)
    edge = lam * (a - b) ** 2 * (a**2 + b**2) / 4
    derivative = sp.expand(sp.diff(edge, a))
    coefficient_l1 = sum(abs(sp.Rational(term)) for term in (1, -sp.Rational(3, 2), 1, -sp.Rational(1, 2)))
    edges = q3_edges()
    degrees = [sum(vertex in edge_pair for edge_pair in edges) for vertex in range(8)]
    component_coefficient = g + max(degrees) * coefficient_l1 * lam
    return {
        "edges": edges,
        "degrees": degrees,
        "derivative": derivative,
        "edge_coefficient_l1": coefficient_l1,
        "component_coefficient": component_coefficient,
        "full_gradient_square_factor": len(degrees),
    }


def graph_fixture() -> dict[str, Any]:
    # Declared exact inputs.
    chi = sp.Rational(2)
    c = sp.Rational(3, 2)
    g = sp.Rational(5)
    lam = sp.Rational(2)
    hbar = sp.Rational(1)
    gamma = sp.Rational(1, 10)
    r_plus = sp.Rational(1)
    z = sp.Rational(6)
    exp_mu = sp.Rational(2)
    support_size = sp.Rational(1)

    c2 = 3 * g + 21 * lam
    epsilon_star = 4 * chi / (hbar**2 * c2)
    exp_minus_mu = 1 / exp_mu
    s_bound = support_size * ((1 + exp_minus_mu) / (1 - exp_minus_mu)) ** 3
    b_star = s_bound * (8 * r_plus + 8 * c * z + hbar**2 * c2**2 / (16 * chi * gamma))
    beta_star = hbar**2 * b_star / (2 * chi)
    kappa_squared = sp.Max(1, beta_star)
    theta = exp_mu - 1
    center_constant = 1 + 2 * theta * (1 + sp.sqrt(kappa_squared))
    # The eighth power removes all quarter powers from the cubic constant.
    cubic_constant_eighth = sp.simplify(gamma ** -6 * kappa_squared**3)
    return {
        "inputs": {
            "chi": chi,
            "c": c,
            "g": g,
            "lambda": lam,
            "hbar": hbar,
            "gamma": gamma,
            "r_plus": r_plus,
            "z": z,
            "exp_mu": exp_mu,
            "support_size": support_size,
        },
        "C2": c2,
        "epsilon_star": epsilon_star,
        "S_bound": s_bound,
        "b_star": sp.simplify(b_star),
        "beta_star": sp.simplify(beta_star),
        "kappa_squared": kappa_squared,
        "cubic_constant_eighth": cubic_constant_eighth,
        "center_constant": center_constant,
        "gamma_admitted": gamma < g / 32,
        "cancellation_coefficient": sp.simplify(hbar**2 * c2 * epsilon_star / (2 * chi)),
    }


def moving_bump_limit() -> dict[str, Any]:
    r = sp.symbols("R", positive=True)
    f, c1 = sp.symbols("f C1", positive=True)
    c0 = sp.symbols("C0", nonnegative=True)
    ratio = (r - 1) ** 3 / (c0 + c1 * f * r**4) ** sp.Rational(3, 4)
    limit = sp.simplify(sp.limit(ratio, r, sp.oo))
    expected = c1 ** (-sp.Rational(3, 4)) * f ** (-sp.Rational(3, 4))
    return {"ratio": ratio, "limit": limit, "expected": expected}


def heat_simplex_audit() -> dict[str, Any]:
    beta, b = sp.symbols("beta b", positive=True)
    rows: list[dict[str, Any]] = []
    for n in range(1, 9):
        dirichlet = sp.simplify(sp.gamma(sp.Rational(1, 2)) ** n * beta ** sp.Rational(n, 2) / sp.gamma(1 + sp.Rational(n, 2)))
        word = sp.simplify(b**n * (2 * sp.E) ** (-sp.Rational(n, 2)) * dirichlet)
        closed = sp.simplify((b * sp.sqrt(sp.pi / (2 * sp.E)) * sp.sqrt(beta)) ** n / sp.gamma(1 + sp.Rational(n, 2)))
        rows.append({"n": n, "dirichlet": dirichlet, "word": word, "closed": closed, "residual": sp.simplify(word - closed)})

    c, gamma = sp.symbols("c gamma", positive=True)
    base_rung = c / sp.sqrt(2 * gamma)
    commutator_activity = sp.simplify(2 * base_rung * sp.sqrt(sp.pi / (2 * sp.E)))
    return {
        "rows": rows,
        "base_rung": base_rung,
        "commutator_activity": commutator_activity,
        "n1_dirichlet": rows[0]["dirichlet"],
        "n2_dirichlet": rows[1]["dirichlet"],
    }


def animal_audit() -> dict[str, Any]:
    sample_m = (2, 4, 8, 16)
    log_ratios = [math.lgamma(4 * m + 1) - math.lgamma(1 + 5 * m / 2) for m in sample_m]
    # Stirling coefficients of m log(m): 4 from (4m)! and 5/2 from Gamma(1+5m/2).
    leading_coefficient = sp.Rational(4) - sp.Rational(5, 2)
    return {
        "sample_m": list(sample_m),
        "edge_counts": [5 * m for m in sample_m],
        "legal_leaf_orders": [math.factorial(4 * m) for m in sample_m],
        "log_ratios": log_ratios,
        "strictly_increasing": all(right > left for left, right in zip(log_ratios, log_ratios[1:])),
        "stirling_m_log_m_coefficient": leading_coefficient,
    }


def strip_and_real_time_audit() -> dict[str, Any]:
    z = sp.Integer(6)
    path_degree = 2 * z - 1
    rho, g_response, hbar = sp.symbols("rho G hbar", positive=True)
    velocity = sp.simplify(path_degree**2 * g_response**2 * sp.exp(2 * rho) / (rho * hbar))

    epsilon, c_strip, s = sp.symbols("epsilon C s", positive=True)
    log_integrand = (s - 1) * sp.log(epsilon) + c_strip / epsilon
    divergence_witness = sp.limit(log_integrand, epsilon, 0, dir="+")
    return {
        "path_degree": path_degree,
        "velocity": velocity,
        "strip_log_integrand": log_integrand,
        "strip_log_limit": divergence_witness,
    }


def equilibrium_scale_audit() -> dict[str, Any]:
    # Declared discriminating fixture: the smallest integer p>d+1 in d=3.
    dimension = sp.Integer(3)
    moment = sp.Integer(5)
    exponent_b = sp.Rational(7, 4)
    lower = sp.simplify(2 * dimension / (moment - 1))
    leakage_exponent = sp.simplify(dimension + exponent_b * (1 - moment) / 2)
    factorial_m_log_m = sp.simplify(exponent_b / 2 - 1)
    return {
        "dimension": dimension,
        "moment": moment,
        "b": exponent_b,
        "lower": lower,
        "upper": sp.Integer(2),
        "interval_admitted": lower < exponent_b < 2,
        "leakage_exponent": leakage_exponent,
        "factorial_m_log_m": factorial_m_log_m,
        "nonempty_symbolic_condition": "p>d+1",
    }


def duhamel_audit() -> dict[str, Any]:
    # exp(-beta)=1/2 is an input. Work with beta times the squared Duhamel norm,
    # which is exact rational arithmetic.
    boltzmann = sp.Rational(1, 2)
    p0 = 1 - boltzmann
    rows: list[dict[str, Any]] = []
    for n in range(1, 33):
        pn = p0 * boltzmann**n
        beta_times_duhamel_squared = sp.simplify((p0 - pn) / n)
        symmetric_gns_squared = sp.simplify((p0 + pn) / 2)
        rows.append(
            {
                "n": n,
                "p_n": pn,
                "beta_times_duhamel_squared": beta_times_duhamel_squared,
                "symmetric_gns_squared": symmetric_gns_squared,
            }
        )

    x = sp.symbols("x", positive=True)
    arithmetic_over_log_mean = sp.simplify(x * (1 + sp.exp(-x)) / (2 * (1 - sp.exp(-x))))
    bandwidth_factor = sp.simplify(x * sp.coth(x / 2) / 2)
    return {
        "rows": rows,
        "duhamel_decreasing": all(
            rows[index + 1]["beta_times_duhamel_squared"] < rows[index]["beta_times_duhamel_squared"]
            for index in range(len(rows) - 1)
        ),
        "symmetric_lower_bound": p0 / 2,
        "arithmetic_over_log_mean": arithmetic_over_log_mean,
        "bandwidth_factor": bandwidth_factor,
        "bandwidth_residual": sp.simplify(arithmetic_over_log_mean - bandwidth_factor),
    }


def run() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")

    audit.check("manifest schema", manifest["schema"] == "tect/pre-a-route-split/1.0", manifest["schema"], "tect/pre-a-route-split/1.0", "provenance")
    audit.check("result number reused", manifest["result_number"] == "R-167", manifest["result_number"], "R-167", "provenance")
    audit.check("result id reused", manifest["result_id"] == parent["result_id"], manifest["result_id"], parent["result_id"], "provenance")
    audit.check("version strengthened", manifest["result_version"] == "v1.1", manifest["result_version"], "v1.1", "provenance")
    audit.check("exploration linkage", manifest["exploration_id"] == "EXP-000796", manifest["exploration_id"], "EXP-000796", "provenance")
    audit.check("certificate result", manifest["result_id"] in certificate and "v1.1" in certificate, manifest["result_id"] in certificate, True, "provenance")
    audit.check("four exact negatives", len(manifest["negative_ids"]) == 4, len(manifest["negative_ids"]), 4, "provenance")

    q3 = q3_force_audit()
    audit.check("Q3 edge count", len(q3["edges"]) == 12, len(q3["edges"]), 12, "Q3")
    audit.check("Q3 degree", q3["degrees"] == [3] * 8, q3["degrees"], [3] * 8, "Q3")
    a, b, lam = sp.symbols("a b lambda", nonnegative=True)
    expected_derivative = lam * (a**3 - sp.Rational(3, 2) * a**2 * b + a * b**2 - sp.Rational(1, 2) * b**3)
    audit.check("Q3 edge derivative", sp.expand(q3["derivative"] - expected_derivative) == 0, q3["derivative"], expected_derivative, "Q3")
    audit.check("Q3 edge L1 coefficient", q3["edge_coefficient_l1"] == 4, q3["edge_coefficient_l1"], 4, "Q3")
    audit.check("Q3 component force", str(q3["component_coefficient"]) == "g + 12*lambda", q3["component_coefficient"], "g+12lambda", "Q3")
    audit.check("Q3 full gradient factor", q3["full_gradient_square_factor"] == 8, q3["full_gradient_square_factor"], 8, "Q3")

    graph = graph_fixture()
    audit.check("graph gamma admitted", bool(graph["gamma_admitted"]), graph["inputs"]["gamma"], "<g/32", "graph")
    audit.check("Laplacian cancellation", graph["cancellation_coefficient"] == 2, graph["cancellation_coefficient"], 2, "graph")
    audit.check("graph beta positive", graph["beta_star"] > 0, graph["beta_star"], ">0", "graph")
    audit.check("cubic constant positive", graph["cubic_constant_eighth"] > 0, graph["cubic_constant_eighth"], ">0", "graph")
    audit.check("center comparison positive", graph["center_constant"] > 1, graph["center_constant"], ">1", "graph")
    audit.check("manifest cubic closed", manifest["cubic_graph_embedding"]["closed"] is True, manifest["cubic_graph_embedding"]["closed"], True, "graph")
    audit.check("manifest graph operator", "||U_f A^-1||<=kappa" in manifest["cubic_graph_embedding"]["operator_bound"], manifest["cubic_graph_embedding"]["operator_bound"], "UA^-1", "graph")
    audit.check("manifest natural powers", "0<=m<=4" in manifest["cubic_graph_embedding"]["all_natural_powers"], manifest["cubic_graph_embedding"]["all_natural_powers"], "0<=m<=4", "graph")
    audit.check("manifest force coefficient", "g+12lambda" in manifest["cubic_graph_embedding"]["q3_force"], manifest["cubic_graph_embedding"]["q3_force"], "g+12lambda", "graph")
    audit.check("moving center theorem", "C_mu=1+2(exp(mu)-1)(1+kappa)" in manifest["moving_center_comparison"]["neighbor_bound"], manifest["moving_center_comparison"]["neighbor_bound"], "C_mu formula", "graph")

    bump = moving_bump_limit()
    audit.check("moving bump exact limit", sp.simplify(bump["limit"] - bump["expected"]) == 0, bump["limit"], bump["expected"], "boundary")
    audit.check("moving-site negative registered", manifest["negative_ids"][0].endswith("UNWEIGHTED-MOVING-SITE-CUBIC-GRAPH-UNIFORMITY"), manifest["negative_ids"][0], "moving-site negative", "boundary")
    audit.check("fixed-site not rejected", "fixed x" in manifest["moving_site_boundary"]["does_not_show"], manifest["moving_site_boundary"]["does_not_show"], "fixed x remains possible", "scope")

    heat = heat_simplex_audit()
    audit.check("heat rows residual", all(row["residual"] == 0 for row in heat["rows"]), [row["residual"] for row in heat["rows"]], "all zero", "heat")
    beta = sp.symbols("beta", positive=True)
    audit.check("heat n=1 Dirichlet", sp.simplify(heat["n1_dirichlet"] - 2 * sp.sqrt(beta)) == 0, heat["n1_dirichlet"], "2sqrt(beta)", "heat")
    audit.check("heat n=2 Dirichlet", sp.simplify(heat["n2_dirichlet"] - sp.pi * beta) == 0, heat["n2_dirichlet"], "pi beta", "heat")
    c, gamma = sp.symbols("c gamma", positive=True)
    audit.check("Q3 base rung", sp.simplify(heat["base_rung"] - c / sp.sqrt(2 * gamma)) == 0, heat["base_rung"], "c/sqrt(2gamma)", "heat")
    audit.check("commutator activity", sp.simplify(heat["commutator_activity"] - c * sp.sqrt(sp.pi / (sp.E * gamma))) == 0, heat["commutator_activity"], "c sqrt(pi/(e gamma))", "heat")
    audit.check("prescribed-word scope", manifest["heat_simplex"]["status"].startswith("PROVED FOR EACH PRESCRIBED WORD"), manifest["heat_simplex"]["status"], "prescribed word only", "scope")

    animal = animal_audit()
    audit.check("animal edge ledger", animal["edge_counts"] == [5 * m for m in animal["sample_m"]], animal["edge_counts"], "5m", "animal")
    audit.check("animal histories factorial", animal["legal_leaf_orders"] == [math.factorial(4 * m) for m in animal["sample_m"]], animal["legal_leaf_orders"], "(4m)!", "animal")
    audit.check("animal logs grow", animal["strictly_increasing"], animal["log_ratios"], "strictly increasing", "animal")
    audit.check("animal Stirling coefficient", animal["stirling_m_log_m_coefficient"] == sp.Rational(3, 2), animal["stirling_m_log_m_coefficient"], "3/2", "animal")
    audit.check("animal route scope", "proof methods" not in manifest["absolute_route_obstructions"]["scope"] and "not nonexistence" in manifest["absolute_route_obstructions"]["scope"], manifest["absolute_route_obstructions"]["scope"], "method-only no-go", "scope")

    strip = strip_and_real_time_audit()
    audit.check("chain degree", strip["path_degree"] == 11, strip["path_degree"], 11, "strip")
    audit.check("strip nonintegrable log", strip["strip_log_limit"] == sp.oo, strip["strip_log_limit"], "infinity", "strip")
    audit.check("velocity positive", strip["velocity"].is_positive is True, strip["velocity"], ">0", "real-time")
    audit.check("RT product remains open", manifest["conditional_real_time_product"]["status"] == "OPEN", manifest["conditional_real_time_product"]["status"], "OPEN", "scope")
    audit.check("RT denominator", "Gamma(1+n/2)" in manifest["conditional_real_time_product"]["response_target"], manifest["conditional_real_time_product"]["response_target"], "Gamma(1+n/2)", "real-time")
    audit.check("RT spatial condition inherited", "rho>mu/4" in manifest["conditional_real_time_product"]["downstream"], manifest["conditional_real_time_product"]["downstream"], "rho>mu/4", "real-time")

    equilibrium = equilibrium_scale_audit()
    audit.check("equilibrium b interval", bool(equilibrium["interval_admitted"]), equilibrium, "2d/(p-1)<b<2", "equilibrium")
    audit.check("equilibrium leakage exponent", equilibrium["leakage_exponent"] == -sp.Rational(1, 2), equilibrium["leakage_exponent"], "-1/2", "equilibrium")
    audit.check("equilibrium factorial exponent", equilibrium["factorial_m_log_m"] == -sp.Rational(1, 8), equilibrium["factorial_m_log_m"], "-1/8", "equilibrium")
    audit.check("moment alone rejected", "alone do not prove" in manifest["equilibrium_cutoff_alternative"]["topology_requirement"], manifest["equilibrium_cutoff_alternative"]["topology_requirement"], "moment alone insufficient", "scope")
    audit.check("modular cutoff gate open", manifest["equilibrium_cutoff_alternative"]["status"] == "OPEN" and "MODULAR-CUTOFF-LOCALITY" in manifest["equilibrium_cutoff_alternative"]["gate_id"], manifest["equilibrium_cutoff_alternative"], "open modular cutoff gate", "scope")

    duhamel = duhamel_audit()
    audit.check("Duhamel squares decrease", duhamel["duhamel_decreasing"], [row["beta_times_duhamel_squared"] for row in duhamel["rows"][:6]], "decreasing", "topology")
    audit.check("symmetric GNS survives", all(row["symmetric_gns_squared"] > duhamel["symmetric_lower_bound"] for row in duhamel["rows"]), duhamel["symmetric_lower_bound"], "positive lower limit", "topology")
    audit.check("modular bandwidth identity", duhamel["bandwidth_residual"] == 0, duhamel["bandwidth_residual"], 0, "topology")
    audit.check("Duhamel squared wording", manifest["duhamel_topology_counterexample"]["duhamel"].startswith("The squared Duhamel norms"), manifest["duhamel_topology_counterexample"]["duhamel"], "squared norm", "scope")
    audit.check("Duhamel does not reject KMS", "itself is not rejected" in manifest["duhamel_topology_counterexample"]["scope"], manifest["duhamel_topology_counterexample"]["scope"], "KMS route retained", "scope")

    for token in (
        "first-passage RT-PV",
        "spatial commutator",
        "fifth onsite-energy moment",
        "common C-star alpha",
        "common-alpha KMS",
        "algebraic ground states",
        "GNS",
        "continuum",
        "physical empty space",
        "C6",
        "CP1",
        "Sector A",
        "Pre-A",
    ):
        audit.check(f"no-overclaim {token}", token in manifest["no_overclaim"], manifest["no_overclaim"], f"contains {token}", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/pre-a-cp1-st8-q3lock-cubic-graph-product-locality-route-split-primary-result/1.0",
        "script_version": __version__,
        "result_id": manifest["result_id"],
        "result_version": manifest["result_version"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "derived": {
            "Q3_edges": len(q3["edges"]),
            "Q3_degrees": q3["degrees"],
            "Q3_force_component_coefficient": str(q3["component_coefficient"]),
            "C2_fixture": str(graph["C2"]),
            "epsilon_star_fixture": str(graph["epsilon_star"]),
            "S_bound_fixture": str(graph["S_bound"]),
            "b_star_fixture": str(graph["b_star"]),
            "beta_star_fixture": str(graph["beta_star"]),
            "cubic_constant_eighth_fixture": str(graph["cubic_constant_eighth"]),
            "center_constant_fixture": str(graph["center_constant"]),
            "moving_bump_limit": str(bump["limit"]),
            "heat_n1_dirichlet": str(heat["n1_dirichlet"]),
            "heat_n2_dirichlet": str(heat["n2_dirichlet"]),
            "commutator_activity": str(heat["commutator_activity"]),
            "animal_log_ratios": animal["log_ratios"],
            "animal_stirling_coefficient": str(animal["stirling_m_log_m_coefficient"]),
            "chain_degree": int(strip["path_degree"]),
            "velocity": str(strip["velocity"]),
            "cutoff_leakage_exponent": str(equilibrium["leakage_exponent"]),
            "cutoff_factorial_exponent": str(equilibrium["factorial_m_log_m"]),
            "duhamel_first_rows": json_safe(duhamel["rows"][:6]),
            "cubic_graph_embedding_closed": True,
            "first_passage_real_time_product_closed": False,
            "fifth_energy_modular_cutoff_closed": False,
            "common_alpha_closed": False,
        },
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (SCRIPT, MANIFEST, CERTIFICATE, PARENT)
        },
        "assertions": audit.rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output, payload)
    summary = payload["summary"]
    print(f"PASS {summary['passed']}/{summary['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
