#!/usr/bin/env python3
"""Primary exact verifier for the Q3LOCK second-energy/Cauchy gate split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-second-weighted-energy-cauchy-gate-manifest.json"
CERTIFICATE = REPO / "strategy/pre-a-cp1-st8-q3lock-second-weighted-energy-cauchy-gate-certificate-260810.md"
PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split-manifest.json"
SLUG = "pre-a-cp1-st8-q3lock-second-weighted-energy-cauchy-gate"
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
    """Convert exact symbolic audit values to deterministic JSON values."""
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


def q3_laplacian() -> dict[str, Any]:
    a, b, g, lam = sp.symbols("a b g lambda", real=True)
    edge = lam * (a - b) ** 2 * (a**2 + b**2) / 4
    edge_laplacian = sp.expand(sp.diff(edge, a, 2) + sp.diff(edge, b, 2))
    edges = q3_edges()
    degrees = [sum(vertex in pair for pair in edges) for vertex in range(8)]
    return {
        "edge_laplacian": edge_laplacian,
        "edge_bound_residual": sp.expand(7 * lam * (a**2 + b**2) - edge_laplacian),
        "edges": edges,
        "degrees": degrees,
        "C2": 3 * g + 21 * lam,
    }


def matrix_power_counterexample() -> dict[str, Any]:
    E = sp.diag(1, 3)
    U = sp.Matrix([[sp.Rational(3, 5), -sp.Rational(4, 5)], [sp.Rational(4, 5), sp.Rational(3, 5)]])
    evolved = sp.simplify(U.T * E * U)
    scale = sp.Rational(5, 2)
    first = sp.simplify(scale * E - evolved)
    second = sp.simplify(scale**2 * E**2 - evolved**2)
    return {
        "orthogonal_residual": sp.simplify(U.T * U - sp.eye(2)),
        "evolved": evolved,
        "first": first,
        "first_minor": first[0, 0],
        "first_det": sp.factor(first.det()),
        "second": second,
        "second_det": sp.factor(second.det()),
    }


def polynomial_rung_counterexample() -> dict[str, Any]:
    sqrt_k = sp.diag(1, 2)
    interaction = sp.Matrix([[0, 1], [1, 0]])
    amplitudes: list[sp.Expr] = []
    for rung in range(9):
        operator = sqrt_k**rung * interaction * sqrt_k ** (-(rung + 1))
        amplitudes.append(sp.simplify(operator[1, 0]))
    return {
        "amplitudes": amplitudes,
        "doubling_residuals": [
            sp.simplify(amplitudes[index + 1] - 2 * amplitudes[index])
            for index in range(len(amplitudes) - 1)
        ],
    }


def convexity_weighted_sign_counterexample() -> dict[str, Any]:
    q = sp.diag(0, 1, 2)
    direction = -sp.ones(3)
    first = q * direction - direction * q
    cubic = q**3 * direction - direction * q**3
    weighted = sp.simplify((first.T * cubic + cubic.T * first) / 2)
    witness = sp.Matrix([-2, 2, -1])
    variable = sp.symbols("z")
    return {
        "matrix": weighted,
        "trace": sp.trace(weighted),
        "witness_value": sp.simplify((witness.T * weighted * witness)[0]),
        "characteristic": sp.factor(weighted.charpoly(variable).as_expr()),
    }


def free_word_identity() -> dict[str, int]:
    # Words are tuples in the noncommuting alphabet q,D.  Expand commutators
    # independently of SymPy's simplifier.
    def add(*polys: dict[tuple[str, ...], int]) -> dict[tuple[str, ...], int]:
        out: dict[tuple[str, ...], int] = {}
        for poly in polys:
            for word, coefficient in poly.items():
                out[word] = out.get(word, 0) + coefficient
        return {word: coefficient for word, coefficient in out.items() if coefficient}

    def mul(left: dict[tuple[str, ...], int], right: dict[tuple[str, ...], int]) -> dict[tuple[str, ...], int]:
        out: dict[tuple[str, ...], int] = {}
        for lword, lc in left.items():
            for rword, rc in right.items():
                word = lword + rword
                out[word] = out.get(word, 0) + lc * rc
        return out

    def scale(poly: dict[tuple[str, ...], int], coefficient: int) -> dict[tuple[str, ...], int]:
        return {word: coefficient * value for word, value in poly.items()}

    q = {("q",): 1}
    d = {("D",): 1}
    q2 = mul(q, q)
    q3 = mul(q2, q)

    def comm(left: dict[tuple[str, ...], int], right: dict[tuple[str, ...], int]) -> dict[tuple[str, ...], int]:
        return add(mul(left, right), scale(mul(right, left), -1))

    c1 = comm(q, d)
    c2 = comm(q, c1)
    c3 = comm(q, c2)
    lhs = comm(q3, d)
    rhs = add(scale(mul(c1, q2), 3), scale(mul(c2, q), 3), c3)
    residual = add(lhs, scale(rhs, -1))
    return {"lhs_terms": len(lhs), "rhs_terms": len(rhs), "residual_terms": len(residual)}


def fixture_constants() -> dict[str, Any]:
    # Inputs only.  The exponential ratio R=exp(mu) is represented exactly.
    g = sp.Rational(2)
    lam = sp.Rational(1, 3)
    c = sp.Rational(3, 2)
    chi = sp.Rational(5, 4)
    hbar = sp.Rational(1)
    gamma = sp.Rational(1, 32)
    ratio = sp.Rational(3, 2)
    theta = ratio - 1
    z = sp.Rational(6)
    epsilon = sp.Rational(1, 10)
    s_f = sp.Rational(7)
    r_plus = sp.Rational(0)
    c2 = 3 * g + 21 * lam
    bracket = c2 * epsilon + s_f * (8 * r_plus + 8 * c * z + c2 / (4 * epsilon * gamma))
    m_squared = sp.simplify(theta**2 * (c * z / chi) * (1 + hbar**2 * bracket / (2 * chi)))
    v_squared = sp.simplify(36 * c * theta**2 / (2 * chi))
    return {
        "g": g,
        "lambda": lam,
        "c": c,
        "chi": chi,
        "hbar": hbar,
        "gamma": gamma,
        "ratio": ratio,
        "theta": theta,
        "z": z,
        "epsilon": epsilon,
        "S_f": s_f,
        "C2": c2,
        "laplacian_bracket": sp.simplify(bracket),
        "M_mu_squared": m_squared,
        "v_mu_squared": v_squared,
        "gamma_admitted": gamma < g / 32,
    }


def run() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")

    audit.check("manifest schema", manifest["schema"] == "tect/pre-a-route-split/1.0", manifest["schema"], "tect/pre-a-route-split/1.0", "provenance")
    audit.check("parent EXP-000792", "EXP-000792" in manifest["parent_explorations"], manifest["parent_explorations"], "contains EXP-000792", "provenance")
    audit.check("parent result reused", parent["result_id"] in certificate, parent["result_id"] in certificate, True, "provenance")
    audit.check("certificate result id", manifest["result_id"] in certificate, manifest["result_id"] in certificate, True, "provenance")

    q3 = q3_laplacian()
    audit.check("Q3 edge count", len(q3["edges"]) == 12, len(q3["edges"]), 12, "Q3")
    audit.check("Q3 degree", q3["degrees"] == [3] * 8, q3["degrees"], [3] * 8, "Q3")
    a, b, lam = sp.symbols("a b lambda", real=True)
    expected_edge_laplacian = lam * (4 * a**2 - 6 * a * b + 4 * b**2)
    audit.check("edge Laplacian", sp.expand(q3["edge_laplacian"] - expected_edge_laplacian) == 0, str(q3["edge_laplacian"]), str(expected_edge_laplacian), "Q3")
    sos_expected = 3 * lam * (a + b) ** 2
    audit.check("edge Laplacian bound SOS", sp.expand(q3["edge_bound_residual"] - sos_expected) == 0, str(q3["edge_bound_residual"]), str(sos_expected), "Q3")
    audit.check("Q3 Laplacian coefficient", str(q3["C2"]) == "3*g + 21*lambda", str(q3["C2"]), "3*g + 21*lambda", "Q3")

    fixture = fixture_constants()
    audit.check("fixture gamma admitted", bool(fixture["gamma_admitted"]), fixture["gamma"], "< g/32", "moment")
    audit.check("fixture C2 derived", fixture["C2"] == 13, str(fixture["C2"]), "13", "moment")
    audit.check("fixture theta derived", fixture["theta"] == sp.Rational(1, 2), str(fixture["theta"]), "1/2", "moment")
    audit.check("M squared positive", fixture["M_mu_squared"] > 0, str(fixture["M_mu_squared"]), ">0", "moment")
    audit.check("first rate positive", fixture["v_mu_squared"] > 0, str(fixture["v_mu_squared"]), ">0", "moment")
    audit.check("manifest C2", manifest["second_moment"]["q3_laplacian"].endswith("C2=3g+21lambda"), manifest["second_moment"]["q3_laplacian"], "C2=3g+21lambda", "moment")
    audit.check("one-sided derivative", "||B_f A^-1||=||A^-1 B_f||<=M_mu" in manifest["second_moment"]["conclusion"], manifest["second_moment"]["conclusion"], "two orientations", "moment")
    audit.check("second moment exponent", "exp(2M_mu|t|)" in manifest["second_moment"]["conclusion"], manifest["second_moment"]["conclusion"], "2M_mu", "moment")

    matrix = matrix_power_counterexample()
    audit.check("counterexample unitary", matrix["orthogonal_residual"] == sp.zeros(2), str(matrix["orthogonal_residual"]), "zero", "ordering")
    audit.check("first order leading minor", matrix["first_minor"] == sp.Rational(11, 50), str(matrix["first_minor"]), "11/50", "ordering")
    audit.check("first order determinant", matrix["first_det"] == sp.Rational(7, 20), str(matrix["first_det"]), "7/20", "ordering")
    audit.check("squared order determinant", matrix["second_det"] == -sp.Rational(127, 16), str(matrix["second_det"]), "-127/16", "ordering")

    audit.check("cubic one-sided power-count target", "s>=3/4" in manifest["fractional_graph_domain"]["sharp_power_count"], manifest["fractional_graph_domain"]["sharp_power_count"], "necessary scalar target s>=3/4", "graph")
    audit.check("cubic symmetric power-count target", "s>=3/8" in manifest["fractional_graph_domain"]["sharp_power_count"], manifest["fractional_graph_domain"]["sharp_power_count"], "necessary scalar target s>=3/8", "graph")
    audit.check("cubic multiplier embedding remains open", manifest["fractional_graph_domain"]["cubic_multiplier_closed"] is False and "neither follows" in manifest["fractional_graph_domain"]["cubic_multiplier_open_obligation"], manifest["fractional_graph_domain"], "cubic_multiplier_closed=false with open embedding obligation", "scope")
    audit.check("three-half moment", "A^(3/2)" in manifest["fractional_graph_domain"]["three_half_moment"], manifest["fractional_graph_domain"]["three_half_moment"], "A^(3/2)", "graph")
    audit.check("position multiplier", "gamma^(-1/4)+hbar/sqrt(2chi)" in manifest["fractional_graph_domain"]["position_multiplier"], manifest["fractional_graph_domain"]["position_multiplier"], "Q0", "graph")

    words = free_word_identity()
    audit.check("cubic commutator identity", words["residual_terms"] == 0, words, {"residual_terms": 0}, "ladder")
    audit.check("infinite ladder gate", manifest["open_commutator_gate"]["gate_id"].endswith("GEVREY-LR-CLOSURE"), manifest["open_commutator_gate"]["gate_id"], "GEVREY-LR-CLOSURE", "ladder")
    rung = polynomial_rung_counterexample()
    audit.check("rung amplitudes exponential", rung["amplitudes"] == [sp.Integer(2) ** index for index in range(9)], rung["amplitudes"], "2^j", "ladder")
    audit.check("rung exact doubling", rung["doubling_residuals"] == [0] * 8, rung["doubling_residuals"], "zero", "ladder")
    audit.check("separate-rung route rejected", "no C(j+1)^alpha" in manifest["open_commutator_gate"]["rejected_separate_rung"], manifest["open_commutator_gate"]["rejected_separate_rung"], "polynomial no-go", "ladder")
    audit.check("product-level replacement retained", "product-level Volterra" in manifest["open_commutator_gate"]["replacement_targets"], manifest["open_commutator_gate"]["replacement_targets"], "product-level Volterra", "ladder")
    audit.check("Gevrey boundaries complete", len(manifest["open_commutator_gate"]["gevrey_boundaries"]) == 4, len(manifest["open_commutator_gate"]["gevrey_boundaries"]), 4, "ladder")

    convex = convexity_weighted_sign_counterexample()
    expected_convex = sp.Matrix([[17, 11, -4], [11, 8, 5], [-4, 5, 23]])
    audit.check("convex weighted matrix", convex["matrix"] == expected_convex, convex["matrix"], expected_convex, "convexity")
    audit.check("convex weighted trace", convex["trace"] == 48, convex["trace"], 48, "convexity")
    audit.check("convex weighted negative witness", convex["witness_value"] == -1, convex["witness_value"], -1, "convexity")
    audit.check("convex weighted characteristic", convex["characteristic"] == (sp.symbols("z") - 24) * (sp.symbols("z") ** 2 - 24 * sp.symbols("z") - 27), convex["characteristic"], "(z-24)(z^2-24z-27)", "convexity")

    audit.check("Cauchy spatial condition", manifest["conditional_cauchy"]["spatial_condition"] == "rho>mu/4", manifest["conditional_cauchy"]["spatial_condition"], "rho>mu/4", "cauchy")
    audit.check("Cauchy two orientations", "both one-sided" in manifest["conditional_cauchy"]["conclusion"], manifest["conditional_cauchy"]["conclusion"], "both one-sided", "cauchy")
    audit.check("C-star boundary retained", "still required" in manifest["conditional_cauchy"]["cstar_boundary"], manifest["conditional_cauchy"]["cstar_boundary"], "still required", "scope")
    audit.check("symmetric topology formula", "(n+1)^(-s)" in manifest["exact_counterexamples"]["symmetric_topology"], manifest["exact_counterexamples"]["symmetric_topology"], "(n+1)^(-s)", "topology")

    for token in (
        "common alpha",
        "common-alpha KMS",
        "algebraic ground states",
        "GNS",
        "regulator removal",
        "physical empty space",
        "C6",
        "CP1",
        "Sector A",
        "Pre-A",
    ):
        audit.check(f"no-overclaim {token}", token in manifest["no_overclaim"], manifest["no_overclaim"], f"contains {token}", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/pre-a-cp1-st8-q3lock-second-weighted-energy-cauchy-gate-primary-result/1.0",
        "script_version": __version__,
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "derived": {
            "Q3_edges": len(q3["edges"]),
            "Q3_degrees": q3["degrees"],
            "edge_laplacian": str(q3["edge_laplacian"]),
            "C2_fixture": str(fixture["C2"]),
            "M_mu_squared_fixture": str(fixture["M_mu_squared"]),
            "v_mu_squared_fixture": str(fixture["v_mu_squared"]),
            "first_order_det": str(matrix["first_det"]),
            "squared_order_det": str(matrix["second_det"]),
            "cubic_identity_residual_terms": words["residual_terms"],
            "rung_amplitudes": [str(value) for value in rung["amplitudes"]],
            "convex_weighted_trace": str(convex["trace"]),
            "convex_weighted_witness": str(convex["witness_value"]),
            "cubic_power_count_target": "3/4",
            "symmetric_cubic_power_count_target": "3/8",
            "cubic_multiplier_closed": False,
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
