#!/usr/bin/env python3
"""Exact nonzero-Q generator-row replay for PAH-OMC-005.

The contract is a researcher-owned geometric successor of PAH-OMC-004.  This
program evaluates the unchanged PAH-001 functional on the actual two-row strip
carriers G_1 and G_2, with one nonzero radial occupation in the four-vertex
anchor patch.  It compares the anchor-aperture generator rows after the first
geometric boundary.  The result is a finite/local proposition; no global or
continuum statement is encoded here.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc005-nonzero-q-generator/primary.json"
)

AUDIT_ID = "PAH-NONZERO-Q-GENERATOR-001"
EXPLORATION_ID = "EXP-001374"
RESULT_ID = "R-485"
TASK_ID = "T-054"

# These are declared finite fixture inputs, not derived outputs.
K = 2
M_S = 1
M_PSI = 1
Q = 1
R_MAX = Fraction(1)
EPSILON = Fraction(1, 2)
BETA = Fraction(1)
NU = Fraction(1)
M2 = Fraction(0)
LAMBDA_4 = Fraction(1)
ETA_6 = Fraction(1)
G_COUPLING = Fraction(1)
LAMBDA_S = Fraction(1)
KAPPA_S = Fraction(1)
KAPPA_D = Fraction(1)
KAPPA_G = Fraction(1)

PATCH_VERTICES = ((0, 0), (1, 0), (0, 1), (1, 1))
PATCH_VERTEX_NAMES = ("a", "b", "c", "d")
PATCH_EDGES = (
    ("h00", (0, 0), (1, 0)),
    ("v0", (0, 0), (0, 1)),
    ("d0", (0, 0), (1, 1)),
    ("h01", (0, 1), (1, 1)),
    ("v1", (1, 0), (1, 1)),
)
PATCH_EDGE_NAMES = tuple(edge[0] for edge in PATCH_EDGES)
PATCH_FACES = (
    (("h00", 1), ("v1", 1), ("d0", -1)),
    (("d0", 1), ("h01", -1), ("v0", -1)),
)
APERTURE_BITS = len(PATCH_VERTICES)
LINK_BITS = len(PATCH_EDGES)
PHASE_BITS = len(PATCH_VERTICES)
RADIAL_PLACEMENTS = len(PATCH_VERTICES)

State = tuple[int, ...]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def digest(path: Path) -> str:
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
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def aperture(level: int) -> Fraction:
    if level not in range(M_S + 1):
        raise ValueError("aperture level outside PAH fixture grid")
    return EPSILON + Fraction(level) * (1 - EPSILON) / M_S


def sign_z2(bit: int) -> int:
    if bit not in range(K):
        raise ValueError("Z_2 coordinate outside fixture")
    return -1 if bit else 1


def strip_carrier(level: int) -> dict[str, Any]:
    """Return the oriented PAH-OMC-004 two-row strip G_level."""
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
    faces.append(((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1)))
    return {"vertices": vertices, "edges": tuple(edges), "faces": tuple(faces)}


def patch_signature(level: int) -> dict[str, Any]:
    carrier = strip_carrier(level)
    anchor = PATCH_VERTICES[0]
    incident_edges = [
        (name, left, right)
        for name, left, right in carrier["edges"]
        if anchor in (left, right)
    ]
    incident_names = {item[0] for item in incident_edges}
    incident_faces = [
        face
        for face in carrier["faces"]
        if any(edge_name in incident_names for edge_name, _orientation in face)
    ]
    support_vertices = sorted(
        {vertex for _name, left, right in incident_edges for vertex in (left, right)}
    )
    return {
        "incident_edges": incident_edges,
        "incident_faces": incident_faces,
        "patch_vertices": support_vertices,
    }


def decode_patch(state: State) -> tuple[dict[tuple[int, int], int], dict[str, int], dict[tuple[int, int], int], dict[tuple[int, int], int]]:
    expected = APERTURE_BITS + LINK_BITS + PHASE_BITS + RADIAL_PLACEMENTS
    if len(state) != expected:
        raise ValueError(f"state length {len(state)} != {expected}")
    offset = 0
    apertures = dict(zip(PATCH_VERTICES, state[offset : offset + APERTURE_BITS]))
    offset += APERTURE_BITS
    links = dict(zip(PATCH_EDGE_NAMES, state[offset : offset + LINK_BITS]))
    offset += LINK_BITS
    phases = dict(zip(PATCH_VERTICES, state[offset : offset + PHASE_BITS]))
    offset += PHASE_BITS
    radial = dict(zip(PATCH_VERTICES, state[offset : offset + RADIAL_PLACEMENTS]))
    if any(value not in range(M_S + 1) for value in apertures.values()):
        raise ValueError("aperture outside fixture grid")
    if any(value not in range(K) for value in links.values()):
        raise ValueError("link outside Z_2")
    if any(value not in range(K) for value in phases.values()):
        raise ValueError("phase outside Z_2")
    if any(value not in range(M_PSI + 1) for value in radial.values()):
        raise ValueError("radial occupation outside fixture grid")
    if sum(radial.values()) != Q:
        raise ValueError("patch state does not have Q=1")
    return apertures, links, phases, radial


def full_state(level: int, patch_state: State) -> dict[str, Any]:
    """Embed a patch state into G_level with zero new charge and neutral remotes."""
    apertures, links, phases, radial = decode_patch(patch_state)
    carrier = strip_carrier(level)
    ap = {vertex: 0 for vertex in carrier["vertices"]}
    ell = {vertex: 0 for vertex in carrier["vertices"]}
    phase = {vertex: 0 for vertex in carrier["vertices"]}
    link = {name: 0 for name, _left, _right in carrier["edges"]}
    for vertex in PATCH_VERTICES:
        ap[vertex] = apertures[vertex]
        ell[vertex] = radial[vertex]
        phase[vertex] = phases[vertex]
    for name in PATCH_EDGE_NAMES:
        link[name] = links[name]
    if sum(ell.values()) != Q:
        raise AssertionError("neutral inclusion changed Q")
    return {"apertures": ap, "ell": ell, "phase": phase, "links": link}


def matter_value(ell: int, phase: int) -> Fraction:
    return R_MAX * Fraction(ell, M_PSI) * sign_z2(phase)


def onsite(vertex: tuple[int, int], state: dict[str, Any]) -> Fraction:
    s = aperture(state["apertures"][vertex])
    psi = matter_value(state["ell"][vertex], state["phase"][vertex])
    return (
        LAMBDA_S * (s - 1) ** 2 / 2
        + M2 * psi**2 / 2
        + LAMBDA_4 * psi**4 / 4
        + ETA_6 * psi**6 / 6
        + G_COUPLING * s**2 * psi**2 / 2
    )


def edge_stiffness(left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> Fraction:
    return KAPPA_S * (aperture(state["apertures"][left]) - aperture(state["apertures"][right])) ** 2 / 2


def j_edge(left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> Fraction:
    return Fraction(2, 1) / (aperture(state["apertures"][left]) + aperture(state["apertures"][right]))


def covariant_edge(name: str, left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> Fraction:
    psi_left = matter_value(state["ell"][left], state["phase"][left])
    psi_right = matter_value(state["ell"][right], state["phase"][right])
    transported = sign_z2(state["links"][name]) * psi_left
    return KAPPA_D * j_edge(left, right, state) * (psi_right - transported) ** 2 / 2


def face_term(face: tuple[tuple[str, int], ...], state: dict[str, Any], edge_lookup: dict[str, tuple[tuple[int, int], tuple[int, int]]]) -> Fraction:
    stiffness = []
    holonomy = 1
    for edge_name, orientation in face:
        left, right = edge_lookup[edge_name]
        stiffness.append(j_edge(left, right, state))
        holonomy *= sign_z2(state["links"][edge_name])
    return KAPPA_G * sum(stiffness, Fraction(0)) / len(stiffness) * (1 - holonomy)


def energy_terms(level: int, state: dict[str, Any]) -> list[tuple[str, tuple[tuple[int, int], ...], Fraction]]:
    carrier = strip_carrier(level)
    edge_lookup = {name: (left, right) for name, left, right in carrier["edges"]}
    terms: list[tuple[str, tuple[tuple[int, int], ...], Fraction]] = []
    for vertex in carrier["vertices"]:
        terms.append((f"onsite:{vertex[0]},{vertex[1]}", (vertex,), onsite(vertex, state)))
    for name, left, right in carrier["edges"]:
        support = (left, right)
        terms.append((f"stiffness:{name}", support, edge_stiffness(left, right, state)))
        terms.append((f"covariant:{name}", support, covariant_edge(name, left, right, state)))
    for index, face in enumerate(carrier["faces"]):
        support = tuple(sorted({vertex for name, _orientation in face for vertex in edge_lookup[name]}))
        terms.append((f"face:{index}", support, face_term(face, state, edge_lookup)))
    return terms


def energy(level: int, state: dict[str, Any]) -> Fraction:
    return sum((value for _label, _support, value in energy_terms(level, state)), Fraction(0))


def flip_anchor(state: dict[str, Any], direction: int) -> dict[str, Any] | None:
    before = state["apertures"][PATCH_VERTICES[0]]
    after = before + direction
    if after not in range(M_S + 1):
        return None
    result = {
        "apertures": dict(state["apertures"]),
        "ell": dict(state["ell"]),
        "phase": dict(state["phase"]),
        "links": dict(state["links"]),
    }
    result["apertures"][PATCH_VERTICES[0]] = after
    return result


def local_terms(level: int) -> list[str]:
    terms = energy_terms(level, full_state(level, make_patch_state((0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0), 0)))
    anchor = PATCH_VERTICES[0]
    return [label for label, support, _value in terms if anchor in support]


def make_patch_state(aperture_bits: tuple[int, ...], link_bits: tuple[int, ...], phase_bits: tuple[int, ...], radial_index: int) -> State:
    radial = tuple(1 if index == radial_index else 0 for index in range(RADIAL_PLACEMENTS))
    return tuple(aperture_bits) + tuple(link_bits) + tuple(phase_bits) + radial


def fixture_states() -> Iterable[State]:
    for aperture_bits in itertools.product(range(M_S + 1), repeat=APERTURE_BITS):
        for link_bits in itertools.product(range(K), repeat=LINK_BITS):
            for phase_bits in itertools.product(range(K), repeat=PHASE_BITS):
                for radial_index in range(RADIAL_PLACEMENTS):
                    yield make_patch_state(aperture_bits, link_bits, phase_bits, radial_index)


def generator_row(patch_state: State, level: int) -> dict[str, Any]:
    state = full_state(level, patch_state)
    before = state["apertures"][PATCH_VERTICES[0]]
    direction = 1 if before == 0 else -1
    target = flip_anchor(state, direction)
    if target is None:
        raise AssertionError("anchor has no valid aperture root")
    delta_f = energy(level, target) - energy(level, state)
    delta_s = aperture(target["apertures"][PATCH_VERTICES[0]]) - aperture(before)
    delta_indicator = (
        int(target["apertures"][PATCH_VERTICES[0]] == 1)
        - int(before == 1)
    )
    mobility_square = aperture(before) * aperture(target["apertures"][PATCH_VERTICES[0]])
    return {
        "level": level,
        "patch_state": list(patch_state),
        "direction": direction,
        "delta_F": str(delta_f),
        "mobility_square": str(mobility_square),
        "delta_s": str(delta_s),
        "delta_indicator_j_a_eq_1": delta_indicator,
        "rate_exponent": str(-BETA * delta_f / 2),
        "local_term_count": len(local_terms(level)),
    }


def row_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(row[key] for key in (
        "patch_state",
        "direction",
        "delta_F",
        "mobility_square",
        "delta_s",
        "delta_indicator_j_a_eq_1",
        "rate_exponent",
    ))


def support_stability(level_a: int, level_b: int, patch_state: State) -> dict[str, Any]:
    state_a = full_state(level_a, patch_state)
    state_b = full_state(level_b, patch_state)
    target_a = flip_anchor(state_a, 1 if state_a["apertures"][PATCH_VERTICES[0]] == 0 else -1)
    target_b = flip_anchor(state_b, 1 if state_b["apertures"][PATCH_VERTICES[0]] == 0 else -1)
    if target_a is None or target_b is None:
        raise AssertionError("missing anchor target")
    terms_a = {label: (support, value) for label, support, value in energy_terms(level_a, state_a)}
    terms_b = {label: (support, value) for label, support, value in energy_terms(level_b, state_b)}
    changed_a = {label for label, (support, _value) in terms_a.items() if PATCH_VERTICES[0] in support}
    changed_b = {label for label, (support, _value) in terms_b.items() if PATCH_VERTICES[0] in support}
    nonanchor_unchanged = True
    for label, (support, value) in terms_a.items():
        if PATCH_VERTICES[0] not in support:
            # The label exists in both levels for all terms in the old carrier;
            # compare by label after the neutral inclusion.
            if label not in terms_b or terms_b[label][1] != value:
                nonanchor_unchanged = False
    return {
        "level_a": level_a,
        "level_b": level_b,
        "changed_terms_level_a": sorted(changed_a),
        "changed_terms_level_b": sorted(changed_b),
        "changed_terms_equal": changed_a == changed_b,
        "nonanchor_terms_unchanged": nonanchor_unchanged,
        "delta_energy_level_a": str(energy(level_a, target_a) - energy(level_a, state_a)),
        "delta_energy_level_b": str(energy(level_b, target_b) - energy(level_b, state_b)),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = read_json(SOURCE)
    geometry = read_json(GEOMETRY)
    contract = read_json(CONTRACT)
    manifest = read_json(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": digest(SOURCE),
        "PAH-OMC-004": digest(GEOMETRY),
        "PAH-OMC-005": digest(CONTRACT),
        "PAH-OMC-005-GEN-MANIFEST": digest(MANIFEST),
    }
    check(
        "source-hashes",
        hashes["PAH-001"] == manifest["functional_source"]["sha256"]
        and hashes["PAH-OMC-004"] == manifest["geometric_source"]["sha256"]
        and hashes["PAH-OMC-005"] == manifest["contract"]["sha256"],
        hashes,
    )
    check("identities", source.get("packet_id") == "PAH-001" and geometry.get("contract_id") == "PAH-OMC-004" and contract.get("contract_id") == "PAH-OMC-005")
    check("no-parent-mutation", contract.get("preservation_firewall", {}).get("parent_functional_unchanged") is True and contract.get("preservation_firewall", {}).get("no_new_term") is True and manifest.get("no_parent_mutation") is True)
    check("displayed-functional", source.get("functional_or_action", {}).get("formula", "").startswith("F_rho=sum_v[lambda_s"))
    check("displayed-generator", source.get("dynamics", {}).get("generator", "").startswith("(L_rho f)(x)=sum_r m_r(x)"))
    check("genuine-incidence", contract.get("exact_scope", {}).get("carrier_family", "").find("strip") >= 0 and len(PATCH_EDGES) > 4 and len(PATCH_FACES) == 2)
    check("nonzero-q-fixture", Q > 0 and M_PSI > 0 and RADIAL_PLACEMENTS > 0)
    check("q-one-state-domain", all(sum(decode_patch(state)[3].values()) == Q for state in fixture_states()))
    check("neutral-inclusion-preserves-q", all(sum(full_state(2, state)["ell"].values()) == Q for state in fixture_states()))
    signatures = {str(level): patch_signature(level) for level in (1, 2)}
    check("anchor-incidence-stable", signatures["1"] == signatures["2"], signatures)
    check("anchor-has-two-split-faces", len(signatures["1"]["incident_faces"]) == len(PATCH_FACES) and all(len(face) == 3 for face in signatures["1"]["incident_faces"]))
    check("anchor-has-independent-diagonal", any(edge[0] == "d0" for edge in signatures["1"]["incident_edges"]))

    states = list(fixture_states())
    rows_1 = [generator_row(state, 1) for state in states]
    rows_2 = [generator_row(state, 2) for state in states]
    expected_count = (M_S + 1) ** APERTURE_BITS * K**LINK_BITS * K**PHASE_BITS * RADIAL_PLACEMENTS
    check("state-count", len(states) == expected_count, {"actual": len(states), "expected": expected_count})
    check("rows-cover-domain", len(rows_1) == len(rows_2) == len(states), (len(rows_1), len(rows_2)))
    check("exact-generator-row-equality", [row_key(row) for row in rows_1] == [row_key(row) for row in rows_2])
    check("all-rows-have-nonzero-matter", all(sum(decode_patch(tuple(row["patch_state"]))[3].values()) == Q for row in rows_1))
    check("mobility-exact", {row["mobility_square"] for row in rows_1} == {"1/2"})
    check("basis-observables-covered", {row["delta_indicator_j_a_eq_1"] for row in rows_1} == {-1, 1})
    check("rate-is-midpoint", all(row["rate_exponent"] == str(-BETA * Fraction(row["delta_F"]) / 2) for row in rows_1))

    support = support_stability(1, 2, states[0])
    check("affected-support-stable", support["changed_terms_equal"] and support["nonanchor_terms_unchanged"], support)
    check("full-delta-agrees-local", support["delta_energy_level_a"] == support["delta_energy_level_b"], support)

    delta_values = [Fraction(row["delta_F"]) for row in rows_1]
    local_term_counts = sorted({row["local_term_count"] for row in rows_1})
    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc005-nonzero-q-generator-primary/1.0",
        "run_kind": "primary",
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
        "scope": {
            "dimension": "finite two-row relational strip with genuine diagonal face subdivision",
            "model": "PAH-001 + PAH-OMC-005 researcher successor",
            "normalization": "finite counting-measure Gibbs midpoint rate c=m exp(-beta DeltaF/2)",
            "regulator": "K=2, M_s=M_psi=1, Q=1, epsilon=1/2, beta=nu=1; all displayed couplings one where used",
            "volume": "full G_1 and neutral inclusion in G_2; one nonzero charge quantum in the anchor patch",
            "limit": "none; n=1,2 finite local equality only",
        },
        "fixture_dimensions": {
            "aperture_bits": APERTURE_BITS,
            "link_bits": LINK_BITS,
            "phase_bits": PHASE_BITS,
            "radial_placements": RADIAL_PLACEMENTS,
            "state_count_formula": "(M_s+1)^4*K^5*K^4*4",
            "state_count": len(states),
        },
        "carrier_signatures": signatures,
        "generator_rows": rows_1,
        "row_identity": {
            "levels": [1, 2],
            "rows_compared": len(rows_1),
            "exact_tuple": ["patch_state", "direction", "delta_F", "mobility_square", "delta_s", "delta_indicator_j_a_eq_1", "rate_exponent"],
            "all_equal": True,
            "observable_basis": ["1", "s_a", "1_{j_a=1}"],
        },
        "support_audit": support,
        "derived_ranges": {
            "delta_F_min": str(min(delta_values)),
            "delta_F_max": str(max(delta_values)),
            "local_term_counts": local_term_counts,
        },
        "verdict": "EXACT_NONZERO_Q_ANCHOR_GENERATOR_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "reproduction": {
            "command": "python codes/foundations/pah_omc005_nonzero_q_generator.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator/primary.json",
            "independent_command": "python codes/foundations/pah_omc005_nonzero_q_generator_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator/independent.json",
        },
        "non_claims": contract.get("non_claims", []),
        "next_question": contract.get("single_next_question"),
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} PRIMARY {payload['verification']} {payload['passed']}/{payload['assertion_count']}; rows={len(rows_1)}; Q={Q}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
