#!/usr/bin/env python3
"""Exact family-level PAH-OMC-009 interaction-envelope obstruction.

This is not another finite carrier fixture.  It uses the cofinal strip family
from PAH-OMC-004 and an exact one-parameter R_max sequence.  The selected
aperture root is evaluated with the unchanged PAH-001 functional and midpoint
rate.  The script derives the quadratic coefficient from the source inputs,
then proves that the weighted root-rate lower bound is unbounded.
"""

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


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
START = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc009-uniform-envelope/primary.json"
)

RESULT_ID = "R-489"
EXPLORATION_ID = "EXP-001434"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-009-UNIFORM-ENVELOPE-PRIMARY-001"
B = (1, 0)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def frac(value: Any) -> Fraction:
    return Fraction(str(value))


def parameters(contract: dict[str, Any]) -> dict[str, Any]:
    raw = contract["exact_scope"]["regulator_path"]
    return {
        "K": int(raw["K"]),
        "M_s": int(raw["M_s"]),
        "M_psi": int(raw["M_psi"]),
        "Q": int(raw["Q"]),
        "epsilon": frac(raw["epsilon"]),
        "beta": frac(raw["beta"]),
        "nu": frac(raw["nu"]),
        "m2": frac(raw["m2"]),
        "lambda_4": frac(raw["lambda_4"]),
        "eta_6": frac(raw["eta_6"]),
        "g": frac(raw["g"]),
        "lambda_s": frac(raw["lambda_s"]),
        "kappa_s": frac(raw["kappa_s"]),
        "kappa_D": frac(raw["kappa_D"]),
        "kappa_g": frac(raw["kappa_g"]),
    }


def strip_carrier(level: int) -> dict[str, Any]:
    if level < 0:
        raise ValueError("level must be nonnegative")
    vertices = tuple((i, j) for i in range(level + 2) for j in (0, 1))
    edges: list[tuple[str, tuple[int, int], tuple[int, int]]] = []
    for i in range(level + 1):
        for j in (0, 1):
            edges.append((f"h{i}{j}", (i, j), (i + 1, j)))
    for i in range(level + 2):
        edges.append((f"v{i}", (i, 0), (i, 1)))
    for i in range(level):
        edges.append((f"d{i}", (i, 0), (i + 1, 1)))
    faces: list[tuple[tuple[str, int], ...]] = []
    for i in range(level):
        faces.extend(
            [
                ((f"h{i}0", 1), (f"v{i + 1}", 1), (f"d{i}", -1)),
                ((f"d{i}", 1), (f"h{i}1", -1), (f"v{i}", -1)),
            ]
        )
    i = level
    faces.append(
        ((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1))
    )
    return {"vertices": vertices, "edges": tuple(edges), "faces": tuple(faces)}


def state(level: int, radius: Fraction) -> dict[str, Any]:
    carrier = strip_carrier(level)
    apertures = {vertex: 1 for vertex in carrier["vertices"]}
    apertures[B] = 0
    ell = {vertex: 0 for vertex in carrier["vertices"]}
    ell[B] = 1
    phase = {vertex: 0 for vertex in carrier["vertices"]}
    links = {name: 0 for name, _left, _right in carrier["edges"]}
    result = {
        "apertures": apertures,
        "ell": ell,
        "phase": phase,
        "links": links,
        "radius": radius,
    }
    if sum(ell.values()) != 1:
        raise AssertionError("witness does not preserve Q=1")
    return result


def aperture(level: int, p: dict[str, Any], vertex: tuple[int, int]) -> Fraction:
    return p["epsilon"] + Fraction(level) * (1 - p["epsilon"]) / p["M_s"]


def sign_z2(bit: int) -> int:
    return -1 if bit % 2 else 1


def matter_value(config: dict[str, Any], vertex: tuple[int, int], p: dict[str, Any]) -> Fraction:
    return config["radius"] * Fraction(config["ell"][vertex], p["M_psi"]) * sign_z2(
        config["phase"][vertex]
    )


def onsite(config: dict[str, Any], vertex: tuple[int, int], p: dict[str, Any]) -> Fraction:
    s = aperture(config["apertures"][vertex], p, vertex)
    psi = matter_value(config, vertex, p)
    return (
        p["lambda_s"] * (s - 1) ** 2 / 2
        + p["m2"] * psi**2 / 2
        + p["lambda_4"] * psi**4 / 4
        + p["eta_6"] * psi**6 / 6
        + p["g"] * s**2 * psi**2 / 2
    )


def j_edge(
    config: dict[str, Any], left: tuple[int, int], right: tuple[int, int], p: dict[str, Any]
) -> Fraction:
    return Fraction(2) / (
        aperture(config["apertures"][left], p, left)
        + aperture(config["apertures"][right], p, right)
    )


