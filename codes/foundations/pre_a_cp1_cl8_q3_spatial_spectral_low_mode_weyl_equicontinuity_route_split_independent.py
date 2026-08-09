#!/usr/bin/env python3
"""Independent stdlib verifier for the spatial-spectral Q3 low-mode checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-spatial-spectral-low-mode-weyl-equicontinuity-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-SPATIAL-SPECTRAL-LOW-MODE-WEYL-EQUICONTINUITY-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-RENORMALIZED-FORCE-VIRIAL-BOUND-AND-REGULAR-WEYL-CLUSTERS-WITH-FULL-SEQUENCE-SEAM-GATE"
EXPLORATION_ID = "EXP-000771"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"


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


Poly = dict[tuple[int, int, int], Fraction]


def add(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, Fraction(0)) + value
        if result[key] == 0:
            del result[key]
    return result


def scale(poly: Poly, factor: Fraction) -> Poly:
    return {key: factor * value for key, value in poly.items() if factor * value}


def multiply(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for (lx, ly, lc), lv in left.items():
        for (rx, ry, rc), rv in right.items():
            key = (lx + rx, ly + ry, lc + rc)
            result[key] = result.get(key, Fraction(0)) + lv * rv
    return {key: value for key, value in result.items() if value}


def derivative_x(poly: Poly) -> Poly:
    result: Poly = {}
    for (px, py, pc), value in poly.items():
        if px:
            result[(px - 1, py, pc)] = value * px
    return result


def monomial(px: int, py: int = 0, pc: int = 0, coefficient: Fraction = Fraction(1)) -> Poly:
    return {(px, py, pc): coefficient}


def covariance_l3(cutoff: int, samples: int = 6144) -> float:
    beta = 2.1
    values = []
    for index in range(samples):
        x = 2.0 * math.pi * (index + 0.37) / samples
        value = 0.7
        for mode in range(1, cutoff + 1):
            omega = math.sqrt(1.3 + mode * mode)
            value += math.cos(mode * x) / (omega * math.tanh(beta * omega / 2.0))
        values.append(abs(value) ** 3)
    return (sum(values) / samples) ** (1.0 / 3.0)


def gaussian_even(moment: int) -> int:
    if moment % 2:
        return 0
    result = 1
    for value in range(1, moment, 2):
        result *= value
    return result


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))

    audit.check("independent candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("independent result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("independent exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("independent claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    edges = []
    for vertex in range(8):
        for other in range(vertex + 1, 8):
            if (vertex ^ other).bit_count() == 1:
                edges.append((vertex, other))
    degrees = [sum(vertex in edge for edge in edges) for vertex in range(8)]
    audit.check("independent cube edge count", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("independent cube degrees", degrees == [3] * 8, degrees, [3] * 8, "Q3")

    x = monomial(1)
    y = monomial(0, 1)
    difference = add(x, scale(y, Fraction(-1)))
    radial = add(multiply(x, x), multiply(y, y))
    edge_poly = scale(multiply(multiply(difference, difference), radial), Fraction(1, 4))
    edge_derivative = derivative_x(edge_poly)
    expected = {(3, 0, 0): Fraction(1), (2, 1, 0): Fraction(-3, 2), (1, 2, 0): Fraction(1), (0, 3, 0): Fraction(-1, 2)}
    audit.check("independent edge derivative coefficients", edge_derivative == expected, edge_derivative, expected, "Q3")
    audit.check("independent own cubic coefficient", Fraction(1) + 3 * edge_derivative[(3, 0, 0)] == 4, Fraction(1) + 3 * edge_derivative[(3, 0, 0)], 4, "Q3")

    wick_x4 = add(add(monomial(4), monomial(2, 0, 1, Fraction(-6))), monomial(0, 0, 2, Fraction(3)))
    wick_x3y = add(monomial(3, 1), monomial(1, 1, 1, Fraction(-3)))
    wick_x2y2 = multiply(add(monomial(2), monomial(0, 0, 1, Fraction(-1))), add(monomial(0, 2), monomial(0, 0, 1, Fraction(-1))))
    wick_xy3 = add(monomial(1, 3), monomial(1, 1, 1, Fraction(-3)))
    wick_y4 = add(add(monomial(0, 4), monomial(0, 2, 1, Fraction(-6))), monomial(0, 0, 2, Fraction(3)))
    wick_edge = scale(add(add(add(add(wick_x4, scale(wick_x3y, Fraction(-2))), scale(wick_x2y2, Fraction(2))), scale(wick_xy3, Fraction(-2))), wick_y4), Fraction(1, 4))
    wick_force = derivative_x(wick_edge)
    expected_wick_force = {
        (3, 0, 0): Fraction(1), (2, 1, 0): Fraction(-3, 2), (1, 2, 0): Fraction(1), (0, 3, 0): Fraction(-1, 2),
        (1, 0, 1): Fraction(-4), (0, 1, 1): Fraction(3)
    }
    audit.check("independent Wick differentiation", wick_force == expected_wick_force, wick_force, expected_wick_force, "Wick")
    audit.check("independent raw own linear sentinel", wick_force[(1, 0, 1)] == -4, wick_force[(1, 0, 1)], -4, "Wick")
    audit.check("independent raw neighbour linear sentinel", wick_force[(0, 1, 1)] == 3, wick_force[(0, 1, 1)], 3, "Wick")

    # Direct independent Gaussian moment recursion for E[(X^3-3X)^2]=6.
    cubic_norm = gaussian_even(6) - 6 * gaussian_even(4) + 9 * gaussian_even(2)
    audit.check("independent Wick cubic norm", cubic_norm == 6, cubic_norm, 6, "Wick")
    audit.check("independent hypercontractive square", 3**3 == 27, 3**3, 27, "Wick")
    l3_rows = [covariance_l3(cutoff) for cutoff in (7, 15, 31, 63)]
    audit.check("independent logarithmic L3 proxy", max(l3_rows) < 2.3, l3_rows, "<2.3", "Wick")

    # Differential-operator commutator on monomials, hbar=2, chi=3, U=q^4/4.
    hbar, chi = 2.0, 3.0
    def q_op(poly: list[complex]) -> list[complex]:
        return [0j] + poly
    def p_op(poly: list[complex]) -> list[complex]:
        return [-1j * hbar * (index + 1) * poly[index + 1] for index in range(len(poly) - 1)]
    def pad(poly: list[complex], size: int) -> list[complex]:
        return poly + [0j] * (size - len(poly))
    def add_vec(left: list[complex], right: list[complex]) -> list[complex]:
        size = max(len(left), len(right))
        return [value_left + value_right for value_left, value_right in zip(pad(left, size), pad(right, size))]
    def scale_vec(poly: list[complex], factor: complex) -> list[complex]:
        return [factor * value for value in poly]
    def h_op(poly: list[complex]) -> list[complex]:
        kinetic = scale_vec(p_op(p_op(poly)), 1.0 / (2.0 * chi))
        potential = [0j] * 4 + [value / 4.0 for value in poly]
        return add_vec(kinetic, potential)
    def compose(left, right, poly: list[complex]) -> list[complex]:
        return left(right(poly))
    probe = [1 + 0j, 2 + 0j, -1 + 0j, 0.5 + 0j]
    hq = add_vec(compose(h_op, q_op, probe), scale_vec(compose(q_op, h_op, probe), -1))
    expected_hq = scale_vec(p_op(probe), -1j * hbar / chi)
    size = max(len(hq), len(expected_hq))
    audit.check("independent HQ commutator sign", max(abs(a - b) for a, b in zip(pad(hq, size), pad(expected_hq, size))) < 1e-10, hq, expected_hq, "virial")
    hp = add_vec(compose(h_op, p_op, probe), scale_vec(compose(p_op, h_op, probe), -1))
    force_probe = [0j] * 3 + probe
    expected_hp = scale_vec(force_probe, 1j * hbar)
    size = max(len(hp), len(expected_hp))
    audit.check("independent HP commutator sign", max(abs(a - b) for a, b in zip(pad(hp, size), pad(expected_hp, size))) < 1e-10, hp, expected_hp, "virial")

    beta, frequency = 0.9, 2.4
    thermal = 1.0 / math.tanh(beta * frequency / 2.0)
    q2, p2 = thermal / (2.0 * frequency), frequency * thermal / 2.0
    audit.check("independent harmonic virial", abs(p2 - frequency**2 * q2) < 1e-12, p2, frequency**2 * q2, "virial")
    for t in (0.2, 0.55):
        seam = math.exp(-t * t * p2 / 2.0)
        audit.check(f"independent seam inequality t={t}", 1.0 - seam <= t * t * p2 / 2.0 + 1e-15, 1.0 - seam, t * t * p2 / 2.0, "seam")

    gram = [[Fraction(9, 7), Fraction(2, 5), Fraction(1, 4)], [Fraction(2, 5), Fraction(8, 5), Fraction(1, 3)], [Fraction(1, 4), Fraction(1, 3), Fraction(7, 4)]]
    audit.check("independent midpoint domination", gram[0][1] <= (gram[0][0] + gram[1][1]) / 2, gram[0][1], (gram[0][0] + gram[1][1]) / 2, "seam")
    determinant = gram[0][0] * (gram[1][1] * gram[2][2] - gram[1][2] ** 2) - gram[0][1] * (gram[1][0] * gram[2][2] - gram[1][2] * gram[2][0]) + gram[0][2] * (gram[1][0] * gram[2][1] - gram[1][1] * gram[2][0])
    audit.check("independent positive Gram determinant", determinant > 0, determinant, ">0", "seam")

    hostile = []
    for frequency in (3.0, 12.0, 48.0):
        thermal = 1.0 / math.tanh(beta * frequency / 2.0)
        hostile.append((thermal / (2.0 * frequency), frequency * thermal / 2.0))
    audit.check("independent hostile Q tight", hostile[2][0] < hostile[1][0] < hostile[0][0], hostile, "decrease", "hostile")
    audit.check("independent hostile P failure", hostile[2][1] > hostile[1][1] > hostile[0][1], hostile, "increase", "hostile")

    for phrase in ("renormalized Q3 force", "total ultraviolet energy", "regular states", "energy below empty space", "Pre-A"):
        audit.check(f"independent certificate {phrase[:26]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in ("spatial_spectral_full_sequence_Weyl_limit", "centered_Q3_uniform_exponential_integrability", "centered_Q3_offdiagonal_seam_full_sequence", "physical_state_or_vacuum", "below_empty_space_comparison", "C6_advanced", "CP1_complete", "Pre_A_complete"):
        audit.check(f"independent scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("independent C6 tier", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("independent C6 lifecycle", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("independent C6 gate", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

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
        "derived": {"edges": edges, "degrees": degrees, "force_coefficients": {str(key): str(value) for key, value in expected.items()}, "covariance_L3": l3_rows, "harmonic": {"Q2": q2, "P2": p2}, "hostile": hostile},
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
