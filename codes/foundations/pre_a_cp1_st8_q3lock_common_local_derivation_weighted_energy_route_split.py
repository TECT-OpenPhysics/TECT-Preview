#!/usr/bin/env python3
"""Primary exact verifier for the ST8/Q3LOCK weighted-energy route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from itertools import combinations, product
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split-manifest.json"
CERTIFICATE = REPO / "strategy/pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split-certificate-260810.md"
PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-os-dynamics-ground-gap-counterterm-empty-route-split-manifest.json"
SLUG = "pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split"
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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})


def q3_edges() -> tuple[list[tuple[int, ...]], list[tuple[int, int]]]:
    vertices = list(product((0, 1), repeat=3))
    edges = [
        (left, right)
        for left, right in combinations(range(len(vertices)), 2)
        if sum(a != b for a, b in zip(vertices[left], vertices[right])) == 1
    ]
    return vertices, edges


def derive_quartic() -> dict[str, Any]:
    vertices, edges = q3_edges()
    q = sp.symbols("q0:8", real=True)
    g, lam, t = sp.symbols("g lambda t", positive=True)
    quartic = g * sum(value**4 for value in q) / 4
    quartic += lam * sum((q[i] - q[j]) ** 2 * (q[i] ** 2 + q[j] ** 2) for i, j in edges) / 4
    ray = sp.simplify(quartic.subs({q[0]: t, **{q[index]: 0 for index in range(1, 8)}}))
    ray_hessian = sp.diff(ray, t, 2)
    coercivity_sos = sp.expand(
        8 * sum(value**4 for value in q)
        - sum(value**2 for value in q) ** 2
        - sum((q[i] ** 2 - q[j] ** 2) ** 2 for i, j in combinations(range(8), 2))
    )
    euler = sp.simplify(sum(value * sp.diff(quartic, value) for value in q) - 4 * quartic)
    return {
        "vertices": vertices,
        "edges": edges,
        "q": q,
        "g": g,
        "lambda": lam,
        "t": t,
        "quartic": quartic,
        "coordinate_ray": ray,
        "coordinate_ray_hessian": ray_hessian,
        "coercivity_sos_residual": coercivity_sos,
        "euler_residual": euler,
    }


def derive_local_current() -> dict[str, Any]:
    x, y, px, py, chi, c = sp.symbols("x y px py chi c", positive=True)
    ux = sp.Function("U")(x)
    uy = sp.Function("U")(y)
    hamiltonian = px**2 / (2 * chi) + py**2 / (2 * chi) + ux + uy + c * (x - y) ** 2 / 2
    local_x = px**2 / (2 * chi) + ux + c * (x - y) ** 2 / 4
    poisson = sum(
        sp.diff(local_x, coordinate) * sp.diff(hamiltonian, momentum)
        - sp.diff(local_x, momentum) * sp.diff(hamiltonian, coordinate)
        for coordinate, momentum in ((x, px), (y, py))
    )
    expected = -c * (px + py) * (x - y) / (2 * chi)
    p_total, relative = sp.symbols("P R", real=True)
    lower_energy = p_total**2 / (4 * chi) + c * relative**2 / 2
    sharp = sp.sqrt(c / (2 * chi))
    current = c * p_total * relative / (2 * chi)
    plus_square = sp.expand(lower_energy - current / sharp)
    minus_square = sp.expand(lower_energy + current / sharp)
    expected_plus = sp.expand((p_total / (2 * sp.sqrt(chi)) - sp.sqrt(c / 2) * relative) ** 2)
    expected_minus = sp.expand((p_total / (2 * sp.sqrt(chi)) + sp.sqrt(c / 2) * relative) ** 2)
    return {
        "poisson": sp.simplify(poisson),
        "expected_poisson": expected,
        "sharp_constant": sharp,
        "plus_residual": sp.simplify(plus_square - expected_plus),
        "minus_residual": sp.simplify(minus_square - expected_minus),
    }


def derive_scalar_envelopes() -> dict[str, Any]:
    rho, epsilon, gamma, c = sp.symbols("rho epsilon gamma c", positive=True)
    q_maximizer = sp.solve(sp.diff(rho**2 - epsilon * gamma * rho**4, rho), rho)
    positive_q = next(value for value in q_maximizer if value.is_positive)
    q_maximum = sp.simplify((rho**2 - epsilon * gamma * rho**4).subs(rho, positive_q))
    s, t = sp.symbols("s t", nonnegative=True)
    dot_envelope = c * (s + t) / 2 - epsilon * gamma * (s**2 + t**2)
    stationary = {s: c / (4 * epsilon * gamma), t: c / (4 * epsilon * gamma)}
    dot_maximum = sp.simplify(dot_envelope.subs(stationary))
    return {"q_maximum": q_maximum, "c_dot_maximum": dot_maximum}


def run() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")

    audit.check("manifest schema", manifest["schema"].endswith("/1.0"), manifest["schema"], "*/1.0", "provenance")
    audit.check("parent exploration", manifest["parent_exploration_id"] == parent["exploration_id"], manifest["parent_exploration_id"], parent["exploration_id"], "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, False, False, "scope")
    audit.check("certificate result id", manifest["result_id"] in certificate, manifest["result_id"] in certificate, True, "provenance")

    quartic = derive_quartic()
    degrees = [sum(index in edge for edge in quartic["edges"]) for index in range(8)]
    audit.check("Q3 vertex count", len(quartic["vertices"]) == 8, len(quartic["vertices"]), 8, "quartic")
    audit.check("Q3 edge count", len(quartic["edges"]) == 12, len(quartic["edges"]), 12, "quartic")
    audit.check("Q3 degree", degrees == [3] * 8, degrees, [3] * 8, "quartic")
    expected_ray = (quartic["g"] + 3 * quartic["lambda"]) * quartic["t"] ** 4 / 4
    audit.check("coordinate-ray quartic", sp.simplify(quartic["coordinate_ray"] - expected_ray) == 0, str(quartic["coordinate_ray"]), str(expected_ray), "quartic")
    expected_hessian = 3 * (quartic["g"] + 3 * quartic["lambda"]) * quartic["t"] ** 2
    audit.check("coordinate-ray Hessian", sp.simplify(quartic["coordinate_ray_hessian"] - expected_hessian) == 0, str(quartic["coordinate_ray_hessian"]), str(expected_hessian), "quartic")
    audit.check("eight-component coercivity SOS", quartic["coercivity_sos_residual"] == 0, str(quartic["coercivity_sos_residual"]), "0", "coercivity")
    audit.check("quartic Euler identity", quartic["euler_residual"] == 0, str(quartic["euler_residual"]), "0", "resolvent")

    envelopes = derive_scalar_envelopes()
    eps, gam, cc = sp.symbols("epsilon gamma c", positive=True)
    audit.check("single-site Young constant", sp.simplify(envelopes["q_maximum"] - 1 / (4 * eps * gam)) == 0, str(envelopes["q_maximum"]), "1/(4*epsilon*gamma)", "coercivity")
    audit.check("bond-dot Young constant", sp.simplify(envelopes["c_dot_maximum"] - cc**2 / (8 * eps * gam)) == 0, str(envelopes["c_dot_maximum"]), "c^2/(8*epsilon*gamma)", "coercivity")
    audit.check("source envelope is a maximum", manifest["source_uniform_coercivity"]["C_gamma"].startswith("max_"), manifest["source_uniform_coercivity"]["C_gamma"], "max_*", "coercivity")

    current = derive_local_current()
    audit.check("local current sign and coefficient", sp.simplify(current["poisson"] - current["expected_poisson"]) == 0, str(current["poisson"]), str(current["expected_poisson"]), "current")
    audit.check("sharp current plus square", current["plus_residual"] == 0, str(current["plus_residual"]), "0", "current")
    audit.check("sharp current minus square", current["minus_residual"] == 0, str(current["minus_residual"]), "0", "current")
    audit.check("sharp current constant in manifest", "sqrt(c/(2chi))" in manifest["weighted_first_local_energy"]["current_form_bound"], manifest["weighted_first_local_energy"]["current_form_bound"], "sqrt(c/(2chi))", "current")
    audit.check("cubic lattice degree factor", manifest["weighted_first_local_energy"]["three_dimensional_growth_bound"].startswith("tau_t^Lambda(E_f)<=exp[6 "), manifest["weighted_first_local_energy"]["three_dimensional_growth_bound"], "degree 6", "weighted")

    obstruction = manifest["fourier_cutoff_obstruction"]
    audit.check("Fourier second-moment lower bound", obstruction["lower_bound"] == "kappa_R>=3(g+3lambda)R^2", obstruction["lower_bound"], "kappa_R>=3(g+3lambda)R^2", "cutoff")
    audit.check("cutoff obstruction scoped", "does not refute exact common dynamics" in obstruction["scope"], obstruction["scope"], "scoped route obstruction", "scope")
    resolvent = manifest["basic_resolvent_core_obstruction"]
    resolvent_lemma_complete = (
        "4s^3 W4(a)" in resolvent["cubic_growth"]
        and "Im(z) nonzero" in resolvent["resolvent"]
        and "s-independent norms" in resolvent["bounded_input_test"]
        and "R^3" in resolvent["cutoff_norm_lower_bound"]
    )
    audit.check("basic resolvent cubic growth", resolvent_lemma_complete, resolvent, "nonreal-z bounded-input R^3 lower-bound lemma", "resolvent")
    audit.check("basic resolvent obstruction scoped", "not finite-time resolvent-algebra invariance" in resolvent["scope"], resolvent["scope"], "scoped route obstruction", "scope")

    scope = manifest["scope"]
    audit.check("local derivation closed", scope["common_local_polynomial_derivation"] is True, True, True, "scope")
    audit.check("first energy cone closed", scope["weighted_first_local_energy_cone"] is True, True, True, "scope")
    for key in (
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
    ):
        audit.check(f"open scope {key}", scope[key] is False, scope[key], False, "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split-primary-result/1.0",
        "script_version": __version__,
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "derived": {
            "Q3_vertices": len(quartic["vertices"]),
            "Q3_edges": len(quartic["edges"]),
            "Q3_degrees": degrees,
            "coordinate_ray_quartic": str(quartic["coordinate_ray"]),
            "coordinate_ray_hessian": str(quartic["coordinate_ray_hessian"]),
            "current_poisson": str(current["poisson"]),
            "sharp_current_constant": str(current["sharp_constant"]),
            "weighted_degree": 6,
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
