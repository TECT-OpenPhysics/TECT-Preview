#!/usr/bin/env python3
"""Primary algebra and normalization verifier for EXP-000789.

The analytic proof is the certificate.  This executable recomputes all
finite constants and polynomial identities used by that proof, including
hostile convention mutations.  It is not a numerical proof of an
infinite-volume state, KMS reconstruction, or a continuum limit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np
import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-ground-equal-time-order-gap-continuum-counterterm-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-GROUND-EQUAL-TIME-ORDER-GAP-CONTINUUM-COUNTERTERM-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-GROUND-EQUAL-TIME-LRO-APPROXIMATE-DOUBLETS-FULL-GAP-COLLAPSE-AND-CONTINUUM-BASIS-OBSTRUCTION"
EXPLORATION_ID = "EXP-000789"
PARENT_GATE = "PA-CP1-ST8-Q3LOCK-INFINITE-VOLUME-DYNAMICS-KMS-GROUND-AND-CONTINUUM-SPLIT"
NEGATIVE_IDS = (
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-UNIFORM-FULL-FINITE-VOLUME-SPECTRAL-GAP",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-G-LAMBDA-ONLY-4D-ONE-LOOP-CLOSURE",
)
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260809.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-st8-q3lock-positive-lambda-fkg-infrared-cusp-phase-route-split/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-primary-{SLUG}/result.json"

# Clearly labelled regression oracles, never theorem inputs.
TEST_ORACLE_I3 = 0.505462019717326006
TEST_ORACLE_J3 = 0.643953733381468096
TEST_ORACLE_J3_L64 = 0.6437978349352834


def portable_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def cube_vertices() -> list[tuple[int, int, int]]:
    return [(a, b, c) for a in range(2) for b in range(2) for c in range(2)]


def cube_edges() -> list[tuple[int, int]]:
    vertices = cube_vertices()
    return [
        (left, right)
        for left in range(8)
        for right in range(left + 1, 8)
        if sum(a != b for a, b in zip(vertices[left], vertices[right])) == 1
    ]


def finite_half_watson(length: int) -> float:
    cosine = np.cos(2.0 * math.pi * np.arange(length) / length)
    energy = 3.0 - cosine[:, None, None] - cosine[None, :, None] - cosine[None, None, :]
    energy[0, 0, 0] = np.inf
    return float(np.sum(1.0 / np.sqrt(energy)) / length**3)


def finite_watson(length: int) -> float:
    cosine = np.cos(2.0 * math.pi * np.arange(length) / length)
    energy = 3.0 - cosine[:, None, None] - cosine[None, :, None] - cosine[None, None, :]
    energy[0, 0, 0] = np.inf
    return float(np.sum(1.0 / energy) / length**3)


def falk_upper(duhamel: float, commutator: float) -> float:
    argument = 0.5 * math.sqrt(commutator / duhamel)
    return 0.5 * math.sqrt(duhamel * commutator) / math.tanh(argument)


def x_from_t(value: float) -> float:
    low, high = 0.0, max(1.0, value + 1.0)
    for _ in range(160):
        middle = (low + high) / 2.0
        if middle * math.tanh(middle) < value:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("parent gate", manifest["gate_resolution"]["parent_gate"] == PARENT_GATE, manifest["gate_resolution"]["parent_gate"], PARENT_GATE, "identity")
    audit.check("next gate retained", manifest["gate_resolution"]["next_gate"] == PARENT_GATE, manifest["gate_resolution"]["next_gate"], PARENT_GATE, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    parent_summary = {key: parent["assertions"][key] for key in ("passed", "total")}
    audit.check("parent passes", parent["verdict"] == "PASS" and parent_summary["passed"] == parent_summary["total"], parent_summary, "all pass", "parent")
    audit.check("parent EXP782", parent["exploration_id"] == "EXP-000782", parent["exploration_id"], "EXP-000782", "parent")

    mp.mp.dps = 45
    watson_mp = mp.quad(lambda t: mp.e ** (-3 * t) * mp.besseli(0, t) ** 3, [0, 1, mp.inf])
    half_watson_mp = mp.quad(
        lambda t: t ** (-mp.mpf("0.5")) * mp.e ** (-3 * t) * mp.besseli(0, t) ** 3 / mp.sqrt(mp.pi),
        [0, 1, mp.inf],
    )
    watson = float(watson_mp)
    half_watson = float(half_watson_mp)
    audit.check("I3 Bessel oracle", abs(watson - TEST_ORACLE_I3) < 5e-15, watson, TEST_ORACLE_I3, "watson")
    audit.check("J3 Bessel oracle", abs(half_watson - TEST_ORACLE_J3) < 5e-15, half_watson, TEST_ORACLE_J3, "watson")
    audit.check("normalized Cauchy strict", half_watson**2 < watson, half_watson**2, watson, "watson")
    audit.check("threshold interval nonempty", half_watson**2 < watson, (half_watson**2, watson), "J3^2<I3", "watson")
    finite_rows: list[dict[str, float]] = []
    for length in (8, 16, 32, 64):
        j_value = finite_half_watson(length)
        i_value = finite_watson(length)
        finite_rows.append({"L": length, "J3_L": j_value, "I3_L": i_value})
        audit.check("finite normalized Cauchy", j_value**2 <= i_value + 1e-14, j_value**2, i_value, "watson")
    audit.check("J3 finite oracle", abs(finite_rows[-1]["J3_L"] - TEST_ORACLE_J3_L64) < 2e-14, finite_rows[-1]["J3_L"], TEST_ORACLE_J3_L64, "watson")
    audit.check("J3 finite convergence", abs(finite_rows[-1]["J3_L"] - half_watson) < 2e-4, finite_rows[-1]["J3_L"], half_watson, "watson")

    for beta, hbar, chi, omega in ((2.0, 3.0, 5.0, 0.7), (0.4, 1.2, 0.8, 2.1), (7.0, 0.9, 3.0, 0.35)):
        duhamel = 1.0 / (beta * chi * omega**2)
        commutator = beta * hbar**2 / chi
        equal_time = hbar / (2.0 * chi * omega) / math.tanh(beta * hbar * omega / 2.0)
        upper = falk_upper(duhamel, commutator)
        audit.check("harmonic inverse Falk equality", abs(upper - equal_time) < 3e-13, upper, equal_time, "falk_bruch")
        hostile = 0.5 * math.sqrt(duhamel * commutator) / math.tanh(math.sqrt(commutator / duhamel))
        audit.check("hostile missing half fails", abs(hostile - equal_time) > 1e-5, hostile, "different", "hostile")
    for commutator in (0.3, 2.0, 11.0):
        values = [falk_upper(duhamel, commutator) for duhamel in (0.02, 0.1, 0.5, 2.0)]
        audit.check("Falk upper monotone in D", all(left < right for left, right in zip(values, values[1:])), values, "strictly increasing", "falk_bruch")

    beta, hbar, chi, c_value, energy = 4.0, 1.3, 0.9, 0.7, 2.2
    d_cap = 1.0 / (2.0 * beta * c_value * energy)
    k_value = beta * hbar**2 / chi
    substituted = falk_upper(d_cap, k_value)
    expected = hbar / (2.0 * math.sqrt(2.0 * chi * c_value * energy)) / math.tanh(
        beta * hbar * math.sqrt(c_value * energy / (2.0 * chi))
    )
    ground_cap = hbar / (2.0 * math.sqrt(2.0 * chi * c_value * energy))
    audit.check("IR-to-equal-time substitution", abs(substituted - expected) < 2e-14, substituted, expected, "ground_order")
    audit.check("finite beta above ground cap", substituted > ground_cap, substituted, ground_cap, "ground_order")

    parameter_rows: list[dict[str, float | bool]] = []
    ground_only_strength = 0.45  # adversarial INPUT in the open interval J3^2 < A0 < I3
    ground_only_theta = math.sqrt(ground_only_strength / 8.0)
    fixtures = (
        {"r": -9.0, "g": 1.0, "lambda": 1.0, "hbar": 1.0, "chi": 1.0, "c": 1.0},
        {"r": -3.0 * (1.0 + 1.0) * ground_only_theta, "g": 1.0, "lambda": 1.0, "hbar": 1.0, "chi": 1.0, "c": 1.0},
    )
    for values in fixtures:
        theta = -values["r"] / (3.0 * (values["g"] + values["lambda"]))
        strength = 8.0 * values["c"] * values["chi"] * theta**2 / values["hbar"] ** 2
        rho_star = theta - values["hbar"] * half_watson / (2.0 * math.sqrt(2.0 * values["chi"] * values["c"]))
        identity_rho = values["hbar"] * (math.sqrt(strength) - half_watson) / math.sqrt(8.0 * values["chi"] * values["c"])
        parameter_rows.append({**values, "theta_Q": theta, "A0": strength, "rho_star": rho_star, "finite_temperature_phase_certified": strength > watson})
        audit.check("rho identity", abs(rho_star - identity_rho) < 2e-14, rho_star, identity_rho, "ground_order")
        audit.check("intrinsic threshold equivalence", (rho_star > 0) is (strength > half_watson**2), rho_star > 0, strength > half_watson**2, "ground_order")
    audit.check("weaker ground-only fixture", bool(parameter_rows[1]["rho_star"] > 0) and not bool(parameter_rows[1]["finite_temperature_phase_certified"]), parameter_rows[1], "J3^2<A0<I3", "ground_order")

    supercritical = parameter_rows[0]
    theta = float(supercritical["theta_Q"])
    strength = float(supercritical["A0"])
    asymptotic_target = (strength - watson) / (2.0 * float(supercritical["c"]))
    asymptotic_values: list[dict[str, float]] = []
    for beta_large in (1.0e3, 1.0e4, 1.0e5):
        t_value = beta_large * float(supercritical["hbar"]) ** 2 / (4.0 * float(supercritical["chi"]) * theta)
        root = x_from_t(t_value)
        delta = theta * math.tanh(root) / root - watson / (2.0 * beta_large * float(supercritical["c"]))
        scaled = beta_large * delta
        asymptotic_values.append({"beta": beta_large, "beta_delta": scaled})
    audit.check("old delta asymptotic converges", abs(asymptotic_values[-1]["beta_delta"] - asymptotic_target) < 2e-4, asymptotic_values[-1]["beta_delta"], asymptotic_target, "old_route")
    audit.check("old magnetization lower collapses", math.sqrt(max(0.0, asymptotic_values[-1]["beta_delta"] / asymptotic_values[-1]["beta"])) < 0.02, math.sqrt(asymptotic_values[-1]["beta_delta"] / asymptotic_values[-1]["beta"]), "tends to zero", "old_route")

    volume, order_density, hbar_gap, chi_gap = 343.0, 0.8, 1.2, 0.9
    double_commutator = volume * hbar_gap**2 / chi_gap
    s2 = volume**2 * order_density
    odd_gap = double_commutator / (2.0 * s2)
    expected_gap = hbar_gap**2 / (2.0 * chi_gap * volume * order_density)
    doublet_excess = odd_gap / 2.0
    audit.check("parity gap quotient", abs(odd_gap - expected_gap) < 1e-16, odd_gap, expected_gap, "gap")
    audit.check("doublet factor half", abs(doublet_excess - hbar_gap**2 / (4.0 * chi_gap * volume * order_density)) < 1e-16, doublet_excess, "hbar^2/(4 chi V m2)", "gap")
    audit.check("V times gap constant", abs(volume * odd_gap - hbar_gap**2 / (2.0 * chi_gap * order_density)) < 1e-14, volume * odd_gap, "constant", "gap")

    vertices = cube_vertices()
    edges = cube_edges()
    audit.check("Q3 vertices", len(vertices) == 8, len(vertices), 8, "q3")
    audit.check("Q3 edges", len(edges) == 12, len(edges), 12, "q3")
    degrees = [0] * 8
    adjacency = sp.zeros(8)
    for left, right in edges:
        degrees[left] += 1
        degrees[right] += 1
        adjacency[left, right] = adjacency[right, left] = 1
    graph_laplacian = 3 * sp.eye(8) - adjacency
    audit.check("Q3 degree", degrees == [3] * 8, degrees, [3] * 8, "q3")
    audit.check("Q3 spectrum", sorted(int(value) for value, count in graph_laplacian.eigenvals().items() for _ in range(count)) == [0, 2, 2, 2, 4, 4, 4, 6], graph_laplacian.eigenvals(), [0, 2, 2, 2, 4, 4, 4, 6], "q3")

    q = sp.symbols("q0:8", real=True)
    g_symbol, lambda_symbol, covariance = sp.symbols("g lambda C", positive=True)
    quartic = g_symbol * sum(item**4 for item in q) / 4
    quartic += lambda_symbol * sum((q[i] - q[j]) ** 2 * (q[i] ** 2 + q[j] ** 2) for i, j in edges) / 4
    laplacian_once = sp.expand(sum(sp.diff(quartic, item, 2) for item in q))
    laplacian_twice = sp.expand(sum(sp.diff(laplacian_once, item, 2) for item in q))
    q_norm = sum(item**2 for item in q)
    graph_form = sp.expand((sp.Matrix(q).T * graph_laplacian * sp.Matrix(q))[0])
    expected_once = 3 * (g_symbol + lambda_symbol) * q_norm + 3 * lambda_symbol * graph_form
    expected_twice = 48 * (g_symbol + 4 * lambda_symbol)
    audit.check("Wick first Laplacian", sp.simplify(laplacian_once - expected_once) == 0, laplacian_once, expected_once, "wick")
    audit.check("Wick second Laplacian", sp.simplify(laplacian_twice - expected_twice) == 0, laplacian_twice, expected_twice, "wick")
    wick = sp.expand(quartic - covariance * laplacian_once / 2 + covariance**2 * laplacian_twice / 8)
    expected_wick = sp.expand(quartic - 3 * covariance * ((g_symbol + lambda_symbol) * q_norm + lambda_symbol * graph_form) / 2 + 6 * covariance**2 * (g_symbol + 4 * lambda_symbol))
    audit.check("full Wick identity", sp.simplify(wick - expected_wick) == 0, wick, expected_wick, "wick")
    audit.check("I and L directions independent", graph_laplacian != sp.zeros(8) and graph_laplacian != sp.eye(8), graph_laplacian, "independent of I", "wick")

    hessian = sp.hessian(quartic, q)
    one_loop = sp.expand(sum(hessian[i, j] ** 2 for i in range(8) for j in range(8)))
    one_loop_poly = sp.Poly(one_loop, *q)
    quartic_poly = sp.Poly(quartic, *q)

    def exponent(left: int, right: int) -> tuple[int, ...]:
        powers = [0] * 8
        powers[left] = powers[right] = 2
        return tuple(powers)

    coeff_d2 = sp.factor(one_loop_poly.coeff_monomial(exponent(0, 3)))
    coeff_d1 = sp.factor(one_loop_poly.coeff_monomial(exponent(0, 1)))
    coeff_d3 = sp.factor(one_loop_poly.coeff_monomial(exponent(0, 7)))
    fourth_power = [0] * 8
    fourth_power[0] = 4
    coeff_d0 = sp.factor(one_loop_poly.coeff_monomial(tuple(fourth_power)))
    audit.check("distance controls", [sum(a != b for a, b in zip(vertices[0], vertices[index])) for index in (1, 3, 7)] == [1, 2, 3], [vertices[index] for index in (1, 3, 7)], [1, 2, 3], "one_loop")
    audit.check("distance-two witness", sp.simplify(coeff_d2 - 4 * lambda_symbol**2) == 0, coeff_d2, 4 * lambda_symbol**2, "one_loop")
    audit.check("distance-one control", sp.simplify(coeff_d1 - lambda_symbol * (12 * g_symbol + 71 * lambda_symbol)) == 0, coeff_d1, lambda_symbol * (12 * g_symbol + 71 * lambda_symbol), "one_loop")
    audit.check("distance-three control", coeff_d3 == 0, coeff_d3, 0, "one_loop")
    audit.check("onsite fourth-power control", sp.simplify(coeff_d0 - sp.Rational(3, 2) * (6 * g_symbol**2 + 36 * g_symbol * lambda_symbol + 65 * lambda_symbol**2)) == 0, coeff_d0, "3(6g^2+36g lambda+65lambda^2)/2", "one_loop")
    audit.check("bare distance-two absent", quartic_poly.coeff_monomial(exponent(0, 3)) == 0, quartic_poly.coeff_monomial(exponent(0, 3)), 0, "one_loop")
    audit.check("lambda zero removes witness", coeff_d2.subs(lambda_symbol, 0) == 0, coeff_d2.subs(lambda_symbol, 0), 0, "one_loop")
    audit.check("half-trace convention remains nonzero", sp.simplify(coeff_d2 / 2 - 2 * lambda_symbol**2) == 0, coeff_d2 / 2, 2 * lambda_symbol**2, "hostile")

    for phrase in (
        "A_0>J_3^2",
        "no positive volume-uniform full finite-volume spectral gap",
        "not yet algebraic ground states",
        "counterterm-basis obstruction, not a no-continuum theorem",
        "Physical empty space is a further, independent comparison",
        "None of these is derived by this certificate",
    ):
        audit.check(f"certificate phrase {phrase}", phrase in certificate, phrase in certificate, True, "certificate")

    true_scope = (
        "beta_first_symmetric_ground_equal_time_LRO",
        "positive_explicit_ground_order_lower_bound",
        "symmetry_broken_approximate_ground_doublets",
        "uniform_positive_full_finite_volume_gap_refuted",
        "standard_4D_one_loop_g_lambda_basis_closure_refuted",
        "independent_I_and_LQ3_quadratic_counterterms_required",
    )
    false_scope = (
        "distinct_infinite_volume_algebraic_ground_states",
        "common_infinite_volume_real_time_dynamics",
        "algebraic_KMS_for_preexisting_common_dynamics",
        "ground_GNS_sector_gap",
        "mass_gap",
        "continuum_regulator_removal",
        "physical_empty_space_reference",
        "below_empty_space",
        "physical_light_speed_derived",
        "gravity_derived",
        "event_horizon_derived",
        "C6_advanced",
        "Pre_A_complete",
    )
    for key in true_scope:
        audit.check(f"scope true {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope:
        audit.check(f"scope false {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    return {
        "schema": f"tect/{SLUG}-primary/0.1",
        "script_version": __version__,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "parent_gate": PARENT_GATE,
        "next_gate": PARENT_GATE,
        "negative_ids": list(NEGATIVE_IDS),
        "claim_bearing": False,
        "assertions": {"passed": len(audit.rows), "total": len(audit.rows), "rows": audit.rows},
        "derived": {
            "watson_I3": watson,
            "half_watson_J3": half_watson,
            "J3_squared": half_watson**2,
            "I3_minus_J3_squared": watson - half_watson**2,
            "finite_torus": finite_rows,
            "parameter_fixtures": parameter_rows,
            "old_delta_asymptotic": asymptotic_values,
            "one_loop_coefficients": {
                "distance_2": str(coeff_d2),
                "distance_1": str(coeff_d1),
                "distance_3": str(coeff_d3),
                "onsite_fourth": str(coeff_d0),
            },
        },
        "scope": manifest["scope"],
        "files": {
            "manifest_sha256": portable_sha256(MANIFEST),
            "certificate_sha256": portable_sha256(CERTIFICATE),
            "script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"),
        },
        "verdict": "PASS",
        "boundary": manifest["no_overclaim"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"EXP-000789 PRIMARY PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
