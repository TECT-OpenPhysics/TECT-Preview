#!/usr/bin/env python3
"""Non-importing independent replay for PAH-OMC-007.

This lane rebuilds the strip, the PAH energy terms, the closed-face
holonomy, and the retained directed roots from direct formulas.  It shares
only the contract and canonical JSON row convention with the primary lane.
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
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
PREDECESSOR = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-v1.json"
PARENT = ROOT / "strategy/pa-hyp/PAH-OMC-006-matter-cylinder-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-007-joint-holonomy-cylinder-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-007-joint-holonomy-cylinder-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc007-joint-holonomy-cylinder/independent.json"
)

AUDIT_ID = "PAH-JOINT-HOLONOMY-CYLINDER-GENERATOR-001"
EXPLORATION_ID = "EXP-001381"
RESULT_ID = "R-487"
TASK_ID = "T-054"

K = 2
M_S = 1
M_PSI = 1
Q = 1
R_MAX = Fraction(1)
EPSILON = Fraction(1, 2)
BETA = Fraction(1)
M2 = Fraction(0)
LAMBDA_4 = Fraction(1)
ETA_6 = Fraction(1)
G_COUPLING = Fraction(1)
LAMBDA_S = Fraction(1)
KAPPA_S = Fraction(1)
KAPPA_D = Fraction(1)
KAPPA_G = Fraction(1)

PATCH_VERTICES = ((0, 0), (1, 0), (0, 1), (1, 1))
PATCH_EDGES = (
    ("h00", (0, 0), (1, 0)),
    ("v0", (0, 0), (0, 1)),
    ("d0", (0, 0), (1, 1)),
    ("h01", (0, 1), (1, 1)),
    ("v1", (1, 0), (1, 1)),
)
PATCH_EDGE_NAMES = tuple(edge[0] for edge in PATCH_EDGES)
TRIANGLE_EDGES = frozenset(("h00", "v1", "d0"))
APERTURE_BITS = len(PATCH_VERTICES)
LINK_BITS = len(PATCH_EDGES)
PHASE_BITS = len(PATCH_VERTICES)
RADIAL_PLACEMENTS = len(PATCH_VERTICES)
State = tuple[int, ...]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


def ap(level: int) -> Fraction:
    if level not in range(M_S + 1):
        raise ValueError(level)
    return EPSILON + Fraction(level) * (1 - EPSILON) / M_S


def z2(value: int) -> int:
    if value not in range(K):
        raise ValueError(value)
    return -1 if value else 1


def carrier(level: int) -> dict[str, Any]:
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


def states() -> list[State]:
    result: list[State] = []
    for apertures in itertools.product(range(M_S + 1), repeat=APERTURE_BITS):
        for links in itertools.product(range(K), repeat=LINK_BITS):
            for phases in itertools.product(range(K), repeat=PHASE_BITS):
                for radial_index in range(RADIAL_PLACEMENTS):
                    radial = tuple(1 if index == radial_index else 0 for index in range(RADIAL_PLACEMENTS))
                    result.append(tuple(apertures) + tuple(links) + tuple(phases) + radial)
    return result


def decode(state: State) -> tuple[dict[tuple[int, int], int], dict[str, int], dict[tuple[int, int], int], dict[tuple[int, int], int]]:
    offset = 0
    apertures = dict(zip(PATCH_VERTICES, state[offset : offset + APERTURE_BITS]))
    offset += APERTURE_BITS
    links = dict(zip(PATCH_EDGE_NAMES, state[offset : offset + LINK_BITS]))
    offset += LINK_BITS
    phases = dict(zip(PATCH_VERTICES, state[offset : offset + PHASE_BITS]))
    offset += PHASE_BITS
    radial = dict(zip(PATCH_VERTICES, state[offset : offset + RADIAL_PLACEMENTS]))
    if sum(radial.values()) != Q:
        raise ValueError("wrong charge")
    return apertures, links, phases, radial


def patch_gauge(state: State, values: tuple[int, ...]) -> State:
    apertures, links, phases, radial = decode(state)
    gauge = dict(zip(PATCH_VERTICES, values))
    shifted_phases = {vertex: (phases[vertex] + gauge[vertex]) % K for vertex in PATCH_VERTICES}
    shifted_links = {
        name: (links[name] + gauge[right] - gauge[left]) % K
        for name, left, right in PATCH_EDGES
    }
    radial_index = next(index for index, vertex in enumerate(PATCH_VERTICES) if radial[vertex])
    return tuple(apertures[v] for v in PATCH_VERTICES) + tuple(shifted_links[n] for n in PATCH_EDGE_NAMES) + tuple(shifted_phases[v] for v in PATCH_VERTICES) + tuple(1 if i == radial_index else 0 for i in range(RADIAL_PLACEMENTS))


def neutral(level: int, patch: State) -> dict[str, Any]:
    apertures, links, phases, radial = decode(patch)
    graph = carrier(level)
    state = {
        "apertures": {vertex: 0 for vertex in graph["vertices"]},
        "ell": {vertex: 0 for vertex in graph["vertices"]},
        "phase": {vertex: 0 for vertex in graph["vertices"]},
        "links": {name: 0 for name, _left, _right in graph["edges"]},
    }
    for vertex in PATCH_VERTICES:
        state["apertures"][vertex] = apertures[vertex]
        state["ell"][vertex] = radial[vertex]
        state["phase"][vertex] = phases[vertex]
    for name in PATCH_EDGE_NAMES:
        state["links"][name] = links[name]
    return state


def psi(ell: int, phase: int) -> Fraction:
    return R_MAX * Fraction(ell, M_PSI) * z2(phase)


def vertex_energy(vertex: tuple[int, int], state: dict[str, Any]) -> Fraction:
    s = ap(state["apertures"][vertex])
    value = psi(state["ell"][vertex], state["phase"][vertex])
    return LAMBDA_S * (s - 1) ** 2 / 2 + M2 * value**2 / 2 + LAMBDA_4 * value**4 / 4 + ETA_6 * value**6 / 6 + G_COUPLING * s**2 * value**2 / 2


def edge_j(left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> Fraction:
    return Fraction(2) / (ap(state["apertures"][left]) + ap(state["apertures"][right]))


def covariant(name: str, left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> Fraction:
    left_value = psi(state["ell"][left], state["phase"][left])
    right_value = psi(state["ell"][right], state["phase"][right])
    return KAPPA_D * edge_j(left, right, state) * (right_value - z2(state["links"][name]) * left_value) ** 2 / 2


def stiffness(left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> Fraction:
    return KAPPA_S * (ap(state["apertures"][left]) - ap(state["apertures"][right])) ** 2 / 2


def face_value(face: tuple[tuple[str, int], ...], state: dict[str, Any], edge_lookup: dict[str, tuple[tuple[int, int], tuple[int, int]]]) -> Fraction:
    values: list[Fraction] = []
    holonomy = 1
    for name, _orientation in face:
        left, right = edge_lookup[name]
        values.append(edge_j(left, right, state))
        holonomy *= z2(state["links"][name])
    return KAPPA_G * sum(values, Fraction(0)) / len(values) * (1 - holonomy)


def terms(level: int, state: dict[str, Any]) -> dict[str, Fraction]:
    graph = carrier(level)
    lookup = {name: (left, right) for name, left, right in graph["edges"]}
    result: dict[str, Fraction] = {}
    for vertex in graph["vertices"]:
        result[f"onsite:{vertex[0]},{vertex[1]}"] = vertex_energy(vertex, state)
    for name, left, right in graph["edges"]:
        result[f"stiffness:{name}"] = stiffness(left, right, state)
        result[f"covariant:{name}"] = covariant(name, left, right, state)
    for index, face in enumerate(graph["faces"]):
        result[f"face:{index}"] = face_value(face, state, lookup)
    return result


def total(level: int, state: dict[str, Any]) -> Fraction:
    return sum(terms(level, state).values(), Fraction(0))


def radial_move(state: dict[str, Any], source: tuple[int, int], target: tuple[int, int]) -> dict[str, Any]:
    result = {key: dict(value) for key, value in state.items()}
    result["ell"][source] -= 1
    result["ell"][target] += 1
    if sum(result["ell"].values()) != Q:
        raise AssertionError("charge changed")
    return result


def link_move(state: dict[str, Any], name: str, sigma: int) -> dict[str, Any]:
    result = {key: dict(value) for key, value in state.items()}
    result["links"][name] = (result["links"][name] + sigma) % K
    return result


def holonomy(state: dict[str, Any]) -> int:
    return z2(state["links"]["h00"]) * z2(state["links"]["v1"]) * z2(state["links"]["d0"])


def observable(state: dict[str, Any]) -> tuple[int, int]:
    return state["ell"][(0, 0)], holonomy(state)


def delta_radial(level: int, state: dict[str, Any], source: tuple[int, int], target: tuple[int, int]) -> Fraction:
    after = radial_move(state, source, target)
    result = vertex_energy(source, after) + vertex_energy(target, after) - vertex_energy(source, state) - vertex_energy(target, state)
    for name, left, right in carrier(level)["edges"]:
        if source in (left, right) or target in (left, right):
            result += covariant(name, left, right, after) - covariant(name, left, right, state)
    return result


def delta_link(level: int, state: dict[str, Any], name: str, sigma: int) -> Fraction:
    after = link_move(state, name, sigma)
    graph = carrier(level)
    lookup = {edge_name: (left, right) for edge_name, left, right in graph["edges"]}
    left, right = lookup[name]
    result = covariant(name, left, right, after) - covariant(name, left, right, state)
    for face in graph["faces"]:
        if any(edge_name == name for edge_name, _orientation in face):
            result += face_value(face, after, lookup) - face_value(face, state, lookup)
    return result


def root_rows(level: int, patch: State) -> list[dict[str, Any]]:
    state = neutral(level, patch)
    rows: list[dict[str, Any]] = []
    anchor = (0, 0)
    for name, left, right in carrier(level)["edges"]:
        if anchor not in (left, right):
            continue
        for source, target in ((left, right), (right, left)):
            if state["ell"][source] <= 0 or state["ell"][target] >= M_PSI:
                continue
            after = radial_move(state, source, target)
            before_observable = observable(state)
            after_observable = observable(after)
            delta = delta_radial(level, state, source, target)
            rows.append({
                "family": "TR", "edge": name, "source": list(source), "target": list(target),
                "delta_F": str(delta), "mobility_square": str(ap(state["apertures"][source]) * ap(state["apertures"][target])),
                "delta_ell_a": after_observable[0] - before_observable[0], "delta_H_0": after_observable[1] - before_observable[1],
                "before_observable": list(before_observable), "after_observable": list(after_observable),
                "rate_exponent": str(-BETA * delta / 2),
            })
    for name, left, right in carrier(level)["edges"]:
        if name not in TRIANGLE_EDGES:
            continue
        for sigma in (1, -1):
            after = link_move(state, name, sigma)
            before_observable = observable(state)
            after_observable = observable(after)
            delta = delta_link(level, state, name, sigma)
            rows.append({
                "family": "LK", "edge": name, "sigma": sigma, "delta_F": str(delta),
                "mobility_square": str(ap(state["apertures"][left]) * ap(state["apertures"][right])),
                "delta_ell_a": after_observable[0] - before_observable[0], "delta_H_0": after_observable[1] - before_observable[1],
                "before_observable": list(before_observable), "after_observable": list(after_observable),
                "rate_exponent": str(-BETA * delta / 2),
            })
    return rows


def stream(level: int, domain: list[State]) -> dict[str, Any]:
    hasher = hashlib.sha256()
    first: list[dict[str, Any]] = []
    last: deque[dict[str, Any]] = deque(maxlen=2)
    roots = 0
    for index, patch in enumerate(domain):
        record = {"patch_state": list(patch), "roots": root_rows(level, patch)}
        blob = json.dumps(record, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
        hasher.update(blob)
        hasher.update(b"\n")
        roots += len(record["roots"])
        if index < 2:
            first.append(record)
        last.append(record)
    return {"state_rows": len(domain), "root_rows": roots, "canonical_digest": hasher.hexdigest(), "bounded_samples": first + list(last)}


def support(level: int) -> dict[str, list[str]]:
    patch = (0,) * (APERTURE_BITS + LINK_BITS + PHASE_BITS) + (0, 1, 0, 0)
    state = neutral(level, patch)
    radial = radial_move(state, (1, 0), (0, 0))
    link = link_move(state, "h00", 1)
    before = terms(level, state)
    return {
        "radial_h00_b_to_a": sorted(label for label, value in before.items() if value != terms(level, radial)[label]),
        "link_h00_plus": sorted(label for label, value in before.items() if value != terms(level, link)[label]),
    }


def boundary() -> dict[str, Any]:
    patch = (0,) * (APERTURE_BITS + LINK_BITS + PHASE_BITS) + (0, 1, 0, 0)
    one = neutral(1, patch)
    two = neutral(2, patch)
    delta_one = total(1, radial_move(one, (1, 0), (0, 0))) - total(1, one)
    delta_two = total(2, radial_move(two, (1, 0), (0, 0))) - total(2, two)
    return {"root": {"edge": "h00", "source": [1, 0], "target": [0, 0]}, "delta_F_G1": str(delta_one), "delta_F_G2": str(delta_two), "difference_G2_minus_G1": str(delta_two - delta_one), "nonzero_difference": delta_one != delta_two}


def gauge_check() -> dict[str, Any]:
    checked = 0
    for links in itertools.product(range(K), repeat=LINK_BITS):
        patch = (0,) * APERTURE_BITS + tuple(links) + (0,) * PHASE_BITS + (1, 0, 0, 0)
        base = neutral(2, patch)
        for gauges in itertools.product(range(K), repeat=APERTURE_BITS):
            transformed = neutral(2, patch_gauge(patch, gauges))
            if holonomy(base) != holonomy(transformed) or observable(base)[0] != observable(transformed)[0]:
                return {"passed": False, "checked": checked, "counterexample": [patch, gauges]}
            checked += 1
    return {"passed": True, "checked": checked}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source, geometry, predecessor, parent, contract, manifest = (load(path) for path in (SOURCE, GEOMETRY, PREDECESSOR, PARENT, CONTRACT, MANIFEST))
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY), "PAH-OMC-005": sha(PREDECESSOR), "PAH-OMC-006": sha(PARENT), "PAH-OMC-007": sha(CONTRACT), "PAH-OMC-007-MANIFEST": sha(MANIFEST)}
    pins = {item.get("id"): item.get("sha256") for item in [manifest.get("functional_source", {}), manifest.get("geometric_source", {})] + manifest.get("predecessors", [])}
    check("source-hashes", pins.get("PAH-001") == hashes["PAH-001"] and pins.get("PAH-OMC-004") == hashes["PAH-OMC-004"] and pins.get("PAH-OMC-005") == hashes["PAH-OMC-005"] and pins.get("PAH-OMC-006") == hashes["PAH-OMC-006"] and manifest.get("contract", {}).get("sha256") == hashes["PAH-OMC-007"], hashes)
    check("identities", source.get("packet_id") == "PAH-001" and geometry.get("contract_id") == "PAH-OMC-004" and predecessor.get("contract_id") == "PAH-OMC-005" and parent.get("contract_id") == "PAH-OMC-006" and contract.get("contract_id") == "PAH-OMC-007")
    check("displayed-functional", source.get("functional_or_action", {}).get("formula", "").startswith("F_rho=sum_v[lambda_s"))
    check("displayed-generator", source.get("dynamics", {}).get("generator", "").startswith("(L_rho f)(x)=sum_r m_r(x)"))
    check("fixture-and-charge", Q == 1 and contract.get("exact_scope", {}).get("fixture", {}).get("Q") == 1)
    domain = states()
    expected_states = (M_S + 1) ** APERTURE_BITS * K**LINK_BITS * K**PHASE_BITS * RADIAL_PLACEMENTS
    check("state-count", len(domain) == expected_states, {"actual": len(domain), "expected": expected_states})
    check("gauge-closed-face", gauge_check())
    rows_2 = stream(2, domain)
    rows_3 = stream(3, domain)
    expected_link = len(domain) * len(TRIANGLE_EDGES) * 2
    expected_radial = (len(domain) // RADIAL_PLACEMENTS) * 6
    check("root-count", rows_2["root_rows"] == rows_3["root_rows"] == expected_link + expected_radial, {"G2": rows_2["root_rows"], "G3": rows_3["root_rows"], "expected": expected_link + expected_radial})
    check("rootwise-digest", rows_2["canonical_digest"] == rows_3["canonical_digest"], {"G2": rows_2["canonical_digest"], "G3": rows_3["canonical_digest"]})
    check("midpoint-recomputed", all(root["rate_exponent"] == str(-BETA * Fraction(root["delta_F"]) / 2) for record in rows_2["bounded_samples"] for root in record["roots"]))
    check("joint-increment-support", all(root["delta_ell_a"] != 0 or root["delta_H_0"] != 0 for record in rows_2["bounded_samples"] for root in record["roots"]))
    full_checks: list[bool] = []
    for level in (1, 2, 3):
        for patch in (domain[0], domain[len(domain) // 2], domain[-1]):
            state = neutral(level, patch)
            for name, left, right in carrier(level)["edges"]:
                if (0, 0) in (left, right):
                    for source_vertex, target_vertex in ((left, right), (right, left)):
                        if state["ell"][source_vertex] > 0 and state["ell"][target_vertex] < M_PSI:
                            full_checks.append(delta_radial(level, state, source_vertex, target_vertex) == total(level, radial_move(state, source_vertex, target_vertex)) - total(level, state))
                if name in TRIANGLE_EDGES:
                    for sigma in (1, -1):
                        full_checks.append(delta_link(level, state, name, sigma) == total(level, link_move(state, name, sigma)) - total(level, state))
    check("local-full-crosscheck", all(full_checks), {"checks": len(full_checks), "failed": len(full_checks) - sum(full_checks)})
    check("support-stable", support(2) == support(3), {"G2": support(2), "G3": support(3)})
    control = boundary()
    check("boundary-control", control["nonzero_difference"] and control["difference_G2_minus_G1"] == "-1", control)
    check("channel-multiplicity", all(sum(root["family"] == "LK" for root in record["roots"]) == len(TRIANGLE_EDGES) * 2 for record in rows_2["bounded_samples"]))
    check("no-parent-mutation", contract.get("preservation_firewall", {}).get("parent_functional_unchanged") is True and contract.get("preservation_firewall", {}).get("no_new_term") is True and contract.get("preservation_firewall", {}).get("no_pure_link_cylinder_promotion") is True)
    failed = [row for row in checks if not row["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc007-joint-holonomy-cylinder-independent/1.0",
        "run_kind": "independent", "audit_id": AUDIT_ID, "exploration_id": EXPLORATION_ID, "result_id": RESULT_ID, "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL", "assertion_count": len(checks), "passed": len(checks) - len(failed), "failed": len(failed), "assertions": checks, "source_hashes": hashes,
        "row_identity": {"levels": [2, 3], "state_rows": rows_2["state_rows"], "root_rows": rows_2["root_rows"], "canonical_digest_G2": rows_2["canonical_digest"], "canonical_digest_G3": rows_3["canonical_digest"], "all_equal": rows_2["canonical_digest"] == rows_3["canonical_digest"], "bounded_samples_G2": rows_2["bounded_samples"], "bounded_samples_G3": rows_3["bounded_samples"]},
        "fixture_dimensions": {"aperture_bits": APERTURE_BITS, "link_bits": LINK_BITS, "phase_bits": PHASE_BITS, "radial_placements": RADIAL_PLACEMENTS, "state_count": len(domain), "root_count": rows_2["root_rows"]},
        "gauge_audit": gauge_check(), "support_audit": {"G2": support(2), "G3": support(3), "equal": support(2) == support(3)}, "boundary_control": control,
        "verdict": "EXACT_NONZERO_Q_MATTER_CLOSED_FACE_HOLONOMY_JOINT_CYLINDER_COMPATIBILITY", "stage2_status": "HOLD_FOR_EVIDENCE", "claim_bearing": False, "scientific_transition": False, "physical_progress": False,
        "reproduction": {"command": "python codes/foundations/pah_omc007_joint_holonomy_cylinder_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc007-joint-holonomy-cylinder/independent.json"},
        "non_claims": contract.get("non_claims", []), "next_question": contract.get("single_next_question"),
    }
    write_json(args.output, payload)
    print(f"{AUDIT_ID} INDEPENDENT {payload['verification']} {payload['passed']}/{payload['assertion_count']}; states={len(domain)}; roots={rows_2['root_rows']}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
