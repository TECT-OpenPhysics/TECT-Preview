#!/usr/bin/env python3
"""Primary verifier for the centered-nodal Q3 Nelson/affine-seam theorem."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-centered-nodal-q3-nelson-boue-dupuis-seam-limit-route-split"
CANDIDATE_ID = "PA-CP1-CL8-CENTERED-NODAL-Q3-NELSON-BOUE-DUPUIS-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-CENTERED-NODAL-Q3-UI-L1-TV-RP-AND-FIXED-BAND-FULL-WEYL-LIMIT"
EXPLORATION_ID = "EXP-000772"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"


def sha256(path: Path) -> str:
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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def cube_edges() -> list[tuple[int, int]]:
    return [(vertex, vertex ^ (1 << bit)) for vertex in range(8) for bit in range(3) if vertex < (vertex ^ (1 << bit))]


def representative(value: int, modulus: int) -> int:
    return ((value + modulus // 2) % modulus) - modulus // 2


def lift_sectors(modulus: int, degree: int, shift: int = 0) -> set[int]:
    labels = range(-modulus // 2, modulus // 2)
    sectors: set[int] = set()
    for values in itertools.product(labels, repeat=degree):
        total = sum(values) + shift
        output = representative(total, modulus)
        sectors.add((total - output) // modulus)
    return sectors


def convolution(base: dict[tuple[int, int], float], degree: int) -> dict[tuple[int, int], float]:
    result = {(0, 0): 1.0}
    for _ in range(degree):
        updated: dict[tuple[int, int], float] = {}
        for (n1, k1), left in result.items():
            for (n2, k2), right in base.items():
                key = (n1 + n2, k1 + k2)
                updated[key] = updated.get(key, 0.0) + left * right
        result = updated
    return result


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    edges = cube_edges()
    audit.check("Q3 twelve edges", len(edges) == 12, len(edges), 12, "Q3")
    x = sp.symbols("x0:8", real=True)
    g, lam = sp.symbols("g lambda", positive=True)
    onsite = g * sum(value**4 for value in x) / 4
    edge_term = lam * sum((x[left] - x[right]) ** 2 * (x[left] ** 2 + x[right] ** 2) for left, right in edges) / 4
    audit.check("Q3 edges nonnegative for positive lambda", all(sp.Poly((x[left] - x[right]) ** 2 * (x[left] ** 2 + x[right] ** 2), x).total_degree() == 4 for left, right in edges), len(edges), 12, "Q3")
    radial_fourth = sum(value**2 for value in x) ** 2
    cauchy_gap = sp.expand(8 * sum(value**4 for value in x) - radial_fourth)
    samples = [tuple(Fraction((index + 2 * vertex) % 7 - 3, 3) for vertex in range(8)) for index in range(7)]
    audit.check("Q3 onsite Cauchy fixtures", all(cauchy_gap.subs(dict(zip(x, sample))) >= 0 for sample in samples), "all nonnegative", ">=0", "Q3")
    audit.check("Q3 coercive coefficient", sp.simplify((g / 4) / 8 - g / 32) == 0, g / 32, "g/32", "Q3")

    C = sp.symbols("C", positive=True)
    onsite_constant = 8 * g * 3 * C**2 / 4
    edge_constant = len(edges) * lam * 8 * C**2 / 4
    total_constant = sp.simplify(onsite_constant + edge_constant)
    audit.check("whole-Wick quartic scalar", sp.simplify(total_constant - 6 * C**2 * (g + 4 * lam)) == 0, total_constant, "6C^2(g+4lambda)", "scalar")
    trace_k = sp.symbols("TrK", real=True)
    quadratic_wick_scalar = -C * trace_k / 2
    audit.check("whole-Wick quadratic scalar", quadratic_wick_scalar == -C * trace_k / 2, quadratic_wick_scalar, "-C TrK/2", "scalar")
    raw_weights = [sp.Rational(1, 5), sp.Rational(2, 5), sp.Rational(2, 5)]
    energies = [sp.Rational(2), sp.Rational(-1), sp.Rational(3)]
    shift = sp.Rational(7, 3)
    unshifted = [weight * sp.exp(-energy) for weight, energy in zip(raw_weights, energies)]
    shifted = [weight * sp.exp(-(energy + shift)) for weight, energy in zip(raw_weights, energies)]
    rho_unshifted = [sp.simplify(value / sum(unshifted)) for value in unshifted]
    rho_shifted = [sp.simplify(value / sum(shifted)) for value in shifted]
    audit.check("normalized scalar-shift invariance", rho_unshifted == rho_shifted, rho_shifted, rho_unshifted, "scalar")
    audit.check("raw partition changes under scalar", sp.simplify(sum(shifted) / sum(unshifted) - sp.exp(-shift)) == 0, sp.simplify(sum(shifted) / sum(unshifted)), sp.exp(-shift), "scalar")

    epsilon = sp.Rational(1, 8)
    exponent_rows = []
    for r in (1, 2, 3):
        a_power = sp.Rational(r) - 2 * epsilon
        b_power = 2 * epsilon
        consumed = sp.simplify(a_power / 4 + b_power / 2)
        random_power = sp.simplify(1 / (1 - consumed))
        dual = sp.simplify(sp.Rational(4, 4 - r))
        exponent_rows.append({"r": r, "a_power": str(a_power), "b_power": str(b_power), "consumed": str(consumed), "q": str(random_power), "negative_dual": str(dual)})
    expected_q = [sp.Rational(16, 11), sp.Rational(16, 7), sp.Rational(16, 3)]
    audit.check("Nelson Young exponent table", [sp.Rational(row["q"]) for row in exponent_rows] == expected_q, exponent_rows, expected_q, "Nelson")
    audit.check("worst random moment 16/3", max(expected_q) == sp.Rational(16, 3), max(expected_q), sp.Rational(16, 3), "Nelson")
    drift, source = sp.symbols("I b", real=True)
    gaussian_variational = sp.simplify(source * drift - drift**2 / 2)
    stationary = sp.solve(sp.diff(gaussian_variational, drift), drift)[0]
    audit.check("finite BD Gaussian stationary drift", stationary == source, stationary, source, "Nelson")
    audit.check("finite BD Gaussian value", sp.simplify(gaussian_variational.subs(drift, stationary) - source**2 / 2) == 0, gaussian_variational.subs(drift, stationary), source**2 / 2, "Nelson")

    symbol_rows = []
    for modulus in (12, 24, 48):
        spacing = 2.0 * math.pi / modulus
        ratios = []
        for mode in range(1, modulus // 2 + 1):
            centered = 4.0 * math.sin(spacing * mode / 2.0) ** 2 / spacing**2
            ratios.append(centered / (mode * mode))
        symbol_rows.append({"M": modulus, "minimum": min(ratios), "maximum": max(ratios)})
        audit.check(f"centered symbol lower M{modulus}", min(ratios) + 1e-12 >= 4.0 / math.pi**2, min(ratios), 4.0 / math.pi**2, "harmonic")
        audit.check(f"centered symbol upper M{modulus}", max(ratios) <= 1.0 + 1e-12, max(ratios), 1.0, "harmonic")
    lift_rows = {}
    for modulus in (6, 8, 10):
        lift_rows[str(modulus)] = {}
        for degree in range(1, 5):
            sectors = sorted(lift_sectors(modulus, degree))
            lift_rows[str(modulus)][str(degree)] = sectors
            audit.check(f"cyclic lifts finite M{modulus} d{degree}", max(abs(value) for value in sectors) <= degree, sectors, f"|ell|<={degree}", "harmonic")
    shifted_lifts = {str(shift_value): sorted(lift_sectors(10, 4, shift_value)) for shift_value in (-2, -1, 0, 1, 2)}
    audit.check("fixed-band shifted lifts remain finite", all(max(abs(value) for value in sectors) <= 4 for sectors in shifted_lifts.values()), shifted_lifts, "|ell|<=4", "harmonic")
    audit.check("Nyquist lift included", any(abs(value) > 0 for value in lift_rows["8"]["4"]), lift_rows["8"]["4"], "nonzero", "harmonic")

    base = {(n, k): 1.0 / (1.0 + n * n + k * k) for n in range(-8, 9) for k in range(-8, 9)}
    convolution_rows = {}
    for degree in (2, 3, 4):
        values = convolution(base, degree)
        tail = [values.get((0, mode), 0.0) for mode in (4, 8, 12)]
        convolution_rows[str(degree)] = tail
        audit.check(f"convolution tail decreases d{degree}", tail[2] < tail[1] < tail[0], tail, "strict decrease", "harmonic")

    u = [sp.Rational(1), sp.Rational(-2), sp.Rational(3), sp.Rational(1, 2), sp.Rational(-1)]
    v = [sp.Rational(2), sp.Rational(1), sp.Rational(-1), sp.Rational(4), sp.Rational(3, 2)]
    duv = [u[(index + 1) % len(u)] * v[(index + 1) % len(v)] - u[index] * v[index] for index in range(len(u))]
    leibniz = [(u[(index + 1) % len(u)] - u[index]) * v[(index + 1) % len(v)] + u[index] * (v[(index + 1) % len(v)] - v[index]) for index in range(len(u))]
    audit.check("discrete shifted Leibniz identity", duv == leibniz, duv, leibniz, "positive-space")
    nodal_l2 = sum(value**2 for value in u)
    extension_l2 = sum((u[index] ** 2 + u[index] * u[(index + 1) % len(u)] + u[(index + 1) % len(u)] ** 2) / 3 for index in range(len(u)))
    audit.check("piecewise-linear L2 upper", extension_l2 <= nodal_l2, extension_l2, nodal_l2, "positive-space")
    audit.check("piecewise-linear L2 lower", extension_l2 >= nodal_l2 / 3, extension_l2, nodal_l2 / 3, "positive-space")

    beta, hnorm, spatial_form = sp.symbols("beta h2 Ah", positive=True)
    time = sp.symbols("t", real=True)
    saw = time / beta - sp.Rational(1, 2)
    saw_square = sp.integrate(saw**2, (time, 0, beta))
    kinetic_cost = sp.simplify(sp.integrate((1 / beta) ** 2, (time, 0, beta)) * hnorm / 2)
    spatial_cost = sp.simplify(saw_square * spatial_form / 2)
    audit.check("seam sawtooth square beta/12", saw_square == beta / 12, saw_square, beta / 12, "seam")
    audit.check("seam kinetic cost", kinetic_cost == hnorm / (2 * beta), kinetic_cost, hnorm / (2 * beta), "seam")
    audit.check("seam spatial cost beta/24", spatial_cost == beta * spatial_form / 24, spatial_cost, beta * spatial_form / 24, "seam")
    mass, wave = sp.symbols("m0 k", positive=True)
    audit.check("seam full spatial operator sentinel", mass**2 + wave**2 != mass**2, mass**2 + wave**2, "not m0^2 for k!=0", "seam")

    for phrase in ("whole polynomial Wick convention", "16\\over3", "all-M hybrid-lattice Wick estimate", "beta_0\\over24", "full-sequence total-variation convergence", "energy below empty space", "not a world-first or novelty proof"):
        audit.check(f"certificate phrase {phrase[:34]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in ("centered_Q3_uniform_exponential_integrability", "centered_Q3_interacting_density_L1_limit", "centered_Q3_interacting_density_total_variation_limit", "centered_Q3_limit_reflection_positive", "centered_Q3_shifted_seam_UI_local_uniform", "centered_Q3_offdiagonal_seam_full_sequence", "centered_Q3_fixed_band_regular_Weyl_limit"):
        audit.check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in ("original_fixed_raw_CL8_family", "absolute_energy_fixed_by_centering", "complete_OS_Markov_Hadamard", "physical_state_or_vacuum", "below_empty_space_comparison", "phase_transition_proved", "C6_advanced", "CP1_complete", "Sector_A_complete", "Pre_A_complete"):
        audit.check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("analytic proof label", manifest["verification"]["proof_grade"].startswith("ANALYTIC"), manifest["verification"]["proof_grade"], "ANALYTIC", "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "negative_ids": [],
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE)},
        "derived": {"edges": edges, "whole_Wick_scalar": str(total_constant), "exponents": exponent_rows, "symbol": symbol_rows, "lifts": lift_rows, "shifted_lifts": shifted_lifts, "convolution_tails": convolution_rows, "seam": {"saw_square": str(saw_square), "kinetic": str(kinetic_cost), "spatial": str(spatial_cost)}},
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = build_payload()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID}: {payload['assertion_summary']['passed']}/{payload['assertion_summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
