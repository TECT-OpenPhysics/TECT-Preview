#!/usr/bin/env python3
"""Non-importing independent replay for PAH-OMC-006.

All carrier and energy formulas are rebuilt here rather than importing the
primary implementation.  The output contains a digest of every enumerated
rootwise tuple plus bounded samples, so the independent lane remains small
while still checking the same complete finite domain.
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
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
PREDECESSOR = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-006-matter-cylinder-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-006-matter-cylinder-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc006-matter-cylinder/independent.json"
)

AUDIT_ID = "PAH-MATTER-CYLINDER-GENERATOR-001"
EXPLORATION_ID = "EXP-001378"
RESULT_ID = "R-486"
TASK_ID = "T-054"

# Independent copy of the declared finite fixture inputs.
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
PATCH_EDGES = (
    ("h00", (0, 0), (1, 0)),
    ("v0", (0, 0), (0, 1)),
    ("d0", (0, 0), (1, 1)),
    ("h01", (0, 1), (1, 1)),
    ("v1", (1, 0), (1, 1)),
)
PATCH_EDGE_NAMES = tuple(item[0] for item in PATCH_EDGES)
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


def z2(bit: int) -> int:
    if bit not in range(K):
        raise ValueError(bit)
    return -1 if bit else 1


def carrier(level: int) -> dict[str, Any]:
    vertices = tuple((i, j) for i in range(level + 2) for j in (0, 1))
    edges = []
    for i in range(level + 1):
        for j in (0, 1):
            edges.append((f"h{i}{j}", (i, j), (i + 1, j)))
    for i in range(level + 2):
        edges.append((f"v{i}", (i, 0), (i, 1)))
    for i in range(level):
        edges.append((f"d{i}", (i, 0), (i + 1, 1)))
    faces = []
    for i in range(level):
        faces.extend(
            [
                ((f"h{i}0", 1), (f"v{i + 1}", 1), (f"d{i}", -1)),
                ((f"d{i}", 1), (f"h{i}1", -1), (f"v{i}", -1)),
            ]
        )
    i = level
    faces.append(((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1)))
    return {"vertices": tuple(vertices), "edges": tuple(edges), "faces": tuple(faces)}


def patch_state(radial_index: int) -> State:
    return (0,) * (APERTURE_BITS + LINK_BITS + PHASE_BITS) + tuple(
        1 if index == radial_index else 0 for index in range(RADIAL_PLACEMENTS)
    )


def states() -> list[State]:
    result = []
    for a_bits in itertools.product(range(M_S + 1), repeat=APERTURE_BITS):
        for link_bits in itertools.product(range(K), repeat=LINK_BITS):
            for phase_bits in itertools.product(range(K), repeat=PHASE_BITS):
                for radial_index in range(RADIAL_PLACEMENTS):
                    radial = tuple(1 if index == radial_index else 0 for index in range(RADIAL_PLACEMENTS))
                    result.append(tuple(a_bits) + tuple(link_bits) + tuple(phase_bits) + radial)
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


def relabel_phase_links(state: State) -> State:
    values = list(state)
    link_start = APERTURE_BITS
    phase_end = APERTURE_BITS + LINK_BITS + PHASE_BITS
    for index in range(link_start, phase_end):
        values[index] = (values[index] + 1) % K
    return tuple(values)


def neutral_state(level: int, state: State) -> dict[str, Any]:
    apertures, links, phases, radial = decode(state)
    graph = carrier(level)
    result = {
        "apertures": {vertex: 0 for vertex in graph["vertices"]},
        "ell": {vertex: 0 for vertex in graph["vertices"]},
        "phase": {vertex: 0 for vertex in graph["vertices"]},
        "links": {name: 0 for name, _left, _right in graph["edges"]},
    }
    for vertex in PATCH_VERTICES:
        result["apertures"][vertex] = apertures[vertex]
        result["ell"][vertex] = radial[vertex]
        result["phase"][vertex] = phases[vertex]
    for name in PATCH_EDGE_NAMES:
        result["links"][name] = links[name]
    return result


def matter(ell: int, phase: int) -> Fraction:
    return R_MAX * Fraction(ell, M_PSI) * z2(phase)


def vertex_term(vertex: tuple[int, int], state: dict[str, Any]) -> Fraction:
    s = ap(state["apertures"][vertex])
    psi = matter(state["ell"][vertex], state["phase"][vertex])
    return LAMBDA_S * (s - 1) ** 2 / 2 + M2 * psi**2 / 2 + LAMBDA_4 * psi**4 / 4 + ETA_6 * psi**6 / 6 + G_COUPLING * s**2 * psi**2 / 2


def j(left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> Fraction:
    return Fraction(2, 1) / (ap(state["apertures"][left]) + ap(state["apertures"][right]))


def edge_terms(name: str, left: tuple[int, int], right: tuple[int, int], state: dict[str, Any]) -> tuple[Fraction, Fraction]:
    stiffness = KAPPA_S * (ap(state["apertures"][left]) - ap(state["apertures"][right])) ** 2 / 2
    psi_left = matter(state["ell"][left], state["phase"][left])
    psi_right = matter(state["ell"][right], state["phase"][right])
    covariant = KAPPA_D * j(left, right, state) * (psi_right - z2(state["links"][name]) * psi_left) ** 2 / 2
    return stiffness, covariant


def face_value(face: tuple[tuple[str, int], ...], state: dict[str, Any], edge_lookup: dict[str, tuple[tuple[int, int], tuple[int, int]]]) -> Fraction:
    values = []
    holonomy = 1
    for name, _orientation in face:
        left, right = edge_lookup[name]
        values.append(j(left, right, state))
        holonomy *= z2(state["links"][name])
    return KAPPA_G * sum(values, Fraction(0)) / len(values) * (1 - holonomy)


def terms(level: int, state: dict[str, Any]) -> dict[str, Fraction]:
    graph = carrier(level)
    edge_lookup = {name: (left, right) for name, left, right in graph["edges"]}
    result: dict[str, Fraction] = {}
    for vertex in graph["vertices"]:
        result[f"onsite:{vertex[0]},{vertex[1]}"] = vertex_term(vertex, state)
    for name, left, right in graph["edges"]:
        stiffness, covariant = edge_terms(name, left, right, state)
        result[f"stiffness:{name}"] = stiffness
        result[f"covariant:{name}"] = covariant
    for index, face in enumerate(graph["faces"]):
        result[f"face:{index}"] = face_value(face, state, edge_lookup)
    return result


def total(level: int, state: dict[str, Any]) -> Fraction:
    return sum(terms(level, state).values(), Fraction(0))


def move(state: dict[str, Any], source: tuple[int, int], target: tuple[int, int]) -> dict[str, Any]:
    result = {key: dict(value) for key, value in state.items()}
    result["ell"][source] -= 1
    result["ell"][target] += 1
    if sum(result["ell"].values()) != Q:
        raise AssertionError("charge changed")
    return result


def roots(level: int, state: State) -> list[dict[str, Any]]:
    before = neutral_state(level, state)
    result = []
    anchor = PATCH_VERTICES[0]
    for name, left, right in carrier(level)["edges"]:
        if anchor not in (left, right):
            continue
        for source, target in ((left, right), (right, left)):
            if before["ell"][source] <= 0 or before["ell"][target] >= M_PSI:
                continue
            after = move(before, source, target)
            delta = total(level, after) - total(level, before)
            result.append(
                {
                    "edge": name,
                    "source": list(source),
                    "target": list(target),
                    "delta_F": str(delta),
                    "mobility_square": str(ap(before["apertures"][source]) * ap(before["apertures"][target])),
                    "delta_ell_a": after["ell"][anchor] - before["ell"][anchor],
                    "rate_exponent": str(-BETA * delta / 2),
                }
            )
    return result


def records(level: int, domain: list[State]) -> list[dict[str, Any]]:
    return [{"patch_state": list(state), "roots": roots(level, state)} for state in domain]


def digest_rows(records_value: list[dict[str, Any]]) -> str:
    blob = json.dumps(records_value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def projection(records_value: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    return [
        (tuple(record["patch_state"]), root["edge"], tuple(root["source"]), tuple(root["target"]), root["delta_F"], root["mobility_square"], root["delta_ell_a"], root["rate_exponent"])
        for record in records_value
        for root in record["roots"]
    ]


def support(level: int, radial_index: int) -> dict[str, list[str]]:
    state = neutral_state(level, patch_state(radial_index))
    before = terms(level, state)
    result: dict[str, list[str]] = {}
    anchor = PATCH_VERTICES[0]
    for name, left, right in carrier(level)["edges"]:
        if anchor not in (left, right):
            continue
        for source, target in ((left, right), (right, left)):
            if state["ell"][source] <= 0 or state["ell"][target] >= M_PSI:
                continue
            after = terms(level, move(state, source, target))
            key = f"{name}:{source[0]},{source[1]}->{target[0]},{target[1]}"
            result[key] = sorted(label for label in before if before[label] != after[label])
    return result


def boundary() -> dict[str, Any]:
    state = patch_state(1)
    one = roots(1, state)
    two = roots(2, state)
    find = lambda rows: next(row for row in rows if row["edge"] == "h00" and row["source"] == [1, 0] and row["target"] == [0, 0])
    left = find(one)["delta_F"]
    right = find(two)["delta_F"]
    return {"delta_F_G1": left, "delta_F_G2": right, "difference_G2_minus_G1": str(Fraction(right) - Fraction(left)), "nonzero_difference": left != right}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source, geometry, predecessor, contract, manifest = (load(path) for path in (SOURCE, GEOMETRY, PREDECESSOR, CONTRACT, MANIFEST))
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY), "PAH-OMC-005": sha(PREDECESSOR), "PAH-OMC-006": sha(CONTRACT), "PAH-OMC-006-MANIFEST": sha(MANIFEST)}
    check("source-hashes", hashes["PAH-001"] == manifest["functional_source"]["sha256"] and hashes["PAH-OMC-004"] == manifest["geometric_source"]["sha256"] and hashes["PAH-OMC-005"] == manifest["predecessor"]["sha256"] and hashes["PAH-OMC-006"] == manifest["contract"]["sha256"], hashes)
    check("identities", source.get("packet_id") == "PAH-001" and geometry.get("contract_id") == "PAH-OMC-004" and predecessor.get("contract_id") == "PAH-OMC-005" and contract.get("contract_id") == "PAH-OMC-006")
    check("formula-and-generator-pinned", source.get("functional_or_action", {}).get("formula", "").startswith("F_rho=sum_v[lambda_s") and source.get("dynamics", {}).get("generator", "").startswith("(L_rho f)(x)=sum_r m_r(x)"))
    check("fixture-charge", Q == 1 and M_PSI == 1 and contract.get("exact_scope", {}).get("fixture", {}).get("Q") == 1)
    domain = states()
    expected = (M_S + 1) ** APERTURE_BITS * K**LINK_BITS * K**PHASE_BITS * RADIAL_PLACEMENTS
    check("state-count", len(domain) == expected, {"actual": len(domain), "expected": expected})
    check("radial-relabel-invariant", all(decode(state)[3] == decode(relabel_phase_links(state))[3] for state in domain))
    records_2 = records(2, domain)
    records_3 = records(3, domain)
    projected_2 = projection(records_2)
    projected_3 = projection(records_3)
    check("rootwise-equality", projected_2 == projected_3, {"roots": len(projected_2)})
    check("midpoint-formula", all(root["rate_exponent"] == str(-BETA * Fraction(root["delta_F"]) / 2) for record in records_2 for root in record["roots"]))
    check("nonzero-observable-increment", {root["delta_ell_a"] for record in records_2 for root in record["roots"]} == {-1, 1})
    check("support-stability", all(support(2, index) == support(3, index) for index in range(RADIAL_PLACEMENTS)))
    control = boundary()
    check("boundary-control", control["nonzero_difference"] and control["difference_G2_minus_G1"] == "-1", control)
    check("no-parent-mutation", contract.get("preservation_firewall", {}).get("parent_functional_unchanged") is True and contract.get("preservation_firewall", {}).get("no_new_term") is True)
    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc006-matter-cylinder-independent/1.0",
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
        "row_identity": {"levels": [2, 3], "state_rows": len(records_2), "root_rows": len(projected_2), "canonical_digest_G2": digest_rows(records_2), "canonical_digest_G3": digest_rows(records_3), "all_equal": projected_2 == projected_3, "bounded_samples_G2": records_2[:2] + records_2[-2:], "bounded_samples_G3": records_3[:2] + records_3[-2:]},
        "boundary_control": control,
        "verdict": "EXACT_NONZERO_Q_MATTER_DENSITY_CYLINDER_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "reproduction": {"command": "python codes/foundations/pah_omc006_matter_cylinder_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc006-matter-cylinder/independent.json"},
        "non_claims": contract.get("non_claims", []),
        "next_question": contract.get("single_next_question"),
    }
    write_json(args.output, payload)
    print(f"{AUDIT_ID} INDEPENDENT {payload['verification']} {payload['passed']}/{payload['assertion_count']}; states={len(domain)}; roots={len(projected_2)}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
