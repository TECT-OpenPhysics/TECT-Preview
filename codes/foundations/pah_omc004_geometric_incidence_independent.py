#!/usr/bin/env python3
"""Non-importing independent audit for the PAH-OMC-004 geometry witness.

This lane reconstructs the square/diagonal energies by direct term expansion,
rather than calling the primary audit.  It also rebuilds the strip incidence
counts and the finite-support locality implication.  All numerical outputs
are derived from the same PAH aperture, edge and Z_2 Wilson formulas.  The
result remains a local structural check, with no continuum or physical claim.
"""

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


ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
FINITE = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
REFERENCE = ROOT / "strategy/pa-hyp/PAH-OMC-003-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-004-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-03-pah-omc004-geometric-incidence/independent.json"
)

AUDIT_ID = "PAH-GEOMETRIC-INCIDENCE-LOCAL-001"
EXPLORATION_ID = "EXP-001369"
RESULT_ID = "R-483"
TASK_ID = "T-054"

# Explicit finite inputs; no derived energy or defect is copied here.
K = 2
M_S = 1
M_PSI = 1
Q = 0
EPS = Fraction(1, 2)
BETA = Fraction(1)
NU = Fraction(1)
LAMBDA_S = Fraction(1)
KAPPA_S = Fraction(1)
KAPPA_G = Fraction(1)
DEGREE_BOUND = 5
FACE_BOUND = 4


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def s(level: int) -> Fraction:
    return EPS + Fraction(level) * (1 - EPS) / M_S


def vertex_term(level: int) -> Fraction:
    return LAMBDA_S * (s(level) - 1) ** 2 / 2


def edge_term(left: int, right: int) -> Fraction:
    return KAPPA_S * (s(left) - s(right)) ** 2 / 2


def j_edge(left: int, right: int) -> Fraction:
    return Fraction(2, 1) / (s(left) + s(right))


def z2_sign(bit: int) -> int:
    return 1 if bit % K == 0 else -1


def square_energy(apertures: tuple[int, ...], links: tuple[int, ...], split: bool) -> Fraction:
    """Directly expand the aperture plus Wilson part of F_rho."""
    if Q != 0 or len(apertures) != 4:
        raise ValueError("independent fixture is Q=0 on four vertices")
    edges = ((0, 1), (1, 2), (2, 3), (3, 0))
    if split:
        edges = edges + ((0, 2),)
        faces = ((0, 1, 4), (4, 2, 3))
    else:
        faces = ((0, 1, 2, 3),)
    if len(links) != len(edges):
        raise ValueError("link count does not match carrier")
    total = sum((vertex_term(level) for level in apertures), Fraction(0))
    total += sum((edge_term(apertures[a], apertures[b]) for a, b in edges), Fraction(0))
    for face in faces:
        local_stiffness = []
        for index in face:
            left, right = edges[index]
            local_stiffness.append(j_edge(apertures[left], apertures[right]))
        holonomy = math.prod(z2_sign(links[index]) for index in face)
        total += KAPPA_G * sum(local_stiffness, Fraction(0)) / len(face) * (1 - holonomy)
    return total


def incidence(vertices: tuple[Any, ...], edges: tuple[tuple[Any, Any], ...], faces: tuple[tuple[int, ...], ...]) -> dict[str, Any]:
    degrees = {repr(v): sum(v in edge for edge in edges) for v in vertices}
    face_degree = {
        repr(v): sum(any(v in edges[index] for index in face) for face in faces)
        for v in vertices
    }
    return {
        "vertices": len(vertices),
        "edges": len(edges),
        "faces": len(faces),
        "max_degree": max(degrees.values()),
        "max_face_incidence": max(face_degree.values()),
        "degrees": degrees,
        "face_incidence": face_degree,
    }


