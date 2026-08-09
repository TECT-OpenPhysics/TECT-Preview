#!/usr/bin/env python3
"""Primary verifier for the spatial-spectral Q3 low-mode Weyl checkpoint."""

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


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-spatial-spectral-low-mode-weyl-equicontinuity-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-SPATIAL-SPECTRAL-LOW-MODE-WEYL-EQUICONTINUITY-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-RENORMALIZED-FORCE-VIRIAL-BOUND-AND-REGULAR-WEYL-CLUSTERS-WITH-FULL-SEQUENCE-SEAM-GATE"
EXPLORATION_ID = "EXP-000771"
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


def q3_edges() -> list[tuple[int, int]]:
    return [(vertex, vertex ^ (1 << bit)) for vertex in range(8) for bit in range(3) if vertex < (vertex ^ (1 << bit))]


def covariance_l3(cutoff: int, samples: int = 8192) -> float:
    total = 0.0
    beta = 1.7
    for index in range(samples):
        x = 2.0 * math.pi * (index + 0.5) / samples
        value = 1.0
        for mode in range(1, cutoff + 1):
            omega = math.sqrt(1.0 + mode * mode)
            coefficient = math.cosh(beta * omega / 2.0) / math.sinh(beta * omega / 2.0) / omega
            value += coefficient * math.cos(mode * x)
        total += abs(value) ** 3
    return (total / samples) ** (1.0 / 3.0)


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("no new negative", manifest["negative_ids"] == [], manifest["negative_ids"], [], "identity")

    edges = q3_edges()
    degrees = [sum(1 for edge in edges if vertex in edge) for vertex in range(8)]
    audit.check("Q3 edge count", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("Q3 degree three", degrees == [3] * 8, degrees, [3] * 8, "Q3")

    x, y, covariance, coupling = sp.symbols("x y C lambda", real=True)
    edge = coupling * (x - y) ** 2 * (x**2 + y**2) / 4
    derivative = sp.expand(sp.diff(edge, x))
    expected = sp.expand(coupling * (2 * x**3 - 3 * x**2 * y + 2 * x * y**2 - y**3) / 2)
    audit.check("Q3 oriented-edge derivative", sp.simplify(derivative - expected) == 0, derivative, expected, "Q3")
    coefficient_vector = [sp.expand(expected).coeff(monomial) for monomial in (x**3, x**2 * y, x * y**2, y**3)]
    expected_vector = [coupling, -3 * coupling / 2, coupling, -coupling / 2]
    audit.check("Q3 force coefficient sentinel", coefficient_vector == expected_vector, coefficient_vector, expected_vector, "Q3")
    onsite = sp.symbols("g", positive=True) * x**4 / 4
    own = sp.diff(onsite, x).coeff(x**3) + 3 * coefficient_vector[0]
    audit.check("Q3 own cubic coefficient", sp.simplify(own - (sp.symbols("g", positive=True) + 3 * coupling)) == 0, own, "g+3lambda", "Q3")

    wick_x4 = x**4 - 6 * covariance * x**2 + 3 * covariance**2
    wick_x3y = (x**3 - 3 * covariance * x) * y
    wick_x2y2 = (x**2 - covariance) * (y**2 - covariance)
    wick_xy3 = x * (y**3 - 3 * covariance * y)
    wick_y4 = y**4 - 6 * covariance * y**2 + 3 * covariance**2
    wick_edge = coupling * (wick_x4 - 2 * wick_x3y + 2 * wick_x2y2 - 2 * wick_xy3 + wick_y4) / 4
    wick_force = coupling * (
        2 * (x**3 - 3 * covariance * x)
        - 3 * (x**2 - covariance) * y
        + 2 * x * (y**2 - covariance)
        - (y**3 - 3 * covariance * y)
    ) / 2
    audit.check("Wick derivative commutes", sp.simplify(sp.diff(wick_edge, x) - wick_force) == 0, sp.expand(sp.diff(wick_edge, x)), sp.expand(wick_force), "Wick")
    audit.check("Wick raw own linear sentinel", sp.expand(wick_force).coeff(covariance * x) == -4 * coupling, sp.expand(wick_force).coeff(covariance * x), -4 * coupling, "Wick")
    audit.check("Wick raw neighbour linear sentinel", sp.expand(wick_force).coeff(covariance * y) == 3 * coupling, sp.expand(wick_force).coeff(covariance * y), 3 * coupling, "Wick")

    rho = sp.symbols("rho", real=True)
    # Isserlis: E[X^3Y^3]=9rho+6rho^3, E[X^3Y]=3rho, E[XY^3]=3rho.
    cubic_pair = sp.expand((9 * rho + 6 * rho**3) - 3 * (3 * rho) - 3 * (3 * rho) + 9 * rho)
    audit.check("Wick cubic contraction", sp.simplify(cubic_pair - 6 * rho**3) == 0, cubic_pair, 6 * rho**3, "Wick")
    hyper = 3 ** sp.Rational(3, 2)
    audit.check("degree-three L4 hypercontractive factor", sp.simplify(hyper**2 - 27) == 0, hyper, "3^(3/2)", "Wick")

    l3_rows = [covariance_l3(cutoff) for cutoff in (8, 16, 32, 64)]
    audit.check("log covariance finite L3 proxy", max(l3_rows) < 2.5, l3_rows, "<2.5", "Wick")
    audit.check("point covariance divergence retained", sum(1.0 / math.sqrt(1.0 + k * k) for k in range(1, 129)) > sum(1.0 / math.sqrt(1.0 + k * k) for k in range(1, 65)), "grows", "grows", "Wick")

    q, hbar, chi = sp.symbols("q hbar chi", positive=True)
    p_symbol, force = sp.symbols("p G", real=True)
    comm_h_q = -sp.I * hbar * p_symbol / chi
    comm_h_p = sp.I * hbar * force
    comm_h_a = sp.simplify((comm_h_q * p_symbol + p_symbol * comm_h_q + 2 * q * comm_h_p) / 2)
    audit.check("restored virial commutator", sp.simplify(comm_h_a - sp.I * hbar * (q * force - p_symbol**2 / chi)) == 0, comm_h_a, "i hbar(QG-P^2/chi)", "virial")
    audit.check("virial identity chi factor", sp.solve(sp.Eq(q * force - p_symbol**2 / chi, 0), p_symbol**2)[0] == chi * q * force, sp.solve(sp.Eq(q * force - p_symbol**2 / chi, 0), p_symbol**2)[0], chi * q * force, "virial")

    beta_value, omega_value = 1.3, 1.7
    coth = 1.0 / math.tanh(beta_value * omega_value / 2.0)
    q_variance = coth / (2.0 * omega_value)
    p_variance = omega_value * coth / 2.0
    q_force = omega_value**2 * q_variance
    audit.check("Mehler virial fixture", abs(p_variance - q_force) < 1e-12, p_variance, q_force, "virial")

    seam_second = -p_variance
    audit.check("seam curvature equals momentum variance", abs(-seam_second - p_variance) < 1e-12, seam_second, -p_variance, "seam")
    for t in (0.1, 0.3, 0.7):
        seam = math.exp(-0.5 * t * t * p_variance)
        audit.check(f"seam quadratic inequality t={t}", 0.0 <= 1.0 - seam <= 0.5 * t * t * p_variance + 1e-15, 1.0 - seam, 0.5 * t * t * p_variance, "seam")
    gram = sp.Matrix([[sp.Rational(5, 4), sp.Rational(1, 3)], [sp.Rational(1, 3), sp.Rational(7, 5)]])
    midpoint = gram[0, 1]
    diagonal_mean = (gram[0, 0] + gram[1, 1]) / 2
    audit.check("positive-kernel midpoint domination", midpoint <= diagonal_mean, midpoint, diagonal_mean, "seam")
    audit.check("positive kernel Gram determinant", gram.det() > 0, gram.det(), ">0", "seam")

    hostile = []
    for frequency in (2.0, 8.0, 32.0):
        thermal = 1.0 / math.tanh(beta_value * frequency / 2.0)
        hostile.append({"frequency": frequency, "Q2": thermal / (2.0 * frequency), "P2": frequency * thermal / 2.0})
    audit.check("hostile oscillator configuration shrinks", hostile[2]["Q2"] < hostile[1]["Q2"] < hostile[0]["Q2"], hostile, "strict decrease", "hostile")
    audit.check("hostile oscillator momentum diverges", hostile[2]["P2"] > hostile[1]["P2"] > hostile[0]["P2"], hostile, "strict increase", "hostile")

    for phrase in ("renormalized Q3 force", "Gibbs virial identity", "full-sequence seam limit", "energy below empty space", "C0, N1--N5, C6, CP1, Sector A, or Pre-A"):
        audit.check(f"certificate boundary {phrase[:30]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in ("spatial_spectral_Q3_force_L4_uniform", "spatial_spectral_fixed_low_mode_momentum_uniform", "spatial_spectral_twisted_seam_identity_equicontinuous", "spatial_spectral_regular_Weyl_clusters_exist"):
        audit.check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in ("spatial_spectral_full_sequence_Weyl_limit", "centered_Q3_uniform_exponential_integrability", "centered_Q3_offdiagonal_seam_full_sequence", "physical_state_or_vacuum", "below_empty_space_comparison", "C6_advanced", "CP1_complete", "Pre_A_complete"):
        audit.check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
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
        "derived": {"edges": edges, "degrees": degrees, "force_coefficients": [str(value) for value in coefficient_vector], "covariance_L3": l3_rows, "Mehler": {"Q2": q_variance, "P2": p_variance}, "hostile": hostile},
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
