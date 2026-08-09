#!/usr/bin/env python3
"""Primary exact audit for the interacting regulator-compatible state route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-interacting-regulator-compatible-state-route-split"
CANDIDATE_ID = "PA-CP1-CL8-INTERACTING-REGULATOR-COMPATIBLE-STATE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-LOW-MODE-GROUND-ENTANGLEMENT-ALL-BETA-PROJECTIVITY-AND-Q3-WICK-COUNTERTERM-OBSTRUCTIONS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-INTERACTING-GROUND-PROJECTIVITY",
    "NG-2026-08-04-PRE-A-CP1-CL8-SCALAR-MASS-ONLY-Q3-WICK-RENORMALIZATION",
)
PARENT_FILES = (
    "strategy/pre-a-cp1-st8-q3lock-manifest.json",
    "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json",
    "strategy/pre-a-cp1-cl8-history-cut-quantum-algebra-state-compatibility-route-split-manifest.json",
    "strategy/pre-a-cp1-cl8-ordered-q3-gaussian-tangent-regulator-route-split-manifest.json",
)
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-04-primary-{SLUG}/result.json"


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def cube_laplacian() -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], sp.Matrix]:
    nodes = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    index = {node: i for i, node in enumerate(nodes)}
    edges: list[tuple[int, int]] = []
    laplacian = sp.zeros(8)
    for node in nodes:
        i = index[node]
        for axis in range(3):
            neighbor = list(node)
            neighbor[axis] ^= 1
            j = index[tuple(neighbor)]
            if i < j:
                edges.append((i, j))
            laplacian[i, i] += 1
            laplacian[i, j] -= 1
    return nodes, edges, laplacian


def walsh(nodes: list[tuple[int, int, int]], alpha: tuple[int, int, int]) -> sp.Matrix:
    return sp.Matrix([(-1) ** sum(a * e for a, e in zip(alpha, node)) for node in nodes])


def wick(poly: sp.Expr, variables: tuple[sp.Symbol, ...], covariance: sp.Symbol) -> sp.Expr:
    result = sp.expand(poly)
    current = sp.expand(poly)
    for order in range(1, 3):
        current = sp.expand(sum(sp.diff(current, variable, 2) for variable in variables))
        result += (-covariance / 2) ** order * current / sp.factorial(order)
    return sp.expand(result)


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parents = [json.loads((REPO / path).read_text(encoding="utf-8")) for path in PARENT_FILES]
    audit = Audit()

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("exploration id", manifest["exploration_id"] == "EXP-000764", manifest["exploration_id"], "EXP-000764", "identity")
    audit.check("parent ids", tuple(parent["candidate_id"] for parent in parents) == tuple(manifest["parent_ids"]), [parent["candidate_id"] for parent in parents], manifest["parent_ids"], "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    # The coarse self-conjugate Nyquist oscillator requires a one-mode squeeze
    # when represented by the fine n=M/2 cosine quadrature.  Derive the
    # symplectic check instead of treating the two normalizations as identical.
    nyquist_squeeze = sp.diag(sp.sqrt(2), 1 / sp.sqrt(2))
    symplectic_form = sp.Matrix([[0, 1], [-1, 0]])
    squeeze_residual = sp.simplify(nyquist_squeeze.T * symplectic_form * nyquist_squeeze - symplectic_form)
    audit.check("coarse Nyquist squeeze is symplectic", squeeze_residual == sp.zeros(2), squeeze_residual, sp.zeros(2), "typing")
    audit.check("coarse Nyquist squeeze is recorded", "sqrt(2)*Phi" in manifest["natural_low_mode_split"]["coarse_identification"] and "Pi_N,M/2/sqrt(2)" in manifest["natural_low_mode_split"]["coarse_identification"], manifest["natural_low_mode_split"]["coarse_identification"], "field/momentum reciprocal squeeze", "typing")

    # Exact collective retained-zero / added-Nyquist plane, derived directly
    # from the fine CL8 sums rather than copied from the certificate.
    L, b, r, c, g = sp.symbols("L b r c g", positive=True)
    r = sp.symbols("r", real=True)
    X, Y = sp.symbols("X Y", real=True)
    N = sp.simplify(L / b)
    q_plus = (X + Y) / sp.sqrt(L)
    q_minus = (X - Y) / sp.sqrt(L)
    onsite_one = lambda q: r * q**2 / 2 + g * q**4 / 4
    onsite = sp.expand((b / 8) * 8 * (N / 2) * (onsite_one(q_plus) + onsite_one(q_minus)))
    gradient = sp.simplify((b / 8) * 8 * N * (c / 2) * (2 * Y / (b * sp.sqrt(L))) ** 2)
    collective_potential = sp.factor(onsite + gradient)
    expected_potential = r * (X**2 + Y**2) / 2 + 2 * c * Y**2 / b**2 + g * (X**4 + 6 * X**2 * Y**2 + Y**4) / (4 * L)
    audit.check("collective plane potential", sp.expand(collective_potential - expected_potential) == 0, collective_potential, expected_potential, "entanglement")
    mixed_derivative = sp.factor(sp.diff(collective_potential, X, 2, Y, 2))
    audit.check("collective low-high mixed derivative", mixed_derivative == 6 * g / L, mixed_derivative, 6 * g / L, "entanglement")
    fixture = sp.factor(collective_potential.subs({L: 4, b: sp.Rational(1, 2), r: -1, c: 1, g: 1}))
    expected_fixture = -X**2 / 2 + 15 * Y**2 / 2 + (X**4 + Y**4) / 16 + 3 * X**2 * Y**2 / 8
    audit.check("collective rational fixture", sp.expand(fixture - expected_fixture) == 0, fixture, expected_fixture, "entanglement")
    fixture_mixed = mixed_derivative.subs({L: 4, g: 1})
    audit.check("fixture mixed derivative", fixture_mixed == sp.Rational(3, 2), fixture_mixed, sp.Rational(3, 2), "entanglement")
    audit.check("Q3 lock vanishes on collective plane", "lock terms vanish identically" in manifest["ground_projectivity_no_go"]["exact_potential_restriction"], manifest["ground_projectivity_no_go"]["exact_potential_restriction"], "contains vanishing lock", "entanglement")

    # Purity control: an entangled rank-two vector has a mixed marginal while a
    # product vector has a pure marginal.  The analytic factorization theorem is
    # stated in the certificate; this finite matrix catches direction errors.
    coeff_entangled = sp.eye(2) / sp.sqrt(2)
    reduced_entangled = sp.simplify(coeff_entangled * coeff_entangled.T)
    coeff_product = sp.Matrix([[1, 0], [0, 0]])
    reduced_product = coeff_product * coeff_product.T
    audit.check("entangled marginal purity", sp.trace(reduced_entangled**2) == sp.Rational(1, 2), sp.trace(reduced_entangled**2), sp.Rational(1, 2), "purity")
    audit.check("product marginal purity", sp.trace(reduced_product**2) == 1, sp.trace(reduced_product**2), 1, "purity")
    audit.check("positive-ground factorization lemma recorded", "strictly positive" in manifest["ground_projectivity_no_go"]["factorization_lemma"], manifest["ground_projectivity_no_go"]["factorization_lemma"], "contains strictly positive", "purity")
    audit.check("ground projectivity conclusion recorded", "restriction is mixed" in manifest["ground_projectivity_no_go"]["conclusion"], manifest["ground_projectivity_no_go"]["conclusion"], "contains mixed restriction", "purity")

    eta = sp.symbols("eta", positive=True)
    eps_m, eps_n = sp.symbols("eps_M eps_N", nonnegative=True)
    lower_bound = 2 * (eta - eps_m - eps_n)
    audit.check("Gibbs tail lower-bound coefficient", lower_bound.subs({eps_m: eta / 4, eps_n: eta / 4}) == eta, lower_bound.subs({eps_m: eta / 4, eps_n: eta / 4}), eta, "Gibbs")
    audit.check("explicit Gibbs beta tail recorded", "beta_*=" in manifest["all_beta_Gibbs_consequence"]["explicit_tail"] and "trace distance at least eta" in manifest["all_beta_Gibbs_consequence"]["explicit_tail"], manifest["all_beta_Gibbs_consequence"]["explicit_tail"], "explicit beta_* and eta bound", "Gibbs")
    audit.check("all-beta boundary retains isolated beta", "does not exclude an isolated" in manifest["all_beta_Gibbs_consequence"]["boundary"], manifest["all_beta_Gibbs_consequence"]["boundary"], "contains isolated-beta boundary", "Gibbs")
    audit.check("mean-force positive substitute", "H_mf(beta)" in manifest["normal_pullback_and_mean_force"]["mean_force"], manifest["normal_pullback_and_mean_force"]["mean_force"], "contains H_mf", "Gibbs")
    audit.check("mean-force logarithm faithfulness", "trivial kernel" in manifest["normal_pullback_and_mean_force"]["fine_Gibbs"], manifest["normal_pullback_and_mean_force"]["fine_Gibbs"], "trivial-kernel input", "Gibbs")
    audit.check("history cut square conditional", manifest["history_cut_consequence"]["conditional_square"].startswith("if an inter-regulator"), manifest["history_cut_consequence"]["conditional_square"], "explicit conditional inter-regulator square", "history")

    # Exact common-diagonal Wick contractions.
    a_var, b_var, C = sp.symbols("a_var b_var C", real=True)
    edge = sp.expand((a_var - b_var) ** 2 * (a_var**2 + b_var**2))
    wick_edge = wick(edge, (a_var, b_var), C)
    expected_wick_edge = edge - 8 * C * (a_var**2 + b_var**2) + 12 * C * a_var * b_var + 8 * C**2
    audit.check("edge Wick identity", sp.expand(wick_edge - expected_wick_edge) == 0, wick_edge, expected_wick_edge, "Wick")
    onsite_wick = wick(a_var**4, (a_var,), C)
    audit.check("onsite Wick identity", onsite_wick == a_var**4 - 6 * C * a_var**2 + 3 * C**2, onsite_wick, a_var**4 - 6 * C * a_var**2 + 3 * C**2, "Wick")
    edge_contraction = sp.Poly(sp.expand(wick_edge - edge), a_var, b_var)
    edge_a2_factor = sp.factor(edge_contraction.coeff_monomial(a_var**2) / C)
    edge_ab_factor = sp.factor(edge_contraction.coeff_monomial(a_var * b_var) / C)
    edge_b2_factor = sp.factor(edge_contraction.coeff_monomial(b_var**2) / C)
    edge_constant_factor = sp.factor(edge_contraction.coeff_monomial(1) / C**2)
    onsite_contraction = sp.Poly(sp.expand(onsite_wick - a_var**4), a_var)
    onsite_q2_factor = sp.factor(onsite_contraction.coeff_monomial(a_var**2) / C)
    onsite_constant_factor = sp.factor(onsite_contraction.coeff_monomial(1) / C**2)

    nodes, edges, laplacian = cube_laplacian()
    q = sp.symbols("q0:8", real=True)
    lam = sp.symbols("lambda", nonnegative=True)
    W4 = g * sum(value**4 for value in q) / 4
    W4 += lam * sum((q[i] - q[j]) ** 2 * (q[i] ** 2 + q[j] ** 2) for i, j in edges) / 4
    wick_W4 = wick(sp.expand(W4), q, C)
    contraction = sp.expand(wick_W4 - W4)
    delta_k = sp.Matrix([[sp.diff(contraction, q[i], q[j]).subs({value: 0 for value in q}) for j in range(8)] for i in range(8)])
    expected_delta_k = -3 * C * ((g + lam) * sp.eye(8) + lam * laplacian)
    delta_residual = (delta_k - expected_delta_k).applyfunc(sp.simplify)
    audit.check("Q3 Wick quadratic matrix", delta_residual == sp.zeros(8), delta_residual, sp.zeros(8), "Wick")
    constant = sp.factor(contraction.subs({value: 0 for value in q}))
    audit.check("Q3 Wick scalar term", constant == 6 * C**2 * (g + 4 * lam), constant, 6 * C**2 * (g + 4 * lam), "Wick")

    alphas = nodes
    spectrum: Counter[int] = Counter()
    shifts: list[sp.Expr] = []
    for alpha in alphas:
        level = sum(alpha)
        vector = walsh(nodes, alpha)
        residual = laplacian * vector - 2 * level * vector
        audit.check(f"Q3 Walsh vector {alpha}", residual == sp.zeros(8, 1), residual, sp.zeros(8, 1), "Q3")
        spectrum[2 * level] += 1
        shift = sp.factor((-3 * C * (g + lam + 2 * level * lam)))
        matrix_residual = (expected_delta_k * vector - shift * vector).applyfunc(sp.simplify)
        audit.check(f"Wick Walsh shift {alpha}", matrix_residual == sp.zeros(8, 1), matrix_residual, sp.zeros(8, 1), "Wick")
        shifts.append(shift)
    audit.check("Q3 spectrum", spectrum == Counter({0: 1, 2: 3, 4: 3, 6: 1}), dict(spectrum), {0: 1, 2: 3, 4: 3, 6: 1}, "Q3")
    fixture_subs = {g: 5, lam: 2, C: 3}
    shift_fixture = [sp.factor(-3 * C * (g + lam + 2 * level * lam)).subs(fixture_subs) for level in range(4)]
    audit.check("Wick Walsh shift fixture", shift_fixture == [-63, -99, -135, -171], shift_fixture, [-63, -99, -135, -171], "Wick")
    constant_fixture = constant.subs(fixture_subs)
    audit.check("Wick scalar fixture", constant_fixture == 702, constant_fixture, 702, "Wick")
    audit.check("scalar counterterm obstruction", "linearly independent of I" in manifest["counterterm_no_go"]["exact_obstruction"], manifest["counterterm_no_go"]["exact_obstruction"], "contains linear independence", "Wick")

    # Centered reference covariance: exact mode inequalities and numerical
    # logarithmic hostile sequence.  The certificate contains the analytic
    # harmonic comparison.
    covariance_values: list[float] = []
    covariance_over_log: list[float] = []
    for size in (16, 32, 64, 128, 256, 512):
        length = 2.0 * math.pi
        spacing = length / size
        total = 0.0
        upper_rows: list[tuple[float, float]] = []
        lower_rows: list[tuple[float, float]] = []
        for mode in range(-size // 2, size // 2):
            wave = 2.0 * math.pi * mode / length
            symbol = 2.0 * math.sin(wave * spacing / 2.0) / spacing
            if mode != 0:
                upper_rows.append((abs(symbol), abs(wave)))
                lower_rows.append((abs(symbol), 2.0 * abs(wave) / math.pi))
            total += 1.0 / math.sqrt(1.0 + symbol * symbol)
        audit.check(f"centered symbol upper all modes N{size}", all(symbol <= wave + 1e-12 for symbol, wave in upper_rows), max(symbol - wave for symbol, wave in upper_rows), "<=0", "covariance")
        audit.check(f"centered symbol lower all modes N{size}", all(symbol + 1e-12 >= bound for symbol, bound in lower_rows), min(symbol - bound for symbol, bound in lower_rows), ">=0", "covariance")
        covariance = total / (2.0 * length)
        covariance_values.append(covariance)
        covariance_over_log.append(covariance / math.log(size))
    audit.check("centered covariance strictly grows", all(covariance_values[i + 1] > covariance_values[i] for i in range(len(covariance_values) - 1)), covariance_values, "strict growth", "covariance")
    audit.check("centered covariance logarithmic window", all(0.12 < value < 0.23 for value in covariance_over_log), covariance_over_log, "bounded positive C_N/log N", "covariance")
    audit.check("Walsh separation grows with C", sp.simplify((-3 * C * (g + lam + 2 * lam)) - (-3 * C * (g + lam))) == -6 * C * lam, sp.simplify((-3 * C * (g + lam + 2 * lam)) - (-3 * C * (g + lam))), -6 * C * lam, "covariance")

    true_scope = (
        "natural_low_mode_tensor_split",
        "fine_interacting_ground_low_high_entangled",
        "common_diagonal_Q3_Wick_counterterm_ledger",
        "reference_covariance_logarithmic_growth",
    )
    false_scope = (
        "natural_exact_ground_projectivity",
        "natural_same_beta_all_temperature_Gibbs_projectivity",
        "natural_ground_anchored_history_cut_projectivity",
        "scalar_mass_only_Q3_Wick_renormalization",
        "Q3_matrix_counterterm_sufficiency",
        "cutoff_uniform_moment_bounds",
        "cutoff_uniform_local_energy_bounds",
        "interacting_state_compactness",
        "typed_inter_regulator_cut_square",
        "interacting_continuum_state",
        "interacting_Hadamard_state",
        "physical_state_or_vacuum",
        "below_empty_space_comparison",
        "physical_phase_transition",
        "physical_light_speed_derived",
        "original_3D_Q3LOCK_parent",
        "C0_closed",
        "N1_through_N5_closed",
        "C6_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in true_scope:
        audit.check(f"scope true: {key}", manifest["scope"].get(key) is True, manifest["scope"].get(key), True, "scope")
    for key in false_scope:
        audit.check(f"scope false: {key}", manifest["scope"].get(key) is False, manifest["scope"].get(key), False, "scope")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-Q3-MATRIX-COUNTERTERM-INTERACTING-STATE-COMPACTNESS-AND-CUT-SQUARE", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-Q3-MATRIX-COUNTERTERM-INTERACTING-STATE-COMPACTNESS-AND-CUT-SQUARE", "scope")

    derived = {
        "collective_fixture": {"potential": fixture, "mixed_derivative": fixture_mixed},
        "Q3_spectrum": {"eigenvalues": sorted(spectrum), "multiplicities": [spectrum[value] for value in sorted(spectrum)]},
        "Wick_fixture": {
            "edge_quadratic_coefficients": [edge_a2_factor, edge_ab_factor, edge_b2_factor],
            "edge_constant": edge_constant_factor,
            "onsite_quadratic_coefficient": onsite_q2_factor,
            "onsite_constant": onsite_constant_factor,
            "Walsh_shifts": shift_fixture,
            "Q3_constant": constant_fixture,
        },
        "covariance_values": covariance_values,
        "covariance_over_log": covariance_over_log,
        "negative_ids": list(NEGATIVE_IDS),
    }
    source_hashes = {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST)}
    for path in PARENT_FILES:
        source_hashes[path] = sha256(REPO / path)
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": manifest["parent_ids"],
        "result_id": RESULT_ID,
        "negative_ids": list(NEGATIVE_IDS),
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": derived,
        "source_sha256": source_hashes,
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if not args.self_test:
        atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID}: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