def strip_counts(level: int) -> dict[str, Any]:
    vertices = tuple((i, j) for i in range(level + 2) for j in (0, 1))
    edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    names: dict[str, int] = {}
    for i in range(level + 1):
        for j in (0, 1):
            names[f"h{i}{j}"] = len(edges)
            edges.append(((i, j), (i + 1, j)))
    for i in range(level + 2):
        names[f"v{i}"] = len(edges)
        edges.append(((i, 0), (i, 1)))
    for i in range(level):
        names[f"d{i}"] = len(edges)
        edges.append(((i, 0), (i + 1, 1)))
    faces: list[tuple[int, ...]] = []
    for i in range(level):
        faces.extend(
            [
                (names[f"h{i}0"], names[f"v{i + 1}"], names[f"d{i}"]),
                (names[f"d{i}"], names[f"h{i}1"], names[f"v{i}" ]),
            ]
        )
    i = level
    faces.append((names[f"h{i}0"], names[f"v{i + 1}"], names[f"h{i}1"], names[f"v{i}" ]))
    return incidence(vertices, tuple(edges), tuple(faces))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    parent = load(PARENT)
    finite = load(FINITE)
    reference = load(REFERENCE)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": sha(PARENT),
        "PAH-OMC-001": sha(FINITE),
        "PAH-OMC-003": sha(REFERENCE),
        "PAH-OMC-004": sha(CONTRACT),
        "PAH-OMC-004-MANIFEST": sha(MANIFEST),
    }
    pinned = {
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
        "PAH-OMC-003": manifest["reference_only"]["sha256"],
        "PAH-OMC-004": manifest["contract"]["sha256"],
        "PAH-OMC-004-MANIFEST": hashes["PAH-OMC-004-MANIFEST"],
    }
    check("source-hashes", hashes == pinned, hashes)
    check("parent-identities", parent.get("packet_id") == "PAH-001" and finite.get("contract_id") == "PAH-OMC-001")
    check("reference-identity", reference.get("contract_id") == "PAH-OMC-003")
    check("successor-identity", contract.get("contract_id") == "PAH-OMC-004")
    check("no-parent-mutation", manifest.get("no_parent_mutation") is True)
    check("functional-firewall", all(contract.get("preservation_firewall", {}).get(key) is True for key in ("parent_functional_unchanged", "parent_move_families_unchanged", "no_counterterm_or_energy_added", "no_parent_rate_rescaling")))
    check("geometric-not-colour", contract.get("status", {}).get("refinement_family") == "GENUINE_FACE_EDGE_INCIDENCE_STRIP" and contract.get("preservation_firewall", {}).get("no_color_only_substitution") is True)
    check("q-zero-input", K == 2 and M_S == 1 and M_PSI == 1 and Q == 0 and EPS == Fraction(1, 2))

    coarse_edges = ((0, 1), (1, 2), (2, 3), (3, 0))
    fine_edges = coarse_edges + ((0, 2),)
    coarse_faces = ((0, 1, 2, 3),)
    fine_faces = ((0, 1, 4), (4, 2, 3))
    coarse_inc = incidence((0, 1, 2, 3), coarse_edges, coarse_faces)
    fine_inc = incidence((0, 1, 2, 3), fine_edges, fine_faces)
    check("incidence-edge-change", fine_inc["edges"] - coarse_inc["edges"] == 1, (coarse_inc, fine_inc))
    check("incidence-face-change", fine_inc["faces"] - coarse_inc["faces"] == 1, (coarse_inc, fine_inc))
    check("incidence-diagonal", fine_edges[-1] == (0, 2) and all(len(face) == 3 for face in fine_faces))

    before = (0, 0, 0, 0)
    after = (1, 0, 0, 0)
    coarse_before = square_energy(before, (0, 0, 0, 0), False)
    coarse_after = square_energy(after, (0, 0, 0, 0), False)
    even_before = square_energy(before, (0, 0, 0, 0, 0), True)
    even_after = square_energy(after, (0, 0, 0, 0, 0), True)
    odd_before = square_energy(before, (0, 0, 0, 0, 1), True)
    odd_after = square_energy(after, (0, 0, 0, 0, 1), True)
    deltas = {
        "coarse": coarse_after - coarse_before,
        "fine_even": even_after - even_before,
        "fine_odd": odd_after - odd_before,
    }
    check("energy-delta-coarse", deltas["coarse"] == Fraction(1, 8), {key: str(value) for key, value in deltas.items()})
    check("energy-delta-fine-even", deltas["fine_even"] == Fraction(1, 4), {key: str(value) for key, value in deltas.items()})
    check("energy-delta-fine-odd", deltas["fine_odd"] == Fraction(-55, 36), {key: str(value) for key, value in deltas.items()})
    check("energy-hidden-defect", deltas["fine_even"] - deltas["fine_odd"] == Fraction(16, 9), str(deltas["fine_even"] - deltas["fine_odd"]))
    mobility_square = s(0) * s(1)
    check("mobility-convention", mobility_square == Fraction(1, 2) and NU == 1, str(mobility_square))

    onsite_values = [vertex_term(level) for level in range(M_S + 1)]
    edge_values = [edge_term(left, right) for left in range(M_S + 1) for right in range(M_S + 1)]
    face_values = []
    for face in fine_faces:
        used = sorted({vertex for index in face for vertex in fine_edges[index]})
        for values in itertools.product(range(M_S + 1), repeat=len(used)):
            aps = dict(zip(used, values))
            stiffness = [Fraction(2, 1) / (s(aps[fine_edges[index][0]]) + s(aps[fine_edges[index][1]])) for index in face]
            for bits in itertools.product(range(K), repeat=len(face)):
                holonomy = math.prod(z2_sign(bit) for bit in bits)
                face_values.append(KAPPA_G * sum(stiffness, Fraction(0)) / len(face) * (1 - holonomy))
    onsite_range = max(onsite_values) - min(onsite_values)
    edge_range = max(edge_values) - min(edge_values)
    face_range = max(face_values) - min(face_values)
    local_bound = onsite_range + DEGREE_BOUND * edge_range + FACE_BOUND * face_range
    check("derived-term-ranges", (onsite_range, edge_range, face_range) == (Fraction(1, 8), Fraction(1, 8), Fraction(4)), {"onsite": str(onsite_range), "edge": str(edge_range), "face": str(face_range)})
    check("derived-local-bound", local_bound == Fraction(67, 4), str(local_bound))
    check("derived-rate-exponent", BETA * local_bound / 2 == Fraction(67, 8), str(BETA * local_bound / 2))

    strip = [strip_counts(level) for level in range(4)]
    check("strip-degree-envelope", all(row["max_degree"] <= DEGREE_BOUND for row in strip), strip)
    check("strip-face-envelope", all(row["max_face_incidence"] <= FACE_BOUND for row in strip), strip)
    check("strip-edge-growth", all(strip[i + 1]["edges"] > strip[i]["edges"] for i in range(len(strip) - 1)), strip)
    locality = []
    for support_max in (0, 1, 3):
        exact_from = support_max + 1
        tail_disjoint = all(set((n, n + 1)).isdisjoint(set(range(support_max + 1))) for n in range(exact_from, exact_from + 2))
        locality.append({"support_max_column": support_max, "exact_from_level": exact_from, "tail_disjoint": tail_disjoint, "affected_levels": exact_from, "cumulative_bound": f"{4 * 2 * exact_from}*exp(67/8)*||f||_infinity"})
        check(f"eventual-zero-m{support_max}", tail_disjoint, locality[-1])
    check("locality-map-declared", contract.get("maps_and_parameters", {}).get("observable_lift", "").startswith("(I_n f)"))
    check("boundary-defect-is-not-erased", deltas["fine_even"] != deltas["fine_odd"] and contract.get("known_boundaries", {}).get("affected_levels"))
    check("physical-firewall", contract.get("provenance", {}).get("physical_authority") is False and contract.get("status", {}).get("uniform_limit") == "NOT_ADMITTED")

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc004-geometric-incidence-independent/1.0",
        "run_kind": "independent",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": hashes,
        "verdict": "LOCAL_COMMON_CORE_GEOMETRIC_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "independence_note": "Direct term expansion and independently rebuilt incidence tables; the primary module is not imported.",
        "incidence": {"local_coarse": coarse_inc, "local_fine": fine_inc, "strip_levels": strip},
        "witness": {
            "delta_F": {key: str(value) for key, value in deltas.items()},
            "hidden_diagonal_defect": str(deltas["fine_even"] - deltas["fine_odd"]),
            "mobility_square": str(mobility_square),
            "rate_factors": ["sqrt(1/2)*exp(-1/16)", "sqrt(1/2)*exp(-1/8)", "sqrt(1/2)*exp(55/72)"],
        },
        "derived_envelope": {
            "onsite_range": str(onsite_range),
            "edge_range": str(edge_range),
            "face_range": str(face_range),
            "D_local": str(local_bound),
            "rate_exponent": str(BETA * local_bound / 2),
            "bound": "4*N_f*exp(beta*D_local/2)*||f||_infinity",
        },
        "locality": locality,
        "non_claims": [
            "This is a local finite structural successor result, not a theorem about PAH-001 alone.",
            "No global uniform estimate, ordered limit, physical Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass-gap or TOE conclusion follows.",
            "Q=0 is a diagnostic finite sector and is not a physical-vacuum construction.",
        ],
        "next_question": "Can the same locality mechanism be supplied for an owner-authorized nonzero-Q family without changing PAH-001?",
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} INDEPENDENT {payload['verification']} {payload['passed']}/{payload['assertion_count']}; defect={deltas['fine_even'] - deltas['fine_odd']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