def covariant(
    config: dict[str, Any],
    name: str,
    left: tuple[int, int],
    right: tuple[int, int],
    p: dict[str, Any],
) -> Fraction:
    psi_left = matter_value(config, left, p)
    psi_right = matter_value(config, right, p)
    transported = sign_z2(config["links"][name]) * psi_left
    return p["kappa_D"] * j_edge(config, left, right, p) * (psi_right - transported) ** 2 / 2


def face_value(
    config: dict[str, Any],
    face: tuple[tuple[str, int], ...],
    edge_lookup: dict[str, tuple[tuple[int, int], tuple[int, int]]],
    p: dict[str, Any],
) -> Fraction:
    stiffness = [j_edge(config, *edge_lookup[name], p) for name, _orientation in face]
    holonomy = 1
    for name, _orientation in face:
        holonomy *= sign_z2(config["links"][name])
    return p["kappa_g"] * sum(stiffness, Fraction(0)) / len(stiffness) * (1 - holonomy)


def energy(config: dict[str, Any], level: int, p: dict[str, Any]) -> Fraction:
    carrier = strip_carrier(level)
    edge_lookup = {name: (left, right) for name, left, right in carrier["edges"]}
    total = sum((onsite(config, vertex, p) for vertex in carrier["vertices"]), Fraction(0))
    for _name, left, right in carrier["edges"]:
        sl = aperture(config["apertures"][left], p, left)
        sr = aperture(config["apertures"][right], p, right)
        total += p["kappa_s"] * (sl - sr) ** 2 / 2
        total += covariant(config, _name, left, right, p)
    for face in carrier["faces"]:
        total += face_value(config, face, edge_lookup, p)
    return total


def raised(config: dict[str, Any]) -> dict[str, Any]:
    result = {key: dict(value) if isinstance(value, dict) else value for key, value in config.items()}
    result["apertures"][B] = 1
    return result


def incident_edges(level: int, vertex: tuple[int, int]) -> list[tuple[str, tuple[int, int], tuple[int, int]]]:
    return [edge for edge in strip_carrier(level)["edges"] if vertex in edge[1:]]


def support(level: int, vertex: tuple[int, int]) -> set[tuple[int, int]]:
    carrier = strip_carrier(level)
    edge_lookup = {name: (left, right) for name, left, right in carrier["edges"]}
    result: set[tuple[int, int]] = {vertex}
    incident = {name for name, left, right in carrier["edges"] if vertex in (left, right)}
    for name in incident:
        result.update(edge_lookup[name])
    for face in carrier["faces"]:
        if any(name in incident for name, _orientation in face):
            for name, _orientation in face:
                result.update(edge_lookup[name])
    return result


