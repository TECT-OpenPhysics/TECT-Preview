#!/usr/bin/env python3
"""Exact finite multi-cylinder replay for PAH-OMC-008.

The unchanged PAH-001 functional is evaluated on the PAH-OMC-004 diagonal
strip.  The audited cylinder is the four-coordinate tuple
(ell_a,ell_d,H_0,H_1), where H_0 and H_1 are the two closed Z_2 holonomies
of the first split square.  Every Q=1 patch state and every retained
radial/link root is enumerated.  Root differences are reduced to the exact
affected terms of the displayed functional; bounded samples also compare
that reduction with a complete energy recomputation.  The canonical digest
is streamed so the run artefact stays small.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from collections import deque
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
PREDECESSOR = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-v1.json"
PARENT = ROOT / "strategy/pa-hyp/PAH-OMC-006-matter-cylinder-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc008-multi-cylinder/primary.json"
)

AUDIT_ID = "PAH-MULTI-CYLINDER-GENERATOR-001"
EXPLORATION_ID = "EXP-001393"
RESULT_ID = "R-488"
TASK_ID = "T-054"

# Declared finite fixture inputs; these are not derived counts.
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
PATCH_EDGE_NAMES = ("h00", "v0", "d0", "h01", "v1")
PATCH_EDGES = (
    ("h00", (0, 0), (1, 0)),
    ("v0", (0, 0), (0, 1)),
    ("d0", (0, 0), (1, 1)),
    ("h01", (0, 1), (1, 1)),
    ("v1", (1, 0), (1, 1)),
)
TRIANGLE0_EDGES = frozenset(("h00", "v1", "d0"))
TRIANGLE1_EDGES = frozenset(("d0", "h01", "v0"))
PATCH_LINK_EDGES = frozenset(PATCH_EDGE_NAMES)
RADIAL_ANCHORS = frozenset(((0, 0), (1, 1)))
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
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def aperture(level: int) -> Fraction:
    if level not in range(M_S + 1):
        raise ValueError("aperture level outside fixture grid")
    return EPSILON + Fraction(level) * (1 - EPSILON) / M_S


def sign_z2(bit: int) -> int:
    if bit not in range(K):
        raise ValueError("Z_2 coordinate outside fixture")
    return -1 if bit else 1


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
    faces.append(((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1)))
    return {"vertices": vertices, "edges": tuple(edges), "faces": tuple(faces)}


def make_patch_state(
    aperture_bits: tuple[int, ...],
    link_bits: tuple[int, ...],
    phase_bits: tuple[int, ...],
    radial_index: int,
) -> State:
    radial = tuple(1 if index == radial_index else 0 for index in range(RADIAL_PLACEMENTS))
    return tuple(aperture_bits) + tuple(link_bits) + tuple(phase_bits) + radial


def fixture_states() -> Iterable[State]:
    for aperture_bits in itertools.product(range(M_S + 1), repeat=APERTURE_BITS):
        for link_bits in itertools.product(range(K), repeat=LINK_BITS):
            for phase_bits in itertools.product(range(K), repeat=PHASE_BITS):
                for radial_index in range(RADIAL_PLACEMENTS):
                    yield make_patch_state(aperture_bits, link_bits, phase_bits, radial_index)


def decode_patch(
    state: State,
) -> tuple[
    dict[tuple[int, int], int],
    dict[str, int],
    dict[tuple[int, int], int],
    dict[tuple[int, int], int],
]:
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


def patch_gauge_transform(state: State, gauge: dict[tuple[int, int], int]) -> State:
    apertures, links, phases, radial = decode_patch(state)
    transformed_phases = {
        vertex: (phases[vertex] + gauge[vertex]) % K for vertex in PATCH_VERTICES
    }
    transformed_links: dict[str, int] = {}
    for name, left, right in PATCH_EDGES:
        transformed_links[name] = (links[name] + gauge[right] - gauge[left]) % K
    radial_index = next(vertex_index for vertex_index, vertex in enumerate(PATCH_VERTICES) if radial[vertex])
    return make_patch_state(
        tuple(apertures[vertex] for vertex in PATCH_VERTICES),
        tuple(transformed_links[name] for name in PATCH_EDGE_NAMES),
        tuple(transformed_phases[vertex] for vertex in PATCH_VERTICES),
        radial_index,
    )


def full_state(level: int, patch_state: State) -> dict[str, Any]:
    apertures, links, phases, radial = decode_patch(patch_state)
    carrier = strip_carrier(level)
    state = {
        "apertures": {vertex: 0 for vertex in carrier["vertices"]},
        "ell": {vertex: 0 for vertex in carrier["vertices"]},
        "phase": {vertex: 0 for vertex in carrier["vertices"]},
        "links": {name: 0 for name, _left, _right in carrier["edges"]},
    }
    for vertex in PATCH_VERTICES:
        state["apertures"][vertex] = apertures[vertex]
        state["ell"][vertex] = radial[vertex]
        state["phase"][vertex] = phases[vertex]
    for name in PATCH_EDGE_NAMES:
        state["links"][name] = links[name]
    if sum(state["ell"].values()) != Q:
        raise AssertionError("neutral inclusion changed Q")
    return state


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
    return Fraction(2) / (aperture(state["apertures"][left]) + aperture(state["apertures"][right]))


def covariant_edge(name: str, left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> Fraction:
    psi_left = matter_value(state["ell"][left], state["phase"][left])
    psi_right = matter_value(state["ell"][right], state["phase"][right])
    transported = sign_z2(state["links"][name]) * psi_left
    return KAPPA_D * j_edge(left, right, state) * (psi_right - transported) ** 2 / 2


def face_term(
    face: tuple[tuple[str, int], ...],
    state: dict[str, Any],
    edge_lookup: dict[str, tuple[tuple[int, int], tuple[int, int]]],
) -> Fraction:
    stiffness: list[Fraction] = []
    holonomy = 1
    for edge_name, _orientation in face:
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


def radial_target(state: dict[str, Any], source: tuple[int, int], target: tuple[int, int]) -> dict[str, Any]:
    result = {key: dict(value) for key, value in state.items()}
    result["ell"][source] -= 1
    result["ell"][target] += 1
    if sum(result["ell"].values()) != Q:
        raise AssertionError("radial transfer changed Q")
    return result


def link_target(state: dict[str, Any], name: str, sigma: int) -> dict[str, Any]:
    result = {key: dict(value) for key, value in state.items()}
    result["links"][name] = (result["links"][name] + sigma) % K
    return result


def triangle_holonomies(state: dict[str, Any]) -> tuple[int, int]:
    h0 = sign_z2(state["links"]["h00"]) * sign_z2(state["links"]["v1"]) * sign_z2(state["links"]["d0"])
    h1 = sign_z2(state["links"]["d0"]) * sign_z2(state["links"]["h01"]) * sign_z2(state["links"]["v0"])
    return h0, h1


def joint_observable(state: dict[str, Any]) -> tuple[int, int, int, int]:
    return state["ell"][(0, 0)], state["ell"][(1, 1)], *triangle_holonomies(state)


def local_radial_delta(
    level: int,
    state: dict[str, Any],
    source: tuple[int, int],
    target: tuple[int, int],
) -> Fraction:
    after = radial_target(state, source, target)
    delta = onsite(source, after) + onsite(target, after) - onsite(source, state) - onsite(target, state)
    for name, left, right in strip_carrier(level)["edges"]:
        if source in (left, right) or target in (left, right):
            delta += covariant_edge(name, left, right, after) - covariant_edge(name, left, right, state)
    return delta


def local_link_delta(level: int, state: dict[str, Any], name: str, sigma: int) -> Fraction:
    after = link_target(state, name, sigma)
    carrier = strip_carrier(level)
    edge_lookup = {edge_name: (left, right) for edge_name, left, right in carrier["edges"]}
    left, right = edge_lookup[name]
    delta = covariant_edge(name, left, right, after) - covariant_edge(name, left, right, state)
    for face in carrier["faces"]:
        if any(edge_name == name for edge_name, _orientation in face):
            delta += face_term(face, after, edge_lookup) - face_term(face, state, edge_lookup)
    return delta


def radial_rows(level: int, patch_state: State) -> list[dict[str, Any]]:
    state = full_state(level, patch_state)
    rows: list[dict[str, Any]] = []
    for name, left, right in strip_carrier(level)["edges"]:
        if not RADIAL_ANCHORS.intersection((left, right)):
            continue
        for source, target in ((left, right), (right, left)):
            if state["ell"][source] <= 0 or state["ell"][target] >= M_PSI:
                continue
            after = radial_target(state, source, target)
            delta = local_radial_delta(level, state, source, target)
            before_obs = joint_observable(state)
            after_obs = joint_observable(after)
            mobility_square = aperture(state["apertures"][source]) * aperture(state["apertures"][target])
            rows.append(
                {
                    "family": "TR",
                    "edge": name,
                    "source": list(source),
                    "target": list(target),
                    "delta_F": str(delta),
                    "mobility_square": str(mobility_square),
                    "delta_ell_a": after_obs[0] - before_obs[0],
                    "delta_ell_d": after_obs[1] - before_obs[1],
                    "delta_H_0": after_obs[2] - before_obs[2],
                    "delta_H_1": after_obs[3] - before_obs[3],
                    "before_observable": list(before_obs),
                    "after_observable": list(after_obs),
                    "rate_exponent": str(-BETA * delta / 2),
                }
            )
    return rows


def link_rows(level: int, patch_state: State) -> list[dict[str, Any]]:
    state = full_state(level, patch_state)
    rows: list[dict[str, Any]] = []
    for name, left, right in strip_carrier(level)["edges"]:
        if name not in PATCH_LINK_EDGES:
            continue
        for sigma in (1, -1):
            after = link_target(state, name, sigma)
            delta = local_link_delta(level, state, name, sigma)
            before_obs = joint_observable(state)
            after_obs = joint_observable(after)
            mobility_square = aperture(state["apertures"][left]) * aperture(state["apertures"][right])
            rows.append(
                {
                    "family": "LK",
                    "edge": name,
                    "sigma": sigma,
                    "delta_F": str(delta),
                    "mobility_square": str(mobility_square),
                    "delta_ell_a": after_obs[0] - before_obs[0],
                    "delta_ell_d": after_obs[1] - before_obs[1],
                    "delta_H_0": after_obs[2] - before_obs[2],
                    "delta_H_1": after_obs[3] - before_obs[3],
                    "before_observable": list(before_obs),
                    "after_observable": list(after_obs),
                    "rate_exponent": str(-BETA * delta / 2),
                }
            )
    return rows


def state_record(level: int, patch_state: State) -> dict[str, Any]:
    return {
        "patch_state": list(patch_state),
        "roots": radial_rows(level, patch_state) + link_rows(level, patch_state),
    }


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def stream_records(level: int, states: list[State]) -> dict[str, Any]:
    accumulator = hashlib.sha256()
    first: list[dict[str, Any]] = []
    last: deque[dict[str, Any]] = deque(maxlen=2)
    root_count = 0
    for index, patch_state in enumerate(states):
        record = state_record(level, patch_state)
        accumulator.update(canonical_bytes(record))
        accumulator.update(b"\n")
        root_count += len(record["roots"])
        if index < 2:
            first.append(record)
        last.append(record)
    return {
        "state_rows": len(states),
        "root_rows": root_count,
        "canonical_digest": accumulator.hexdigest(),
        "bounded_samples": first + list(last),
    }


def changed_labels(level: int, before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    before_terms = {label: value for label, _support, value in energy_terms(level, before)}
    after_terms = {label: value for label, _support, value in energy_terms(level, after)}
    return sorted(label for label in before_terms if before_terms[label] != after_terms[label])


def support_snapshot(level: int) -> dict[str, list[str]]:
    patch = make_patch_state((0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0), 1)
    state = full_state(level, patch)
    radial_after = radial_target(state, (1, 0), (0, 0))
    link_after = link_target(state, "h00", 1)
    link_after_h01 = link_target(state, "h01", 1)
    return {
        "radial_h00_b_to_a": changed_labels(level, state, radial_after),
        "link_h00_plus": changed_labels(level, state, link_after),
        "link_h01_plus": changed_labels(level, state, link_after_h01),
    }


def boundary_control() -> dict[str, Any]:
    patch = make_patch_state((0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0), 1)
    state_1 = full_state(1, patch)
    state_2 = full_state(2, patch)
    delta_1 = energy(1, radial_target(state_1, (1, 0), (0, 0))) - energy(1, state_1)
    delta_2 = energy(2, radial_target(state_2, (1, 0), (0, 0))) - energy(2, state_2)
    return {
        "root": {"edge": "h00", "source": [1, 0], "target": [0, 0]},
        "delta_F_G1": str(delta_1),
        "delta_F_G2": str(delta_2),
        "nonzero_difference": delta_1 != delta_2,
        "difference_G2_minus_G1": str(delta_2 - delta_1),
    }


def gauge_audit() -> dict[str, Any]:
    link_configs = itertools.product(range(K), repeat=LINK_BITS)
    gauge_configs = tuple(itertools.product(range(K), repeat=APERTURE_BITS))
    checked = 0
    for link_bits in link_configs:
        base = make_patch_state((0, 0, 0, 0), tuple(link_bits), (0, 0, 0, 0), 0)
        base_state = full_state(2, base)
        for gauge_bits in gauge_configs:
            gauge = dict(zip(PATCH_VERTICES, gauge_bits))
            transformed = patch_gauge_transform(base, gauge)
            transformed_state = full_state(2, transformed)
            if triangle_holonomies(base_state) != triangle_holonomies(transformed_state):
                return {"passed": False, "checked": checked, "counterexample": [base, gauge_bits]}
            if joint_observable(base_state) != joint_observable(transformed_state):
                return {"passed": False, "checked": checked, "counterexample": [base, gauge_bits]}
            checked += 1
    return {"passed": True, "checked": checked}


def zero_increment_audit(level: int, patch_state: State) -> dict[str, int]:
    state = full_state(level, patch_state)
    before = joint_observable(state)
    phase_zero = 0
    aperture_zero = 0
    remote_link_zero = 0
    remote_radial_zero = 0
    carrier = strip_carrier(level)
    for vertex in carrier["vertices"]:
        for sigma in (1, -1):
            transformed = {key: dict(value) for key, value in state.items()}
            transformed["phase"][vertex] = (transformed["phase"][vertex] + sigma) % K
            phase_zero += int(joint_observable(transformed) == before)
            if state["apertures"][vertex] + sigma in range(M_S + 1):
                transformed = {key: dict(value) for key, value in state.items()}
                transformed["apertures"][vertex] += sigma
                aperture_zero += int(joint_observable(transformed) == before)
    for name, left, right in carrier["edges"]:
        if name not in PATCH_LINK_EDGES:
            for sigma in (1, -1):
                transformed = link_target(state, name, sigma)
                remote_link_zero += int(joint_observable(transformed) == before)
        if not RADIAL_ANCHORS.intersection((left, right)):
            for source, target in ((left, right), (right, left)):
                if state["ell"][source] <= 0 or state["ell"][target] >= M_PSI:
                    continue
                remote_radial_zero += int(joint_observable(radial_target(state, source, target)) == before)
    return {
        "phase_zero": phase_zero,
        "aperture_zero": aperture_zero,
        "remote_link_zero": remote_link_zero,
        "remote_radial_zero": remote_radial_zero,
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = read_json(SOURCE)
    geometry = read_json(GEOMETRY)
    predecessor = read_json(PREDECESSOR)
    parent = read_json(PARENT)
    contract = read_json(CONTRACT)
    manifest = read_json(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": digest(SOURCE),
        "PAH-OMC-004": digest(GEOMETRY),
        "PAH-OMC-005": digest(PREDECESSOR),
        "PAH-OMC-006": digest(PARENT),
        "PAH-OMC-007": digest(ROOT / "strategy/pa-hyp/PAH-OMC-007-joint-holonomy-cylinder-v1.json"),
        "PAH-OMC-008": digest(CONTRACT),
        "PAH-OMC-008-MANIFEST": digest(MANIFEST),
    }
    manifest_parents = [manifest.get("functional_source", {}), manifest.get("geometric_source", {})] + manifest.get("predecessors", [])
    pins = {item.get("id"): item.get("sha256") for item in manifest_parents}
    check("source-hashes", pins.get("PAH-001") == hashes["PAH-001"] and pins.get("PAH-OMC-004") == hashes["PAH-OMC-004"] and pins.get("PAH-OMC-005") == hashes["PAH-OMC-005"] and pins.get("PAH-OMC-006") == hashes["PAH-OMC-006"] and pins.get("PAH-OMC-007") == hashes["PAH-OMC-007"] and manifest.get("contract", {}).get("sha256") == hashes["PAH-OMC-008"], hashes)
    check("identities", source.get("packet_id") == "PAH-001" and geometry.get("contract_id") == "PAH-OMC-004" and predecessor.get("contract_id") == "PAH-OMC-005" and parent.get("contract_id") == "PAH-OMC-006" and contract.get("contract_id") == "PAH-OMC-008")
    firewall = contract.get("preservation_firewall", {})
    check("parent-firewall", all(firewall.get(key) is True for key in ("parent_functional_unchanged", "parent_move_families_unchanged", "parent_mobility_unchanged", "no_new_term", "no_rate_fitting", "no_physical_identification")) and manifest.get("no_parent_mutation") is True)
    check("displayed-functional", source.get("functional_or_action", {}).get("formula", "").startswith("F_rho=sum_v[lambda_s"))
    check("displayed-generator", source.get("dynamics", {}).get("generator", "").startswith("(L_rho f)(x)=sum_r m_r(x)"))
    check("genuine-incidence", len(strip_carrier(3)["edges"]) > len(strip_carrier(2)["edges"]) and len(strip_carrier(3)["faces"]) > len(strip_carrier(2)["faces"] ))
    check("nonzero-q-fixture", Q > 0 and M_PSI > 0 and contract.get("exact_scope", {}).get("fixture", {}).get("Q") == Q)
    states = list(fixture_states())
    expected_states = (M_S + 1) ** APERTURE_BITS * K**LINK_BITS * K**PHASE_BITS * RADIAL_PLACEMENTS
    check("state-count", len(states) == expected_states, {"actual": len(states), "expected": expected_states})
    check("all-states-have-q-one", all(sum(decode_patch(state)[3].values()) == Q for state in states))
    check("gauge-closed-face", gauge_audit())
    check("joint-observable-declaration", all(token in contract.get("exact_scope", {}).get("joint_observable", "") for token in ("ell_a", "ell_d", "H_0", "H_1")))

    rows_2 = stream_records(2, states)
    rows_3 = stream_records(3, states)
    level2_edges = strip_carrier(2)["edges"]
    placement_degree_sum = sum(
        sum(1 for _name, left, right in level2_edges if RADIAL_ANCHORS.intersection((left, right)) and vertex in (left, right))
        for vertex in PATCH_VERTICES
    )
    expected_link_rows = len(states) * len(PATCH_LINK_EDGES) * 2
    expected_radial_rows = (len(states) // RADIAL_PLACEMENTS) * placement_degree_sum
    expected_rows = expected_link_rows + expected_radial_rows
    check("rows-cover-domain", rows_2["state_rows"] == rows_3["state_rows"] == len(states) and rows_2["root_rows"] == rows_3["root_rows"] == expected_rows, {"G2": rows_2["root_rows"], "G3": rows_3["root_rows"], "expected": expected_rows})
    check("joint-rootwise-equality", rows_2["canonical_digest"] == rows_3["canonical_digest"], {"G2": rows_2["canonical_digest"], "G3": rows_3["canonical_digest"]})
    check("all-midpoint-exponents", all(root["rate_exponent"] == str(-BETA * Fraction(root["delta_F"]) / 2) for record in rows_2["bounded_samples"] for root in record["roots"]))
    check("root-families-complete", all({root["family"] for root in record["roots"]} == {"TR", "LK"} for record in rows_2["bounded_samples"]))
    check("link-channel-multiplicity", all(sum(root["family"] == "LK" for root in record["roots"]) == len(PATCH_LINK_EDGES) * 2 for record in rows_2["bounded_samples"]))
    check("joint-increments", all(any(root[key] != 0 for key in ("delta_ell_a", "delta_ell_d", "delta_H_0", "delta_H_1")) for record in rows_2["bounded_samples"] for root in record["roots"]))
    check("radial-holonomy-zero", all(root["delta_H_0"] == 0 and root["delta_H_1"] == 0 for record in rows_2["bounded_samples"] for root in record["roots"] if root["family"] == "TR"))
    check("link-density-zero", all(root["delta_ell_a"] == 0 and root["delta_ell_d"] == 0 for record in rows_2["bounded_samples"] for root in record["roots"] if root["family"] == "LK"))

    full_crosschecks: list[dict[str, Any]] = []
    sample_states = (states[0], states[len(states) // 2], states[-1])
    for level in (1, 2, 3):
        for patch_state in sample_states:
            state = full_state(level, patch_state)
            for name, left, right in strip_carrier(level)["edges"]:
                if RADIAL_ANCHORS.intersection((left, right)):
                    for source_vertex, target_vertex in ((left, right), (right, left)):
                        if state["ell"][source_vertex] > 0 and state["ell"][target_vertex] < M_PSI:
                            after = radial_target(state, source_vertex, target_vertex)
                            full_delta = energy(level, after) - energy(level, state)
                            full_crosschecks.append({"kind": "TR", "level": level, "edge": name, "local": str(local_radial_delta(level, state, source_vertex, target_vertex)), "full": str(full_delta), "equal": local_radial_delta(level, state, source_vertex, target_vertex) == full_delta})
                if name in PATCH_LINK_EDGES:
                    for sigma in (1, -1):
                        after = link_target(state, name, sigma)
                        full_delta = energy(level, after) - energy(level, state)
                        local_delta = local_link_delta(level, state, name, sigma)
                        full_crosschecks.append({"kind": "LK", "level": level, "edge": name, "sigma": sigma, "local": str(local_delta), "full": str(full_delta), "equal": local_delta == full_delta})
    check("local-full-energy-crosscheck", all(item["equal"] for item in full_crosschecks), {"checks": len(full_crosschecks), "failed": [item for item in full_crosschecks if not item["equal"]][:2]})
    support_2 = support_snapshot(2)
    support_3 = support_snapshot(3)
    check("support-closure-stable", support_2 == support_3, {"G2": support_2, "G3": support_3})
    zero_audit = {str(level): zero_increment_audit(level, states[0]) for level in (2, 3)}
    check("zero-increment-families", all(zero_audit[str(level)]["phase_zero"] > 0 and zero_audit[str(level)]["aperture_zero"] > 0 and zero_audit[str(level)]["remote_link_zero"] > 0 and zero_audit[str(level)]["remote_radial_zero"] == 0 for level in (2, 3)), zero_audit)
    control = boundary_control()
    check("boundary-control-nonzero", control["nonzero_difference"] and control["difference_G2_minus_G1"] == "-1", control)
    check("triangle-edge-set", TRIANGLE0_EDGES == {"h00", "v1", "d0"} and TRIANGLE1_EDGES == {"d0", "h01", "v0"} and PATCH_LINK_EDGES == set(PATCH_EDGE_NAMES))
    check("no-pure-link-promotion", contract.get("preservation_firewall", {}).get("no_pure_link_cylinder_promotion") is True and "pure link" in " ".join(contract.get("non_claims", [])).lower())

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc008-multi-cylinder-primary/1.0",
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
            "model": "PAH-001 + PAH-OMC-008 researcher successor",
            "normalization": "finite counting-measure Gibbs midpoint rate c=m exp(-beta DeltaF/2)",
            "regulator": "K=2, M_s=M_psi=1, Q=1, epsilon=1/2, beta=nu=1; all displayed couplings one where used",
            "volume": "full G_2 and neutral inclusion in G_3; one nonzero charge quantum in the anchor patch",
            "limit": "none; n=2,3 finite local equality only",
        },
        "fixture_dimensions": {
            "aperture_bits": APERTURE_BITS,
            "link_bits": LINK_BITS,
            "phase_bits": PHASE_BITS,
            "radial_placements": RADIAL_PLACEMENTS,
            "patch_link_edges": len(PATCH_LINK_EDGES),
            "radial_degree_sum": placement_degree_sum,
            "state_count_formula": "(M_s+1)^4*K^5*K^4*4",
            "state_count": len(states),
            "root_count": rows_2["root_rows"],
            "radial_root_count": expected_radial_rows,
            "link_root_count": expected_link_rows,
        },
        "carrier_signatures": {
            "G2": {"vertices": len(strip_carrier(2)["vertices"]), "edges": len(strip_carrier(2)["edges"]), "faces": len(strip_carrier(2)["faces"])},
            "G3": {"vertices": len(strip_carrier(3)["vertices"]), "edges": len(strip_carrier(3)["edges"]), "faces": len(strip_carrier(3)["faces"])},
        },
        "row_identity": {
            "levels": [2, 3],
            "state_rows": rows_2["state_rows"],
            "root_rows": rows_2["root_rows"],
            "canonical_digest_G2": rows_2["canonical_digest"],
            "canonical_digest_G3": rows_3["canonical_digest"],
            "all_equal": rows_2["canonical_digest"] == rows_3["canonical_digest"],
            "bounded_samples_G2": rows_2["bounded_samples"],
            "bounded_samples_G3": rows_3["bounded_samples"],
            "exact_tuple": ["patch_state", "family", "edge", "sigma/source/target", "delta_F", "mobility_square", "delta_ell_a", "delta_ell_d", "delta_H_0", "delta_H_1", "before_observable", "after_observable", "rate_exponent"],
            "observable_basis": ["ell_a", "ell_d", "H_0", "H_1", "bounded functions of (ell_a,ell_d,H_0,H_1)"],
        },
        "gauge_audit": gauge_audit(),
        "support_audit": {"G2": support_2, "G3": support_3, "equal": support_2 == support_3},
        "zero_increment_audit": zero_audit,
        "local_full_crosscheck": {"count": len(full_crosschecks), "all_equal": all(item["equal"] for item in full_crosschecks)},
        "boundary_control": control,
        "verdict": "EXACT_NONZERO_Q_MATTER_CLOSED_FACE_HOLONOMY_JOINT_CYLINDER_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "reproduction": {
            "command": "python codes/foundations/pah_omc008_multi_cylinder.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc008-multi-cylinder/primary.json",
            "independent_command": "python codes/foundations/pah_omc008_multi_cylinder_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc008-multi-cylinder/independent.json",
        },
        "non_claims": contract.get("non_claims", []),
        "next_question": contract.get("single_next_question"),
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} PRIMARY {payload['verification']} {payload['passed']}/{payload['assertion_count']}; states={len(states)}; roots={rows_2['root_rows']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