def local_formula(p: dict[str, Any], degree: int) -> tuple[Fraction, Fraction]:
    """Return (quadratic coefficient, constant) from the displayed terms."""
    eps = p["epsilon"]
    quadratic = p["g"] * (1 - eps**2) / 2
    quadratic += degree * p["kappa_D"] * (1 - Fraction(2) / (1 + eps)) / 2
    constant = -(1 + degree) * p["lambda_s"] * (1 - eps) ** 2 / 2
    return quadratic, constant


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = read_json(SOURCE)
    geometry = read_json(GEOMETRY)
    start = read_json(START)
    contract = read_json(CONTRACT)
    manifest = read_json(MANIFEST)
    p = parameters(contract)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(GEOMETRY),
        "PAH-OMC-008": sha(START),
        "PAH-OMC-009": sha(CONTRACT),
        "PAH-OMC-009-MANIFEST": sha(MANIFEST),
    }
    pins = manifest.get("functional_source", {}), manifest.get("geometric_source", {}), manifest.get("starting_contract", {})
    check(
        "source-hashes",
        pins[0].get("sha256") == hashes["PAH-001"]
        and pins[1].get("sha256") == hashes["PAH-OMC-004"]
        and pins[2].get("sha256") == hashes["PAH-OMC-008"]
        and manifest.get("contract", {}).get("sha256") == hashes["PAH-OMC-009"],
        hashes,
    )
    check("source-identities", source.get("packet_id") == "PAH-001" and geometry.get("contract_id") == "PAH-OMC-004" and start.get("contract_id") == "PAH-OMC-008" and contract.get("contract_id") == "PAH-OMC-009")
    firewall = contract.get("preservation_firewall", {})
    check("preservation-firewall", all(firewall.get(key) is True for key in ("parent_functional_unchanged", "parent_move_families_unchanged", "parent_mobility_unchanged", "no_new_hamiltonian", "no_counterterm", "no_averaging", "no_rate_fitting", "no_physical_identification")) and manifest.get("no_parent_mutation") is True and manifest.get("no_new_finite_fixture") is True)
    check("displayed-functional", source.get("functional_or_action", {}).get("formula", "").startswith("F_rho=sum_v[lambda_s"))
    check("displayed-rate", source.get("dynamics", {}).get("generator", "").startswith("(L_rho f)(x)=sum_r m_r(x)"))
    degrees = {str(level): len(incident_edges(level, B)) for level in range(2, 10)}
    check("cofinal-incidence", all(value == 4 for value in degrees.values()), degrees)
    witness_states = {str(radius): state(2, Fraction(radius)) for radius in (0, 1, 2, 4, 8)}
    check("fixed-Q-witness", all(sum(config["ell"].values()) == p["Q"] for config in witness_states.values()) and p["Q"] == 1)
    check("aperture-root-admissible", all(config["apertures"][B] == 0 and raised(config)["apertures"][B] == 1 for config in witness_states.values()))

    deltas = {}
    for radius, config in witness_states.items():
        deltas[radius] = energy(raised(config), 2, p) - energy(config, 2, p)
    degree = degrees["2"]
    derived_quadratic, derived_constant = local_formula(p, degree)
    full_quadratic = deltas["1"] - deltas["0"]
    full_constant = deltas["0"]
    check("full-energy-local-polynomial", full_quadratic == derived_quadratic and full_constant == derived_constant, {"full_quadratic": str(full_quadratic), "derived_quadratic": str(derived_quadratic), "full_constant": str(full_constant), "derived_constant": str(derived_constant), "deltas": {key: str(value) for key, value in deltas.items()}})
    check("polynomial-holds-on-sequence", all(value == full_quadratic * Fraction(int(radius)) ** 2 + full_constant for radius, value in deltas.items()))
    rate_exponents = {radius: -p["beta"] * (full_quadratic * Fraction(radius) ** 2 + full_constant) / 2 for radius in (1, 2, 4, 8)}
    check("positive-rate-growth-coefficient", -p["beta"] * full_quadratic / 2 > 0, {"quadratic_rate_coefficient": str(-p["beta"] * full_quadratic / 2)})
    check("strict-exponent-growth", rate_exponents[1] < rate_exponents[2] < rate_exponents[4] < rate_exponents[8], {key: str(value) for key, value in rate_exponents.items()})
    mobility_square = aperture(0, p, B) * aperture(1, p, B)
    root_support = support(2, B)
    root_weight = 1 + len(root_support)
    check("source-mobility", mobility_square == p["epsilon"] and p["nu"] == 1, {"mobility_square": str(mobility_square), "support": sorted(root_support)})
    check("positive-geometric-weight", root_weight >= 1)
    logs = {radius: math.log(root_weight) + 0.5 * math.log(float(mobility_square)) + float(exponent) for radius, exponent in rate_exponents.items()}
    check("weighted-lower-bound-grows", logs[1] < logs[2] < logs[4] < logs[8], {key: value for key, value in logs.items()})
    check("envelope-fails", -p["beta"] * full_quadratic / 2 > 0 and root_weight > 0)

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc009-uniform-envelope-primary/1.0",
        "run_kind": "primary",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": hashes,
        "verdict": "NEGATIVE_RESULT_RMAX_UNIFORM_ENVELOPE",
        "classification": "EXACT_FAMILY_LEVEL_RATE_DIVERGENCE",
        "scope": contract["exact_scope"],
        "family": {"levels_checked_for_incidence": [2, 3, 4, 5, 6, 7, 8, 9], "cofinal_definition": contract["exact_scope"]["carrier_family"]},
        "witness": {
            "vertex": list(B),
            "degree": degree,
            "root": "AP((1,0),+1)",
            "support": [list(vertex) for vertex in sorted(root_support)],
            "weight": root_weight,
            "mobility_square": str(mobility_square),
            "delta_F": {key: str(value) for key, value in deltas.items()},
            "quadratic_coefficient": str(full_quadratic),
            "constant": str(full_constant),
            "rate_exponent": {str(key): str(value) for key, value in rate_exponents.items()},
            "weighted_rate_log": logs,
            "divergence_certificate": "positive quadratic coefficient in -beta*DeltaF/2, hence the exact midpoint rate and any positive support weight diverge as R_max tends to infinity",
        },
        "eventual_intertwining": {"status": "NOT_DECIDED_AFTER_ENVELOPE_FAILURE", "reason": "The requested conjunction is already rejected by the exact rate envelope divergence; no repair or extra boundary calculation was introduced."},
        "claim_bearing": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "scientific_transition": False,
        "non_claims": contract["non_claims"],
        "reproduction": {"command": "python codes/foundations/pah_omc009_uniform_envelope.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc009-uniform-envelope/primary.json"},
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; delta={full_quadratic}*R^2+({full_constant}); rate-coefficient={-p['beta']*full_quadratic/2}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
